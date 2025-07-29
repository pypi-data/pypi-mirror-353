# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import unittest

import onnx.onnx_ml_pb2
import torch
from configparser import ConfigParser
from monitizer.network.neural_network import *
from monitizer.benchmark.load import load


class TestNetwork(unittest.TestCase):

    def test_init(self):
        model = NeuralNetwork()
        self.assertEqual(model._model, None)


class TestPytorch(unittest.TestCase):
    def test_load_torch(self):
        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)

    def test_activations_single(self):
        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        test_tensor = torch.rand(1, 28, 28)
        acti = nn.get_activations_single(test_tensor)
        self.assertEqual(len(acti), 7)
        self.assertEqual(acti['7'].shape, torch.Size([1, 10]))

    def test_activations_single_gradient(self):
        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        test_tensor = torch.rand(1, 28, 28)
        acti = nn.get_activations_single(test_tensor, grad=True)
        self.assertEqual(len(acti), 7)
        self.assertEqual(acti['7'].shape, torch.Size([1, 10]))
        self.assertIsNotNone(acti['7'].grad_fn)

    def test_activations_loader(self):
        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)

        acti = nn.get_activations_loader(data.get_ID_test())
        self.assertEqual(len(acti), 7)
        self.assertEqual(acti['7'].shape, torch.Size([10000, 10]))

    def test_call(self):
        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)

        output = nn(data.get_ID_test())
        self.assertEqual(output.shape, torch.Size([10000, 10]))

    def test_output_after(self):
        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)

        output = nn.get_activations_loader(data.get_ID_test(), layers=['3'])['3']
        final_output = nn.output_after(output, '4')

        direct_output = nn(data.get_ID_test())
        self.assertTrue(((final_output - direct_output) < 1e-5).all())


class TestONNX(unittest.TestCase):
    def test_load_onnx(self):
        model = onnx.load_model("example-networks/ONNX-MNIST3x100.onnx")
        nn = NeuralNetwork()
        nn.set_onnx_model(model)

    def test_activations_single(self):
        model = onnx.load_model("example-networks/ONNX-MNIST3x100.onnx")
        nn = NeuralNetwork()
        nn.set_onnx_model(model)
        test_tensor = torch.rand(1, 28, 28)
        acti = nn.get_activations_single(test_tensor)
        self.assertEqual(len(acti), 7)
        self.assertEqual(acti[list(acti.keys())[-1]].shape, torch.Size([1, 10]))

    def test_activations_single_gradient(self):
        model = onnx.load_model("example-networks/ONNX-MNIST3x100.onnx")
        nn = NeuralNetwork()
        nn.set_onnx_model(model)
        test_tensor = torch.rand(1, 28, 28)
        acti = nn.get_activations_single(test_tensor, grad=True)
        self.assertEqual(len(acti), 7)
        self.assertEqual(acti[list(acti.keys())[-1]].shape, torch.Size([1, 10]))
        self.assertIsNotNone(acti[list(acti.keys())[-1]].grad_fn)

    def test_activations_loader(self):
        model = onnx.load_model("example-networks/ONNX-MNIST3x100.onnx")
        nn = NeuralNetwork()
        nn.set_onnx_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)

        acti = nn.get_activations_loader(data.get_ID_test())
        self.assertEqual(len(acti), 7)
        self.assertEqual(acti[list(acti.keys())[-1]].shape, torch.Size([10000, 10]))

    def test_call(self):
        model = onnx.load_model("example-networks/ONNX-MNIST3x100.onnx")
        nn = NeuralNetwork()
        nn.set_onnx_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)

        output = nn(data.get_ID_test())
        self.assertEqual(output.shape, torch.Size([10000, 10]))

    def test_output_after(self):
        model = onnx.load_model("example-networks/ONNX-MNIST3x100.onnx")
        nn = NeuralNetwork()
        nn.set_onnx_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)

        output = nn.get_activations_loader(data.get_ID_test(), layers=['Gemm_/3/Gemm_output_0'])[
            'Gemm_/3/Gemm_output_0']
        final_output = nn.output_after(output, 'Relu_/4/Relu_output_0')

        direct_output = nn(data.get_ID_test())
        self.assertTrue(((final_output - direct_output) < 1e-5).all())
