# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import unittest
from monitizer.evaluate import *
import pandas as pd
import os
from monitizer.monitors.EnergyMonitor import Monitor
from configparser import ConfigParser
from monitizer.benchmark.load import load
from monitizer.network.neural_network import NeuralNetwork
import torch

class TestEvaluation(unittest.TestCase):

    def test_evaluate(self):
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data: Dataset = load("MNIST", data_folder)
        nn = NeuralNetwork()
        model = torch.load('example-networks/MNIST3x100')
        nn.set_pytorch_model(model)
        energy_monitor = Monitor(nn, data)
        energy_monitor._parameters['threshold'] = 62
        evaluate(energy_monitor, "full", data, 'tests/test-files/evaluate-output')

    def test_create_line_plot(self):
        OOD_FILE = 'tests/test-files/ood.csv'
        ID_FILE = 'tests/test-files/id.csv'
        ood_results = pd.read_csv(OOD_FILE)
        id_results = pd.read_csv(ID_FILE)

        com = pd.DataFrame(ood_results[["data", "TPR"]])
        com.loc[len(com)] = ["ID", id_results["TNR"][0]]
        com = com.rename(columns={"TPR": "accuracy"})
        outputfile = f"{OOD_FILE.replace('-ood.csv', '')}"
        create_line_plot(com, outputfile)
        self.assertTrue(os.path.isfile(outputfile))
