# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from torch.utils.data import Dataset

class Restricted_Index_Dataset(Dataset):
    def __init__(self, dataset, filename):
        #TODO: Can we improve the speed if we store a dataloader instead of the set, then 
        # store and index and increase it. Then we would just iterate over the set until we reach the next important index.
        self.base_dataset = dataset
        with open(filename, 'r') as f:
            string = f.readline()
            string = string[1:-1]
            string = string.split(", ")
            l = [int(x) for x in string]
            self.list_of_indices = l

    def __len__(self):
        return len(self.list_of_indices)

    def __getitem__(self, idx):
        data = self.base_dataset.__getitem__(self.list_of_indices[idx])        
        return data
    

class Transform_With_Label_Dataset(Dataset):
    def __init__(self, dataset, transform) -> None:
        self.dataset = dataset
        self.transform = transform

    def __len__(self):
        return self.dataset.__len__()

    def __getitem__(self, idx):
        data = self.dataset.__getitem__(idx)
        if self.transform:
            data = self.transform(data)
        return data