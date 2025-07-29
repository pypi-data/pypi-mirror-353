# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from torchvision import transforms
from monitizer.benchmark.generators.distortiontransformers import To_Tensor_With_Label_Transform, FGSM_Transform
from monitizer.benchmark.generators.distortiondatasets import Restricted_Index_Dataset, Transform_With_Label_Dataset
from monitizer.benchmark.datasets.datasets import get_cifar10_set, get_dtd_set, get_cifar100_set, get_gtsrb_set
import os
from torch.utils.data import DataLoader
import monitizer.benchmark.utils as utils


## New World -------------------------------------------------

def get_cifar10_dtd_dataloader(usecase, data_folder='./', root='./', num_workers=os.cpu_count() - 1) -> DataLoader:
    filename = root + f"specifications/cifar10/dtd_list_{usecase}.txt"
    transform = transforms.Compose([transforms.ToTensor(), transforms.Resize(size=(32, 32), antialias=None)])
    dtd_trainset = get_dtd_set(usecase, transform, data_folder=data_folder)
    new_world_set = Restricted_Index_Dataset(dtd_trainset, filename)
    trainloader = DataLoader(new_world_set, batch_size=64, shuffle=False, num_workers=num_workers)
    return trainloader


def get_cifar10_gtsrb_dataloader(usecase, validation_split=0.2, data_folder='./', root='./',
                                 num_workers=os.cpu_count() - 1) -> DataLoader:
    filename = root + f"specifications/cifar10/gtsrb_list_{usecase}.txt"
    transform = transforms.Compose([transforms.ToTensor(), transforms.Resize(size=(32, 32), antialias=None)])
    gtsrb_trainset = get_gtsrb_set(usecase, transform, validation_split, data_folder)
    new_world_set = Restricted_Index_Dataset(gtsrb_trainset, filename)
    trainloader = DataLoader(new_world_set, batch_size=64, shuffle=False, num_workers=num_workers)
    return trainloader


## Unseen Environment -------------------------------------

# TODO: Empty, need to discuss. Probably there is just weather going to be here.


## Unseen Object -------------------------------------------

def get_cifar10_cifar100_dataloader(usecase, validation_split=0.2, data_folder='./', root='./',
                                    num_workers=os.cpu_count() - 1) -> DataLoader:
    filename = root + f"specifications/cifar10/cifar100_list_{usecase}.txt"
    transform = transforms.ToTensor()
    fashioncifar10_trainset = get_cifar100_set(usecase, transform, validation_split, data_folder)
    ood_set = Restricted_Index_Dataset(fashioncifar10_trainset, filename)
    trainloader = DataLoader(ood_set, batch_size=64, shuffle=False, num_workers=num_workers)
    return trainloader


## Wrong Prediction --------------------------------------------------

# TODO: I need a cifar10 model
def get_cifar10_fgsm_dataloader(usecase, model=None, validation_split=0.2, data_folder='./', root='./',
                                num_workers=os.cpu_count() - 1) -> DataLoader:
    if model == None:
        model = utils.load_cifar10_network_net1(root)
        # model = utils.load_cifar10_network(root)
    transform = None
    cifar10_trainset = get_cifar10_set(usecase, transform, validation_split=validation_split, data_folder=data_folder)
    transform = transforms.Compose(
        [To_Tensor_With_Label_Transform(), FGSM_Transform(model, 0.1)])
    cifar10_trainset = Transform_With_Label_Dataset(cifar10_trainset, transform)
    testloader = DataLoader(cifar10_trainset, batch_size=64, shuffle=False, num_workers=num_workers)
    return testloader
