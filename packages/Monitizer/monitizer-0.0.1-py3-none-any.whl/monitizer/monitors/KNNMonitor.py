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
from sklearn.neighbors import NearestNeighbors


class Monitor(BaseMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    paper: arXiv <https://proceedings.mlr.press/v162/sun22d.html>
    Title: Out-of-Distribution Detection with Deep Nearest Neighbors
    Authors: Yiyou Sun, Yifei Ming, Xiaojin Zhu, Yixuan Li
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

        # other parameter
        self._knn = NearestNeighbors(n_neighbors=1, n_jobs=-1)

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
        score = self.get_scores(input)
        return score <= self.threshold

    def get_scores(self, input: DataLoader) -> np.ndarray:
        """
        Given an input to the NN, get the scores for each input

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: Array[bool]
        :return: an array of the scores
        """
        output = []
        for idx, (images, labels) in enumerate(input):
            with torch.no_grad():
                predictions = self._model(images)
                dist, idx = self._knn.kneighbors(predictions.numpy(), n_neighbors=1, return_distance=True)
                output.append(np.squeeze(dist))
        if self._model.device()=='cuda':
            torch.cuda.empty_cache()
        return np.hstack(output)

    def fit(self):
        """
        Initialize the monitor. Get all possible energy-scores on the training dataset to set the bounds for the
         threshold parameter.
        """
        train_input = self.data.get_ID_train()

        train_data = self.data.get_ID_train()
        acti = self._model.get_activations_loader(train_data)
        features = acti[list(acti.keys())[-1]]

        self._knn.fit(features.numpy())

        scores = self.get_scores(train_input)
        self._bounds['threshold'] = FloatBounds(min(scores), max(scores))
        logging.debug(
            f"Set the bounds for the threshold to {self._bounds['threshold'].lower, self._bounds['threshold'].upper}.")
        super().fit()
