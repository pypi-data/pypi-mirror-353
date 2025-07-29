# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import torch
import torchvision
from torchvision.datasets import ImageFolder
from torchvision.transforms import ToTensor
from torch.utils.data import random_split
from torch.utils.data.dataloader import DataLoader
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import matplotlib.pyplot as plt
import numpy as np
import os
from torch.utils.data import Subset

# without = ["bird", "automobile", "horse"]
# data_dir = './cifar10'

# print(os.listdir(data_dir))
# classes = os.listdir(data_dir + "/train")
# print(classes)

# airplane_files = os.listdir(data_dir + "/train/airplane")
# print('No. of training examples for airplanes:', len(airplane_files))
# print(airplane_files[:5])

# dataset = ImageFolder(data_dir+'/train', transform=ToTensor())
# dataset_test = ImageFolder(data_dir+'/test', transform=ToTensor())

# # select the indices of all other folders
# supressed_indices = []
# for c in without:
#     supressed_indices.append(dataset.class_to_idx[c])
# idx = [i for i in range(len(dataset)) if dataset.imgs[i][1] not in supressed_indices]
# # build the appropriate subset
# subset = Subset(dataset, idx)

# random_seed = 42
# torch.manual_seed(random_seed);

# val_size = 2000
# train_size = len(subset) - val_size

# train_ds, val_ds = random_split(subset, [train_size, val_size])
# len(train_ds), len(val_ds)

# batch_size = 4

# train_dl = DataLoader(train_ds, batch_size, shuffle=True, num_workers=0, pin_memory=True)
# val_dl = DataLoader(val_ds, batch_size*2, num_workers=0, pin_memory=True)
# test_dl = val_dl = DataLoader(dataset_test, batch_size*2, shuffle=True, num_workers=0, pin_memory=True)


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    
class Net2(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 8, 5)
        self.batch1 = nn.BatchNorm2d(8)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(8, 24, 3)
        self.batch2 = nn.BatchNorm2d(24)
        self.conv3 = nn.Conv2d(24, 48, 1)
        self.batch3 = nn.BatchNorm2d(48)
        self.fc1 = nn.Linear(48 * 3 * 3, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.batch1(self.conv1(x))))
        x = self.pool(F.relu(self.batch2(self.conv2(x))))
        x = self.pool(F.relu(self.batch3(self.conv3(x))))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# # Todo: change to the right model
# PATH = './cifar_net2'
# for c in without:
#     PATH += f"_w{c}"
# model = Net2()


# criterion = nn.CrossEntropyLoss()
# optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
        

# for epoch in range(4):  # loop over the dataset multiple times

#     running_loss = 0.0
#     for i, data in enumerate(train_dl, 0):
#         # get the inputs; data is a list of [inputs, labels]
#         inputs, labels = data

#         # zero the parameter gradients
#         optimizer.zero_grad()

#         # forward + backward + optimize
#         outputs = model(inputs)
#         loss = criterion(outputs, labels)
#         loss.backward()
#         optimizer.step()

#         # print statistics
#         running_loss += loss.item()
#         if i % 2000 == 1999:    # print every 2000 mini-batches
#             print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 2000:.3f}')
#             running_loss = 0.0

# print('Finished Training')

# torch.save(model.state_dict(), PATH)


# dataiter = iter(test_dl)
# images, labels = next(dataiter)

# def imshow(img):
#     img = img / 2 + 0.5     # unnormalize
#     npimg = img.numpy()
#     plt.imshow(np.transpose(npimg, (1, 2, 0)))
#     plt.show()

# # print images
# imshow(torchvision.utils.make_grid(images))
# print('GroundTruth: ', ' '.join(f'{classes[labels[j]]:5s}' for j in range(4)))

# net = Net2()
# net.load_state_dict(torch.load(PATH))
# outputs = net(images)

# _, predicted = torch.max(outputs, 1)

# print('Predicted: ', ' '.join(f'{classes[predicted[j]]:5s}'
#                               for j in range(4)))

# correct = 0
# total = 0
# # since we're not training, we don't need to calculate the gradients for our outputs
# with torch.no_grad():
#     for data in test_dl:
#         images, labels = data
#         # calculate outputs by running images through the network
#         outputs = net(images)
#         # the class with the highest energy is what we choose as prediction
#         _, predicted = torch.max(outputs.data, 1)
#         total += labels.size(0)
#         correct += (predicted == labels).sum().item()

# print(f'Accuracy of the network on the 10000 test images: {100 * correct // total} %')

# # prepare to count predictions for each class
# correct_pred = {classname: 0 for classname in classes}
# total_pred = {classname: 0 for classname in classes}

# # again no gradients needed
# with torch.no_grad():
#     for data in test_dl:
#         images, labels = data
#         outputs = net(images)
#         _, predictions = torch.max(outputs, 1)
#         # collect the correct predictions for each class
#         for label, prediction in zip(labels, predictions):
#             if label == prediction:
#                 correct_pred[classes[label]] += 1
#             total_pred[classes[label]] += 1


# # print accuracy for each class
# for classname, correct_count in correct_pred.items():
#     accuracy = 100 * float(correct_count) / total_pred[classname]
#     print(f'Accuracy for class: {classname:5s} is {accuracy:.1f} %')