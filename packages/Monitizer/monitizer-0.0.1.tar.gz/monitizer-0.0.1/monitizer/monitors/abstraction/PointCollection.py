# This file is part of Monitizer, but was adapted from https://github.com/VeriXAI/Outside-the-Box/tree/master
#
# SPDX-FileCopyrightText: 2020 Anna Lukina
#
# SPDX-License-Identifier: LicenseRef-arxiv

from scipy.spatial.distance import euclidean
import numpy as np

CONVEX_HULL_HALF_SPACE_DISTANCE_CORNER_CASE = 0.0
COMPUTE_MEAN = False
PRINT_CREDIBILITY = True


class PointCollection(object):
    def __init__(self):
        self.sum = None
        self.n_points = 0
        self._mean = None
        self.n_novelty_points = 0
        self._incredibility = None

    def create(self, point):
        if COMPUTE_MEAN:
            self.sum = point
        self.n_points = 1

    def isempty(self):
        return self.n_points == 0

    def add_novelty_point(self):
        self.n_novelty_points += 1

    def add(self, point):
        if COMPUTE_MEAN:
            for i, pi in enumerate(point):
                self.sum[i] += pi
        self.n_points += 1

    def mean(self):
        if self._mean is None:
            assert COMPUTE_MEAN, "Mean computation was deactivated!"
            self._mean = [pi / self.n_points for pi in self.sum]
        return self._mean

    def center(self):
        return self.mean()

    def euclidean_distance(self, point, epsilon, epsilon_relative):
        closest_point = self.get_closest_point(point, epsilon, epsilon_relative)
        assert list(point) != closest_point, "Confidence for points inside the set should not be asked for!"
        dist = euclidean(point, closest_point)
        radius = euclidean(closest_point, self.center())
        if radius == 0.0:
            # corner case: the set consists of a single point only
            confidence = dist
        else:
            # normalization so that confidence 1.0 corresponds to dist == radius
            confidence = dist / radius
        return confidence

    def get_closest_point(self, point, epsilon, epsilon_relative):
        raise NotImplementedError("get_closest_point() is not implemented by {}".format(type(self)))



