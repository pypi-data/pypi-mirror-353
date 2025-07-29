# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from torchvision import transforms
from monitizer.benchmark.generators.distortiontransformers import Salt_And_Pepper_Transform, Gaussian_Noise_Transform, \
    load_noise_file, Brightness_Transform, Contrast_Transform, Invert_Transform, Rotate_Transform
from torch.utils.data import DataLoader
import copy, os


## Noise --------------------------------
# TODO: update the files
def get_salt_and_pepper_noise_dataloader(usecase, dataset_name, point_of_params, base_transform,
                                         dataloader_function, validation_split=0.2, data_folder='./',
                                         root='./', num_workers=os.cpu_count() - 1) -> DataLoader:
    base = copy.copy(base_transform)
    file = root + "specifications/" + dataset_name.lower() + "/salt_pepper_params.txt"
    params_seed, params_mean, params_stddev = load_noise_file(file)
    base.append(Salt_And_Pepper_Transform(params_seed[point_of_params],
                                          params_mean[point_of_params],
                                          params_stddev[point_of_params]))
    transform = transforms.Compose(base)
    return dataloader_function(usecase=usecase, transform=transform, validation_split=validation_split,
                               data_folder=data_folder, num_workers=num_workers)


def get_guassian_noise_dataloader(usecase, dataset_name, point_of_params, base_transform,
                                  dataloader_function, validation_split=0.2, data_folder='./',
                                  root='./', num_workers=os.cpu_count() - 1) -> DataLoader:
    base = copy.copy(base_transform)
    file = root + "specifications/" + dataset_name.lower() + "/gauss_params.txt"
    params_seed, params_mean, params_stddev = load_noise_file(file)
    base.append(Gaussian_Noise_Transform(params_seed[point_of_params],
                                         params_mean[point_of_params],
                                         params_stddev[point_of_params]))
    transform = transforms.Compose(base)
    return dataloader_function(usecase=usecase, transform=transform, validation_split=validation_split,
                               data_folder=data_folder, num_workers=num_workers)


## Perturbation ------------------------------------------------------------

def get_contrast_dataloader(usecase, factor, base_transform, dataloader_function,
                            validation_split=0.2, data_folder='./', root='./',
                            num_workers=os.cpu_count() - 1) -> DataLoader:
    base = copy.copy(base_transform)
    base.append(Contrast_Transform(contrast_factor=factor))
    transform = transforms.Compose(base)
    return dataloader_function(usecase=usecase, transform=transform, validation_split=validation_split,
                               data_folder=data_folder, num_workers=num_workers)


def get_blur_dataloader(usecase, kernel_size, sigma, base_transform, dataloader_function,
                        validation_split=0.2, data_folder='./',
                        root='./', num_workers=os.cpu_count() - 1) -> DataLoader:
    # I hope, this is enough to guarantee reproducability
    # Careful, it might effect every random number from now
    base = copy.copy(base_transform)
    base.append(transforms.GaussianBlur(kernel_size=kernel_size, sigma=sigma))
    transform = transforms.Compose(base)
    return dataloader_function(usecase=usecase, transform=transform, validation_split=validation_split,
                               data_folder=data_folder, num_workers=num_workers)


def get_brightness_dataloader(usecase, factor, base_transform, dataloader_function,
                              validation_split=0.2, data_folder='./', root='./',
                              num_workers=os.cpu_count() - 1) -> DataLoader:
    base = copy.copy(base_transform)
    base.append(Brightness_Transform(brightness_factor=factor))
    transform = transforms.Compose(base)
    return dataloader_function(usecase=usecase, transform=transform, validation_split=validation_split,
                               data_folder=data_folder, num_workers=num_workers)


def get_invert_dataloader(usecase, base_transform, dataloader_function,
                          validation_split=0.2, data_folder='./', root='./',
                          num_workers=os.cpu_count() - 1) -> DataLoader:
    base = copy.copy(base_transform)
    base.append(Invert_Transform())
    transform = transforms.Compose(base)
    return dataloader_function(usecase=usecase, transform=transform, validation_split=validation_split,
                               data_folder=data_folder, num_workers=num_workers)


def get_rotate_dataloader(usecase, factor, base_transform, dataloader_function,
                          validation_split=0.2, data_folder='./', root='./',
                          num_workers=os.cpu_count() - 1) -> DataLoader:
    base = copy.copy(base_transform)
    base.append(Rotate_Transform(rotation_factor=factor))
    transform = transforms.Compose(base)
    return dataloader_function(usecase=usecase, transform=transform, validation_split=validation_split,
                               data_folder=data_folder, num_workers=num_workers)
