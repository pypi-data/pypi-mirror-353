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
    paper: `ArXiv <https://arxiv.org/abs/1911.11132>`
    Title: Scaling Out-of-Distribution Detection for Real-World Settings
    Authors: Dan Hendrycks, Steven Basart, Mantas Mazeika, Andy Zou, Joe Kwon, Mohammadreza Mostajabi, Jacob Steinhardt, Dawn Song
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
        self._dists = {}
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

        p = self._model(input).softmax(dim=1)
        predictions = p.argmax(dim=1)
        scores = torch.empty(size=(p.shape[0],))
        output = []
        for label in predictions.unique():
            if str(label.item()) not in self._dists:
                raise ValueError(f"Label {label.item()} not fitted.")
            dist = self._dists[str(label.item())]
            class_p = p[predictions == label]
            class_d = dist.unsqueeze(0).repeat(class_p.shape[0], 1)
            d_kl = class_p * (class_p / class_d)
            d_kl[d_kl == 0] = 1
            d_kl = (d_kl.log()).sum(dim=1)
            scores[predictions == label] = d_kl
        if self._model.device()=='cuda':
            torch.cuda.empty_cache()
        return scores.detach().numpy()

    def fit(self):
        """
        Initialize the monitor. Get all possible energy-scores on the training dataset to set the bounds for the
         threshold parameter.
        """
        train_input = self.data.get_ID_train()
        train_labels = self.data.get_ID_val_labels()
        acti = self._model.get_activations_loader(train_input)
        logits = acti[list(acti.keys())[-1]]
        y_hat = logits.argmax(dim=1)
        probabilities = logits.softmax(dim=1)
        for label in y_hat.unique():
            d_k = probabilities[y_hat == label].mean(dim=0)
            self._dists[str(label.item())] = d_k

        scores = self.get_scores(train_input)
        self._bounds['threshold'] = FloatBounds(min(scores), max(scores))
        logging.debug(
            f"Set the bounds for the threshold to {self._bounds['threshold'].lower, self._bounds['threshold'].upper}.")
        super().fit()
