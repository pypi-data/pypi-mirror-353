# This file is part of Monitizer, but was adapted from https://github.com/VeriXAI/Outside-the-Box/tree/master
#
# SPDX-FileCopyrightText: 2020 Anna Lukina
#
# SPDX-License-Identifier: LicenseRef-arxiv

from .SetBasedAbstraction import SetBasedAbstraction
from .Box import Box


class BoxAbstraction(SetBasedAbstraction):
    def __init__(self, size=1, epsilon=0., epsilon_relative=True):
        super().__init__(size, epsilon, epsilon_relative)

    def name(self):
        return "Box"

    def set_type(self):
        return Box


