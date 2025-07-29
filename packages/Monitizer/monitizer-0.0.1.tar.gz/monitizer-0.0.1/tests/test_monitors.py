# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import unittest
from monitizer.network.neural_network import NeuralNetwork
from configparser import ConfigParser
from monitizer.benchmark.load import load


class TestBaseMonitor(unittest.TestCase):
    def test_BaseMonitor(self):
        from monitizer.monitors.Monitor import BaseMonitor
        # Test if the base monitor can be created
        BaseMonitor.__abstractmethods__ = set()
        nn = NeuralNetwork()
        bla = BaseMonitor(nn, None, None)


class TestGaussMonitor(unittest.TestCase):
    def test_GaussMonitor_init_fit(self):
        from monitizer.monitors.GaussMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.fit()
        gm.set_parameters({'thresholds': [1, 2, 3, 4, 5, 6, 7]})
        gm.evaluate(data.get_ID_val())

    def test_GaussMonitor_conv(self):
        from monitizer.monitors.GaussMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST_conv")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.fit()
        gm.set_parameters({'thresholds': [1, 2, 3, 4, 5, 7, 8, 9, 10]})
        x = gm.evaluate(data.get_ID_val())

    def test_GaussMonitor_conv_CIFAR(self):
        from monitizer.monitors.GaussMonitor import Monitor
        import torch

        model = torch.load("example-networks/CIFAR10_net2")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("CIFAR10", data_folder)
        gm = Monitor(nn, data)
        gm.fit()
        gm.set_parameters({'thresholds': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]})
        x = gm.evaluate(data.get_ID_val())


class TestBoxMonitor(unittest.TestCase):
    def test_BoxMonitor_init(self):
        from monitizer.monitors.BoxMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        boxmonitor = Monitor(nn, data, 37)
        boxmonitor.fit()
        self.assertEqual(len(boxmonitor._layer2abstraction['1']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['2']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['3']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['4']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['5']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['6']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['7']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['3']._abstractions[0].sets), 12)
        self.assertAlmostEqual(boxmonitor._layer2abstraction['3']._abstractions[0].sets[0].high[0], 3.9533515, 2)
        boxmonitor.evaluate(data.get_ID_val())

        boxmonitor = Monitor(nn, data, 1630196)
        boxmonitor.fit()
        self.assertEqual(len(boxmonitor._layer2abstraction['1']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['2']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['3']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['4']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['5']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['6']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['7']._abstractions), 10)
        self.assertEqual(len(boxmonitor._layer2abstraction['3']._abstractions[0].sets), 15)
        self.assertAlmostEqual(boxmonitor._layer2abstraction['3']._abstractions[0].sets[0].high[0], 3.828534, 2)


class TestEnergyMonitor(unittest.TestCase):
    def test_EnergyMonitor_init_fit(self):
        from monitizer.monitors.EnergyMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.fit()
        gm.set_parameters({'threshold': 50, 'temperature': 1})
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestODINMonitor(unittest.TestCase):
    def test_ODINMonitor_init_fit(self):
        from monitizer.monitors.ODINMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.fit()
        gm.set_parameters({'confidence_threshold': 50})
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestMSPMonitor(unittest.TestCase):
    def test_MSPMonitor_init_fit(self):
        from monitizer.monitors.MSPMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.fit()
        gm.set_parameters({'threshold': 50})
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestMDSMonitor(unittest.TestCase):
    def test_MDSMonitor_init_fit(self):
        from monitizer.monitors.MDSMonitor import Monitor
        import torch
        return
        # TAKES TOO LONG AND TIMES OUT
        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.fit()
        gm.set_parameters({'threshold': 50})
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestVIMMonitor(unittest.TestCase):
    def test_VIMMonitor_init_fit(self):
        from monitizer.monitors.VIMMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.set_parameters({'threshold': 50, 'dimension': 50})
        gm.fit()
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestTScalingMonitor(unittest.TestCase):
    def test_ScalingMonitor_init_fit(self):
        from monitizer.monitors.TemperatureScalingMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.set_parameters({'threshold': 50})
        gm.fit()
        print("MONITOR TEMPERATURE", gm._temperature)
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestSHEMonitor(unittest.TestCase):
    def test_SHEMonitor_init_fit(self):
        from monitizer.monitors.SHEMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.set_parameters({'threshold': 50})
        gm.fit()
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestRMDMonitor(unittest.TestCase):
    def test_RMDMonitor_init_fit(self):
        from monitizer.monitors.RMDMonitor import Monitor
        import torch
        return
        # TAKES TOO LONG AND TIMES OUT
        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder, num_workers=0)
        gm = Monitor(nn, data)
        gm.set_parameters({'threshold': 50})
        gm.fit()
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestMaxLogitMonitor(unittest.TestCase):
    def test_MaxLogitMonitor_init_fit(self):
        from monitizer.monitors.MaxLogitMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.set_parameters({'threshold': 50})
        gm.fit()
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestKNNMonitor(unittest.TestCase):
    def test_KNNMonitor_init_fit(self):
        from monitizer.monitors.KNNMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.set_parameters({'threshold': 50})
        gm.fit()
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestKLMatchingMonitor(unittest.TestCase):
    def test_KLMatchingMonitor_init_fit(self):
        from monitizer.monitors.KLMatchingMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.set_parameters({'threshold': 50})
        gm.fit()
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestEntropyMonitor(unittest.TestCase):
    def test_EntropyMonitor_init_fit(self):
        from monitizer.monitors.EntropyMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.set_parameters({'threshold': 50})
        gm.fit()
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestDICEMonitor(unittest.TestCase):
    def test_DICEMonitor_init_fit(self):
        from monitizer.monitors.DICEMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.set_parameters({'threshold': 50})
        gm.fit()
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestReActMonitor(unittest.TestCase):
    def test_ReActMonitor_init_fit(self):
        from monitizer.monitors.ReActMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.set_parameters({'threshold': 50, 'maximum': 0.1, 'layer': 4})
        gm.fit()
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestAshMonitor(unittest.TestCase):
    def test_AshMonitor_init_fit(self):
        from monitizer.monitors.ASHMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.set_parameters({'threshold': 50, 'maximum': 0.1, 'layer': 4})
        gm.fit()
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))


class TestGradNormMonitor(unittest.TestCase):
    def test_GradNormMonitor_init_fit(self):
        from monitizer.monitors.GradNormMonitor import Monitor
        import torch

        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        gm = Monitor(nn, data)
        gm.set_parameters({'threshold': 50})
        gm.fit()
        gm.evaluate(data.get_ID_val())
        auroc = gm.get_auroc_score(data.get_ID_test(), data.get_OOD_test("Noise/Gaussian"))
