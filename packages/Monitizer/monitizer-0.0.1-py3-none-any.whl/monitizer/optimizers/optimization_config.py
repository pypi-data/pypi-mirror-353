# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from configparser import ConfigParser
import os


# EXPECTED STRUCTURE OF THE CONFIG
# [Optimization]
# [Optimization.Objective]
# type = single-objective
# function = OptimalForOODClassSubjectToFNR
# file =
# # single-objective currently contains: OptimalForOODClass, OptimalForOODClassSubjectToFNR
# # multi-objective currently contains: OptimalForOODClasses, OptimalForOODClassesSubjectToFNR
#
# [Optimization.Objective.Specification]
# ood_classes = Noise/Gaussian
# tnr_minimum = 70
#
# [Optimization.Optimizer]
# type = random
#
# [Optimization.Optimizer.Random]
# episodes = 1
#
# [Optimization.Optimizer.Grid-search]
# grid_count = 4
#
# [Optimization.Optimizer.Gradient-descent]
# episodes = 1
# learning_rate = 1
#
# [Multi-Objective]
# num_splits = 4

class OptimizationConfig:
    """
    Configuration that reads a config-file and stores everything in a more readable and useable format.
    """
    def __init__(self, config_file: str):
        """
        Parse the config-file and store the values in variables.
        """
        if not os.path.isfile(config_file):
            raise ValueError(f"The optimization config in {config_file} does not exist!")
        config = ConfigParser()
        config.read(config_file)

        if config.has_option("Optimization", "output_plots"):
            self.output_plots = True
        else:
            self.output_plots = False

        if config.has_option('Optimization.Objective', 'type'):
            self.objective_type = config.get('Optimization.Objective', 'type')
        else:
            raise KeyError(
                f'The config {config_file} does not have the right structure.\n For single-objective, please add \n'
                f'[Optimization.Objective]\n'
                f'type = single-objective\n')
        if config.has_option('Optimization.Objective', 'function'):
            self.objective_function = config.get('Optimization.Objective', 'function')
        else:
            raise KeyError(
                f'The config {config_file} does not have the right structure.\n Please define the objective function.'
                f'For example, if you want to use "OptimalForOODClassSubjectToFNR" as objective, add \n'
                f'[Optimization.Objective]\n'
                f'function = OptimalForOODClassSubjectToFNR\n')

        if config.has_option('Optimization.Objective', 'file'):
            self.objective_file = config.get('Optimization.Objective', 'file')
        else:
            self.objective_file = ""

        if config.has_section('Optimization.Objective.Specification'):
            self.additional_objective_info = config['Optimization.Objective.Specification']
        else:
            raise UserWarning("If your objective needs some specification, you should add a section for this in the config.\n"
                              "This could look like this:\n"
                              "[Optimization.Objective.Specification]\n"
                              "ood_classes=Noise/Gaussian,NewWorld/CIFAR10\n")

        if config.has_option('Optimization.Optimizer','type'):
            self.optimiziation_function = config.get('Optimization.Optimizer', 'type')
        else:
            raise KeyError(
                f'The config {config_file} does not have the right structure.\n '
                f'Please define the optimization function.'
                f'For example, if you want to use random optimization, add \n'
                f'[Optimization.Optimizer]\n'
                f'function = random\n')

        if self.optimiziation_function == 'random':
            if config.has_option('Optimization.Optimizer.Random', 'episodes'):
                self.episodes = config.getint('Optimization.Optimizer.Random', 'episodes')
            else:
                raise KeyError(
                    f'The config {config_file} does not have the right structure.\n '
                    f'Please define the information for the optimization function.'
                    f'You specified random optimization, so please add \n'
                    f'[Optimization.Optimizer.Random]\n'
                    f'episodes = 10\n')

        elif self.optimiziation_function == 'grid-search':
            if config.has_option('Optimization.Optimizer.Grid-search', 'grid_count'):
                self.grid_count = config.getint('Optimization.Optimizer.Grid-search', 'grid_count')
            else:
                raise KeyError(
                    f'The config {config_file} does not have the right structure.\n '
                    f'Please define the information for the optimization function.'
                    f'You specified grid-search, so please add\n'
                    f'[Optimization.Optimizer.Grid-search]\n'
                    f'grid_count = 10\n')

        elif self.optimiziation_function == 'gradient-descent':
            if config.has_section('Optimization.Optimizer.Gradient-descent'):
                if config.has_option('Optimization.Optimizer.Gradient-descent', 'episodes'):
                    self.episodes = config.getint('Optimization.Optimizer.Gradient-descent', 'episodes')
                else:
                    raise KeyError(
                        f'The config {config_file} does not have the right structure.\n '
                        f'Please define the information for the optimization function.'
                        f'You specified gradient descent, so please add\n'
                        f'[Optimization.Optimizer.Gradient-descent]\n'
                        f'episodes = 10\n'
                        f'learning_rate = 1\n')
                if config.has_option('Optimization.Optimizer.Gradient-descent', 'learning_rate'):
                    self.learning_rate = config.getfloat('Optimization.Optimizer.Gradient-descent', 'learning_rate')
                else:
                    raise KeyError(
                    f'The config {config_file} does not have the right structure.\n '
                    f'Please define the information for the optimization function.'
                    f'You specified gradient descent, so please add\n'
                    f'[Optimization.Optimizer.Gradient-descent]\n'
                    f'episodes = 10\n'
                    f'learning_rate = 1\n')

            else:
                raise KeyError(
                    f'The config {config_file} does not have the right structure.\n '
                    f'Please define the information for the optimization function.'
                    f'You specified gradient descent, so please add\n'
                    f'[Optimization.Optimizer.Gradient-descent]\n'
                    f'episodes = 10\n'
                    f'learning_rate = 1\n')

        if self.objective_type == 'multi-objective':
            if config.has_option('Multi-Objective', 'num_splits'):
                self.num_splits = config.getint('Multi-Objective', 'num_splits')
            else:
                raise KeyError(
                    f'The config {config_file} does not have the right structure.\n '
                    f'Please define the information for the multi objective case. Please add\n'
                    f'[Multi-Objective]\n'
                    f'num_splits=4\n')

        self._config = config