# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import logging
import pickle
from abc import abstractmethod, ABC
import numpy as np
from monitizer.network.neural_network import NeuralNetwork
from torch.utils.data import DataLoader
from monitizer.benchmark.dataset import Dataset
import copy
from sklearn.metrics import roc_auc_score


class BaseMonitor(ABC):
    """
    Class that contains a monitor for a specific model and dataset
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
        self._model = model
        self.data = data
        self._bounds = None
        self._initialized = False
        self._parameters_for_optimization = parameters_for_optimization
        self._parameters = None

    @abstractmethod
    def evaluate(self, input: DataLoader) -> np.ndarray:
        """
        Given an input to the NN (input), evaluate the monitor on all the inputs and return an array of the results
        True: for OOD (alarm), False: for ID (trustworthy)

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: np.array[bool]
        :return: an array of results of the monitor. One entry per input, where True: for DANGER, False: for we trust
         the input
        """
        pass

    @abstractmethod
    def get_scores(self, input: DataLoader) -> np.ndarray:
        """
        Given an input to the NN (input), evaluate the monitor on all the inputs and return an array of the scores

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: np.array
        :return: an array of scores of the monitor.
        """
        pass

    @abstractmethod
    def fit(self, *args, **kwargs):
        """
        Using the dataset, create the monitor
        """
        logging.debug("Monitor is initialized.")
        self._initialized = True

    def _set_parameters_for_optimization(self, parameters: list):
        self._parameters_for_optimization = parameters

    def __getattr__(self, item):
        if item in self._parameters:
            return self._parameters[item]
        else:
            raise AttributeError

    def is_initialized(self):
        """
        Checks whether the monitor was already initialized (i.e. whether it is only a monitor template or a full
         monitor
        """
        return self._initialized

    def save(self, filename: str):
        """
        store the monitor for later use in a file
        :param filename: file where to store the monitor in
        :type filename: str
        """
        another = copy.deepcopy(self)
        another._model = None
        with open(filename, "wb") as f:
            pickle.dump(another, f)

    @classmethod
    def load(cls, filename: str) -> "BaseMonitor":
        """
        load a monitor from a file
        """
        with open(filename, "rb") as f:
            return pickle.load(f)

    @abstractmethod
    def set_parameters(self, parameters: dict):
        """
        sets the parameters of the monitor
        """
        pass

    def get_parameters(self) -> dict:
        """
        returns the parameters of this monitor that should be optimized

        :rtype: dict
        :return: mapping of parameter-name to parameter-value
        """
        parameters_for_optimization = {}
        if self._parameters_for_optimization is None:
            return {}
        for parameter in self._parameters_for_optimization:
            parameters_for_optimization[parameter] = self._parameters[parameter]
        return parameters_for_optimization

    def get_all_parameters(self) -> dict:
        """
        returns all parameters of this monitor

        :rtype: dict
        :return: mapping of parameter-name to parameter-value
        """
        return self._parameters

    def get_parameter_bounds(self) -> dict:
        """
        returns the lower and upper bound of this monitor

        :rtype: dict
        :return: dictionary of parameter to its bounds
        """
        return self._bounds

    def get_auroc_score(self, id_data: DataLoader, ood_data: DataLoader) -> float:
        '''
        Given an ID-dataset and an OOD-dataset, compute the AUROC score

        :param id_data: dataloader for the ID-dataset
        :type id_data: DataLoader
        :param ood_data: dataloader for the OOD-dataset
        :type ood_data: DataLoader
        :rtype: float
        :return: the AUROC score
        '''
        id_scores = self.get_scores(id_data)
        ood_scores = self.get_scores(ood_data)
        labels = np.zeros(len(id_scores) + len(ood_scores), dtype=np.int32)
        labels[:len(id_scores)] += 1
        examples = np.squeeze(np.hstack((id_scores, ood_scores)))

        auroc = roc_auc_score(labels, examples)
        return auroc

    def get_auroc_scores_all_test(self, subsets=None, get_confidences=False) -> np.ndarray:
        logging.debug("Compute AUROCS")
        aurocs = []
        confidences = []
        id_scores = self.get_scores(self.data.get_ID_test())
        if subsets is None:
            subsets = self.data.get_all_subset_names()
        for subset in subsets:
            logging.debug(f"    Get AUROC for {subset}")
            ood_data = self.data.get_OOD_test(subset)
            ood_scores = self.get_scores(ood_data)
            labels = np.zeros(len(id_scores) + len(ood_scores), dtype=np.int32)
            labels[:len(id_scores)] += 1
            examples = np.squeeze(np.hstack((id_scores, ood_scores)))
            auroc = roc_auc_score(labels, examples)
            N1 = sum(labels == 1)
            N2 = sum(labels != 1)
            Q1 = auroc / (2 - auroc)
            Q2 = 2 * auroc ** 2 / (1 + auroc)
            SE_auroc = np.sqrt(
                (auroc * (1 - auroc) + (N1 - 1) * (Q1 - auroc ** 2) + (N2 - 1) * (Q2 - auroc ** 2)) / (N1 * N2))
            lower = np.clip(auroc - 1.96 * SE_auroc, 0, 1)
            upper = np.clip(auroc + 1.96 * SE_auroc, 0, 1)
            confidences.append([lower, upper])
            aurocs.append(auroc)
        if get_confidences:
            return np.hstack([np.array(aurocs)[...,np.newaxis],confidences]).T
        return np.array(aurocs)
