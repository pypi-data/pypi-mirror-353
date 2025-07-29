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
from torch.optim import LBFGS
from torch.nn.functional import nll_loss, log_softmax

class Monitor(BaseMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    TemperatureScalingMonitor - using the energy score

    paper: https://arxiv.org/pdf/1706.04599.pdf
    Title: On Calibration of Modern Neural Networks
    Authors: C Guo, G Pleiss, Y Sun
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

        self._temperature = 1
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
        energy = self.get_scores(input)
        return energy <= self.threshold

    def get_scores(self, input: DataLoader) -> np.ndarray:
        """
        Given an input to the NN, get the energy scores for each input

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: Array[bool]
        :return: an array of the energy scores
        """
        output = []
        for idx, (images, labels) in enumerate(input):
            with torch.no_grad():
                logits = self._model(images)
                energy = self._temperature * torch.logsumexp(logits / self._temperature, axis=1)
                output.append(energy)
        if self._model.device()=='cuda':
            torch.cuda.empty_cache()
        return torch.cat(output).cpu().detach().numpy()

    def fit(self):
        """
        Initialize the monitor. Get all possible energy-scores on the training dataset to set the bounds for the
         threshold parameter.
        """
        train_input = self.data.get_ID_train()
        logits = self._model(train_input)
        labels = self.data.get_ID_train_labels()
        temperature = torch.nn.Parameter(torch.tensor(1.0))
        optimizer = LBFGS([temperature], lr=0.01, max_iter=50)
        with torch.no_grad():
            loss = nll_loss(log_softmax(logits / temperature), labels).item()

        def closure():
            optimizer.zero_grad()
            loss = nll_loss(log_softmax(logits / temperature), labels)
            loss.backward()
            return loss

        optimizer.step(closure)

        with torch.no_grad():
            loss = nll_loss(log_softmax(logits / temperature), labels).item()

        self._temperature = temperature.item()
        logging.debug(f"Optimal temperature: {self._temperature}")
        logging.debug(f"NLL after scaling: {loss:.2f}'")

        energy = self.get_scores(train_input)
        self._bounds['threshold'] = FloatBounds(min(energy), max(energy))
        logging.debug(
            f"Set the bounds for the threshold to {self._bounds['threshold'].lower, self._bounds['threshold'].upper}.")
        super().fit()
