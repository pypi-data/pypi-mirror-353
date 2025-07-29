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
from sklearn.covariance import empirical_covariance


class Monitor(BaseMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    VIM
    paper: 'ArXiv <https://arxiv.org/abs/2203.10807>`
    Implementation: `GitHub <https://github.com/haoqiwang/vim/>`
    Title: ViM: Out-Of-Distribution with Virtual-logit Matching
    Authors: Haoqi Wang, Zhizhong Li, Litong Feng, Wayne Zhang
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
            'dimension': 1,
            'threshold': 0,
        }

        # bounds for temperature are hard-coded and set to 1, for simplicity
        self._bounds = {'threshold': FloatBounds(0, 0), 'dimension': IntegerBounds(1, 1)}

        # other parameter
        self._u = None
        self._subspace = None
        self._alpha = None
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
        if "dimension" in parameters:
            self._parameters['dimension'] = parameters["dimension"]

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

    def get_scores(self, input: DataLoader) -> np.array:
        """
        Given an input to the NN, get the scores for each input

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: Array[bool]
        :return: an array of the scores
        """
        acti = self._model.get_activations_loader(input)
        x = acti[list(acti.keys())[-2]]
        logits = acti[list(acti.keys())[-1]]

        x_p_t = torch.norm(torch.matmul(x - self._u, self._subspace), dim=-1)
        vlogit = x_p_t * self._alpha
        energy = torch.logsumexp(torch.clip(logits, -100, 100), dim=-1)
        score = -vlogit + energy
        if self._model.device()=='cuda':
            torch.cuda.empty_cache()
        return -score.numpy()

    def fit(self):
        """
        Initialize the monitor. Get all possible energy-scores on the training dataset to set the bounds for the
         threshold parameter.
        """
        # compute offset
        w, b = self._model.get_last_weights()
        self._u = torch.Tensor(-np.matmul(np.linalg.pinv(w.detach().numpy()), b.detach().numpy()))

        train_data = self.data.get_ID_train()
        acti = self._model.get_activations_loader(train_data)
        features = acti[list(acti.keys())[-2]]
        logits = acti[list(acti.keys())[-1]]

        cov = empirical_covariance((features - self._u).numpy(), assume_centered=True)
        eigen_vals, eigen_vectors = np.linalg.eig(cov)

        eigvals_idx = np.argsort(eigen_vals * -1)[self.dimension:]
        self._subspace = torch.Tensor(np.ascontiguousarray((eigen_vectors.T[eigvals_idx]).T))

        # calculate residual
        x_p_t = torch.matmul(features - self._u, self._subspace)
        vlogits = torch.norm(x_p_t, dim=-1)
        self._alpha = logits.max(axis=-1)[0].mean() / vlogits.mean()

        scores = self.get_scores(train_data)
        self._bounds['threshold'] = FloatBounds(min(scores), max(scores))
        self._bounds['dimension'] = IntegerBounds(1, features.shape[1]-1)
        logging.debug(
            f"Set the bounds for the threshold to {self._bounds['threshold'].lower, self._bounds['threshold'].upper}.")
        super().fit()
