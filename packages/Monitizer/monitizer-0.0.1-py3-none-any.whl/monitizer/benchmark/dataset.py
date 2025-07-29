# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import torch, os
from torch.utils.data import DataLoader
from abc import ABC, abstractmethod
from typing_extensions import Literal
from torchvision import transforms
import monitizer.benchmark.datasets.generated_ood_dataloaders as udataloader
import typing


class Dataset(ABC):
    """
    This class describes the general dataset object as used in Monitizer.
    It allows to get ID and generated OOD data.
    """

    def __init__(self, name: str, get_dataset_function: typing.Callable, data_folder='./data', specification_root='./',
                 preprocessing_transformers=[transforms.ToTensor()], image_size=(32, 32),
                 num_workers=os.cpu_count() - 1):
        """
        Generate a dataset object.

        :param name: name of the dataset
        :type name: str
        :param get_dataset_function: a function to load the ID-dataset
        :type get_dataset_function: Callable (=function)
        :param data_folder: location of the data, defaults to './data'
        :type data_folder: str
        :param specification_root: location of the specification files (e.g., parameter for the noises), defaults to './'
        :type specification_root: str
        :param preprocessing_transformers: necessary transformations to the image, defaults to [transforms.ToTensor()]
        :type preprocessing_transformers: list[transforms]
        :param image_size: define the size of the images
        :type image_size: tuple (height, width)
        """
        self.name = name
        self.data_folder = data_folder
        self.specification_root = specification_root
        self.validation_split = 0.2  # TODO: What should it be?
        self.preprocessing_transformers = preprocessing_transformers
        self.image_size = image_size
        self.get_dataset = get_dataset_function

        self.test_set = None
        self.train_set = None
        self.validation_set = None
        self.num_workers = num_workers if not torch.cuda.is_available() else 0

    @abstractmethod
    def get_ID_train(self) -> DataLoader:
        """
        Loads the training set of the ID data
        """
        pass

    @abstractmethod
    def get_ID_train_labels(self) -> torch.Tensor:
        """
        Loads the labels of the training set of the ID data
        """
        pass

    @abstractmethod
    def get_ID_val_labels(self) -> torch.Tensor:
        """
        Loads the labels of the validation set of the ID data
        """
        pass

    @abstractmethod
    def get_ID_val(self) -> DataLoader:
        """
        Loads the validation set of the ID data
        """
        pass

    @abstractmethod
    def get_ID_test(self) -> DataLoader:
        """
        Loads the test set of the ID data
        Note: there is no function to load the test-labels, since they are assumed to be actual test-data with no
        labels available
        """
        pass

    @abstractmethod
    def get_OOD_data_specific(self, name: str, usecase: Literal['val', 'train', 'test']) -> DataLoader:
        """
        Load OOD data that is specific to this ID dataset, i.e., the not-generated OOD.

        :param name: the name of the OOD-class
        :type name: str
        :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
        :type usecase: str
        :rtype: DataLoader
        :return: returns a Dataloader for the specified OOD class
        """
        pass

    def get_OOD_data(self, name: str, usecase: Literal['val', 'train', 'test']) -> DataLoader:
        """
         Load OOD data for this dataset.
         This function does not need to be changed, it automatically loads generated OOD data or calls the
         function `get_OOD_data_specific`.

        :param name: the name of the OOD-class
        :type name: str
        :param usecase: whether to load the training ('train'), validation ('val') or test ('test') set
        :type usecase: str
        :rtype: DataLoader
        :return: returns a Dataloader for the specified OOD class
        """
        if name == "Noise/Gaussian":
            return udataloader.get_guassian_noise_dataloader(usecase, self.name, 0,
                                                             self.preprocessing_transformers,
                                                             self.get_dataset,
                                                             data_folder=self.data_folder,
                                                             root=self.specification_root,
                                                             num_workers=self.num_workers)  # TODO: decide on params
        elif name == "Noise/SaltAndPepper":
            return udataloader.get_salt_and_pepper_noise_dataloader(usecase, self.name, 0,
                                                                    self.preprocessing_transformers, self.get_dataset,
                                                                    data_folder=self.data_folder,
                                                                    root=self.specification_root,
                                                                    num_workers=self.num_workers)
        elif name == "Perturbation/Contrast":
            return udataloader.get_contrast_dataloader(usecase, factor=3,
                                                       base_transform=self.preprocessing_transformers,
                                                       dataloader_function=self.get_dataset,
                                                       data_folder=self.data_folder,
                                                       root=self.specification_root,
                                                       num_workers=self.num_workers)  # TODO: decide on factor
        elif name == "Perturbation/GaussianBlur":
            return udataloader.get_blur_dataloader(usecase, 5, 0.8,
                                                   base_transform=self.preprocessing_transformers,
                                                   dataloader_function=self.get_dataset, data_folder=self.data_folder,
                                                   root=self.specification_root,
                                                   num_workers=self.num_workers)  # TODO: decide on factor
        elif name == "Perturbation/Light":
            return udataloader.get_brightness_dataloader(usecase, 1.5,
                                                         base_transform=self.preprocessing_transformers,
                                                         dataloader_function=self.get_dataset,
                                                         data_folder=self.data_folder,
                                                         root=self.specification_root,
                                                         num_workers=self.num_workers)  # TODO: decide on factor
        elif name == "Perturbation/Invert":
            return udataloader.get_invert_dataloader(usecase, base_transform=self.preprocessing_transformers,
                                                     dataloader_function=self.get_dataset, data_folder=self.data_folder,
                                                     root=self.specification_root, num_workers=self.num_workers)
        elif name == "Perturbation/Rotate":
            return udataloader.get_rotate_dataloader(usecase, 15, base_transform=self.preprocessing_transformers,
                                                     dataloader_function=self.get_dataset, data_folder=self.data_folder,
                                                     root=self.specification_root,
                                                     num_workers=self.num_workers)  # TODO: decide on factor
        else:
            return self.get_OOD_data_specific(name, usecase)

    def get_OOD_val(self, name: str) -> DataLoader:
        """
        Loads the validation set of an OOD class
        :param name: the name of the OOD-class
        :type name: str
        """
        return self.get_OOD_data(name, "val")

    def get_OOD_test(self, name: str) -> DataLoader:
        """
        Loads the test set of an OOD class
        :param name: the name of the OOD-class
        :type name: str
        """
        return self.get_OOD_data(name, "test")

    @abstractmethod
    def get_all_subset_names(self) -> list:
        """
        returns a list of all available OOD-classes
        """
        pass

    def get_generated_ood_names(self) -> list:
        generated_ood = ["Noise/Gaussian", "Noise/SaltAndPepper", "Perturbation/Contrast",
                         "Perturbation/GaussianBlur", "Perturbation/Invert", "Perturbation/Rotate",
                         "Perturbation/Light"]
        return generated_ood
