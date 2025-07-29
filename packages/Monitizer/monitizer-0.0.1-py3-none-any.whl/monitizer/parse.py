# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import logging
import onnx
import torch
from google.protobuf.message import DecodeError
from pickle import UnpicklingError
from monitizer.network.neural_network import NeuralNetwork
from monitizer.benchmark.dataset import Dataset
from monitizer.benchmark.load import load
import sys, os
from monitizer.monitors.Monitor import BaseMonitor
from monitizer.optimizers.objective import Objective
import json
from typing import Callable
from configparser import ConfigParser, ParsingError
from monitizer.optimizers.optimization_config import OptimizationConfig


def parse_monitor_template(monitor_template: str, model: NeuralNetwork, dataset: Dataset, seed: int) -> BaseMonitor:
    """
    Given the name of the monitor-template, create an instance of this template.

    :param monitor_template: name of the monitor-template
    :type monitor_template: str
    :param model: Neural Network that is stored in the monitor, i.e., the network that the monitor is monitoring
    :type model: NeuralNetwork
    :param dataset: the ID-dataset on which the monitor is trained
    :type dataset: Dataset
    :param seed: The random seed for determination (necessary for the Box monitor and irrelevant for the others)
    :type seed: int
    :rtype: BaseMonitor
    :return: A monitor-template object
    """
    if "gauss-one" in monitor_template.lower():
        from monitizer.monitors.GaussMonitorOneLayer import Monitor
        monitor = Monitor(model, dataset)
    elif "gauss" in monitor_template.lower():
        logging.debug("Create a Gaussian monitor.")
        from monitizer.monitors.GaussMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "energy" in monitor_template.lower():
        logging.debug("Create an Energy monitor.")
        from monitizer.monitors.EnergyMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "odin" in monitor_template.lower():
        logging.debug("Create an ODIN monitor.")
        from monitizer.monitors.ODINMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "box" in monitor_template.lower():
        logging.debug("Create a Box monitor.")
        from monitizer.monitors.BoxMonitor import Monitor
        monitor = Monitor(model, dataset, seed)
    elif "msp" in monitor_template.lower():
        logging.debug("Create a MSP monitor.")
        from monitizer.monitors.MSPMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "mds_old" in monitor_template.lower() in monitor_template.lower():
        from monitizer.monitors.MDSMonitor_old import Monitor
        monitor = Monitor(model, dataset)
    elif "mds" in monitor_template.lower():
        from monitizer.monitors.MDSMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "vim" in monitor_template.lower():
        from monitizer.monitors.VIMMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "she" in monitor_template.lower() or "hopfield" in monitor_template.lower():
        from monitizer.monitors.SHEMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "rmd_old" in monitor_template.lower():
        from monitizer.monitors.RMDMonitor_old import Monitor
        monitor = Monitor(model, dataset)
    elif "rmd" in monitor_template.lower():
        from monitizer.monitors.RMDMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "maxlogit" in monitor_template.lower() or (
            "max" in monitor_template.lower() and "logit" in monitor_template.lower()):
        from monitizer.monitors.MaxLogitMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "knn" in monitor_template.lower():
        from monitizer.monitors.KNNMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "klmatching" in monitor_template.lower():
        from monitizer.monitors.KLMatchingMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "dice" in monitor_template.lower():
        from monitizer.monitors.DICEMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "ash" in monitor_template.lower():
        from monitizer.monitors.ASHMonitor import Monitor
        monitor = Monitor(model, dataset, monitor_template)
    elif "entropy" in monitor_template.lower():
        from monitizer.monitors.EntropyMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "react" in monitor_template.lower():
        from monitizer.monitors.ReActMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "temperature" in monitor_template.lower() or "scaling" in monitor_template.lower():
        from monitizer.monitors.TemperatureScalingMonitor import Monitor
        monitor = Monitor(model, dataset)
    elif "gradnorm" in monitor_template.lower():
        from monitizer.monitors.GradNormMonitor import Monitor
        monitor = Monitor(model, dataset)
    else:
        raise NotImplementedError(f"'{monitor_template}' is currently not supported!")
    monitor._set_parameters_for_optimization(monitor.get_all_parameters())
    return monitor


def parse_monitor_by_user(monitor_by_user, model: NeuralNetwork, dataset: Dataset,
                          monitor_name: str = "Monitor") -> BaseMonitor:
    """
    Parses a given python file with the given module name into a monitor-template object

    :param monitor_by_user: location of the implementation
    :type monitor_by_user: str
    :param model: Neural Network that is stored in the monitor, i.e., the network that the monitor is monitoring
    :type model: NeuralNetwork
    :param dataset: the ID-dataset on which the monitor is trained
    :type dataset: Dataset
    :param monitor_name: the name of the class where the monitor-template is implemented, defaults to "Monitor"
    :type monitor_name: str
    :rtype: BaseMonitor
    :return: A monitor-template object
    """
    include_directory = os.path.dirname(monitor_by_user)
    logging.debug(f"Location of the monitor as given by the user: {include_directory}")
    if include_directory == '':
        include_directory = '.'
    sys.path.insert(0, include_directory)
    mod = __import__(os.path.splitext(os.path.basename(monitor_by_user))[0])
    monitor = getattr(mod, monitor_name)
    monitor = monitor(model, dataset)
    monitor._set_parameters_for_optimization(monitor.get_all_parameters())
    return monitor


def parse_monitor_config(monitor_config: str, model: NeuralNetwork, dataset: Dataset, seed: int) -> BaseMonitor:
    """
    Given the name of the monitor-template, create an instance of this template.

    :param monitor_config: location of the config file
    :type monitor_config: str
    :param model: Neural Network that is stored in the monitor, i.e., the network that the monitor is monitoring
    :type model: NeuralNetwork
    :param dataset: the ID-dataset on which the monitor is trained
    :type dataset: Dataset
    :param seed: The random seed for determination (necessary for the Box monitor and irrelevant for the others)
    :type seed: int
    :rtype: BaseMonitor
    :return: A monitor-template object
    """
    config = ConfigParser()
    try:
        config.read(monitor_config)
        if config.has_option('Monitor', 'name'):
            monitor_name = config.get('Monitor', 'name')
        else:
            raise ParsingError(f"You must provide the monitor name in \n[Monitor]\n name=MONITOR_NAME\n")
        if config.has_option('Monitor', 'location'):
            monitor_location = config.get('Monitor', 'location')
            if monitor_location == 'monitizer':
                monitor = parse_monitor_template(monitor_name, model, dataset, seed)
            else:
                monitor = parse_monitor_by_user(monitor_location, model, dataset, monitor_name)
        else:
            monitor = parse_monitor_by_user(".", model, dataset, monitor_name)

        # set the monitor parameters
        #  set the parameters for optimization
        parameters = config.get("Monitor.Parameter.Optimization", "parameters")
        parameters = json.loads(parameters)
        monitor._set_parameters_for_optimization(parameters)

        #  set the parameters with default values
        parameters = config.get("Monitor.Parameter.Default", "parameter_values")
        parameters = json.loads(parameters)
        monitor.set_parameters(parameters)

        #  check if all parameters are optimized or set
        all_parameters = monitor.get_all_parameters()
        optimized_parameters = monitor.get_parameters()
        default_parameters = set(all_parameters) - set(optimized_parameters)
        for param in default_parameters:
            if all_parameters[param] is None:
                raise ValueError(f"The parameter {param} needs to be optimized or a default value!")

        # set the parameter bounds (if given)
        # todo implement this option

        # set additional specifications
        # todo implement this option

        return monitor
    except ParsingError as e:
        # not a config
        raise ParsingError(f"The config file {monitor_config} is not in the right format.")
    pass


def parse_neural_network(neural_network_file: str) -> NeuralNetwork:
    """
    Parse a given neural network file. We can parse onnx and pickle-dumps of pytorch-networks. They are stored as torch-
    networks internally.

    :param neural_network_file: location of the neural network
    :type neural_network_file: str
    :rtype: NeuralNetwork
    :return: a NeuralNetwork that internally represents the model as a pytorch-model and has some additional functions
    """
    parsed_neural_network = NeuralNetwork()
    try:
        model = onnx.load_model(neural_network_file)
        parsed_neural_network.set_onnx_model(model)
        logging.debug("Neural network was loaded as onnx.")
    except Exception as e:
        logging.debug("The network was not in onnx format, try pytorch.")
        if not type(e) is DecodeError:
            raise (e)
    if not parsed_neural_network.is_initialized():
        try:
            model = torch.load(neural_network_file, weights_only=False)
            parsed_neural_network.set_pytorch_model(model)
            logging.debug("Neural network was loaded as a pytorch model.")
        except Exception as e:
            if not type(e) is UnpicklingError:
                raise (e)
    if not parsed_neural_network.is_initialized():
        raise (NotImplementedError("We only support onnx and pytorch."))
    return parsed_neural_network


def parse_dataset(dataset_name: str) -> Dataset:
    """
    Parse the dataset

    :param dataset_name: the name of the ID dataset
    :type dataset_name: str
    :rtype: Dataset
    :return: a dataset-object that can load ID and OOD data
    """
    internal_config = ConfigParser()
    internal_config.read('monitizer/config/config.ini')
    data_folder = internal_config['DEFAULT']['data_folder']
    logging.debug(f"The location of the data as given by the config is {data_folder}")
    dataset = load(dataset_name, data_folder=data_folder, num_workers=0)
    return dataset


def parse_parameters(parameter_by_user: str) -> dict:
    """
    Parses parameters that are given by the user.
    They must follow the shape of:
    "{'PARAMETER_ONE' : VALUE, 'PARAMETER_TWO' : VALUE}"
    such that they are readable by a json-loader.
    The naming of the parameters must match the ones of the monitor.

    :param parameter_by_user: the string containing the parameters given by the user
    :type parameter_by_user: str
    :rtype: dict
    :return: a dictionary of the mapping from paramter-name to value
    """
    if "'" in parameter_by_user:
        parameter_by_user = parameter_by_user.replace("'", '"')
    result = json.loads(parameter_by_user)
    logging.debug(f"The user has provided parameters for the monitor. They are parsed as : {result}.")
    return result


def parse_optimization_objective(config: OptimizationConfig):
    """
    Load the optimization objective.

    :param config: the loaded optimization configuration file
    :type config: OptimizationConfig
    :rtype: class
    :return: returns the class of the objective, not (!) an instance of it
    """
    logging.debug("Parse optimization objective...")
    if config is None:
        return None
    objective_type = config.objective_type
    logging.debug(f"Objective type is {objective_type}.")
    objective_name = config.objective_function
    logging.debug(f"Objective name is {objective_name}.")
    objective_file = config.objective_file
    logging.debug(f"Objective file is {objective_file}.")
    if objective_file == "":
        logging.debug("The user has not provided a file for the optimization objective. Try to get the function from "
                      "within Monitizer.")
        if objective_type == "single-objective":
            import monitizer.optimizers.single_objectives
            if objective_name == "OptimalForOODClass":
                logging.debug("The chosen objective is 'OptimalForOODClass'.")
                return monitizer.optimizers.single_objectives.OptimalForOODClass
            elif objective_name == "OptimalForOODClassSubjectToFNR":
                logging.debug("The chosen objective is 'OptimalForOODClassSubjectToFNR'.")
                return monitizer.optimizers.single_objectives.OptimalForOODClassSubjectToFNR
            elif objective_name == "OptimalForAverageGeneratedOOD":
                logging.debug("The chosen objective is 'OptimalForAverageGeneratedOOD'.")
                return monitizer.optimizers.single_objectives.OptimalForAverageGeneratedOOD
            else:
                raise NotImplementedError(f"The class {objective_name} does not exist in single_objectives!")
        elif objective_type == "multi-objective":
            import monitizer.optimizers.multi_objectives
            if objective_name == "OptimalForOODClasses":
                logging.debug("The chosen objective is 'OptimalForOODClasses'.")
                return monitizer.optimizers.multi_objectives.OptimalForOODClasses
            elif objective_name == "OptimalForOODClassesSubjectToFNR":
                logging.debug("The chosen objective is 'OptimalForOODClassesSubjectToFNR'.")
                return monitizer.optimizers.multi_objectives.OptimalForOODClassesSubjectToFNR
            else:
                raise NotImplementedError(f"The class {objective_name} does not exist in multi_objectives!")

    else:
        # the user has specified their own file from where to take the objective
        logging.debug(f"The user has provided a location for the objective in a file at {objective_file}.")
        include_directory = os.path.dirname(objective_file)
        if include_directory == '':
            include_directory = '.'
        sys.path.insert(0, include_directory)
        objective = __import__(os.path.splitext(os.path.basename(objective_file))[0], fromlist=["UserObjective"])
        logging.debug(f"Loaded the objective function from the file.")
        return objective.UserObjective


def parse_optimization_function(config: OptimizationConfig) -> Callable:
    """
    Parses the optimization function from the configuration file.

    :param config: the loaded optimization configuration file
    :type config: OptimizationConfig
    :rtype: Callable
    :return: the optimization function as a function (=Callable)
    """
    optimization_function = config.optimiziation_function
    if optimization_function == "random":
        logging.debug("Optimization is done randomly.")
        from monitizer.optimizers.optimization_functions import optimize_monitor_random
        return optimize_monitor_random
    elif optimization_function == "grid-search":
        logging.debug("Optimization is done with grid search.")
        from monitizer.optimizers.optimization_functions import optimize_monitor_grid_search
        return optimize_monitor_grid_search
    elif optimization_function == "gradient-descent":
        logging.debug("Optimization is done with gradient-descent.")
        from monitizer.optimizers.optimization_functions import optimize_monitor_gradient_descent
        return optimize_monitor_gradient_descent
    else:
        raise NotImplementedError(f"We don't support {optimization_function}.")


def parse_config(optimization_config: str) -> OptimizationConfig:
    """
    Load the configuration file into a configuration object.

    :param optimization_config: the location of the configuration file
    :type optimization_config: str
    :rtype: OptimizationConfig
    :return: the optimization configuration in an object
    """
    return OptimizationConfig(optimization_config)


def parse_evaluation_datasets(evaluation_datasets: list, dataset: Dataset) -> list:
    possible_subsets = dataset.get_all_subset_names()
    possible_subsets_small = [x.lower() for x in possible_subsets]
    evaluation_dataset_new = []
    for i,subset in enumerate(possible_subsets_small):
        for ed in evaluation_datasets:
            if ed.lower() in subset:
                evaluation_dataset_new.append(possible_subsets[i])
    return evaluation_dataset_new


def parse(monitor_template: str, monitor_by_user: str, monitor_by_user_name: str, monitor_config: str,
          neural_network_file: str,
          dataset_name: str, parameter_by_user: str, optimization_objective_specs: str, optimize: bool, seed: int, evaluation_datasets: list=None) -> (
        BaseMonitor, Objective, Callable, list):
    """
    Parses all inputs by the user and creates instances of the objects.

    :param monitor_template: name of the monitor-template
    :type monitor_template: str
    :param monitor_by_user: location of the implementation
    :type monitor_by_user: str
    :param monitor_by_user_name: name of the class containing the monitor
    :type monitor_by_user_name: str
    :param monitor_config: a configuration for the monitor-template (for more complex structures)
    :type monitor_config: str
    :param neural_network_file: location of the neural network
    :type neural_network_file: str
     :param dataset_name: the name of the ID dataset
    :type dataset_name: str
    :param parameter_by_user: the string containing the parameters given by the user
    :type parameter_by_user: str
    :param optimization_objective_specs: the location of the configuration file
    :type optimization_objective_specs: str
    :param optimize: whether to optimize
    :type optimize: bool
    :param seed: The random seed for determinization (necessary for the Box monitor and irrelevant for the others)
    :type seed: int
    :return: the instanciated monitor-template, the optimization objective and the optimization function
    :rtype: (BaseMonitor, Objective, Callable)
    """
    model = parse_neural_network(neural_network_file)
    logging.debug("Neural network is parsed.")
    dataset = parse_dataset(dataset_name)
    logging.debug("Dataset is parsed.")
    if monitor_template is not None:
        monitor = parse_monitor_template(monitor_template, model, dataset, seed)
    elif monitor_by_user is not None:
        monitor = parse_monitor_by_user(monitor_by_user, model, dataset, monitor_by_user_name)
    elif monitor_config is not None:
        monitor = parse_monitor_config(monitor_config, model, dataset, seed)
    else:
        monitor = parse_monitor_template("", model, dataset, seed)
    logging.debug("The monitor is parsed.")
    if parameter_by_user is not None:
        logging.debug(f"The user provided parameters for the monitor: {parameter_by_user}.")
        monitor.set_parameters(parse_parameters(parameter_by_user))
        some = set(monitor.get_all_parameters()) - set(parameter_by_user)
        monitor._set_parameters_for_optimization(some)
    if optimization_objective_specs is not None and optimize:
        config = parse_config(optimization_objective_specs)
        optimization_objective = parse_optimization_objective(config)(config)
        assert (isinstance(optimization_objective, Objective))
        optimization_function = parse_optimization_function(config)
        logging.debug("Information about optimization is parsed.")
    elif optimize:
        config = OptimizationConfig('monitizer/config/default-optimization-objective.ini')
        optimization_objective = parse_optimization_objective(config)(config)
        assert (isinstance(optimization_objective, Objective))
        optimization_function = parse_optimization_function(config)
        logging.debug("Default information about optimization is parsed.")
    else:
        logging.debug("No optimization is performed.")
        config = None
        optimization_objective = None
        optimization_function = None
    if evaluation_datasets is not None:
        evaluation_datasets = parse_evaluation_datasets(evaluation_datasets, dataset)
    return monitor, optimization_objective, optimization_function, config, evaluation_datasets
