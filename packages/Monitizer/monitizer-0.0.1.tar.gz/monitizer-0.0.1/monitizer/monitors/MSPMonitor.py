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


class Monitor(BaseMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    MSP
    paper: 'ArXiv <https://arxiv.org/abs/1610.02136>`__
    Title: A  Baseline for Detecting Misclassified and Out-of-Distribution Examples in Neural Networks
    Authors: Dan Hendrycks, Kevin Gimpel
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
        }

        # bounds for temperature are hard-coded and set to 1, for simplicity
        self._bounds = {'threshold': FloatBounds(0, 0)}
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
        max_softmax = self.get_scores(input)
        return max_softmax <= self.threshold

    def get_scores(self, input: DataLoader) -> np.ndarray:
        """
        Given an input to the NN, get the maximum softmax probability for each input

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: Array[bool]
        :return: an array of the energy scores
        """
        output = []
        for idx, (images, labels) in enumerate(input):
            with torch.no_grad():
                logits = self._model(images)
                max_softmax = torch.softmax(logits, dim=1)
                max_softmax = torch.max(max_softmax, dim=1)[0]
                output.append(max_softmax)
        if self._model.device()=='cuda':
            torch.cuda.empty_cache()
        return torch.cat(output).cpu().detach().numpy()

    def fit(self):
        """
        Initialize the monitor. Get all possible energy-scores on the training dataset to set the bounds for the
         threshold parameter.
        """
        self._bounds['threshold'] = FloatBounds(0, 1)
        logging.debug(
            f"Set the bounds for the threshold to {self._bounds['threshold'].lower, self._bounds['threshold'].upper}.")
        super().fit()
