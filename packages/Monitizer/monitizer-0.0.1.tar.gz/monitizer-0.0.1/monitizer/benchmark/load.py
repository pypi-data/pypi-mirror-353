# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from monitizer.benchmark.dataset import Dataset
import os


def load(dataset_name: str, data_folder: str, num_workers: int = os.cpu_count() - 1) -> Dataset:
    """
    Load the specified ID dataset as a dataset-object

    :param dataset_name: the name of the dataset
    :type dataset_name: str
    :param data_folder: the location of the data
    :type data_folder: str
    :param num_workers: amount of workers for the dataloaders (allows parallel data loading)
    :type num_workers: int
    :rtype: class:`Dataset`
    :return: returns a dataset object
    """
    if dataset_name.lower() == "mnist":
        from monitizer.benchmark.datasets.MNIST.mnist_dataset import MNISTDataset
        return MNISTDataset(dataset_name, data_folder=data_folder, num_workers=num_workers)
    elif dataset_name.lower() == "cifar10":
        from monitizer.benchmark.datasets.CIFAR10.cifar10_dataset import CIFAR10Dataset
        return CIFAR10Dataset(dataset_name, data_folder=data_folder, num_workers=num_workers)
    elif dataset_name.lower() == "imagenet":
        from monitizer.benchmark.datasets.Imagenet.imagenet_dataset import ImageNetDataset
        return ImageNetDataset(dataset_name, data_folder=data_folder, num_workers=num_workers)
    elif dataset_name.lower() == "cifar100":
        from monitizer.benchmark.datasets.CIFAR100.cifar100_dataset import CIFAR100Dataset
        return CIFAR100Dataset(dataset_name, data_folder=data_folder, num_workers=num_workers)
    elif dataset_name.lower() == "gtsrb":
        from monitizer.benchmark.datasets.GTSRB.gtsrb_dataset import GTSRBDataset
        return GTSRBDataset(dataset_name, data_folder=data_folder, num_workers=num_workers)
    elif dataset_name.lower() == "svhn":
        from monitizer.benchmark.datasets.SVHN.svhn_dataset import SVHNDataset
        return SVHNDataset(dataset_name, data_folder=data_folder, num_workers=num_workers)
    elif dataset_name.lower() == "dtd":
        from monitizer.benchmark.datasets.DTD.dtd_dataset import DTDDataset
        return DTDDataset(dataset_name, data_folder=data_folder, num_workers=num_workers)
    elif dataset_name.lower() == "fashionmnist":
        from monitizer.benchmark.datasets.FashionMNIST.fashionmnist_dataset import FashionMNISTDataset
        return FashionMNISTDataset(dataset_name, data_folder=data_folder, num_workers=num_workers)
    elif dataset_name.lower() == "kmnist":
        from monitizer.benchmark.datasets.KMNIST.kmnist_dataset import KMNISTDataset
        return KMNISTDataset(dataset_name, data_folder=data_folder, num_workers=num_workers)
    else:
        raise NotImplementedError(f"{dataset_name} is not known!")
