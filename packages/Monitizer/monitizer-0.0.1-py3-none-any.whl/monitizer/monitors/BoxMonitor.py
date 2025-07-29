# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from copy import deepcopy
import numpy as np
from monitizer.network.neural_network import NeuralNetwork
from monitizer.benchmark.dataset import Dataset
from .Monitor import BaseMonitor
import torch
from torch.utils.data import DataLoader
from .Bounds import UniqueList
from monitizer.monitors.abstraction import AbstractionVector
from monitizer.monitors.abstraction.BoxAbstraction import BoxAbstraction
from monitizer.monitors.abstraction.Clusters import cluster_refinement
from monitizer.monitors.Bounds import FloatBounds
from sklearn.utils._testing import ignore_warnings
from sklearn.exceptions import ConvergenceWarning


class Monitor(BaseMonitor):
    """
    Class that contains a monitor for a specific model and dataset
    Out-of-the-box - a boolean monitor, based on the idea of layer -> abstraction
    Title: Outside the Box: Abstraction-Based Monitoring of Neural Networks
    Authors: Thomas Henzinger, Anna Lukina, Christian Schilling
    """

    def __init__(self, model: NeuralNetwork, data: Dataset, seed: int, parameters_for_optimization: [str] = None):
        """
        Initializes the monitor

        :param model: the neural network which the monitor should watch
        :type model: monitizer.network.NeuralNetwork
        :param data: the representation of the dataset
        :type data: monitizer.benchmark.dataset.Dataset
        :param seed: random seed for the clustering
        :type seed: int
        :param parameters_for_optimization: set which parameters should be optimized, defaults to None (i.e.,
         all parameters)
        :type parameters_for_optimization: list(str)
        """
        super().__init__(model, data, parameters_for_optimization)

        # parameters
        self._parameters = {'layer_indices': [7],
                            'clustering_threshold': 0.07}

        self._layer2abstraction = None
        self._layer2values = None
        self._n_clusters = None
        self._seed = seed

        # for every 'known'-class we have an abstraction
        self._bounds = {"layer_indices": UniqueList([]), "clustering_threshold": FloatBounds(0, 0)}

    # working idea: which layers and what threshold
    # i need to learn both of these, abstraction should be fix to nothing to learn
    def set_parameters(self, parameters: dict):
        """
        Sets the parameters of the monitor

        :param parameters: the given parameter values
        :type parameters: mapping of parameter-name to parameter-value
        :rtype: None
        """
        if 'layer_indices' in parameters:
            self._parameters['layer_indices'] = parameters['layer_indices']
        if 'clustering_threshold' in parameters:
            self._parameters['clustering_threshold'] = parameters['clustering_threshold']

    def fit(self, layers=None, *args, **kwargs):
        self._parameters['layer_indices'] = []

        if layers is not None:
            self._parameters['layer_indices'] = layers
        else:
            self._parameters['layer_indices'] = []

        self.get_monitor()
        assert (self.layer_indices is not None)
        self._bounds['layer_indices'] = UniqueList(self.layer_indices)
        self._bounds['clustering_threshold'] = FloatBounds(0.8, 0.13)
        super().fit()

    def evaluate(self, input: DataLoader) -> np.ndarray:
        """
        get abstraction boxes for all the layers that we want to watch
        then check if the input is out of the abstraction

        :param input: DataLoader containing the input
        :type input: DataLoader
        :rtype: Array[bool]
        :return: an array of results of the monitor. One entry per input, where True: for DANGER, False: for we trust
         the input
        """
        layer2values = self._model.get_activations_loader(input, layers=self.layer_indices, size=len(input.dataset))
        predictions = np.argmax(np.array(self._model(input)), axis=1)

        # for layer, abstraction in self._layer2abstraction.items():
        # one value for each input to the NN
        acceptance = [[] for _ in layer2values[self.layer_indices[0]]]
        # iterate over the layers and check whether each layer accepts each input
        for layer in self.layer_indices:
            for j, vj in enumerate(layer2values[layer]):
                c_predicted = predictions[j]
                # accepts, confidence = abstraction.isknown(c_predicted, vj.numpy())
                accepts, confidence = self._layer2abstraction[layer].isknown(c_predicted, vj.numpy())
                acceptance[j].append(accepts)

        results = np.all(np.array(acceptance), axis=1)
        return results

    def get_scores(self, input: torch.utils.data.DataLoader) -> np.ndarray:
        """
        This function does not work on the Box monitor
        """
        raise RuntimeWarning(
            "The Box monitor does not have a single threshold and thus does not compute 'scores'.")
        return None

    def get_auroc_score(self, id_data: torch.utils.data.DataLoader, ood_data: torch.utils.data.DataLoader) -> float:
        '''
        The Box monitor does not have a single threshold,t therefore we cannot compute the AUROC
        '''
        raise RuntimeWarning(
            "The Box monitor does not have a single threshold,t therefore we cannot compute the AUROC.")
        return 0

    # the abstraction boxes are computed using KMeans clustering
    def watch_layer_activation(self, dataloader: DataLoader, layer_name) -> np.ndarray:
        # Initialize an empty list to store activations for each input batch
        activations = []

        # Define a hook function to capture the layer's output activations
        def hook_fn(module, input, output):
            # Append the output activations to the list after detaching from the computation graph
            # and moving to the CPU
            activations.append(output.detach().cpu().numpy)

        # Attach the hook function to the specified layer in the model
        # Using 'getattr', fetch a specific layer by its name
        hook = getattr(self._model, layer_name).register_forward_hook(hook_fn)

        # Disable gradient computation to improve performance during inference
        with torch.no_grad():
            for images, labels in dataloader:
                # Forward pass: Process each batch of images through the network
                # The hook function will capture the activations for the specified layer
                self._model(images)

        # Remove the hook to ensure it doesn't affect future forward passes
        hook.remove()

        # Convert the list of activations into a single numpy array for easier analysis
        return np.concatenate(activations, axis=0)

    def watch(self, dataloader: DataLoader) -> dict:
        """
        Monitor and capture the activations of specified layers when processing the input data.

        :param dataloader: DataLoader providing batches of input data for monitoring.
        :return: A dictionary mapping layer names to their corresponding activation vectors.
        """

        # Dictionary to store activations for each specified layer
        layers_activations = {}

        # Iterate over each layer index
        for layer in self.layer_indices:
            # For each layer, fetch its activations when processing the input data
            # The watch_layer_activation function returns a numpy array of activations for the specified layer
            layers_activations[layer] = self.watch_layer_activation(dataloader, layer)

        # Return the dictionary containing activations for all specified layers
        return layers_activations

    def box_abstraction_given_layers(self):
        layer2abstraction = dict()
        for layer in self.layer_indices:
            layer2abstraction[layer] = BoxAbstraction()
        return layer2abstraction

    @ignore_warnings(category=ConvergenceWarning)
    def get_monitor(self, num_classes=10, size=0):
        """`
        Using the dataset, create the monitor
        """
        if size == 0:
            size = len(self.data.train_set)

        # layer2values = self.watch(self.data.get_ID_train())
        layer2values = self._model.get_activations_loader(self.data.get_ID_train(), layers=self.layer_indices,
                                                          size=size)
        self._parameters['layer_indices'] = list(layer2values.keys())
        self._layer2abstraction = self.box_abstraction_given_layers()
        self._layer2values = layer2values

        # extract values for watched layers

        # clustering
        layer2class2clusterer = self._clustering(self.data.get_ID_train(), layer2values=layer2values)

        # monitor training
        self._train_monitor(self.data.get_ID_train(), layer2values=layer2values,
                            layer2class2clusterer=layer2class2clusterer)

    def _clustering(self, dataloader: DataLoader, layer2values):
        #     Since the vectors collected for each class often cover different regions of the state space,
        #     we use a clustering algorithm to group the vectors based on their region.
        #     This step is not mandatory, but it is mentioned that it can improve the precision substantially.
        #     we use k-means clustering for this.
        layers = self.layer_indices
        self._normalize_abstraction(dataloader)

        # cluster classes in each layer
        layer2class2clusterer = dict()
        for layer in layers:
            class2values = dict()  # mapping: class_index -> values from watched layer
            values = layer2values[layer]
            for i, (inputs, labels) in enumerate(dataloader):
                if i == 10:
                    break
                for j, yj in enumerate(labels):
                    vj = values[j]
                    yj = yj.tolist()

                    if yj in class2values.keys():
                        class2values[yj].append(vj.numpy())
                    else:
                        class2values[yj] = [vj.numpy()]

            # find number of clusters
            # get clusters for every class
            class2clusters = cluster_refinement(class2values, threshold=self.clustering_threshold,
                                                n_clusters=self._n_clusters, seed=self._seed)

            layer2class2clusterer[layer] = class2clusters

            # update abstraction with number of clusters
            self.update_clustering(layer, class2clusters)

        return layer2class2clusterer

    def _normalize_abstraction(self, dataloader: DataLoader):
        ground_truths = []
        for data, labels in dataloader:
            ground_truths.append(labels)
        # concatenate them into a single tensor afterward
        ground_truths = torch.cat(ground_truths)
        n_classes = len(set(ground_truths.tolist()))

        layer2abstraction_new = dict()
        for layer, abstraction in self._layer2abstraction.items():  # type: int, Abstraction
            # obtain number of neurons
            n_neurons = self._layer2values[layer].shape[1]
            # normalize abstraction (wrap in AbstractionVectors)
            abstraction_new = AbstractionVector.AbstractionVector(abstraction, n_classes)
            # initialize abstraction
            abstraction_new.initialize(n_neurons)
            # update new mapping
            if layer in layer2abstraction_new:
                raise (ValueError("Duplicate layer index", layer, "found. Please use unique indexing."))
            layer2abstraction_new[layer] = abstraction_new
        self._layer2abstraction = layer2abstraction_new

    def _train_monitor(self, dataloader: DataLoader, layer2values, layer2class2clusterer):
        ground_truths = []
        for data, labels in dataloader:
            ground_truths.append(labels)
        # concatenate them into a single tensor afterward
        ground_truths = torch.cat(ground_truths)
        # n_classes = len(set(ground_truths.tolist()))
        #
        # layer2abstraction_new = dict()
        # for layer, abstraction in self._layer2abstraction.items():  # type: int, Abstraction
        #     # obtain number of neurons
        #     n_neurons = self._layer2values[layer].shape[1]
        #     # normalize abstraction (wrap in AbstractionVectors)
        #     abstraction_new = AbstractionVector.AbstractionVector(abstraction, n_classes)
        #     # initialize abstraction
        #     abstraction_new.initialize(n_neurons)
        #     # update new mapping
        #     if layer in layer2abstraction_new:
        #         raise (ValueError("Duplicate layer index", layer, "found. Please use unique indexing."))
        #     layer2abstraction_new[layer] = abstraction_new
        # self._layer2abstraction = layer2abstraction_new
        self.add_clustered(layer2values, ground_truths, layer2class2clusterer)

    def add_clustered(self, layer2values, ground_truths, layer2class2clusterer):
        for layer, abstraction_vector in self._layer2abstraction.items():
            values = layer2values[layer]

            # mapping: class_index -> values from watched layer
            class2values = dict()
            for j, yj in enumerate(ground_truths):
                vj = values[j]
                yj = yj.tolist()
                if yj in class2values:
                    class2values[yj].append(vj.numpy())
                else:
                    class2values[yj] = [vj.numpy()]

            class2clusters = layer2class2clusterer[layer]
            for class_index, values in class2values.items():
                clusterer = class2clusters[class_index]
                values_copy = deepcopy(values)  # for some reason, the list is modified below
                abstraction_vector.add_clustered(class_index, values_copy, clusterer)

    def update_clustering(self, layer: int, class2clusters: dict):
        abstraction_vector = self._layer2abstraction[layer]
        # print(abstraction_vector)
        # print("type: ", type(abstraction_vector))
        if abstraction_vector is None:
            # this monitor does not watch the given layer
            return
        # assert isinstance(abstraction_vector, AbstractionVector)
        for class_index, clusters in class2clusters.items():
            # print("class_index: ", class_index, "clusters:", clusters)
            abstraction_vector.update_clustering(class_index, clusters)
