# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from torchvision import datasets
from torch.utils.data import DataLoader, Subset
import torch
from typing_extensions import Literal, Callable
import os


def get_dataloader(set: torch.utils.data.Dataset, num_workers=0) -> DataLoader:
    """
    Generates a DataLoader for a given set

    :param set: the given dataset
    :type set: class:`torch.utils.data.Dataset`
    :return: returns a DataLoader for the given set
    :rtype: DataLoader
    """
    trainloader = DataLoader(set, batch_size=64, shuffle=False, num_workers=num_workers)
    return trainloader


def get_mnist_set(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                  data_folder: str = './') -> torch.utils.data.Dataset:
    """
    Loads the MNIST <http://yann.lecun.com/exdb/mnist/>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a torch.Dataset containing the MNIST images
    :rtype: torch.utils.data.Dataset
    """
    if usecase == "val":
        mnist_trainset = datasets.MNIST(root=data_folder, train=True, download=False, transform=transform)
        mnist_trainset = Subset(mnist_trainset, range(int(len(mnist_trainset) * validation_split)))
    elif usecase == "train":
        mnist_trainset = datasets.MNIST(root=data_folder, train=True, download=False, transform=transform)
        mnist_trainset = Subset(mnist_trainset, range(int(len(mnist_trainset) * validation_split), len(mnist_trainset)))
    elif usecase == "test":
        mnist_trainset = datasets.MNIST(root=data_folder, train=False, download=False, transform=transform)
    else:
        raise ValueError(f"Unknown usecase '{usecase}'")
    return mnist_trainset


def get_mnist(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
              data_folder: str = './', num_workers=os.cpu_count() - 1) -> DataLoader:
    """
    Loads the MNIST <http://yann.lecun.com/exdb/mnist/>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a DataLoader containing the MNIST images of the usecase
    :rtype: DataLoader
    """
    return get_dataloader(get_mnist_set(usecase, transform, validation_split, data_folder), num_workers=num_workers)


def get_fashionmnist_set(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                         data_folder: str = './') -> torch.utils.data.Dataset:
    """
    Loads the `Fashion-MNIST <https://github.com/zalandoresearch/fashion-mnist>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a torch.Dataset containing the Fashion-MNIST images
    :rtype: torch.utils.data.Dataset
    """
    if usecase == "val":
        fmnist_trainset = datasets.FashionMNIST(root=data_folder, train=True, download=False, transform=transform)
        fmnist_trainset = Subset(fmnist_trainset, range(int(len(fmnist_trainset) * validation_split)))
    elif usecase == "train":
        fmnist_trainset = datasets.FashionMNIST(root=data_folder, train=True, download=False, transform=transform)
        fmnist_trainset = Subset(fmnist_trainset,
                                 range(int(len(fmnist_trainset) * validation_split), len(fmnist_trainset)))
    elif usecase == "test":
        fmnist_trainset = datasets.FashionMNIST(root=data_folder, train=False, download=False, transform=transform)
    else:
        raise ValueError(f"Unknown usecase '{usecase}'")
    return fmnist_trainset


def get_fashionmmnist(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                      data_folder: str = './', num_workers=os.cpu_count() - 1) -> DataLoader:
    """
    Loads the `Fashion-MNIST <https://github.com/zalandoresearch/fashion-mnist>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a DataLoader containing the Fashion-MNIST images
    :rtype: DataLoader
    """
    return get_dataloader(get_fashionmnist_set(usecase, transform, validation_split, data_folder),
                          num_workers=num_workers)


def get_kmnist_set(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                   data_folder: str = './') -> torch.utils.data.Dataset:
    """
    Loads the KMNIST-dataset, aka. `Kuzushiji-MNIST <https://github.com/rois-codh/kmnist>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a torch.Dataset containing the KMNIST images
    :rtype: torch.utils.data.Dataset
    """
    if usecase == "val":
        kmnist_trainset = datasets.KMNIST(root=data_folder, train=True, download=False, transform=transform)
        kmnist_trainset = Subset(kmnist_trainset, range(int(len(kmnist_trainset) * validation_split)))
    elif usecase == "train":
        kmnist_trainset = datasets.KMNIST(root=data_folder, train=True, download=False, transform=transform)
        kmnist_trainset = Subset(kmnist_trainset,
                                 range(int(len(kmnist_trainset) * validation_split), len(kmnist_trainset)))
    elif usecase == "test":
        kmnist_trainset = datasets.KMNIST(root=data_folder, train=False, download=False, transform=transform)
    else:
        raise ValueError(f"Unknown usecase '{usecase}'")
    return kmnist_trainset


def get_kmnist(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
               data_folder: str = './', num_workers=os.cpu_count() - 1) -> DataLoader:
    """
    Loads the KMNIST-dataset, aka. `Kuzushiji-MNIST <https://github.com/rois-codh/kmnist>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a DataLoader containing the KMNIST images
    :rtype: DataLoader
    """
    return get_dataloader(get_kmnist_set(usecase, transform, validation_split, data_folder), num_workers=num_workers)


def get_svhn_set(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                 data_folder: str = './') -> torch.utils.data.Dataset:
    """
    Loads the `SVHN <http://ufldl.stanford.edu/housenumbers/>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param data_folder: location of the data, defaults to './'
    :return: returns a torch.Dataset containing the SVHN images
    :rtype: torch.utils.data.Dataset
    """
    if usecase == "val":
        svhn_trainset = datasets.SVHN(root=data_folder, split="extra", download=False, transform=transform)
    elif usecase == "train":
        svhn_trainset = datasets.SVHN(root=data_folder, split="train", download=False, transform=transform)
    elif usecase == "test":
        svhn_trainset = datasets.SVHN(root=data_folder, split="test", download=False, transform=transform)
    else:
        raise ValueError(f"Unknown usecase '{usecase}'")
    return svhn_trainset


def get_svhn(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
             data_folder: str = './', num_workers=os.cpu_count() - 1) -> DataLoader:
    """
    Loads the `SVHN <http://ufldl.stanford.edu/housenumbers/>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param data_folder: location of the data, defaults to './'
    :return: returns a torch.Dataset containing the SVHN images
    :rtype: torch.utils.data.Dataset
    """
    return get_dataloader(get_svhn_set(usecase, transform, validation_split, data_folder), num_workers=num_workers)


def get_cifar10_set(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                    data_folder: str = './') -> torch.utils.data.Dataset:
    """
    Loads the `CIFAR10 <https://www.cs.toronto.edu/~kriz/cifar.html>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a torch.Dataset containing the CIFAR10 images
    :rtype: torch.utils.data.Dataset
    """
    if usecase == "val":
        cifar_trainset = datasets.CIFAR10(root=data_folder, train=True, download=False, transform=transform)
        cifar_trainset = Subset(cifar_trainset, range(int(len(cifar_trainset) * validation_split)))
    elif usecase == "train":
        cifar_trainset = datasets.CIFAR10(root=data_folder, train=True, download=False, transform=transform)
        cifar_trainset = Subset(cifar_trainset, range(int(len(cifar_trainset) * validation_split), len(cifar_trainset)))
    elif usecase == "test":
        cifar_trainset = datasets.CIFAR10(root=data_folder, train=False, download=False, transform=transform)
    else:
        raise ValueError(f"Unknown usecase '{usecase}'")
    return cifar_trainset


def get_cifar10(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                data_folder: str = './', num_workers=os.cpu_count() - 1) -> DataLoader:
    """
    Loads the `CIFAR10 <https://www.cs.toronto.edu/~kriz/cifar.html>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a DataLoader containing the CIFAR10 images
    :rtype: DataLoader
    """
    return get_dataloader(get_cifar10_set(usecase, transform, validation_split, data_folder), num_workers=num_workers)


def get_cifar100_set(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                     data_folder: str = './') -> torch.utils.data.Dataset:
    """
    Loads the `CIFAR100 <https://www.cs.toronto.edu/~kriz/cifar.html>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a torch.Dataset containing the CIFAR100 images
    :rtype: torch.utils.data.Dataset
    """
    if usecase == "val":
        cifar_trainset = datasets.CIFAR100(root=data_folder, train=True, download=False, transform=transform)
        cifar_trainset = Subset(cifar_trainset, range(int(len(cifar_trainset) * validation_split)))
    elif usecase == "train":
        cifar_trainset = datasets.CIFAR100(root=data_folder, train=True, download=False, transform=transform)
        cifar_trainset = Subset(cifar_trainset, range(int(len(cifar_trainset) * validation_split), len(cifar_trainset)))
    elif usecase == "test":
        cifar_trainset = datasets.CIFAR100(root=data_folder, train=False, download=False, transform=transform)
    else:
        raise ValueError(f"Unknown usecase '{usecase}'")
    return cifar_trainset


def get_cifar100(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                 data_folder: str = './', num_workers=os.cpu_count() - 1) -> DataLoader:
    """
    Loads the `CIFAR100 <https://www.cs.toronto.edu/~kriz/cifar.html>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a DataLoader containing the CIFAR100 images
    :rtype: DataLoader
    """
    return get_dataloader(get_cifar100_set(usecase, transform, validation_split, data_folder), num_workers=num_workers)


def get_dtd_set(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                data_folder: str = './') -> torch.utils.data.Dataset:
    """
    Loads the `Describable Textures Dataset (DTD) <https://www.robots.ox.ac.uk/~vgg/data/dtd/>`_.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param data_folder: location of the data, defaults to './'
    :return: returns a torch.Dataset containing the DTD images
    :rtype: torch.utils.data.Dataset
    """
    if usecase == "val":
        dtd_trainset = datasets.DTD(root=data_folder, split="val", download=False, transform=transform)
    elif usecase == "train":
        dtd_trainset = datasets.DTD(root=data_folder, split="train", download=False, transform=transform)
    elif usecase == "test":
        dtd_trainset = datasets.DTD(root=data_folder, split="test", download=False, transform=transform)
    else:
        raise ValueError(f"Unknown usecase '{usecase}'")
    return dtd_trainset


def get_dtd(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
            data_folder: str = './', num_workers=os.cpu_count() - 1) -> DataLoader:
    """
    Loads the `Describable Textures Dataset (DTD) <https://www.robots.ox.ac.uk/~vgg/data/dtd/>`_.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param data_folder: location of the data, defaults to './'
    :return: returns a DataLoader containing the DTD images
    :rtype: DataLoader
    """
    return get_dataloader(get_dtd_set(usecase, transform, validation_split, data_folder), num_workers=num_workers)


def get_gtsrb_set(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                  data_folder: str = './') -> torch.utils.data.Dataset:
    """
    Loads the `German Traffic Sign Recognition Benchmark (GTSRB) <https://benchmark.ini.rub.de/>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a torch.Dataset containing the GTSRB images
    :rtype: torch.utils.data.Dataset
    """
    if usecase == "val":
        gtsrb_trainset = datasets.GTSRB(root=data_folder, split="train", download=False, transform=transform)
        gtsrb_trainset = Subset(gtsrb_trainset, range(int(len(gtsrb_trainset) * validation_split)))
    elif usecase == "train":
        gtsrb_trainset = datasets.GTSRB(root=data_folder, split="train", download=False, transform=transform)
        gtsrb_trainset = Subset(gtsrb_trainset, range(int(len(gtsrb_trainset) * validation_split), len(gtsrb_trainset)))
    elif usecase == "test":
        gtsrb_trainset = datasets.GTSRB(root=data_folder, split="test", download=False, transform=transform)
    else:
        raise ValueError(f"Unknown usecase '{usecase}'")
    return gtsrb_trainset


def get_gtsrb(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
              data_folder: str = './', num_workers=os.cpu_count() - 1) -> DataLoader:
    """
    Loads the `German Traffic Sign Recognition Benchmark (GTSRB) <https://benchmark.ini.rub.de/>`_ Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a DataLoader containing the GTSRB images
    :rtype: DataLoader
    """
    return get_dataloader(get_gtsrb_set(usecase, transform, validation_split, data_folder), num_workers=num_workers)


def get_imagenet_set(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                     data_folder: str = './') -> torch.utils.data.Dataset:
    """
    Loads the ImageNet <http://image-net.org/>`_ 2012 Classification Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a torch.Dataset containing the GTSRB images
    :rtype: torch.utils.data.Dataset
    """
    if usecase == "val":
        imagenet_trainset = datasets.ImageNet(root=data_folder, split='train', transform=transform)
        number_of_images = max(int(len(imagenet_trainset) * validation_split), 10000)
        imagenet_trainset = Subset(imagenet_trainset, range(number_of_images))
    elif usecase == "train":
        imagenet_trainset = datasets.ImageNet(root=data_folder, split='train', transform=transform)
        number_of_images = 50000
        imagenet_trainset = Subset(imagenet_trainset,
                                   range(int(len(imagenet_trainset) * validation_split), int(len(imagenet_trainset) * validation_split)+number_of_images))
    elif usecase == "test":
        imagenet_trainset = datasets.ImageNet(root=data_folder, split="val", transform=transform)
        imagenet_trainset = Subset(imagenet_trainset, range(10000))
    else:
        raise ValueError(f"Unknown usecase '{usecase}'")
    return imagenet_trainset


def get_imagenet(usecase: Literal['val', 'train', 'test'], transform: Callable, validation_split: float = 0.2,
                 data_folder: str = './', num_workers=os.cpu_count() - 1) -> DataLoader:
    """
    Loads the ImageNet <http://image-net.org/>`_ 2012 Classification Dataset.

    :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
    :type usecase: str
    :param transform: the transformation to be applied to the images
    :type transform: (list of) transformations (=functions)
    :param validation_split: ratio of validation images to be split from the training set, defaults to 0.2
    :type validation_split: float
    :param data_folder: location of the data, defaults to './'
    :return: returns a DataLoader containing the GTSRB images
    :rtype: DataLoader
    """
    return get_dataloader(get_imagenet_set(usecase, transform, validation_split, data_folder), num_workers=num_workers)
