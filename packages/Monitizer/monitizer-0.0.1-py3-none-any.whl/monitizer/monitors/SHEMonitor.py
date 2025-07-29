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
    Simplified Hopfield Energy
    Paper: `OpenReview <https://openreview.net/pdf?id=KkazG4lgKL>`
    Title: Out-of-Distribution Detection based on In-Distribution Data Patterns Memorization with Modern Hopfield Energy
    Authors:Jinsong Zhang, Qiang Fu, Xu Chen, Lun Du, Zelin Li, Gang Wang, xiaoguang Liu, Shi Han, Dongmei Zhang
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

        # other parameters
        self._patterns = None
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
        scores = self.get_scores(input)
        return scores <= self.threshold

    def get_scores(self, input: DataLoader) -> np.ndarray:
        """
        Given an input to the NN, get the scores for each input

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: Array[bool]
        :return: an array of the scores
        """
        acti = self._model.get_activations_loader(input)
        features = acti[list(acti.keys())[-2]]
        logits = acti[list(acti.keys())[-1]]

        y_hat = logits.argmax(dim=1)
        scores = torch.sum(torch.mul(features, self._patterns[y_hat]), dim=1)
        if self._model.device()=='cuda':
            torch.cuda.empty_cache()
        return -scores.numpy()

    def fit(self):
        """
        Initialize the monitor. Get all possible energy-scores on the training dataset to set the bounds for the
         threshold parameter.
        """
        num_classes = self._model.get_num_output_classes()
        train_data = self.data.get_ID_train()
        labels = self.data.get_ID_train_labels()
        acti = self._model.get_activations_loader(train_data)
        features = acti[list(acti.keys())[-2]]
        logits = acti[list(acti.keys())[-1]]

        # select correctly classified
        y_hat = logits.argmax(dim=1)
        features = features[y_hat == labels]
        y = y_hat[y_hat == labels]

        m = []
        for class_idx in range(num_classes):
            mav = torch.mean(features[y == class_idx], dim=0)
            m.append(mav)

        self._patterns = torch.stack(m)

        scores = self.get_scores(train_data)
        self._bounds['threshold'] = FloatBounds(min(scores), max(scores))
        logging.debug(
            f"Set the bounds for the threshold to {self._bounds['threshold'].lower, self._bounds['threshold'].upper}.")
        super().fit()
