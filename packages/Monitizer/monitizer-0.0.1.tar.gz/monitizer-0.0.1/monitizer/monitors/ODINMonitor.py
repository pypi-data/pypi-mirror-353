# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from monitizer.benchmark.dataset import Dataset
import numpy as np
from monitizer.network.neural_network import NeuralNetwork
from .Monitor import BaseMonitor
import torch, logging
from torch.utils.data import DataLoader
from .Bounds import FloatBounds


class Monitor(BaseMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    ODINMonitor - using the temperature score and perturbation
    Title: Enhancing The Reliability of Out-of-distribution Image Detection in Neural Networks
    Authors: Shiyu Liang, Yixuan Li, R. Srikat
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
        # currently using the temperature and perturbation from literature
        # todo: probably we want to use hyperparameter learning for this as well
        #  to see what works good
        self._parameters = {
            'temperature': 1000,
            'perturbation': 0.0014,
            'confidence_threshold': None
        }

        self._input_std = [0.5, 0.5, 0.5]
        # the bounds for temperature and perturbation are hard-coded
        self._bounds = {'confidence_threshold': FloatBounds(0.0, 0.0),
                        'temperature': FloatBounds(1, 1),
                        'perturbation': FloatBounds(0, 0.1)}

    def set_parameters(self, parameters: dict):
        """
        Sets the parameters of the monitor

        :param parameters: the given parameter values
        :type parameters: mapping of parameter-name to parameter-value
        :rtype: None
        """
        if "confidence_threshold" in parameters.keys():
            self._parameters['confidence_threshold'] = parameters["confidence_threshold"]
        if "temperature" in parameters.keys():
            self._parameters['temperature'] = parameters["temperature"]
        if "perturbation" in parameters.keys():
            self._parameters['perturbation'] = parameters["perturbation"]

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
        confidence = self.get_scores(input)
        return confidence <= self.confidence_threshold

    def get_scores(self, input: DataLoader) -> np.ndarray:
        """
        Given an input to the NN, get the ODIN scores for each input

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: Array[bool]
        :return: an array of the scores
        """
        confidences = []
        criterion = torch.nn.CrossEntropyLoss()  # Cross-entropy loss for calculating perturbation
        for idx, (images, labels) in enumerate(input):
            # Forward pass for initial output
            if not images.requires_grad:
                images.requires_grad = True
            if not images.retains_grad:
                images.retain_grad()

            logits = self._model(images, grad=True)
            # Computing the perturbation
            labels = logits.detach().argmax(dim=1)
            logits_temp_scaled = logits / self.temperature  # Apply temperature scaling
            loss = criterion(logits_temp_scaled, labels)

            loss.backward()
            # Normalizing the gradient to binary in {0, 1}
            gradient = torch.ge(images.grad.detach(), 0)
            gradient = (gradient.float() - 0.5) * 2

            gradient[:, 0] /= self._input_std[0]
            # gradient[:, 1] /= self._input_std[1]
            # gradient[:, 2] /= self._input_std[2]

            # Add perturbation to images
            perturbed_images = torch.add(images.detach(), gradient, alpha=-self.perturbation)

            # Forward pass with perturbed images
            perturbed_logits = self._model(perturbed_images)
            perturbed_logits_temp_scaled = perturbed_logits / self.temperature

            # Confidence calculation
            softmax_outputs = torch.nn.Softmax(dim=1)(perturbed_logits_temp_scaled)
            _, conf = softmax_outputs.max(dim=1)
            confidences.append(conf)
        if self._model.device()=='cuda':
            torch.cuda.empty_cache()
        return torch.cat(confidences).cpu().numpy()

    def fit(self):
        """
        Initialize the monitor. Get all possible odin-confidence-scores on the training dataset to set the bounds for the
         threshold parameter.
        """
        if self.confidence_threshold is None:
            train_input = self.data.get_ID_train()
            confidences = self.get_scores(train_input)
            self._bounds["confidence_threshold"] = FloatBounds(min(confidences), max(confidences))
            logging.debug(f"Set the bounds for the threshold to "
                          f"{self._bounds['confidence_threshold'].lower, self._bounds['confidence_threshold'].upper}.")
            super().fit()
        else:
            super().fit()
