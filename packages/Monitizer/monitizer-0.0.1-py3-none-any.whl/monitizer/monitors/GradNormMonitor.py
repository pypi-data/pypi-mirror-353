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
from torch.utils.data import DataLoader
from monitizer.monitors.Bounds import FloatBounds
from torch.autograd import Variable


class Monitor(BaseMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    GradNorm, from paper 'https://proceedings.neurips.cc/paper_files/paper/2021/file/063e26c670d07bb7c4d30e6fc69fe056-Paper.pdf'
    Title: On the Importance of Gradients for Detecting Distributional Shifts in the Wild
    Authors: Rui Huang, Andrew Geng, Yixuan Li
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
            'temperature': 1
        }

        # bounds for temperature are hard-coded and set to 1, for simplicity
        self._bounds = {'threshold': FloatBounds(0, 0), 'temperature': FloatBounds(1, 1)}
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
        if "temperature" in parameters:
            self._parameters['temperature'] = parameters["temperature"]

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
        confs = self.get_scores(input)
        return confs <= self.threshold

    def get_scores(self, input: DataLoader) -> np.ndarray:
        """
        Given an input to the NN, get the gradnorm scores for each input

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: Array[bool]
        :return: an array of the energy scores
        """
        confs = []
        logsoftmax = torch.nn.LogSoftmax(dim=-1).to(self._model.device())
        for idx, (images, labels) in enumerate(input):
            inputs = Variable(images.to(self._model.device()), requires_grad=True)
            self._model._model.zero_grad()

            outputs = self._model(inputs, grad=True).to(self._model.device())
            targets = torch.ones((inputs.shape[0], self._model.get_num_output_classes())).to(self._model.device())
            outputs = outputs / self.temperature
            loss = torch.mean(torch.sum(-targets * logsoftmax(outputs), dim=-1))

            loss.backward()

            layer_grad = self._model.get_last_layer_gradients()

            layer_grad_norm = torch.sum(torch.abs(layer_grad)).cpu()
            confs.append(layer_grad_norm.detach().numpy())
        if self._model.device() == 'cuda':
            torch.cuda.empty_cache()
        return np.array(confs)

    def fit(self):
        """
        Initialize the monitor. Get all possible energy-scores on the training dataset to set the bounds for the
         threshold parameter.
        """
        train_input = self.data.get_ID_train()
        confs = self.get_scores(train_input)
        self._bounds['threshold'] = FloatBounds(min(confs), max(confs))
        logging.debug(
            f"Set the bounds for the threshold to {self._bounds['threshold'].lower, self._bounds['threshold'].upper}.")
        super().fit()
