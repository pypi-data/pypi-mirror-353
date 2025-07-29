# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from torchvision import transforms
from monitizer.benchmark.generators.distortiontransformers import To_Tensor_With_Label_Transform, \
    FGSM_Transform
from monitizer.benchmark.generators.distortiondatasets import Restricted_Index_Dataset, Transform_With_Label_Dataset
from monitizer.benchmark.datasets.datasets import get_cifar10_set, get_dtd_set, get_svhn_set, get_gtsrb_set
import torch
from torch.utils.data import DataLoader


## New World -------------------------------------------------

def get_gtsrb_dtd_dataloader(usecase, input_shape, data_folder='./', root='./') -> DataLoader:
    filename = root + f"specifications/gtsrb/dtd_list_{usecase}.txt"
    transform = transforms.Compose([transforms.ToTensor(), transforms.Resize(size=input_shape, antialias=None)])
    dtd_trainset = get_dtd_set(usecase, transform, data_folder)
    new_world_set = Restricted_Index_Dataset(dtd_trainset, filename)
    trainloader = DataLoader(new_world_set, batch_size=64, shuffle=False)
    return trainloader


def get_gtsrb_cifar10_dataloader(usecase, input_shape, validation_split=0.2, data_folder='./', root='./') -> DataLoader:
    filename = root + f"specifications/gtsrb/cifar10_list_{usecase}.txt"
    transform = transforms.Compose([transforms.ToTensor(), transforms.Resize(size=input_shape, antialias=None)])
    cifar10_trainset = get_cifar10_set(usecase, transform, validation_split, data_folder)
    new_world_set = Restricted_Index_Dataset(cifar10_trainset, filename)
    trainloader = DataLoader(new_world_set, batch_size=64, shuffle=False)
    return trainloader


def get_gtsrb_svhn_dataloader(usecase, input_size, data_folder='./', root='./') -> DataLoader:
    filename = root + f"specifications/gtsrb/svhn_list_{usecase}.txt"
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Resize(size=input_size, antialias=None)])
    svhn_trainset = get_svhn_set(usecase, transform, data_folder=data_folder)
    ood_set = Restricted_Index_Dataset(svhn_trainset, filename)
    trainloader = DataLoader(ood_set, batch_size=64, shuffle=False)
    return trainloader

## Unseen Environment -------------------------------------

## Unseen Object -------------------------------------------

# TODO: chinese dataset (how to get it in pytorch?)


## Wrong Prediction --------------------------------------------------

def get_gtsrb_fgsm_dataloader(usecase, model=None, validation_split=0.2, data_folder='./', root='./') -> DataLoader:
     if model == None:
         model = torch.load(root + "/networks/GTSRB")
     transform = None
     gtsrb_trainset = get_gtsrb_set(usecase, transform, validation_split=validation_split, data_folder=data_folder)
     transform = transforms.Compose(
         [To_Tensor_With_Label_Transform(
             [transforms._presets.ImageClassification(crop_size=32, resize_size=32, mean=(0, 0, 0), std=(1, 1, 1))]),
             FGSM_Transform(model, 0.1)])
     gtsrb_trainset = Transform_With_Label_Dataset(gtsrb_trainset, transform)
     testloader = DataLoader(gtsrb_trainset, batch_size=64, shuffle=False)
     return testloader
