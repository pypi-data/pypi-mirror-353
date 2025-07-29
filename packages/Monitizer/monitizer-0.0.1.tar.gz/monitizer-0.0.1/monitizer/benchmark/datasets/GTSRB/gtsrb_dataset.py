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
import monitizer.benchmark.datasets.GTSRB.gtsrb_dataloaders as gtsrb_data
from monitizer.benchmark.datasets.datasets import get_gtsrb, get_gtsrb_set, get_dataloader


class GTSRBDataset(Dataset):
    def __init__(self, name: str, data_folder: str = './data', root='monitizer/benchmark/',
                 num_workers=os.cpu_count() - 1):
        super().__init__(name, get_gtsrb, data_folder, root)

        # TODO: this will most likely depend on the network as GTSRB does not have a comon shape
        self.input_shape = (32, 32)
        self.preprocessing_transformers = [
            transforms._presets.ImageClassification(crop_size=32, resize_size=32, mean=(0, 0, 0), std=(1, 1, 1))]
        self.get_dataset = get_gtsrb
        self.test_set = get_gtsrb_set("test",
                                      transforms.Compose(self.preprocessing_transformers),
                                      self.validation_split, self.data_folder)
        self.train_set = get_gtsrb_set("train",
                                       transforms.Compose(self.preprocessing_transformers),
                                       self.validation_split, self.data_folder)
        self.validation_set = get_gtsrb_set("val",
                                            transforms.Compose(self.preprocessing_transformers),
                                            self.validation_split, self.data_folder)

    def get_ID_train(self):
        return get_dataloader(self.train_set)

    def get_ID_train_labels(self) -> torch.Tensor:
        return self.train_set.dataset.targets[self.train_set.indices]

    def get_ID_val_labels(self) -> torch.Tensor:
        return self.validation_set.dataset.targets[self.validation_set.indices]

    def get_ID_val(self):
        return get_dataloader(self.validation_set)

    def get_ID_test(self):
        return get_dataloader(self.test_set)

    def get_OOD_data_specific(self, name, usecase) -> DataLoader:
        if name == "NewWorld/CIFAR10":
            return gtsrb_data.get_gtsrb_cifar10_dataloader(usecase, self.input_shape, data_folder=self.data_folder,
                                                           root=self.specification_root)
        elif name == "NewWorld/DTD":
            return gtsrb_data.get_gtsrb_dtd_dataloader(usecase, self.input_shape, data_folder=self.data_folder,
                                                       root=self.specification_root)
        elif name == "NewWorld/SVHN":
            return gtsrb_data.get_gtsrb_svhn_dataloader(usecase, self.input_shape, data_folder=self.data_folder,
                                                        root=self.specification_root)
        elif name == "WrongPrediction/FGSM":
             return gtsrb_data.get_gtsrb_fgsm_dataloader(usecase, data_folder=self.data_folder,
                                                         root=self.specification_root)
        else:
            raise NotImplementedError(f"The OOD-dataset {name} is not known!")

    def get_all_subset_names(self) -> list:
        generated_ood = ["Noise/Gaussian", "Noise/SaltAndPepper", "Perturbation/Contrast",
                         "Perturbation/GaussianBlur", "Perturbation/Invert", "Perturbation/Rotate",
                         "Perturbation/Light"]
        specific_ood = ["NewWorld/CIFAR10", "NewWorld/DTD", "WrongPrediction/FGSM", "NewWorld/SVHN"]
        return generated_ood + specific_ood
