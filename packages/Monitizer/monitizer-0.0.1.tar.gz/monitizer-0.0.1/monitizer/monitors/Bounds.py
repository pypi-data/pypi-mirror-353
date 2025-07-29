# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import numpy as np
from abc import abstractmethod, ABC
import random

class Bounds(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_random_draw(self):
        pass

    @abstractmethod
    def get_grid_params(self, count: int) -> list:
        pass


class FloatBounds(Bounds):
    def __init__(self, lower: float, upper: float):
        self.lower = lower
        self.upper = upper

    def get_random_draw(self) -> float:
        return random.uniform(self.lower, self.upper)

    def get_grid_params(self, count: int) -> list:
        # if count == "low":
        #     grid_params = [self.lower, self.upper]
        #     return grid_params
        # elif count == "medium":
        #     count = 5
        # elif count == "large":
        #     count = 20
        if count == "1":
            grid_params = [(self.lower + self.upper) / 2]
            return grid_params
        if self.lower == self.upper:
            return [self.lower]
        return list(np.linspace(self.lower, self.upper, count))


class IntegerBounds(Bounds):
    def __init__(self, lower: int, upper: int):
        self.lower = lower
        self.upper = upper

    def get_random_draw(self) -> int:
        return random.randint(self.lower, self.upper)

    def get_grid_params(self, count: int) -> list:
        if count == 1:
            grid_params = [(self.lower + self.upper) // 2]
            return grid_params
        if self.lower == self.upper:
            return [self.lower]
        grid_params = list(np.unique(np.round(np.linspace(self.lower, self.upper, count)).astype(int)))
        return grid_params
        # np.random.choice(np.arange(self.lower, self.upper + 1), size=count, replace=False)


class UniqueList(Bounds):
    def __init__(self, input: list):
        self.selection_list = input

    def get_random_draw(self) -> list:
        res = [x for x in self.selection_list if random.choice((True, False))]
        if len(res)==0:
            res = random.sample(self.selection_list, 1)
        return res

    def get_grid_params(self, count: int) -> list:
        if count > len(self.selection_list):
            grid_params = self.selection_list
        else:
            grid_params = random.sample(self.selection_list, count)
        return grid_params


class ListOfBounds(Bounds):
    def __init__(self, input: list):
        self.list_of_bounds = input

    def get_random_draw(self) -> list:
        result = []
        for bound in self.list_of_bounds:
            result.append(bound.get_random_draw())
        return result

    def get_grid_params(self, count: int) -> list:
        # todo: this case can be fixed by keeping layer and threshold in a dictionary,
        #  currently same as random
        result = []
        for bound in self.list_of_bounds:
            result.append(bound.get_random_draw())
        return result
