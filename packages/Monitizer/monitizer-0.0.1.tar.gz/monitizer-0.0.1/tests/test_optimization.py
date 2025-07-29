# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import unittest
from monitizer.optimizers.optimization_functions import *
from monitizer.optimizers.optimization_config import *
from monitizer.optimizers.single_objectives import *
from monitizer.network.neural_network import *
from monitizer.monitors.EnergyMonitor import *
import torch, random, numpy, logging
from monitizer.benchmark.load import load

class TestOptimization(unittest.TestCase):

    def test_optimizeMonitor(self):
        pass

    def test_gradient_descent(self):
        config = OptimizationConfig('tests/test-files/optimization-gradient-output')
        objective = OptimalForOODClassSubjectToFNR(config)
        model = torch.load("example-networks/MNIST3x100")
        nn = NeuralNetwork()
        nn.set_pytorch_model(model)
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("MNIST", data_folder)
        monitor = Monitor(nn, data)
        monitor._set_parameters_for_optimization(monitor.get_all_parameters())
        random.seed(11)
        numpy.random.seed(11)
        logging.basicConfig(filename='tests/test-files/test-log.log', encoding='utf-8', level=logging.DEBUG,
                            format='%(levelname)s:%(message)s')
        optimize_monitor_gradient_descent(monitor, objective, config)