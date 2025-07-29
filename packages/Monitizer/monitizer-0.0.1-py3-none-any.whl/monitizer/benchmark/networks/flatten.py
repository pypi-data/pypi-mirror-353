# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import torch

def add_flatten_layer_to_model(name):
    filename = name
    old_model = torch.load(filename)
    modules = [torch.nn.Flatten(1,-1)]
    for layer in old_model:
        modules.append(layer)
        
    new_model = torch.nn.Sequential(*modules)
    torch.save(new_model, filename+"-flatten")

add_flatten_layer_to_model("./networks/cifar_net")