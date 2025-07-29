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
import warnings


class Monitor(BaseMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    Paper: https://openreview.net/pdf?id=ndYXTEL6cZz
    Title: EXTREMELY SIMPLE ACTIVATION SHAPING FOR OUT-OF-DISTRIBUTION DETECTION
    Authors: Andrija Djurisic, Nebojsa Bozanic, Arjun Ashok, Rosanne Liu
    """

    def __init__(self, model: NeuralNetwork, data: Dataset, version: str="ash_p", parameters_for_optimization: [str] = None):
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
            'percentile': 65,
        }

        # bounds for temperature are hard-coded and set to 1, for simplicity
        self._bounds = {'threshold': FloatBounds(0, 0), 'layer': IntegerBounds(1, 1),
                        'percentile': IntegerBounds(1, 99)}

        # other parameter
        self._layer_names = self._model.get_feature_layer_names()
        self._type = version
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
        elif "layer" in parameters:
            assert parameters["layer"] < len(self._layer_names)
            self._parameters['layer'] = parameters["layer"]
        elif "percentile" in parameters:
            assert parameters["percentile"] < 100
            assert parameters["percentile"] > 0
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
        energy = self.get_scores(input)
        return energy <= self.threshold

    def ash_process(self, x: torch.Tensor) -> torch.Tensor:
        if self._type == "ash_b":
            return self.ash_b(x)
        elif self._type == "ash_p":
            return self.ash_p(x)
        elif self._type == "ash_s":
            return self.ash_s(x)
        elif self._type == "ash_rand":
            return self.ash_rand(x)
        elif self._type == "ash":
            warnings.warn("Please select 'ash_b', 'ash_p', 'ash_s' or 'ash_rand! Proceeding with ash_p.")
            return self.ash_p(x)

    def ash_b(self, x: torch.Tensor) -> torch.Tensor:
        """
        adapted from 'https://github.com/andrijazz/ash/blob/main/ash.py'
        """
        b = x.shape[0]

        # calculate the sum of the input per sample
        s1 = x.sum(dim=list(range(len(x.shape)))[1:])

        n = x.shape[1:].numel()
        k = n - int(np.round(n * self.percentile / 100.0))
        t = x.view((b, n))
        v, i = torch.topk(t, k, dim=1)
        fill = s1 / k
        fill = fill.unsqueeze(dim=1).expand(v.shape)
        t.zero_().scatter_(dim=1, index=i, src=fill)
        return x

    def ash_p(self, x: torch.Tensor) -> torch.Tensor:
        """
        adapted from 'https://github.com/andrijazz/ash/blob/main/ash.py'
        """
        b = x.shape[0]

        n = x.shape[1:].numel()
        k = n - int(np.round(n * self.percentile / 100.0))
        t = x.view((b, n))
        v, i = torch.topk(t, k, dim=1)
        t.zero_().scatter_(dim=1, index=i, src=v)

        return x

    def ash_s(self, x: torch.Tensor) -> torch.Tensor:
        """
        adapted from 'https://github.com/andrijazz/ash/blob/main/ash.py'
        """
        b = x.shape[0]

        # calculate the sum of the input per sample
        s1 = x.sum(dim=list(range(len(x.shape)))[1:])
        n = x.shape[1:].numel()
        k = n - int(np.round(n * self.percentile / 100.0))
        t = x.view((b, n))
        v, i = torch.topk(t, k, dim=1)
        t.zero_().scatter_(dim=1, index=i, src=v)

        # calculate new sum of the input per sample after pruning
        s2 = x.sum(dim=list(range(len(x.shape)))[1:])

        # apply sharpening
        scale = s1 / s2
        x = x * torch.exp(scale.view([b]+[1]*(len(x.shape)-1)))

        return x

    def ash_rand(self, x: torch.Tensor) -> torch.Tensor:
        """
        adapted from 'https://github.com/andrijazz/ash/blob/main/ash.py'
        """
        b = x.shape[0]

        n = x.shape[1:].numel()
        k = n - int(np.round(n * self.percentile / 100.0))
        t = x.view((b, n))
        v, i = torch.topk(t, k, dim=1)
        v = v.uniform_(0, 10)
        t.zero_().scatter_(dim=1, index=i, src=v)
        return x

    def get_scores(self, input: DataLoader, set_bound: bool = False) -> np.ndarray:
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
        max_val = max_val if max_val > max_val_i else max_val_i
        intermediate = self.ash_process(intermediate)
        logits = self._model.output_after(intermediate, layer_name=self._layer_names[self.layer])
        energy = torch.logsumexp(logits, axis=1)
        output.append(energy)
        if set_bound:
            self._bounds['maximum'] = FloatBounds(0.001, max_val)
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
        self._bounds['layer'] = IntegerBounds(1, len(self._layer_names) - 1)
        logging.debug(
            f"Set the bounds for the threshold to {self._bounds['threshold'].lower, self._bounds['threshold'].upper}.")
        super().fit()
