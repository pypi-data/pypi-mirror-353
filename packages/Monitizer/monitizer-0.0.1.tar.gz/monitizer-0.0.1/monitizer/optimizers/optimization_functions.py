# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import logging
from monitizer.monitors.Monitor import BaseMonitor
import pandas as pd
from monitizer.monitors.Bounds import FloatBounds, IntegerBounds
from monitizer.optimizers.objective import Objective
from monitizer.optimizers.optimization_config import OptimizationConfig
import copy
import math
from tqdm import tqdm
import matplotlib.pyplot as plt


def dummy_optimization_function(monitor: BaseMonitor, optimization_objective: Objective,
                                config: OptimizationConfig) -> BaseMonitor:
    """
    Any optimization function should look like this:
    Input:
    - monitor (BaseMonitor) that should be optimized
    - optimization_objective (Objective) on which the monitor is evaluated
    - specs (ConfigParser) the specification for the optimization
    Output:
    - the optimized monitor (BaseMonitor)
    """
    return


def optimize_monitor_random(monitor: BaseMonitor, optimization_objective: Objective,
                            config: OptimizationConfig) -> BaseMonitor:
    """
    Optimizes a monitor randomly for a given objective.
    This function tries out a number (specified in the config) of randomly sampled parameters and choses the best.

    :param monitor: the monitor to be optimized
    :type monitor: BaseMonitor
    :param optimization_objective: the objective that should be maximized
    :type optimization_objective: Objective
    :param config: the configuration for the optimization
    :type config: OptimizationConfig
    :rtype: BaseMonitor
    :return: the optimized monitor
    """
    monitor.fit()
    results = {}
    params = monitor.get_parameters()
    logging.debug(f"This monitor has the parameters: {params}.")
    param_bounds = monitor.get_parameter_bounds()
    logging.debug(f"The bounds for the parameters are: {param_bounds}.")
    columns = list(monitor.get_parameters().keys()) + ['objective']
    df = pd.DataFrame(columns=columns)
    logging.debug(f"Trying out {config.episodes} random combinations...")
    for i in tqdm(range(config.episodes)):
        # initialize random monitor
        for parameter in params.keys():
            params[parameter] = param_bounds[parameter].get_random_draw()
        logging.debug(f"Trying out the random combination {params}.")
        monitor.set_parameters(params)

        # evaluate monitor
        result = optimization_objective(monitor)
        logging.debug(f"The objective returns {result} for this monitor.")
        row = [params[k] for k in list(df.columns)[:-1]] + [result]
        df.loc[len(df)] = row
        results[result] = copy.deepcopy(params)
    print(df.to_markdown())
    best_param = results[max(results)]
    logging.debug(f"The best parameters are {best_param}.")

    monitor.set_parameters(best_param)
    return monitor


def optimize_monitor_grid_search(monitor: BaseMonitor, optimization_objective: Objective,
                                 config: OptimizationConfig) -> BaseMonitor:
    """
    Optimizes a given monitor for an objective using grid-search.
    For each parameter (that is either integer or float), we define a grid (i.e., a set of possible values). We then
    try out every combination.
    Note: this function scales exponential in the number of parameters of a monitor!

    :param monitor: the monitor to be optimized
    :type monitor: BaseMonitor
    :param optimization_objective: the objective that should be maximized
    :type optimization_objective: Objective
    :param config: the configuration for the optimization
    :type config: OptimizationConfig
    :rtype: BaseMonitor
    :return: the optimized monitor
    """
    from sklearn.model_selection import ParameterGrid
    monitor.fit()
    results = {}
    params = monitor.get_parameters()
    logging.debug(f"This monitor has the parameters: {params}.")
    params_bounds = monitor.get_parameter_bounds()
    logging.debug(f"The bounds for the parameters are: {params_bounds}.")
    for bound in params_bounds.keys():
        if not (isinstance(params_bounds[bound], IntegerBounds) or isinstance(params_bounds[bound], FloatBounds)):
            raise ValueError(f"This monitor contains a parameter with bounds {bound}. They cannot be optimized using "
                             f"grid search!")

    # add
    grid_params = {}
    for parameter in params.keys():
        grid_params[parameter] = params_bounds[parameter].get_grid_params(config.grid_count)
        logging.debug(f"Adding the grid-values for parameter {parameter}: {grid_params[parameter]}.")
    grid_search_space = ParameterGrid(grid_params)
    logging.debug(f"The size of the grid is {len(grid_search_space)}.")

    columns = list(monitor.get_parameters().keys()) + ['objective']
    df = pd.DataFrame(columns=columns)

    # now evaluate every instance from this grid search space
    '''
    grid_search_space is a list of dictionaries (mapping,iterable) of parameters
    and can directly be given as input to set parameters
    '''
    for e in tqdm(list(grid_search_space)):
        monitor.set_parameters(e)
        logging.debug(f"Evaluating the parameters {e}....")
        # evaluate monitor
        result = optimization_objective(monitor)
        logging.debug(f"THe value of the objective is {result}.")
        row = [e[k] for k in list(df.columns)[:-1]] + [result]
        df.loc[len(df)] = row
        if not result in results:
            results[result] = copy.deepcopy(e)
    print(df.to_markdown())
    best_param = results[max(results)]
    logging.debug(f"The best parameters are {best_param}.")

    monitor.set_parameters(best_param)
    return monitor


def optimize_monitor_gradient_descent(monitor: BaseMonitor, optimization_objective: Objective,
                                      config: OptimizationConfig) -> BaseMonitor:
    """
    Optimizes a given monitor for an objective using gradient descent.
    The gradient is approximated by looking left and right of the current value and evaluating the objective there.

    :param monitor: the monitor to be optimized
    :type monitor: BaseMonitor
    :param optimization_objective: the objective that should be maximized
    :type optimization_objective: Objective
    :param config: the configuration for the optimization
    :type config: OptimizationConfig
    :rtype: BaseMonitor
    :return: the optimized monitor
    """
    iteration = config.episodes
    learning_rate = config.learning_rate
    logging.debug(f"Gradient descent done with {iteration} episodes and learning rate {learning_rate}.")
    # initialize params
    monitor.fit()
    params = monitor.get_parameters()
    logging.debug(f"This monitor has the parameters: {params}.")
    parameter_bounds = monitor.get_parameter_bounds()
    logging.debug(f"The bounds for the parameters are: {parameter_bounds}.")

    for param in parameter_bounds.keys():
        bound = parameter_bounds[param]
        if not (isinstance(bound, FloatBounds) or isinstance(bound, IntegerBounds)):
            raise ValueError(
                f"Gradient descent only works with reel or integer numbers, but {param} has bounds of type {type(bound)}.")

    best_params_values = {}
    for param in params.keys():
        best_params_values[param] = parameter_bounds[param].get_random_draw()
        logging.debug(f"Random intialization of {param} to {best_params_values[param]}.")

    best_performance = float('-inf')
    columns = list(monitor.get_parameters().keys()) + ['objective']
    df = pd.DataFrame(columns=columns)
    gradients = {}
    stop_counter = 0
    for i in tqdm(range(iteration)):
        logging.debug(f" iteration {i}")
        for param, val in best_params_values.items():
            logging.debug(f"  Gradient for parameter {param}")
            gradient = 0
            success = False
            noise = (parameter_bounds[param].upper - parameter_bounds[param].lower) / 100
            for i in range(3):
                noise = noise * 10
                logging.debug(f"   Noise: {noise}")
                if noise == 0:
                    gradients[param] = 0
                    success=True
                    logging.debug(f"   Noise is zero, stopping for this parameter.")
                    break
                epsilon_perturb_param = copy.deepcopy(best_params_values)
                if isinstance(parameter_bounds[param], IntegerBounds):
                    epsilon_perturb_param[param] = math.ceil(val + noise)
                else:
                    epsilon_perturb_param[param] = val + noise
                logging.debug(f"   Parameter + epsilon: {epsilon_perturb_param[param]}")
                epsilon_perturb_param[param] = min(epsilon_perturb_param[param], parameter_bounds[param].upper)
                monitor.set_parameters(epsilon_perturb_param)
                performance_plus = optimization_objective(monitor)
                logging.debug(f"   Performance plus: {performance_plus}")

                if isinstance(parameter_bounds[param], IntegerBounds):
                    epsilon_perturb_param[param] = math.floor(val - noise)
                else:
                    epsilon_perturb_param[param] = val - noise
                logging.debug(f"   Parameter - epsilon: {epsilon_perturb_param[param]}")
                epsilon_perturb_param[param] = max(epsilon_perturb_param[param], parameter_bounds[param].lower)
                monitor.set_parameters(epsilon_perturb_param)
                performance_minus = optimization_objective(monitor)
                logging.debug(f"   Performance minus: {performance_minus}")

                gradient = (performance_plus - performance_minus) / (2 * noise)
                logging.debug(f"   Gradient: {gradient}")
                success = gradient!=0
                if success:
                    logging.debug("   Gradient is not zero, continue gradient descent")
                    break
                logging.debug("   Gradient is zero, continue with different noises...")
            if not success:
                logging.debug("   Gradient is still zero, don't do gradient descent for this parameter.")
                gradient = 0
                logging.debug(
                    "   We've not yet found a good gradient. Do another random initialization of the parameters.")
                for param in params.keys():
                    best_params_values[param] = parameter_bounds[param].get_random_draw()
                    logging.debug(f"   Random intialization of {param} to {best_params_values[param]}.")

            if gradient == 0:
                if len(gradients)>0:
                    # use the old gradient
                    logging.debug(f"   Gradient is still zero, use the last gradient {gradients[param]}")
                    gradient = gradients[param]
                    stop_counter += 1
                else:
                    # we have not yet found a reasonable gradient
                    # do another initialization
                    logging.debug("   We've not yet found a good gradient. Do another random initialization of the parameters.")
                    for param in params.keys():
                        best_params_values[param] = parameter_bounds[param].get_random_draw()
                        logging.debug(f"   Random intialization of {param} to {best_params_values[param]}.")
            else:
                if gradient>0:
                    gradient = max((1 - performance_plus),0.1) / gradient
                    logging.debug(f"  Scale the gradient to {gradient}")
                else:
                    gradient = max((1-performance_minus, 0.1)) / gradient
                    logging.debug(f"  Scale the gradient to {gradient}")
            if not param in gradients or not gradient == 0:
                gradients[param] = gradient
            #print(f"{gradient=}")
        logging.debug(f" The gradients are {gradients}.")

        total_gradient = 0
        for param, gradient in gradients.items():
            total_gradient += abs(gradient)
            if isinstance(parameter_bounds[param], IntegerBounds):
                best_params_values[param] = max(
                    min(math.ceil(learning_rate * gradient + best_params_values[param]), parameter_bounds[param].upper),
                    parameter_bounds[param].lower)
            else:
                best_params_values[param] = max(
                    min(learning_rate * gradient + best_params_values[param], parameter_bounds[param].upper),
                    parameter_bounds[param].lower)
            logging.debug(f" Gradient descent step for {param} setting new value to {best_params_values[param]}.")
        if total_gradient == 0:
            stop_counter+=1
            logging.debug(f" All the gradients are zero. Increase the stepcounter to {stop_counter}.")
            #print(f"inc stepcounter")
        if stop_counter / len(best_params_values) >= 3:
            logging.debug(f"We have not seen a good gradient for the last 2 steps, stop gradient descent.")
            break
        monitor.set_parameters(best_params_values)
        logging.debug(f"Current best paramters: {best_params_values}")
        current_performance = optimization_objective(monitor)
        row = [best_params_values[p] for p in params.keys()] + [current_performance]
        df.loc[len(df)] = row
        logging.debug(f"Current performance: {current_performance} vs. best performance: {best_performance}.")
        # saving the best param
        # todo: fix it for all the optimization objectives
        if current_performance >= 1:
            break
        if current_performance >= best_performance:
            best_performance = current_performance
            best_params_values = copy.deepcopy(best_params_values)

    if config.output_plots:
        plt.plot(df['objective'])
        plt.xticks(range(len(df['objective'])))
        plt.xlabel("Episode")
        plt.ylabel("Objective")
        plt.savefig("Gradient_descent_optimization.jpg")
    print(df.to_markdown())
    # set the monitor params to best found
    monitor.set_parameters(best_params_values)
    logging.debug(f"The best parameters are {best_params_values}.")
    return monitor
