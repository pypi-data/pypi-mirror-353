# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import logging
from monitizer.benchmark.dataset import Dataset
import numpy as np
from monitizer.network.neural_network import NeuralNetwork
from monitizer.monitors.Monitor import BaseMonitor
import torch
from sklearn.covariance import empirical_covariance
from torch.utils.data import DataLoader
from monitizer.monitors.Bounds import FloatBounds, UniqueList, ListOfBounds


class Monitor(BaseMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    Paper: 'NeurIPS <https://papers.nips.cc/paper_files/paper/2018/file/abdeb6f575ac5c6676b747bca8d09cc2-Paper.pdf>`
    Title: A Simple Unified Framework for Detecting Out-of-Distribution Samples and Adversarial Attacks
    Authors: Kimin Lee, Kibok Lee, Honglak Lee, Jinwoo Shin
    """

    def __init__(self, model: NeuralNetwork, data: Dataset, parameters_for_optimization: [str] = None):
        """
        Initializes the monitor

        :param model: the neural network which the monitor should watch
        :type model: monitizer.network.NeuralNetwork
        :param data: the representation of the dataset
        :type data: monitizer.benchmark.dataset.Dataset
        :param parameters_for_optimization: set which parameters should be optimized, defaults to None (i.e.,
         all parameters)
        :type parameters_for_optimization: list(str)
        """
        super().__init__(model, data, parameters_for_optimization)

        # parameters
        self._parameters = {
            'threshold': 0,
            'perturbation': 0.0014,
            'layer_indices': None,
            'weights': None
        }

        # bounds for temperature are hard-coded and set to 1, for simplicity
        self._bounds = {'threshold': FloatBounds(0, 0), 'layer_indices': UniqueList([]),
                        'perturbation': FloatBounds(0, 0.1),
                        'weights': ListOfBounds([])}

        self._labels = None
        self._means = None
        self._stds = None
        return

    def set_parameters(self, parameters: dict):
        """
        Sets the parameters of the monitor

        :param parameters: the given parameter values
        :type parameters: mapping of parameter-name to parameter-value
        :rtype: None
        """
        if "threshold" in parameters:
            self._parameters['threshold'] = parameters["threshold"]
        if 'layer_indices' in parameters.keys():
            self._parameters['layer_indices'] = parameters['layer_indices']
        if "perturbation" in parameters.keys():
            self._parameters['perturbation'] = parameters["perturbation"]
        if "weights" in parameters.keys():
            assert len(parameters['weights']) == len(self.layer_indices)
            self._parameters['weights'] = parameters['weights']

    def evaluate(self, input: DataLoader) -> np.ndarray:
        """
        Given an input to the NN (input), evaluate the monitor on all the inputs and return an array of the results
        True: for OOD (alarm), False: for ID (trustworthy)

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: Array[bool]
        :return: an array of results of the monitor. One entry per input, where True: for DANGER, False: for we trust
         the input
        """
        confidences = self.get_scores(input)
        return confidences <= self.threshold

    def get_scores(self, input: DataLoader) -> np.ndarray:
        """
        Given an input to the NN, get the confidences for each input

        Note that the covariance matrix was already inverted during setup to reduce computational overhead

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: Array[bool]
        :return: an array of the confidences
        """
        outputs = []
        for (images, labels) in input:
            images.requires_grad = True
            layer_outputs = []
            acti = self._model.get_activations_single(images, layers=self.layer_indices, grad=True)
            for layer in self._model.get_feature_layer_names(layers=self.layer_indices):
                class_values = []
                for label in self._labels:
                    centered = acti[layer] - self._means[layer][label].repeat(len(labels),1)
                    c = torch.matmul(centered[:,None,:], self._stds[layer][label].repeat(len(labels),1,1))
                    c = torch.matmul(c, centered[:,:,None])
                    c = c[:,0,0]
                    class_values.append(c)
                class_values = torch.stack(class_values)
                c_hat = torch.argmin(class_values, dim=0)
                class_values[c_hat,range(len(labels))].backward(retain_graph=True, gradient=torch.Tensor(len(labels)))
                #torch.autograd.grad(class_values[c_hat,range(len(labels))], images, grad_outputs=torch.Tensor(len(labels)), allow_unused=True, create_graph=True)
                gradient_sign = torch.ge(images.grad.detach(), 0)
                x_hat = torch.add(images.detach(), gradient_sign, alpha=-self.perturbation)
                confidences = []
                #with torch.no_grad():
                acti_x_hat = self._model.get_activations_single(x_hat, layers=self.layer_indices)
                for label in self._labels:
                    centered = acti_x_hat[layer] - self._means[layer][label].repeat(len(labels), 1)
                    c = torch.matmul(centered[:, None, :], self._stds[layer][label].repeat(len(labels), 1, 1))
                    c = -torch.matmul(c, centered[:, :, None])
                    c = c[:, 0, 0]
                    confidences.append(c)
                confidences = torch.stack(confidences)
                layer_outputs.append(torch.max(confidences,dim=0)[0])
            layer_outputs = torch.stack(layer_outputs)
            output = torch.sum(layer_outputs * self.weights[:,None], dim=0)
            outputs.append(output)
        if self._model.device()=='cuda':
            torch.cuda.empty_cache()
        return torch.cat(outputs).detach().cpu().numpy()

    def get_mean_stds(self, train_input, activations, train_labels):
        """

        """
        for layer in activations:
            means = []
            stds = []
            for label in self._labels:
                relevant_features = activations[layer][train_labels == label]
                mean = torch.mean(relevant_features, dim=0)
                std = empirical_covariance(relevant_features.detach().numpy())
                std = np.linalg.pinv(std)
                means.append(mean)
                stds.append(torch.Tensor(std))
            self._means[layer] = torch.stack(means)
            self._stds[layer] = torch.stack(stds)
        self._parameters['layer_indices'] = list(activations.keys())


    def fit(self, layers=None):
        """
        Initialize the monitor. Get all possible energy-scores on the training dataset to set the bounds for the
         threshold parameter.

        :param layers: list of layers to be monitored
        :type layers: list
        """
        if layers is not None:
            self._parameters['layer_indices'] = layers
        else:
            self._parameters['layer_indices'] = []

        self._means = {}
        self._stds = {}

        train_input = self.data.get_ID_val()
        train_labels = self.data.get_ID_val_labels()
        acti = self._model.get_activations_loader(train_input, layers=self.layer_indices, grad=False)
        self._labels = list(range(self._model.get_num_output_classes()))

        self.get_mean_stds(train_input, acti, train_labels)

        self._parameters['weights'] = torch.Tensor([1]*len(self.layer_indices))

        confidences = self.get_scores(train_input)

        weight_bounds = []
        for layer_index in self.layer_indices:
            weight_bounds.append(FloatBounds(-10, 10))
        self._bounds['weights'] = ListOfBounds(weight_bounds)
        self._bounds['layer_indices'] = UniqueList(self.layer_indices)
        self._bounds['threshold'] = FloatBounds(min(confidences), max(confidences))

        logging.debug(
            f"Set the bounds for the threshold to {self._bounds['threshold'].lower, self._bounds['threshold'].upper}.")
        super().fit()
