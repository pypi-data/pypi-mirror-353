# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import pandas as pd
from monitizer.monitors.Monitor import BaseMonitor
from typing import Callable
from monitizer.optimizers.optimization_config import OptimizationConfig
from monitizer.optimizers.objective import Objective
from monitizer.optimizers.multi_objectives import MultiObjective
import numpy as np
import logging


def optimize_general(monitor: BaseMonitor, optimization_objective: Objective, config: OptimizationConfig,
                     optimization_method: Callable) -> (BaseMonitor, pd.DataFrame):
    """
    This function distinguishes between multi-objective and single-objective optimization.
    The single-objective case can simply be done once.
    The multi-objective optimization means that we have to do a single-optimization for each possible weighting
    of the objectives.

    :param monitor: the monitor to be optimized
    :type monitor: BaseMonitor
    :param optimization_objective: the objective function that is to be maximized
    :type optimization_objective: Objective
    :param config: the optimization configuration containing all necessary information and specifications
    :type config: OptimizationConfig
    :param optimization_method: the algorithm for optimization
    :type optimization_method: Callable
    :rtype: (BaseMonitor, pd.DataFrame)
    :return: the optimized monitor or the information about different weightings of the objectives for the single-
     and multi-objective optimization respectively
    """
    if isinstance(optimization_objective, MultiObjective):
        logging.debug("## Multi-Objective Optimization")
        columns = optimization_objective.get_columns()
        columns += ['param-' + j for j in monitor.get_parameters().keys()]
        df = pd.DataFrame(columns=columns)
        weight_choices = get_weight_choices(optimization_objective.get_num_objectives(),
                                            int(config.num_splits))
        logging.debug(f"Trying out {len(weight_choices)} many combinations: {weight_choices}.")
        for weight_choice in weight_choices:
            logging.debug(f"Optimizing weighting {weight_choice}.")
            optimization_objective.set_weights(weight_choice)
            intermediate_monitor = optimization_method(monitor, optimization_objective, config)
            logging.debug(f"Finished single-objective optimization.")
            result = optimization_objective.evaluate(intermediate_monitor)
            line = result[0]
            line += list([monitor.get_parameters()[j] for j in monitor.get_parameters().keys()])
            df.loc[len(df)] = line
        logging.debug("Finished multi-objective optimization.")
        return None, df
    else:
        logging.debug("## Single-Objective Optimization")
        return optimization_method(monitor, optimization_objective, config), None


def get_weight_choices(num_objectives: int, num_split: int) -> list:
    """
    Given the number of objectives and the number of possible weights per objective, compute a grid for the weights.

    :param num_objectives: the amount of objectives in a multi-objective query
    :type num_objectives: int
    :param num_split: the number of possible weights per objective
    :type num_split: int
    :rtype: list(list(float))
    :return: a list of possible weight combinations (each a list of weights)
    """
    v = np.append(np.arange(0, 1, 1 / num_split), 1)
    G = np.meshgrid(*[v] * num_objectives)
    m = sum(G) == 1
    result = list(zip(*[g[m] for g in G]))
    return result
