# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from torchvision import transforms
import torch
from monitizer.benchmark.generators.distortiontransformers import To_Tensor_With_Label_Transform, FGSM_Transform
from monitizer.benchmark.generators.distortiondatasets import Transform_With_Label_Dataset
from monitizer.benchmark.datasets.datasets import get_dtd_set
import os
from torch.utils.data import DataLoader


## Wrong Prediction --------------------------------------------------
def get_dtd_fgsm_dataloader(usecase, model=None, validation_split=0.2, data_folder='./', root='./',
                            num_workers=os.cpu_count() - 1) -> DataLoader:
    if model is None:
        model = torch.load(root + "networks/DTD")
    transform = None
    dtd_trainset = get_dtd_set(usecase, transform, data_folder=data_folder)
    transform = transforms.Compose(
        [To_Tensor_With_Label_Transform(
            [transforms._presets.ImageClassification(crop_size=32, resize_size=32, mean=(0, 0, 0), std=(1, 1, 1))]),
         FGSM_Transform(model, 0.1)])
    dtd_trainset = Transform_With_Label_Dataset(dtd_trainset, transform)
    testloader = DataLoader(dtd_trainset, batch_size=64, shuffle=False, num_workers=num_workers)
    return testloader
