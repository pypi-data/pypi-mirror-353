# This file is part of Monitizer, but was adapted from https://github.com/VeriXAI/Outside-the-Box/tree/master
#
# SPDX-FileCopyrightText: 2020 Anna Lukina
#
# SPDX-License-Identifier: LicenseRef-arxiv

# Import the utility function for computing the cluster center.
from .Clusters import cluster_center


class Abstraction:
    """
    Represents a general abstraction, providing basic methods for string representation and computing mean.
    This class can be subclassed to provide more specialized abstraction behaviors.
    """

    def short_str(self) -> str:
        """
        Provides a shortened string representation of the abstraction.

        Returns:
            str: A short description of the abstraction, in this case, its name.
        """
        return self.name

    @property
    def name(self) -> str:
        """
        Property that returns the name of the abstraction.
        Used for representation purposes.

        Returns:
            str: The name of the abstraction.
        """
        return f"Abstraction"

    def mean_computer(self, clusterer, cj) -> callable:
        """
        Creates and returns a lambda function to compute the mean for a given cluster.

        Args:
            clusterer: The clusterer object that contains clustering information.
            cj: The specific cluster for which the mean should be computed.

        Returns:
            callable: A function that, when called, computes and returns the center of the given cluster.
        """
        return lambda: cluster_center(clusterer, cj)
