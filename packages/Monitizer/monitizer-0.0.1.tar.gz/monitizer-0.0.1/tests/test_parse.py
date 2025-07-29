# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import unittest
from monitizer.parse import *
from monitizer.network.neural_network import *
from monitizer.benchmark.dataset import Dataset
from monitizer.benchmark.datasets.datasets import get_mnist
from monitizer.optimizers.single_objectives import OptimalForOODClassSubjectToFNR
from monitizer.optimizers.multi_objectives import MultiObjective

class TestParse(unittest.TestCase):

    def test_parseMonitorTemplate(self):
        from monitizer.monitors.GaussMonitor import Monitor as GaussMonitor
        from monitizer.monitors.ASHMonitor import Monitor as AshMonitor
        from monitizer.monitors.BoxMonitor import Monitor as BoxMonitor
        from monitizer.monitors.DICEMonitor import Monitor as DICEMonitor
        from monitizer.monitors.EntropyMonitor import Monitor as EntropyMonitor
        from monitizer.monitors.EnergyMonitor import Monitor as EnergyMonitor
        from monitizer.monitors.KLMatchingMonitor import Monitor as KLMatchingMonitor
        from monitizer.monitors.KNNMonitor import Monitor as KNNMonitor
        from monitizer.monitors.MaxLogitMonitor import Monitor as MaxLogitMonitor
        from monitizer.monitors.MDSMonitor import Monitor as MDSMonitor
        from monitizer.monitors.MSPMonitor import Monitor as MSPMonitor
        from monitizer.monitors.ODINMonitor import Monitor as ODINMonitor
        from monitizer.monitors.ReActMonitor import Monitor as ReActMonitor
        from monitizer.monitors.RMDMonitor import Monitor as RMDMonitor
        from monitizer.monitors.SHEMonitor import Monitor as SHEMonitor
        from monitizer.monitors.TemperatureScalingMonitor import Monitor as TScalingMonitor
        from monitizer.monitors.VIMMonitor import Monitor as VIMMonitor
        Dataset.__abstractmethods__ = set()
        nn = NeuralNetwork()
        data = Dataset("test", get_mnist)
        monitor_template = parse_monitor_template("gauss", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, GaussMonitor))
        monitor_template = parse_monitor_template("ash_p", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, AshMonitor))
        monitor_template = parse_monitor_template("box", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, BoxMonitor))
        monitor_template = parse_monitor_template("dice", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, DICEMonitor))
        monitor_template = parse_monitor_template("entropy", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, EntropyMonitor))
        monitor_template = parse_monitor_template("energy", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, EnergyMonitor))
        monitor_template = parse_monitor_template("klmatching", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, KLMatchingMonitor))
        monitor_template = parse_monitor_template("knn", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, KNNMonitor))
        monitor_template = parse_monitor_template("maxlogit", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, MaxLogitMonitor))
        monitor_template = parse_monitor_template("mds", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, MDSMonitor))
        monitor_template = parse_monitor_template("msp", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, MSPMonitor))
        monitor_template = parse_monitor_template("odin", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, ODINMonitor))
        monitor_template = parse_monitor_template("react", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, ReActMonitor))
        monitor_template = parse_monitor_template("rmd", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, RMDMonitor))
        monitor_template = parse_monitor_template("she", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, SHEMonitor))
        monitor_template = parse_monitor_template("scaling", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, TScalingMonitor))
        monitor_template = parse_monitor_template("vim", nn, data, 47)
        self.assertTrue(isinstance(monitor_template, VIMMonitor))

    def test_parseNeuralNetworkONNX(self):
        neural_network = parse_neural_network('example-networks/MNIST3x100')
        self.assertTrue(isinstance(neural_network, NeuralNetwork))

    def test_parseDataset(self):
        dataset = parse_dataset('mnist')
        self.assertTrue(isinstance(dataset, Dataset))

    def test_parseAll(self):
        pass

    def test_parseObjective(self):
        config = OptimizationConfig("tests/test-files/optimization-objective.ini")
        objective = parse_optimization_objective(config)(config)
        self.assertIsInstance(objective, OptimalForOODClassSubjectToFNR)

        config = OptimizationConfig("tests/test-files/optimization-objective-by-user.ini")
        objective = parse_optimization_objective(config)
        print(objective)
        objective = objective(config)
        print(objective)
        self.assertIsInstance(objective, MultiObjective)

    def test_parseMonitorConfig(self):
        from monitizer.monitors.GaussMonitor import Monitor as GaussMonitor
        monitor = parse_monitor_config('tests/test-files/monitor.ini',"nn","data", 17)
        self.assertIsInstance(monitor, GaussMonitor)
        monitor = parse_monitor_config('tests/test-files/monitor2.ini', "nn", "data", 17)
        self.assertIsInstance(monitor, BaseMonitor)

    def test_parseEvaluationDatasets(self):
        dataset = parse_dataset('mnist')
        eds = ["FashionMNIST"]
        eds = parse_evaluation_datasets(eds, dataset)
        self.assertEqual(eds, ["UnseenObject/FashionMNIST"])
        eds = ["FashionMNIST", "Rotate"]
        eds = parse_evaluation_datasets(eds, dataset)
        self.assertEqual(eds, ["Perturbation/Rotate", "UnseenObject/FashionMNIST"])
        eds = ["FashionMNIST", "Whatever"]
        eds = parse_evaluation_datasets(eds, dataset)
        self.assertEqual(eds, ["UnseenObject/FashionMNIST"])

    def test_parseMonitorByUser(self):
        monitor = parse_monitor_by_user("tests/test-files/UserMonitor.py", "nn", "data", "Monitor")
        self.assertIsInstance(monitor, BaseMonitor)