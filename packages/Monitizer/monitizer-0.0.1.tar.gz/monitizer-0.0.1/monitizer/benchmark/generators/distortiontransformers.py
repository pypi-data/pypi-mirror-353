# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import torch
from torchvision import transforms
import torch.nn.functional as F


class Salt_And_Pepper_Transform(object):
    def __init__(self, seed, mean, std):
        self.seed = seed
        torch.manual_seed(seed)  # TODO: test if this works
        self.std = std
        self.mean = mean

    def __call__(self, tensor):
        noise_size = tensor.size()
        num_channels = 0
        if len(noise_size) == 3:
            num_channels = noise_size[0]
            noise_size = (noise_size[1], noise_size[2])  # remove the cannel
        noise_prob = torch.randn(noise_size) * self.std + self.mean
        # Generate random salt and pepper noise for each pixel
        mask = torch.rand(noise_size)
        noisy_image = tensor
        if num_channels >= 1:
            mask = torch.unsqueeze(mask, 0)
            noise_prob = torch.unsqueeze(noise_prob, 0)
            mask = mask.expand(num_channels, -1, -1)
            noise_prob = noise_prob.expand(num_channels, -1, -1)
        noisy_image[mask < noise_prob / 2] = 0  # Set black pixel (pepper noise)
        noisy_image[mask > 1 - noise_prob / 2] = 1  # Set white pixel (salt noise)
        return noisy_image

    def __repr__(self):
        return self.__class__.__name__ + '(mean={0}, std={1})'.format(self.mean, self.std)


class Gaussian_Noise_Transform(object):
    def __init__(self, seed, mean, std):
        self.seed = seed
        torch.manual_seed(seed)  # TODO: test if this works
        self.std = std
        self.mean = mean

    def __call__(self, tensor):
        noisy_image = tensor + torch.randn(tensor.size()) * self.std + self.mean
        if torch.max(tensor) > 1:
            noisy_image = torch.clip(noisy_image, 0, 255)
        else:
            noisy_image = torch.clip(noisy_image, 0, 1)
        return noisy_image

    def __repr__(self):
        return self.__class__.__name__ + '(mean={0}, std={1})'.format(self.mean, self.std)


class FGSM_Transform(object):
    def __init__(self, model, epsilon):
        self.model = model
        self.epsilon = epsilon

    def transform(self, data, target):
        '''
        single input!
        '''
        epsilon = self.epsilon

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = self.model.to(device)
        data, target = data.to(device), target.to(device)
        data.requires_grad = True
        output = model(data)
        label = output.argmax()
        if label != target.item():
            return [data[0].detach().cpu(), target.detach().cpu()]
        else:
            loss = F.nll_loss(output, target)
            model.zero_grad()
            loss.backward(retain_graph=True)
            data_grad = data.grad.data
            sign_data_grad = data_grad.sign()

            while epsilon < 1:
                perturbed_data = self.fgsm_attack(data, self.epsilon, sign_data_grad)
                pert_output = model(perturbed_data)
                pert_label = pert_output.argmax()
                if pert_label.item() != label:
                    return [perturbed_data[0].detach().cpu(), target.detach().cpu()]
                else:
                    epsilon = epsilon + 0.05
        return [perturbed_data[0].detach().cpu(), target.detach().cpu()]

    def __call__(self, sample):
        data, target = sample
        if len(data.shape) < 4:
            data = data[None, :]
            return self.transform(data, target)
        else:
            images,labels = [],[]
            for idx, input in enumerate(data):
                perturbed_input = self.transform(input[None, :], target[idx].unsqueeze(0))
                images.append(perturbed_input[0])
                labels.append(perturbed_input[1])
            return [torch.stack(images,dim=0),torch.cat(labels,dim=0)]

    def fgsm_attack(self, image, epsilon, sign_data_grad):
        perturbed_image = image + epsilon * sign_data_grad
        if torch.max(image) > 1:
            perturbed_image = torch.clip(perturbed_image, 0, 255)
        else:
            perturbed_image = torch.clip(perturbed_image, 0, 1)
        return perturbed_image


class To_Tensor_With_Label_Transform(object):
    def __init__(self, transform=[]) -> None:
        self.transform = transforms.Compose([transforms.ToTensor()]+ transform)

    def __call__(self, sample):
        image, label = sample
        image = self.transform(image)
        label = torch.tensor([label])
        return (image, label)


class Contrast_Transform(object):
    def __init__(self, contrast_factor):
        self.factor = contrast_factor

    def __call__(self, sample):
        return transforms.functional.adjust_contrast(sample, self.factor)


class Brightness_Transform(object):
    def __init__(self, brightness_factor):
        self.factor = brightness_factor

    def __call__(self, sample):
        return transforms.functional.adjust_brightness(sample, self.factor)


class Invert_Transform(object):
    def __call__(self, sample):
        return transforms.functional.invert(sample)


class Rotate_Transform(object):
    def __init__(self, rotation_factor):
        self.factor = rotation_factor

    def __call__(self, sample):
        return transforms.functional.rotate(sample, self.factor)


class Add_Dimension_Transform(object):
    def __call__(self, sample):
        data, label = sample
        return [data[None, :], label]


class Remove_Dimension_Transform(object):
    def __call__(self, sample):
        data, label = sample
        return [data[0], label[0]]


def load_noise_file(file):
    with open(file, "r") as file:
        result_seed = []
        result_mean = []
        result_stddev = []
        for line in file:
            # Split the line by space
            parameters = line.strip().split()

            seed = int(parameters[0])
            mean = float(parameters[1])
            stddev = float(parameters[2])
            result_seed.append(seed)
            result_mean.append(mean)
            result_stddev.append(stddev)
    return result_seed, result_mean, result_stddev
