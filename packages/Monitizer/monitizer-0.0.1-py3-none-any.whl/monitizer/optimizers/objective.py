# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from monitizer.monitors.Monitor import BaseMonitor
from monitizer.optimizers.optimization_config import OptimizationConfig
from abc import abstractmethod, ABC


class Objective(ABC):
    """
    The interface for a general objective.

    Any objective must have onw function: __call__, i.e., it must be possible to do Objective(monitor) to evaluate
     a monitor relative to this objective.
    """
    def __init__(self, config: OptimizationConfig):
        """
        Initialize the objective and store the configuration.
        """
        self.config = config

    @abstractmethod
    def __call__(self, monitor: BaseMonitor) -> float:
        """
        Call the objective to evaluate a monitor.

        :param monitor: the monitor to be evaluated (must be initialized)
        :type monitor: BaseMonitor
        :rtype: float
        :return: the value of the objective function on the monitor
        """
        assert monitor.is_initialized()
