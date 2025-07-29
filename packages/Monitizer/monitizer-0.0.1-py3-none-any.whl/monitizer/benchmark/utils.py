# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import torch
from monitizer.benchmark.networks.cifar_10 import Net, Net2


def load_cifar10_network_net1(root):
    model = Net()
    model.load_state_dict(torch.load(root + "networks/cifar_net"))
    return model


def load_cifar10_network(root):
    model = torch.load(root + "networks/CIFAR10-VGG11")
    return model
