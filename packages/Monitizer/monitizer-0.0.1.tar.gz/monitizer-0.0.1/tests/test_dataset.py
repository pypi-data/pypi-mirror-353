# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import unittest

import torch.utils.data

from monitizer.benchmark.load import *
from monitizer.benchmark.dataset import Dataset
from configparser import ConfigParser


class TestDataset(unittest.TestCase):

    def test_MNIST(self):
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data: Dataset = load("MNIST", data_folder)
        test = data.get_ID_test()
        self.assertIsInstance(test, torch.utils.data.DataLoader)
        train = data.get_ID_train()
        self.assertIsInstance(train, torch.utils.data.DataLoader)
        val = data.get_ID_val()
        self.assertIsInstance(val, torch.utils.data.DataLoader)
        train_labels = data.get_ID_train_labels()
        self.assertGreater(len(train_labels), 0)

    def test_MNIST_OOD(self):
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data: Dataset = load("MNIST", data_folder)
        all_subsets = data.get_all_subset_names()
        for name in all_subsets:
            ood_set = data.get_OOD_test(name)
            self.assertIsInstance(ood_set, torch.utils.data.DataLoader)
            self.assertGreater(len(ood_set), 0)
            ood_set = data.get_OOD_val(name)
            self.assertIsInstance(ood_set, torch.utils.data.DataLoader)
            self.assertGreater(len(ood_set), 0)

    def test_CIFAR10(self):
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("CIFAR10", data_folder)
        test = data.get_ID_test()
        self.assertIsInstance(test, torch.utils.data.DataLoader)
        train = data.get_ID_train()
        self.assertIsInstance(train, torch.utils.data.DataLoader)
        val = data.get_ID_val()
        self.assertIsInstance(val, torch.utils.data.DataLoader)
        train_labels = data.get_ID_train_labels()
        self.assertGreater(len(train_labels), 0)

    def test_CIFAR10_OOD(self):
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        data = load("CIFAR10", data_folder)
        all_subsets = data.get_all_subset_names()
        for name in all_subsets:
            ood_set = data.get_OOD_test(name)
            self.assertIsInstance(ood_set, torch.utils.data.DataLoader)
            self.assertGreater(len(ood_set), 0)
            ood_set = data.get_OOD_val(name)
            self.assertIsInstance(ood_set, torch.utils.data.DataLoader)
            self.assertGreater(len(ood_set), 0)

    def test_Imagenet(self):
        import os
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        data_folder = internal_config['DEFAULT']['data_folder']
        if not os.path.isfile(os.path.join(data_folder, "ILSVRC2012_img_val.tar")) or not os.path.isfile(
                os.path.join(data_folder, "ILSVRC2012_img_train.tar")):
            return
        data = load("ImageNet", data_folder)
        all_subsets = data.get_all_subset_names()
        for name in all_subsets:
            ood_set = data.get_OOD_test(name)
            self.assertIsInstance(ood_set, torch.utils.data.DataLoader)
            self.assertGreater(len(ood_set), 0)
            ood_set = data.get_OOD_val(name)
            self.assertIsInstance(ood_set, torch.utils.data.DataLoader)
            self.assertGreater(len(ood_set), 0)
