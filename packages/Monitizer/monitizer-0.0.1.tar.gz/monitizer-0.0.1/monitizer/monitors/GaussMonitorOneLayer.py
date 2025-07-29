# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from monitizer.benchmark.dataset import Dataset
import numpy as np
from monitizer.network.neural_network import NeuralNetwork
import torch, logging
from .Monitor import BaseMonitor
from .Bounds import UniqueList, ListOfBounds, IntegerBounds, FloatBounds


class Monitor(BaseMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    Title: Gaussian-based runtime detection of out-of-distribution inputs for neural networks
    Authors: Vahid Hashemi, Jan Kretınsky, Stefanie Mohr, and Emmanouil Seferis
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

        # Parameters
        self._parameters = {
            'thresholds': None
        }

        self._bounds = {'threshold':FloatBounds(0,0)}

        # Additional attributes
        self._layer = None

    def set_parameters(self, parameters: dict):
        """
        Sets the parameters of the monitor

        :param parameters: the given parameter values
        :type parameters: mapping of parameter-name to parameter-value
        :rtype: None
        """
        if 'threshold' in parameters.keys():
            self._parameters['threshold'] = parameters['threshold']

    def fit(self, layers=None, size=1000):
        """
        Initialize the monitor. For each layer defined in layers, get the means and standard deviations of all neurons
         for the intervals.

        :param layers: list of layers to be monitored
        :type layers: list
        :param size: number of inputs to use for training
        :type size: int
        :rtype: None
        """
        self.get_monitor(size=size, num_classes=self._model.get_num_output_classes())
        assert (self._layer is not None)
        threshold_bounds = []
        train_input = self.data.get_ID_train()
        scores = self.get_scores(train_input)
        self._bounds['threshold'] = FloatBounds(0, max(scores))
        super().fit()

    def evaluate(self, input: torch.utils.data.DataLoader) -> np.ndarray:
        """
        Given an input to the NN (input), evaluate the monitor on all the inputs and return an array of the results
        True: for OOD (alarm), False: for ID (trustworthy)

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: np.array[bool]
        :return: an array of results of the monitor. One entry per input, where True: for DANGER, False: for we trust
         the input
        """
        scores = self.get_scores(input)
        return scores <= self.threshold

    def get_monitor(self, num_classes: int, size=0):
        """`
        Using the dataset, create the monitor

        :param num_classes: number of outputs of the NN
        :type num_classes: int
        :param size: number of inputs to the NN to learn from
        :type size: int
        :rtype: None
        """
        if size == 0:
            size = len(self.data.train_set)
        # get the activation values
        acti = self._model.get_activations_loader(self.data.get_ID_train(), layers=[f'{len(self._model)-1}'], size=size)
        labels = self.data.get_ID_train_labels()
        if len(labels.shape) > 1:
            labels = torch.argmax(labels, dim=1)[:size]
        else:
            labels = labels[:size]
        self._layer = MonitorLayer(acti[f'{len(self._model)-1}'], labels, num_classes)

    def get_scores(self, input: torch.utils.data.DataLoader) -> np.ndarray:
        """
        This function does not work on the Gaussian monitor
        """
        acts = self._model.get_activations_loader(input, layers=[f'{len(self._model)-1}'], size=len(input.dataset))
        labels = np.argmax(np.array(self._model(input)), axis=1)
        scores = self._layer.vote_learning(np.array(acts[f'{len(self._model)-1}']), labels)
        return scores


class MonitorLayer:
    """
    Class that stores a monitored layer of the NN
    """

    def __init__(self, activations: np.array = None, labels: np.array = None, classes: int = 10):
        """
        Initializes the monitored layer

        :param activations: the activation values for this layer
        :type activations: Array[number, size]
        :param labels: prediction of the NN for the inputs
        :type labels: Array[number]
        :param classes: number of output classes
        :type classes: int
        """
        if activations is None:
            return
        # if len(activations.shape) > 2:
        #    raise NotImplementedError("We can't monitor convolutional layers (yet)!")

        # means and standard deviations
        self.mus = []
        self.stds = []
        for c in range(classes):
            relevant_inputs = labels == c
            self.mus.append(np.array(torch.mean(activations[relevant_inputs], dim=0)))
            self.stds.append(np.array(torch.std(activations[relevant_inputs], dim=0)))
        self.mus = np.array(self.mus)
        self.stds = np.array(self.stds)

    def __len__(self):
        return self.mus.shape[1]

    def vote(self, input: np.array, label: int) -> int:
        """
        Voting on a special input, if the input is in 2*stdev around the mean

        :param input: activation of this layer for a specific input
        :type input: Array
        :param label: prediction of this input
        :type label: int
        :rtype: int
        :return: count of all OOD-votes for this layer
        """
        assert (input.shape == self.mus[0].shape)
        # smaller than the lower bound
        res1 = (input < self.mus[label] - 2 * self.stds[label]).flatten()
        # greater than the upper bound
        res2 = (input > self.mus[label] + 2 * self.stds[label]).flatten()
        # result: outside of the interval
        return sum(res1 | res2)

    def vote_learning(self, input: np.array, labels: np.array) -> np.array:
        """
        Voting on several inputs
        Return TRUE if OOD
        Return FALSE if ID

        :param input: inputs to the NN
        :type input: Array[number, size]
        :param labels: predictions of the NN for the inputs
        :type labels: Array[number]
        :rtype: Array
        :return: list of votes
        """
        assert (input.shape[1:] == self.mus[0].shape)
        # smaller than the lower bound
        res1 = input < self.mus[labels] - 2 * self.stds[labels]
        # greater than the upper bound
        res2 = input > self.mus[labels] + 2 * self.stds[labels]
        # result: outside of the interval
        return np.sum(res1 | res2, axis=tuple(range(1, len(input.shape))))
