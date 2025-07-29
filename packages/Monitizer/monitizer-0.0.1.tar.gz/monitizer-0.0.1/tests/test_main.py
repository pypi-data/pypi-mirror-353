# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import unittest
from monitizer.monitizer import *
from monitizer.monitors.Monitor import BaseMonitor


class TestMain(unittest.TestCase):

    def test_basicMain(self):
        monitor = run_monitizer(["energy"], None, None, None,'example-networks/MNIST3x100',
                                'tests/test-files/optimization-objective.ini',
                                "full", "MNIST", None, True, True, 'tests/test-files/results', False)
        self.assertIsInstance(monitor, BaseMonitor)

    def test_parameterByUser(self):
        monitor = run_monitizer(["energy"], None, None, None, 'example-networks/MNIST3x100',
                                'tests/test-files/optimization-objective.ini',
                                "short", "MNIST", "{'threshold':61}", False, True, 'tests/test-files/results', False)
        self.assertIsInstance(monitor, BaseMonitor)

    def test_monitorConfig(self):
        monitor = run_monitizer(None, None, None, 'tests/test-files/monitor.ini', 'example-networks/MNIST3x100',
                                'tests/test-files/optimization-objective.ini',
                                "short", "MNIST", None, True, True, 'tests/test-files/results', False)
        self.assertIsInstance(monitor, BaseMonitor)

    def test_allMonitor(self):
        #print('\n\n\n ################################# RUN ALL #############################')
        #monitor = run_monitizer('all', None, None, None, "example-networks/MNIST3x100",
        #                        None, 'auroc', 'MNIST', None, False, True, 'test/test-files/results-all', False)
        #print('########################## Done with all #########################\n\n\n')
        pass