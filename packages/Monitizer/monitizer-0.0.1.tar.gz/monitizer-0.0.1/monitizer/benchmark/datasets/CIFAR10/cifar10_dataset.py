# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from monitizer.benchmark.dataset import Dataset
import torch, os
from torch.utils.data import DataLoader
from torchvision import transforms
import monitizer.benchmark.datasets.CIFAR10.cifar10_dataloaders as cifar10_data
from monitizer.benchmark.datasets.datasets import get_cifar10, get_cifar10_set, get_dataloader


class CIFAR10Dataset(Dataset):
    def __init__(self, name: str, data_folder: str = './data', root='monitizer/benchmark/',
                 num_workers=os.cpu_count() - 1):
        super().__init__(name, get_cifar10, data_folder, root, num_workers=num_workers)
        self.get_dataset = get_cifar10
        self.preprocessing_transformers = [transforms.ToTensor()]
        self.test_set = get_cifar10_set("test",
                                        transforms.Compose(self.preprocessing_transformers),
                                        self.validation_split, self.data_folder)
        self.train_set = get_cifar10_set("train",
                                         transforms.Compose(self.preprocessing_transformers),
                                         self.validation_split, self.data_folder)
        self.validation_set = get_cifar10_set("val",
                                              transforms.Compose(self.preprocessing_transformers),
                                              self.validation_split, self.data_folder)

    def get_ID_train(self):
        return get_dataloader(self.train_set, num_workers=self.num_workers)

    def get_ID_train_labels(self) -> torch.Tensor:
        return torch.Tensor(self.train_set.dataset.targets)[self.train_set.indices]

    def get_ID_val_labels(self) -> torch.Tensor:
        return torch.Tensor(self.validation_set.dataset.targets)[self.validation_set.indices]

    def get_ID_val(self):
        return get_dataloader(self.validation_set, num_workers=self.num_workers)

    def get_ID_test(self):
        return get_dataloader(self.test_set, num_workers=self.num_workers)

    def get_OOD_data_specific(self, name, usecase) -> DataLoader:
        if name == "NewWorld/GTSRB":
            return cifar10_data.get_cifar10_gtsrb_dataloader(usecase, data_folder=self.data_folder,
                                                             root=self.specification_root, num_workers=self.num_workers)
            # Do something to produce the dataloader from cifar10
        elif name == "NewWorld/DTD":
            return cifar10_data.get_cifar10_dtd_dataloader(usecase, data_folder=self.data_folder,
                                                           root=self.specification_root, num_workers=self.num_workers)
        elif name == "UnseenObject/Cifar100":
            return cifar10_data.get_cifar10_cifar100_dataloader(usecase, data_folder=self.data_folder,
                                                                root=self.specification_root,
                                                                num_workers=self.num_workers)
        elif name == "WrongPrediction/FGSM":
            return cifar10_data.get_cifar10_fgsm_dataloader(usecase, data_folder=self.data_folder,
                                                            root=self.specification_root, num_workers=self.num_workers)
        else:
            raise NotImplementedError(f"The OOD-dataset {name} is not known!")

    def get_all_subset_names(self) -> list:
        generated_ood = ["Noise/Gaussian", "Noise/SaltAndPepper", "Perturbation/Contrast",
                         "Perturbation/GaussianBlur", "Perturbation/Invert", "Perturbation/Rotate",
                         "Perturbation/Light"]
        specific_ood = ["NewWorld/GTSRB", "NewWorld/DTD", "UnseenObject/Cifar100", "WrongPrediction/FGSM"]
        return generated_ood + specific_ood
