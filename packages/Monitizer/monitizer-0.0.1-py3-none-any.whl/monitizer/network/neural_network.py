# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import logging
import onnx
import torch
from typing import Union
import onnx2pytorch


class NeuralNetwork:
    """
    Class for storing neural networks. It includes functions to get the activation values of the NN on some input.
    """

    def __init__(self):
        self._model = None
        self._no_batch = False
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

    def set_onnx_model(self, model: onnx.ModelProto):
        """
        Converts a given onnx model to a pytorch model that will be used for internal computation.

        :param model: neural network in onnx-format
        :type model: onnx.ModelProto
        :rypte: None
        """
        self._model = onnx2pytorch.ConvertModel(model).to(self._device)
        self._no_batch = True

    def set_pytorch_model(self, model: Union[torch.nn.Module, torch.nn.Sequential]):
        """
        Stores a given pytorch-model.

        :param model: torch model
        :type model: torch.nn.Module or torch.nn.Sequential
        """
        self._model = model.to(self._device)

    def output_after(self, input: torch.Tensor, layer_name: str, grad=False):
        named_layers = dict(self._model.named_modules())
        del named_layers[""]
        layer_names = list(named_layers.keys())
        if layer_name not in layer_names:
            raise ValueError(f"The layer '{layer_name}' does not exist in the network.")
        layer_index = layer_names.index(layer_name)
        if self._no_batch:
            outputs = []
            for image in input:
                output = image.to(self._device)
                output = output[None, :]
                for layer_name in layer_names[layer_index:]:
                    output = named_layers[layer_name](output)
                outputs.append(output)
            output = torch.cat(outputs)
        else:
            output = input.to(self._device)
            for layer_name in layer_names[layer_index:]:
                output = named_layers[layer_name](output)
        if not grad:
            output = output.detach()
        output = output.cpu()
        return output

    def output_after_loader(self, input: torch.utils.data.DataLoader, layer_name: str, grad=False) -> torch.Tensor:
        named_layers = dict(self._model.named_modules())
        del named_layers[""]
        layer_names = list(named_layers.keys())
        if layer_name not in layer_names:
            raise ValueError(f"The layer '{layer_name}' does not exist in the network.")
        layer_index = layer_names.index(layer_name)
        outputs = []
        if self._no_batch:
            outputs = []
            for (images, labels) in input:
                for image in images:
                    output = image.to(self._device)
                    output = output[None, :]
                    for layer_name in layer_names[layer_index:]:
                        output = named_layers[layer_name](output)
                    outputs.append(output)
            outputs = torch.cat(outputs)
        else:
            for (images, labels) in input:
                output = images.to(self._device)
                for layer_name in layer_names[layer_index:]:
                    output = named_layers[layer_name](output)
                outputs.append(output)
            outputs = torch.cat(outputs)
        if not grad:
            outputs = outputs.detach()
        outputs = outputs.cpu()
        return outputs

    def get_activations_single(self, input: torch.Tensor, layers=[], grad=False):
        """
        Given input data to the NN, produce activation values of all (or the given) layers of the model.

        :param input: input to the NN
        :type input: DataLoader
        :param layers: for which layers to produce the activation values, defaults to [] (which results in all layers)
        :type layers: list
        :param size: the number of inputs to input to the NN, defaults to 0 (which results in all inputs given in input)
        :type size: int
        :rtype: dict
        :return: a mapping of layer-name to activations
        """

        activation = {}

        def get_activation(name):
            def hook(model, input, output):
                if grad:
                    activation[name] = output.cpu()
                else:
                    activation[name] = output.detach().cpu()

            return hook

        named_layers = dict(self._model.named_modules())
        del named_layers[""]

        delete = []
        for i, layer in enumerate(named_layers.keys()):
            if (type(named_layers[layer]) == torch.nn.modules.flatten.Flatten) or (
                    type(named_layers[layer]) == onnx2pytorch.operations.flatten.Flatten):
                delete.append(layer)
            elif len(layers) > 0 and layer not in layers:
                delete.append(layer)

        for x in delete:
            del named_layers[x]

        for i, layer in enumerate(named_layers.keys()):
            named_layers[layer].register_forward_hook(get_activation(layer))
            logging.debug(f"Getting activations for layer {layer}")

        input = input.to(self._device)
        r = self._model(input)
        return activation

    def get_feature_layer_names(self, layers=[]) -> list:
        if not self._model:
            return []
        named_layers = dict(self._model.named_modules())
        del named_layers[""]

        delete = []
        for i, layer in enumerate(named_layers.keys()):
            if (type(named_layers[layer]) == torch.nn.modules.flatten.Flatten) or (
                    type(named_layers[layer]) == onnx2pytorch.operations.flatten.Flatten):
                delete.append(layer)
            elif len(layers) > 0 and layer not in layers:
                delete.append(layer)

        for x in delete:
            del named_layers[x]
        return list(named_layers.keys())

    def get_activations_loader(self, input: torch.utils.data.DataLoader, layers=[], size=0, grad=False) -> dict:
        """
        Given input data to the NN, produce activation values of all (or the given) layers of the model.

        :param input: input to the NN
        :type input: DataLoader
        :param layers: for which layers to produce the activation values, defaults to [] (which results in all layers)
        :type layers: list
        :param size: the number of inputs to input to the NN, defaults to 0 (which results in all inputs given in input)
        :type size: int
        :rtype: dict
        :return: a mapping of layer-name to activations
        """
        # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # self._model = self._model.to(device)
        if size == 0:
            size = len(input.dataset)
            logging.debug(f"Generate {size} activation values")
        activations_total = {}
        activation = {}

        def get_activation(name):
            def hook(model, input, output):
                if grad:
                    activation[name] = output.cpu()
                else:
                    activation[name] = output.detach().cpu()

            return hook

        named_layers = dict(self._model.named_modules())
        del named_layers[""]

        delete = []
        for i, layer in enumerate(named_layers.keys()):
            if (type(named_layers[layer]) == torch.nn.modules.flatten.Flatten) or (
                    type(named_layers[layer]) == onnx2pytorch.operations.flatten.Flatten):
                delete.append(layer)
            elif len(layers) > 0 and layer not in layers:
                delete.append(layer)

        for x in delete:
            del named_layers[x]

        for i, layer in enumerate(named_layers.keys()):
            named_layers[layer].register_forward_hook(get_activation(layer))
            logging.debug(f"Getting activations for layer {layer}")

        total = 0
        for idx, (images, labels) in enumerate(input):
            if grad:
                images = images.to(self._device)
                if total >= size:
                    break
                total += len(images)
                if grad:
                    images.requires_grad = True
                if self._no_batch:
                    for image in images:
                        image = image.to(self._device)
                        output = self._model(image.unsqueeze(0)).cpu()
                        for layer in named_layers.keys():
                            if not layer in activations_total.keys():
                                activations_total[layer] = activation[layer]
                            else:
                                activations_total[layer] = torch.cat([activations_total[layer], activation[layer]])
                else:
                    r = self._model(images)
                    for layer in named_layers.keys():
                        if not layer in activations_total.keys():
                            activations_total[layer] = activation[layer]
                        else:
                            activations_total[layer] = torch.cat([activations_total[layer], activation[layer]])
            else:
                with torch.no_grad():
                    images = images.to(self._device)
                    if total >= size:
                        break
                    total += len(images)
                    if grad:
                        images.requires_grad = True
                    if self._no_batch:
                        for image in images:
                            image = image.to(self._device)
                            output = self._model(image.unsqueeze(0)).cpu()
                            for layer in named_layers.keys():
                                if not layer in activations_total.keys():
                                    activations_total[layer] = activation[layer]
                                else:
                                    activations_total[layer] = torch.cat([activations_total[layer], activation[layer]])
                    else:
                        r = self._model(images)
                        for layer in named_layers.keys():
                            if not layer in activations_total.keys():
                                activations_total[layer] = activation[layer]
                            else:
                                activations_total[layer] = torch.cat([activations_total[layer], activation[layer]])
        if not len(activations_total.keys()) == 0:
            for layer in activations_total.keys():
                if len(activations_total[layer]) > size:
                    activations_total[layer] = activations_total[layer][:size]
        return activations_total

    def __len__(self) -> int:
        """
        Return the size of the model.

        :rtype: int
        :return: the number of layers in the model
        """
        return len(self._model._modules)

    def is_initialized(self) -> bool:
        """
        Check whether this object contains an actual NN

        :rtype: bool
        :return: whether this object has been initialized
        """
        return self._model is not None

    def __call__(self, input, grad=False, *args, **kwargs):
        """
        Forward pass to the internal NN.

        Some ONNX-Pytorch converted models don't accept batches as inputs. For those, we have to unsqueeze the batches.

        :param input: the input to the NN
        """
        if type(input) == torch.utils.data.DataLoader:
            result = []
            for idx, (images, labels) in enumerate(input):
                images = images.to(self._device)
                if self._no_batch:
                    for image in images:
                        image = image.to(self._device)
                        if grad:
                            output = self._model(image.unsqueeze(0)).cpu()
                        else:
                            with torch.no_grad():
                                output = self._model(image.unsqueeze(0)).detach().cpu()
                        result.append(output)
                else:
                    if grad:
                        output = self._model(images).cpu()
                    else:
                        with torch.no_grad():
                            output = self._model(images).detach().cpu()
                    result.append(output)
            return torch.cat(result)
        else:
            if self._no_batch:
                result = []
                for image in input:
                    image = torch.Tensor(image)
                    image = image.to(self._device)
                    if grad:
                        output = self._model(image.unsqueeze(0)).cpu()
                    else:
                        with torch.no_grad():
                            output = self._model(image.unsqueeze(0)).detach().cpu()
                    result.append(output)
                return torch.cat(result)
            else:
                input = torch.Tensor(input)
                input = input.to(self._device)
                if grad:
                    result = self._model(input).cpu()
                else:
                    with torch.no_grad():
                        result = self._model(input).detach().cpu()
                return result

    def get_num_output_classes(self) -> int:
        layers: dict[str, torch.nn.Module] = dict(self._model.named_modules())
        layer_names = list(layers.keys())
        num_classes = layers[layer_names[-1]].out_features
        return num_classes

    def get_last_weights(self) -> tuple:
        layer = None
        for x in self._model.children():
            layer = x
        w = layer.weight.cpu()
        b = layer.bias.cpu()
        return w, b

    def get_last_layer_gradients(self):
        layer = None
        for x in self._model.children():
            layer = x
        return layer.weight.grad.data.cpu()

    def device(self) -> str:
        return self._device
