# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from torchvision import transforms
from monitizer.benchmark.generators.distortiontransformers import To_Tensor_With_Label_Transform, \
    FGSM_Transform
from monitizer.benchmark.generators.distortiondatasets import Transform_With_Label_Dataset
from monitizer.benchmark.datasets.datasets import get_fashionmnist_set
import torch, os
from torch.utils.data import DataLoader


## Wrong Prediction --------------------------------------------------

def get_fashionmnist_fgsm_dataloader(usecase, model=None, validation_split=0.2, data_folder='./', root='./',
                                     num_workers=os.cpu_count() - 1) -> DataLoader:
    if model == None:
        model = torch.load(root + "networks/FashionMNIST")
    transform = None
    fashionmnist_trainset = get_fashionmnist_set(usecase, transform, validation_split=validation_split,
                                                 data_folder=data_folder)
    transform = transforms.Compose(
        [To_Tensor_With_Label_Transform(), FGSM_Transform(model, 0.1)])
    fashionmnist_trainset = Transform_With_Label_Dataset(fashionmnist_trainset, transform)
    testloader = DataLoader(fashionmnist_trainset, batch_size=64, shuffle=False, num_workers=num_workers)
    return testloader
