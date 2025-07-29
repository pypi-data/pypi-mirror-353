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
from monitizer.monitors.MDSMonitor import Monitor as MDSMonitor
import torch
from torch.utils.data import DataLoader
from monitizer.monitors.Bounds import FloatBounds
from sklearn.covariance import empirical_covariance


class Monitor(MDSMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    Paper:  <https://arxiv.org/pdf/2106.09022.pdf>
    Relative Mahalanobis Distance
    Title: A Simple Fix to Mahalanobis Distance for Improving Near-OOD Detection
    Authors:Ren, Jie and Fort, Stanislav and Liu, Jeremiah and Roy, Abhijit Guha and Padhy, Shreyas and Lakshminarayanan, Balaji
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
            'layer_indices': None,
        }

        # bounds for temperature are hard-coded and set to 1, for simplicity
        self._bounds = {'threshold': FloatBounds(0, 0)}

        # other parameters
        self._background_means = {}
        self._background_stds = {}
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
        if "layer_indices" in parameters:
            self._parameters['layer_Indices'] = parameters['layer_indices']

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
        scores = self.get_scores(input)
        return scores <= self.threshold

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
            acti = self._model.get_activations_single(images, grad=False)
            layer_outputs = []
            for layer in acti:
                class_values = []
                for label in self._labels:
                    centered = acti[layer] - self._means[layer][label].repeat(len(labels), 1)
                    c = torch.matmul(centered[:, None, :], self._stds[layer]
                    #[label].repeat(len(labels), 1, 1)
                    )
                    c = torch.matmul(c, centered[:, :, None])
                    c = c[:, 0, 0]
                    class_values.append(c)
                class_values = torch.stack(class_values)
                c_hat = torch.min(class_values, dim=0)[0]
                centered = acti[layer] - self._background_means[layer].repeat(len(labels), 1)
                c = torch.matmul(centered[:, None, :], self._background_stds[layer].repeat(len(labels), 1, 1))
                c = torch.matmul(c, centered[:, :, None])
                base_distance = c[:, 0, 0]
                confidences = base_distance - c_hat
                layer_outputs.append(confidences)
            layer_outputs = torch.stack(layer_outputs)
            output = torch.sum(layer_outputs * self.weights[:, None], dim=0)
            outputs.append(output)
        if self._model.device()=='cuda':
            torch.cuda.empty_cache()
        return torch.cat(outputs).cpu().detach().numpy()

    def get_background_gaussian(self, activations):
        for layer in activations:
            relevant_features = activations[layer]
            mean = torch.mean(relevant_features, dim=0)
            std = empirical_covariance(relevant_features.detach().numpy())
            std = torch.Tensor(np.linalg.pinv(std))
            self._background_means[layer] = mean
            self._background_stds[layer] = std

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
        self.get_background_gaussian(acti)
        self._parameters['weights'] = torch.Tensor([1] * len(self.layer_indices))

        scores = self.get_scores(train_input)
        self._bounds['threshold'] = FloatBounds(min(scores), max(scores))
        logging.debug(
            f"Set the bounds for the threshold to {self._bounds['threshold'].lower, self._bounds['threshold'].upper}.")
        logging.debug("Monitor is initialized.")
        self._initialized = True
