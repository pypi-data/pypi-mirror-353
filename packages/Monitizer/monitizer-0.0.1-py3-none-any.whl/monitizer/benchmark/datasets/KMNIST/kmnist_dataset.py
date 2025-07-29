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
import monitizer.benchmark.datasets.KMNIST.kmnist_dataloaders as kmnist_data
from monitizer.benchmark.datasets.datasets import get_kmnist, get_kmnist_set, get_dataloader


class KMNISTDataset(Dataset):
    def __init__(self, name: str, data_folder: str = './data', root='monitizer/benchmark/',
                 num_workers=os.cpu_count() - 1):
        super().__init__(name, get_kmnist, data_folder, root, num_workers=num_workers)

        self.preprocessing_transformers = [transforms.ToTensor()]
        self.get_dataset = get_kmnist
        self.test_set = get_kmnist_set("test",
                                      transforms.Compose(self.preprocessing_transformers),
                                      self.validation_split, self.data_folder)
        self.train_set = get_kmnist_set("train",
                                       transforms.Compose(self.preprocessing_transformers),
                                       self.validation_split, self.data_folder)
        self.validation_set = get_kmnist_set("val",
                                            transforms.Compose(self.preprocessing_transformers),
                                            self.validation_split, self.data_folder)

    def get_ID_train(self):
        return get_dataloader(self.train_set, num_workers=self.num_workers)

    def get_ID_train_labels(self) -> torch.Tensor:
        return self.train_set.dataset.targets[self.train_set.indices]

    def get_ID_val_labels(self) -> torch.Tensor:
        return self.validation_set.dataset.targets[self.validation_set.indices]

    def get_ID_val(self):
        return get_dataloader(self.validation_set, num_workers=self.num_workers)

    def get_ID_test(self):
        return get_dataloader(self.test_set, num_workers=self.num_workers)

    def get_OOD_data_specific(self, name, usecase) -> DataLoader:
        if name == "WrongPrediction/FGSM":
            return kmnist_data.get_kmnist_fgsm_dataloader(usecase, data_folder=self.data_folder,
                                                        root=self.specification_root, num_workers=self.num_workers)
        else:
            raise NotImplementedError(f"The OOD-dataset {name} is not known!")

    def get_all_subset_names(self) -> list:
        generated_ood = ["Noise/Gaussian", "Noise/SaltAndPepper", "Perturbation/Contrast",
                         "Perturbation/GaussianBlur", "Perturbation/Invert", "Perturbation/Rotate",
                         "Perturbation/Light"]
        specific_ood = ["WrongPrediction/FGSM"]
        return generated_ood + specific_ood
