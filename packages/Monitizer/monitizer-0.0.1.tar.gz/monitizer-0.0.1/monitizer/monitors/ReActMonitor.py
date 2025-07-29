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
from monitizer.monitors.Bounds import FloatBounds, IntegerBounds


class Monitor(BaseMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    Paper: https://arxiv.org/abs/2111.12797
    Title: ReAct: Out-of-distribution Detection With Rectified Activations
    Authors: Yiyou Sun, Chuan Guo, Yixuan Li
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
            'layer': 1,
            'maximum' : 1,
        }

        # bounds for temperature are hard-coded and set to 1, for simplicity
        self._bounds = {'threshold': FloatBounds(0, 0), 'layer': IntegerBounds(1, 1), 'maximum': FloatBounds(1,1)}

        # other parameter
        self._layer_names = self._model.get_feature_layer_names()
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
        if "layer" in parameters:
            assert parameters["layer"] < len(self._layer_names)
            self._parameters['layer'] = parameters["layer"]
        if "maximum" in parameters:
            self._parameters["maximum"] = parameters["maximum"]

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
        energy = self.get_scores(input)
        return energy <= self.threshold

    def get_scores(self, input: DataLoader, set_bound: bool=False) -> np.ndarray:
        """
        Given an input to the NN, get the energy scores for each input

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: Array[bool]
        :return: an array of the energy scores
        """
        output = []
        max_val = 0
        intermediate = self._model.get_activations_loader(input, layers=self._layer_names[self.layer])[
            self._layer_names[self.layer]]
        max_val_i = intermediate.max().item()
        max_val = max_val if max_val> max_val_i else max_val_i
        intermediate = intermediate.clip(max=self.maximum)
        logits = self._model.output_after(intermediate, layer_name=self._layer_names[self.layer])
        energy = torch.logsumexp(logits, axis=1)
        output.append(energy)
        if set_bound:
            self._bounds['maximum'] = FloatBounds(0.001,max_val)
        if self._model.device()=='cuda':
            torch.cuda.empty_cache()
        return torch.cat(output).cpu().detach().numpy()

    def fit(self):
        """
        Initialize the monitor. Get all possible energy-scores on the training dataset to set the bounds for the
         threshold parameter.
        """
        train_input = self.data.get_ID_train()
        energy = self.get_scores(train_input, set_bound=True)
        self._bounds['threshold'] = FloatBounds(min(energy), max(energy))
        self._bounds['layer'] = IntegerBounds(1,len(self._layer_names)-1)
        logging.debug(
            f"Set the bounds for the threshold to {self._bounds['threshold'].lower, self._bounds['threshold'].upper}.")
        super().fit()
