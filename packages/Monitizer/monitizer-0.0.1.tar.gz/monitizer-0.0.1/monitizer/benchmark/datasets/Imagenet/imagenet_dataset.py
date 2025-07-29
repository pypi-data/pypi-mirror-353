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
from monitizer.benchmark.datasets.datasets import get_dataloader, get_imagenet_set, get_imagenet


class ImageNetDataset(Dataset):
    def __init__(self, name: str, data_folder: str = './data', root='monitizer/benchmark/', num_workers=os.cpu_count() - 1):
        super().__init__(name, get_imagenet, data_folder, root, num_workers=num_workers)

        self.preprocessing_transformers = [transforms._presets.ImageClassification(crop_size=224,resize_size=232)]
        self.get_dataset = get_imagenet
        self.test_set = get_imagenet_set("test",
                                         transforms.Compose(self.preprocessing_transformers),
                                         self.validation_split, self.data_folder)
        self.train_set = get_imagenet_set("train",
                                          transforms.Compose(self.preprocessing_transformers),
                                          self.validation_split, self.data_folder)
        self.validation_set = get_imagenet_set("val",
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
        raise NotImplementedError(f"The OOD-dataset {name} is not known!")

    def get_all_subset_names(self) -> list:
        generated_ood = ["Noise/Gaussian", "Noise/SaltAndPepper", "Perturbation/Contrast",
                         "Perturbation/GaussianBlur", "Perturbation/Invert", "Perturbation/Rotate",
                         "Perturbation/Light"]
        specific_ood = []
        return generated_ood + specific_ood
