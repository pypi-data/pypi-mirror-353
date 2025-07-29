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
from monitizer.monitors.EnergyMonitor import Monitor as EnergyMonitor
import torch
from torch.utils.data import DataLoader
from monitizer.monitors.Bounds import FloatBounds


class Monitor(EnergyMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    paper: ArXiv <https://arxiv.org/abs/2111.09805>
    Title: DICE: Leveraging Sparsification for Out-of-Distribution Detection
    Authors: Yiyou Sun, Yixuan Li
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
            'percentile':0.5,
        }

        # bounds for temperature are hard-coded and set to 1, for simplicity
        self._bounds = {'threshold': FloatBounds(0, 0), 'percentile': FloatBounds(0,1)}

        # other parameter
        self._masked_w = None
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
        if "percentile" in parameters:
            self._parameters['percentile'] = parameters["percentile"]

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
        acti = self._model.get_activations_loader(input)
        features = acti[list(acti.keys())[-2]]
        _,bias = self._model.get_last_weights()
        vote = features[:,None,:]*self._masked_w
        output = vote.sum(2) + bias
        score = torch.logsumexp(output, axis=1)
        if self._model.device()=='cuda':
            torch.cuda.empty_cache()
        return score.detach().numpy()

    def fit(self):
        """
        Initialize the monitor. Get all possible energy-scores on the training dataset to set the bounds for the
         threshold parameter.
        """
        train_input = self.data.get_ID_train()
        acti = self._model.get_activations_loader(train_input)
        features = acti[list(acti.keys())[-2]]

        mean_activation = features.mean(dim=0)
        weight, bias = self._model.get_last_weights()
        contrib = mean_activation[None, :] * weight
        threshold = np.percentile(contrib.detach().numpy(), self.percentile)
        self._masked_w = torch.where(contrib > threshold, weight, 0)

        scores = self.get_scores(train_input)
        self._bounds['threshold'] = FloatBounds(min(scores), max(scores))
        logging.debug(
            f"Set the bounds for the threshold to {self._bounds['threshold'].lower, self._bounds['threshold'].upper}.")
        logging.debug("Monitor is initialized.")
        self._initialized = True
