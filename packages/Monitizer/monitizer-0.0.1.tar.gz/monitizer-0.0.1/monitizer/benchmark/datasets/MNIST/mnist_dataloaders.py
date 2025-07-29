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
from monitizer.benchmark.datasets.datasets import get_cifar10_set, get_dtd_set, get_fashionmnist_set, get_kmnist_set, \
    get_svhn_set, get_mnist_set
import torch, os
from torch.utils.data import DataLoader


## New World -------------------------------------------------

def get_mnist_dtd_dataloader(usecase, data_folder='./', root='./', num_workers=os.cpu_count() - 1) -> DataLoader:
    filename = root + f"specifications/mnist/dtd_list_{usecase}.txt"
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Resize(size=(28, 28), antialias=None), transforms.Grayscale(1)])
    dtd_trainset = get_dtd_set(usecase=usecase, transform=transform, data_folder=data_folder)
    new_world_set = Restricted_Index_Dataset(dtd_trainset, filename)
    trainloader = DataLoader(new_world_set, batch_size=64, shuffle=False, num_workers=num_workers)
    return trainloader


def get_mnist_cifar10_dataloader(usecase, validation_split=0.2, data_folder='./', root='./',
                                 num_workers=os.cpu_count() - 1) -> DataLoader:
    filename = root + f"specifications/mnist/cifar10_list_{usecase}.txt"
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Resize(size=(28, 28), antialias=None), transforms.Grayscale(1)])
    cifar_trainset = get_cifar10_set(usecase=usecase, transform=transform, validation_split=validation_split,
                                     data_folder=data_folder)
    new_world_set = Restricted_Index_Dataset(cifar_trainset, filename)
    trainloader = DataLoader(new_world_set, batch_size=64, shuffle=False, num_workers=num_workers)
    return trainloader


## Unseen Environment -------------------------------------

def get_mnist_svhn_dataloader(usecase, data_folder='./', root='./', num_workers=os.cpu_count() - 1) -> DataLoader:
    filename = root + f"specifications/mnist/svhn_list_{usecase}.txt"
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Resize(size=(28, 28), antialias=None), transforms.Grayscale(1)])
    svhn_trainset = get_svhn_set(usecase, transform, data_folder=data_folder)
    ood_set = Restricted_Index_Dataset(svhn_trainset, filename)
    trainloader = DataLoader(ood_set, batch_size=64, shuffle=False, num_workers=num_workers)
    return trainloader


## Unseen Object -------------------------------------------

def get_mnist_fashionmnist_dataloader(usecase, validation_split=0.2, data_folder='./', root='./',
                                      num_workers=os.cpu_count() - 1) -> DataLoader:
    filename = root + f"specifications/mnist/fashionmnist_list_{usecase}.txt"
    transform = transforms.ToTensor()
    fashionmnist_trainset = get_fashionmnist_set(usecase, transform, validation_split, data_folder)
    ood_set = Restricted_Index_Dataset(fashionmnist_trainset, filename)
    trainloader = DataLoader(ood_set, batch_size=64, shuffle=False, num_workers=num_workers)
    return trainloader


def get_mnist_kmnist_dataloader(usecase, validation_split=0.2, data_folder='./', root='./',
                                num_workers=os.cpu_count() - 1) -> DataLoader:
    filename = root + f"specifications/mnist/kmnist_list_{usecase}.txt"
    transform = transforms.ToTensor()
    kmnist_trainset = get_kmnist_set(usecase, transform, validation_split, data_folder)
    ood_set = Restricted_Index_Dataset(kmnist_trainset, filename)
    trainloader = DataLoader(ood_set, batch_size=64, shuffle=False, num_workers=num_workers)
    return trainloader


## Wrong Prediction --------------------------------------------------

def get_mnist_fgsm_dataloader(usecase, model=None, validation_split=0.2, data_folder='./', root='./',
                              num_workers=os.cpu_count() - 1) -> DataLoader:
    if model == None:
        model = torch.load(root + "/networks/MNIST4x350-flatten")
    transform = None
    mnist_trainset = get_mnist_set(usecase, transform, validation_split=validation_split, data_folder=data_folder)
    transform = transforms.Compose(
        [To_Tensor_With_Label_Transform(), FGSM_Transform(model, 0.1)])
    mnist_trainset = Transform_With_Label_Dataset(mnist_trainset, transform)
    testloader = DataLoader(mnist_trainset, batch_size=64, shuffle=False, num_workers=num_workers)
    return testloader
