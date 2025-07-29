# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import os, argparse
import warnings
import monitizer.monitors.Monitor
from monitizer.monitors import get_all_monitors, get_all_monitor_names, get_all_auroc_monitors
from monitizer.parse import parse
from monitizer.optimize import *
from monitizer.evaluate import *
import torch
from torchvision import datasets
import random
import time
from configparser import ConfigParser
import pathlib

# Make sure that GPU also computes more precisely
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False


def run_monitizer(monitor_templates, monitor_by_user, monitor_by_user_name, monitor_config,
                  neural_network_file, optimization_objective_specs, evaluation_criteria,
                  dataset_name, parameter_by_user,
                  optimize: bool, evaluation: bool = False,
                  output_file: str = "results", output_latex: bool = False,
                  seed: int = 42, get_confidences: bool = False,
                  evaluation_datasets: list = None) -> (
        monitizer.monitors.Monitor.BaseMonitor, pd.DataFrame):
    """
    Middle function to account for processing of several monitor-templates.
    It calls run_monitizer_single on every separate monitor-template and collects the results in one table.

    :param monitor_templates: input by the user for a list of chosen monitor templates
    :type monitor_template: str, optional
    :param monitor_by_user: input a user-defined monitor template
    :type monitor_by_user: str, optional
    :param monitor_by_user_name: name of the class containing the monitor
    :type monitor_by_user_name: str
    :param monitor_config: a configuration for the monitor-template (for more complex structures)
    :type monitor_config: str
    :param neural_network_file: file containing the neural network (onnx or torch.save())
    :type neural_network_file: str
    :param optimization_objective_specs: optimization configuration
    :type optimization_objective_specs: str, optional
    :param evaluation_criteria: additional inputs for evaluation
    :type evaluation_criteria: str, optional
    :param dataset_name: name of the ID-dataset (used to generate OOD data)
    :type dataset_name: str
    :param parameter_by_user: parameters for a monitor
    :type parameter_by_user: str
    :param optimize: whether to optimize
    :type optimize: bool
    :param evaluation: whether to evaluate the monitor, defaults to False
    :type evaluation: bool, optional
    :param output_file: location of the outputs, defaults to "results"
    :type output_file: str, optional
    :param output_latex: whether to output the results in latex-format (useful for paper writing), defaults to False
    :type output_latex: bool, optional
    :param seed: random seed for any use that is not in 'random' or 'numpy.random', defaults to 42
    :type seed: int
    :param get_confidences: boolean parameter to define whether to compute confidence intervals
    :type get_confidences: bool
    :param evaluation_datasets: list of datasets on which to evaluate (must be implemented!)
    :type evaluation_datasets: list

    :return: Returns the (optimized) monitor object
    :rtype: BaseMonitor

    """
    if not monitor_templates is None and 'all' in monitor_templates:
        if (not optimize and evaluation) or (evaluation and 'auroc' in evaluation_criteria):
            monitor_templates_temp = get_all_auroc_monitors()
        else:
            monitor_templates_temp = get_all_monitors()
        for monitor in monitor_templates:
            if not monitor=='all':
                if not monitor in monitor_templates_temp:
                    monitor_templates_temp.append(monitor)
        monitor_templates = monitor_templates_temp
    all_results = None
    if monitor_templates is None:
        monitor, _ = run_monitizer_single(None, monitor_by_user, monitor_by_user_name,
                             monitor_config, neural_network_file, optimization_objective_specs,
                             evaluation_criteria,
                             dataset_name, parameter_by_user,
                             optimize, evaluation,
                             output_file, output_latex, seed, get_confidences, evaluation_datasets)
        return monitor
    else:
        for monitor_template in monitor_templates:
            print(f"\n#### PROCESS '{monitor_template}' ####")
            if len(monitor_templates)>1:
                if os.path.split(output_file)[0] == '':
                    output_file_monitor = monitor_template + '_' + os.path.split(output_file)[-1]
                else:
                    output_file_monitor = os.path.split(output_file)[0] + '/' + monitor_template + '_' + os.path.split(output_file)[-1]
            else:
                output_file_monitor = output_file
            monitor, results = run_monitizer_single(monitor_template, monitor_by_user, monitor_by_user_name,
                                              monitor_config, neural_network_file, optimization_objective_specs,
                                              evaluation_criteria,
                                              dataset_name, parameter_by_user,
                                              optimize, evaluation,
                                              output_file_monitor, output_latex, seed, get_confidences, evaluation_datasets)
            if evaluation and not results is None:
                results.insert(0, 'monitor', [monitor_template] * len(results))
                if all_results is None:
                    all_results = results
                else:
                    all_results = pd.concat([all_results, results], ignore_index=True)
        if evaluation and len(monitor_templates) > 1:
            all_results.to_csv(f"{output_file}-collective.csv", index=False)
            if output_latex:
                all_results.to_latex(f"{output_file}-collective.tex", index=False, float_format="%3.2f")
            print("\n ### Collective Results ###")
            print(all_results.to_markdown())
        if len(monitor_templates)==1:
            return monitor
    return None


def run_monitizer_single(monitor_template, monitor_by_user, monitor_by_user_name, monitor_config,
                         neural_network_file, optimization_objective_specs, evaluation_criteria,
                         dataset_name, parameter_by_user,
                         optimize: bool, evaluation: bool = False,
                         output_file: str = "results", output_latex: bool = False,
                         seed: int = 42, get_confidences: bool = False,
                         evaluation_datasets: list = None) -> (
        monitizer.monitors.Monitor.BaseMonitor, pd.DataFrame):
    """
    Contains the core functionality of Monitizer.
    It processes a given monitor template (either monitor-template or monitor-by user) by optimizing/evaluating it.

    :param monitor_template: input by the user for a chosen monitor template
    :type monitor_template: str, optional
    :param monitor_by_user: input a user-defined monitor template
    :type monitor_by_user: str, optional
    :param monitor_by_user_name: name of the class containing the monitor
    :type monitor_by_user_name: str
    :param monitor_config: a configuration for the monitor-template (for more complex structures)
    :type monitor_config: str
    :param neural_network_file: file containing the neural network (onnx or torch.save())
    :type neural_network_file: str
    :param optimization_objective_specs: optimization configuration
    :type optimization_objective_specs: str, optional
    :param evaluation_criteria: additional inputs for evaluation
    :type evaluation_criteria: str, optional
    :param dataset_name: name of the ID-dataset (used to generate OOD data)
    :type dataset_name: str
    :param parameter_by_user: parameters for a monitor
    :type parameter_by_user: str
    :param optimize: whether to optimize
    :type optimize: bool
    :param evaluation: whether to evaluate the monitor, defaults to False
    :type evaluation: bool, optional
    :param output_file: location of the outputs, defaults to "results"
    :type output_file: str, optional
    :param output_latex: whether to output the results in latex-format (useful for paper writing), defaults to False
    :type output_latex: bool, optional
    :param seed: random seed for any use that is not in 'random' or 'numpy.random', defaults to 42
    :type seed: int
    :param get_confidences: boolean parameter to define whether to compute confidence intervals
    :type get_confidences: bool
    :param evaluation_datasets: list of datasets on which to evaluate (must be implemented!)
    :type evaluation_datasets: list

    :return: Returns the (optimized) monitor object
    :rtype: BaseMonitor

    """
    # Parsing
    timer_start1 = time.time()
    cpu_timer_start1 = time.process_time()
    print("### Parse the input ###")
    logging.info("# Parsing")
    monitor, optimization_objective, optimization_function, config, evaluation_datasets = parse(monitor_template,
                                                                                                monitor_by_user,
                                                                                                monitor_by_user_name,
                                                                                                monitor_config,
                                                                                                neural_network_file,
                                                                                                dataset_name,
                                                                                                parameter_by_user,
                                                                                                optimization_objective_specs,
                                                                                                optimize, seed,
                                                                                                evaluation_datasets)
    timer_end1 = time.time()
    cpu_timer_end1 = time.process_time()
    print(f"Time for parsing: {timer_end1 - timer_start1}s User / {cpu_timer_end1 - cpu_timer_start1}s CPU")
    logging.info(f"Time for parsing: {timer_end1 - timer_start1}s User / {cpu_timer_end1 - cpu_timer_start1}s CPU")

    # Optimization
    optimized_monitor = None
    data = None
    logging.info("# Optimization")
    if optimize and len(monitor.get_parameters()) > 0:
        # Standard optimization (if there is at least one parameter to be optimized), otherwise skip
        logging.info("Optimization started")
        timer_start2 = time.time()
        cpu_timer_start2 = time.process_time()
        print("\n### Optimize the monitor ###")
        optimized_monitor, data = optimize_general(monitor, optimization_objective, config,
                                                   optimization_function)
        if optimized_monitor is None:
            # In the multi-objective case there is no single "optimal monitor"
            logging.debug("The optimization was multi-objective.")
            data.to_csv(output_file + '.csv', index=False)
            print(f" The optimal parameters for each weight combination is stored in {output_file}.csv.")
            logging.info(f"The optimal parameters for each weight combination is stored in {output_file}.csv.")
        else:
            logging.debug("The optimization was single-objective.")
            print(f" The optimal parameters are {optimized_monitor.get_parameters()}.")
            logging.info(f"The optimal parameters are {optimized_monitor.get_parameters()}.")
        timer_end2 = time.time()
        cpu_timer_end2 = time.process_time()
        print(f"Time for optimization: {timer_end2 - timer_start2}s User / {cpu_timer_end2 - cpu_timer_start2}s CPU")
        logging.info(
            f"Time for optimization: {timer_end2 - timer_start2}s User / {cpu_timer_end2 - cpu_timer_start2}s CPU")

    # Evaluating
    logging.info("# Evaluation")
    result_evaluation = None
    if evaluation:
        logging.info("Evaluation started")
        timer_start3 = time.time()
        cpu_timer_start3 = time.process_time()
        print("\n### Evaluate the monitor ###")
        if optimized_monitor is None and (parameter_by_user or monitor_config):
            # If the monitor was not optimized, but there are parameters given (either parameters_by_user or in the config)
            logging.debug("The user has defined parameter for the monitor.")
            monitor.fit()
            logging.debug("The monitor is set up with the given parameters. Evaluating it...")
            result_evaluation = evaluate(monitor, evaluation_criteria, monitor.data, output_file, output_latex,
                                         get_confidences, evaluation_datasets)
        elif optimized_monitor is None and evaluation_criteria == 'auroc':
            # If the monitor was not optimized, we can still compute the AUROC on default parameters
            # This is necessary since it is what is mostly done in the literature
            logging.debug("We are just computing the AUROC (no threshold parameter necessary).")
            monitor.fit()
            logging.debug("Evaluating the monitor...")
            result_evaluation = evaluate(monitor, evaluation_criteria, monitor.data, output_file, output_latex,
                                         get_confidences, evaluation_datasets)
        elif optimize and optimized_monitor:
            # Evaluation of an optimized monitor
            logging.debug("The monitor was optimized. Evaluating it...")
            result_evaluation = evaluate(optimized_monitor, evaluation_criteria, optimized_monitor.data, output_file,
                                         output_latex, get_confidences, evaluation_datasets)
        elif data is not None:
            # If the optimization was multi-objective, we only show the results
            logging.debug("The optimization was multi-objective. Start visualization.")
            show_results_multi_objective(data, output_file)
            print(
                "The evaluation for multi-objective is currently not possible. Please evaluate a selected optimized monitor.")
            logging.info(
                "The evaluation for multi-objective is currently not possible. Please evaluate a selected optimized monitor.")
        else:
            # Default is to evaluate on AUROC since it works with only default parameters
            if not 'auroc' in evaluation_criteria:
                warnings.warn("The monitor was not optimized or defined by the user. Compute the AUROC instead.")
            monitor.fit()
            logging.debug("Evaluating the monitor...")
            result_evaluation = evaluate(monitor, evaluation_criteria + ['auroc'], monitor.data, output_file,
                                         output_latex, get_confidences, evaluation_datasets)
            # raise ValueError("The monitor must be optimized or defined by the user before evaluation.")
        timer_end3 = time.time()
        cpu_timer_end3 = time.process_time()
        print(f"Time for evaluation: {timer_end3 - timer_start3}s User / {cpu_timer_end3 - cpu_timer_start3}s CPU")
        logging.info(
            f"Time for evaluation: {timer_end3 - timer_start3}s User / {cpu_timer_end3 - cpu_timer_start3}s CPU")

    timer_end4 = time.time()
    cpu_timer_end4 = time.process_time()

    print(f"Time total: {timer_end4 - timer_start1}s User / {cpu_timer_end4 - cpu_timer_start1}s CPU")
    logging.info(f"Time total: {timer_end4 - timer_start1}s User / {cpu_timer_end4 - cpu_timer_start1}s CPU")
    return optimized_monitor if optimized_monitor is not None else monitor, result_evaluation


def check_arguments(args: argparse.Namespace, dataset_arg, nn_arg, monitor_arg,
                    optimization_objective_arg) -> argparse.Namespace:
    """
    Check the arguments from the user on consistency

    :param args: the input namespace
    :type args: argparse.Namespace
    :param dataset_arg: the argument defining the dataset
    :type dataset_arg: argparse.Argument
    :param nn_arg: the argument defining the neural network file
    :type nn_arg: argparse.Argument
    :param monitor_arg: the argument of a monitor-template
    :type monitor_arg: argparse.Argument
    :param optimization_objective_arg: the argument for the optimization configuration
    :type optimization_objective_arg: argparse.Argument
    :rtype: argparse.Namespace
    :return: the corrected Namespace

    """
    if not args.setup:
        if args.dataset is None:
            raise argparse.ArgumentError(dataset_arg,
                                         f"the following arguments are required: -d/--dataset, -nn/--neural-network")
        if args.neural_network is None:
            raise argparse.ArgumentError(nn_arg,
                                         f"the following arguments are required: -d/--dataset, -nn/--neural-network")
        if args.monitor_template is None and args.monitor_by_user is None and args.monitor_config is None:
            raise argparse.ArgumentError(monitor_arg,
                                         "A monitor must be selected! Either use the pre-impemented monitors "
                                         "or provide your implementation!")
        if args.optimize and args.optimization_objective is None:
            raise argparse.ArgumentError(optimization_objective_arg,
                                         "You must specify the objective function using --optimization-objective "
                                         "when you want to optimize!")
    # todo check the optimization objective for reasonable inputs
    return args


def setup_monitizer(dataset_names: list, data_folder: str):
    """
    Setup function

    It downloads necessary data into the specified folder and stores this information.

    :param dataset_names: Names of the ID-datasets, for which Monitizer is set up.
    :type dataset_names: list[str]
    :param data_folder: Location where the data is to be downloaded at.
    :type data_folder: str
    :rtype: None

    """
    data_path = pathlib.Path(data_folder).expanduser().resolve()
    print("The data is stored at ", data_path)
    internal_config = ConfigParser()
    internal_config.read('monitizer/config/config.ini')
    internal_config['DEFAULT']['data_folder'] = data_folder
    with open('monitizer/config/config.ini', 'w') as configfile:
        internal_config.write(configfile)
    if not os.path.isdir(data_folder):
        os.mkdir(data_folder)
    if len(dataset_names)>0 and dataset_names[0].lower() == "all":
        dataset_names = ["mnist", "cifar10", "cifar100", "gtsrb", "svhn", "dtd", "fashionmnist", "kmnist", "imagenet"]
    for dataset in dataset_names:
        root = data_folder
        if dataset.lower() == 'mnist':
            datasets.CIFAR10(root=root, download=True)
            datasets.MNIST(root=root, download=True)
            datasets.FashionMNIST(root=root, download=True)
            datasets.KMNIST(root=root, download=True)
            datasets.SVHN(root=root, download=True, split="extra")
            datasets.SVHN(root=root, download=True, split="test")
            datasets.SVHN(root=root, download=True, split="train")
            datasets.DTD(root=root, download=True)
        elif dataset.lower() == 'cifar10':
            datasets.CIFAR10(root=root, download=True)
            datasets.CIFAR100(root=root, download=True)
            datasets.DTD(root=root, download=True)
            datasets.GTSRB(root=root, download=True, split='train')
            datasets.GTSRB(root=root, download=True, split='test')
        elif dataset.lower() == "imagenet":
            if not os.path.isfile(data_folder + "/ILSVRC2012_devkit_t12.tar.gz"):
                raise RuntimeError(
                    f"The archive ILSVRC2012_devkit_t12.tar.gz is not present in '{root}' or is corrupted. Due to "
                    f"licensing, you need to download it externally by visiting "
                    f"'https://www.image-net.org/challenges/LSVRC/2012/2012-downloads.php' and place it in '{root}'.")
            elif not os.path.isfile(data_folder + "/ILSVRC2012_img_val.tar"):
                raise RuntimeError(
                    f"The archive ILSVRC2012_img_val.tar is not present in '{root}' or is corrupted. Due to "
                    f"licensing, you need to download it externally by visiting "
                    f"'https://www.image-net.org/challenges/LSVRC/2012/2012-downloads.php' and place it in '{root}'.")
            elif not os.path.isfile(data_folder + "/ILSVRC2012_img_val.tar"):
                raise RuntimeError(
                    f"The archive ILSVRC2012_devkit_t12.tar.gz is not present in '{root}' or is corrupted. Due to "
                    f"licensing, you need to download it externally by visiting "
                    f"'https://www.image-net.org/challenges/LSVRC/2012/2012-downloads.php' and place it in '{root}'.")
            datasets.ImageNet(root=root, split='train')
            datasets.ImageNet(root=root, split='val')
        elif dataset.lower() == 'cifar100':
            datasets.CIFAR10(root=root, download=True)
            datasets.CIFAR100(root=root, download=True)
            datasets.DTD(root=root, download=True)
            datasets.GTSRB(root=root, download=True, split='train')
            datasets.GTSRB(root=root, download=True, split='test')
        elif dataset.lower() == 'gtsrb':
            datasets.CIFAR10(root=root, download=True)
            datasets.SVHN(root=root, download=True, split="extra")
            datasets.SVHN(root=root, download=True, split="test")
            datasets.SVHN(root=root, download=True, split="train")
            datasets.DTD(root=root, download=True)
            datasets.GTSRB(root=root, download=True, split='train')
            datasets.GTSRB(root=root, download=True, split='test')
        elif dataset.lower() == 'svhn':
            datasets.SVHN(root=root, download=True, split="extra")
            datasets.SVHN(root=root, download=True, split="test")
            datasets.SVHN(root=root, download=True, split="train")
        elif dataset.lower() == 'dtd':
            datasets.DTD(root=root, download=True)
        elif dataset.lower() == "fashionmnist":
            datasets.FashionMNIST(root=root, download=True)
        elif dataset.lower() == "kmnist":
            datasets.KMNIST(root=root, download=True)


def main():
    """
    Main function to start the tool

    It parses the given arguments and performs sanity checks
    """
    parser = argparse.ArgumentParser(description='Processing inputs.')

    # SETUP
    parser.add_argument('--setup', nargs='+', help='Define the datasets for which to setup monitizer.')
    parser.add_argument('--data-folder', help="Define the location where to store the datasets.", type=str,
                        required=False, default='./data')

    # RUN MONITIZER
    ## Define the dataset
    dataset_arg = parser.add_argument('-d', '--dataset', type=str, required=False, help='Dataset')

    ## The monitor to be optimized can either be one/several of the implemented monitors (--monitor_template)
    ## or a python-file with an implementation (--monitor_by_user)
    monitor_arg = parser.add_argument('-m', '--monitor-template', type=str, required=False,
                                      help='Monitor templates to be processed. Append ',
                                      choices=get_all_monitor_names() + ['all', ""], nargs='+')
    parser.add_argument('-mu', '--monitor-by-user', type=str, required=False, help='Monitor implementation by user')
    parser.add_argument('-mu-name', '--monitor-by-user-name', type=str, required=False, help="Name of the class "
                                                                                             "containing the monitor.",
                        default="Monitor")
    ## EXPERIMENTAL! You can also input a config file that contains ALL information
    parser.add_argument('-mc', '--monitor-config', type=str, required=False,
                        help='(EXPERIMENTAL!) Monitor configuration')

    ## The neural network as input (torch.save or onnx)
    nn_arg = parser.add_argument('-nn', '--neural-network', type=str, required=False,
                                 help="Neural network")

    ## Choose whether to do optimization
    parser.add_argument('-op', '--optimize', required=False, help="Whether or not to optimize",
                        action='store_true')
    ## Choose an optimization-objective
    optimization_objective_arg = parser.add_argument('-oo', '--optimization-objective', type=str, required=False,
                                                     help='Optimization objective')

    ## or choose parameters for the monitor
    parser.add_argument('-p', '--parameters', type=str, required=False,
                        help='Describes the parameters for the monitor.')

    ## Choose whether to do evaluation
    parser.add_argument('-e', '--evaluate', required=False, help="Whether or not to evaluate",
                        action='store_true')
    ## Choose evaluation criteria
    parser.add_argument('-ec', '--evaluation-criteria', type=str, required=False, help='Evaluation criteria',
                        choices=["short", "test", "full", "auroc"], nargs='+', default=[])
    parser.add_argument('-ed', '--evaluation-datasets', type=str, required=False,
                        help='On which OOD-datasets to evaluate.', nargs='+')
    parser.add_argument('-c', '--confidence-intervals', required=False,
                        help="Whether to compute confidence intervals for accuracy/AUROC", action='store_true')

    ## define where to store the results
    parser.add_argument('-o', '--output', type=str, required=False, help="Where to store the output.",
                        default="results")
    ## Define whether to output also a latex-table
    parser.add_argument('-l', '--output-latex', required=False,
                        help="Whether to output the results also to latex.", action='store_true')

    ## Define a seed for reproducability
    parser.add_argument('-s', '--seed', type=int, required=False, help="Set a seed to have reproducible results.",
                        default=42)

    ## Define where to store the log
    parser.add_argument('--log', type=str, required=False, help="Where to store the log.", nargs='?',
                        const='arg_was_not_given')

    args = parser.parse_args()

    if not args.log is None:
        if args.log == 'arg_was_not_given':
            log_file = f"log_{int(round(time.time(), 2))}.log"
        else:
            log_file = args.log
        logging.basicConfig(filename=log_file, level=logging.DEBUG,
                            format='%(levelname)s:%(message)s', filemode='w')
    else:
        logging.basicConfig(level=logging.WARNING)

    args = check_arguments(args, dataset_arg, nn_arg, monitor_arg, optimization_objective_arg)
    logging.info("# Setup")
    logging.info(f"Monitizer is run with {args}")

    random.seed(args.seed)
    np.random.seed(args.seed)

    if args.setup:
        print(f"Monitizer is setup for {args.setup}")
        logging.info(f"Setting up Monitizer for the datasets: {args.setup}.")
        setup_monitizer(args.setup, args.data_folder)
        print("\n\n### Setup done ###")
        return
    else:
        internal_config = ConfigParser()
        internal_config.read('monitizer/config/config.ini')
        if not internal_config.has_option('DEFAULT', 'data_folder') or not os.path.isdir(
                internal_config['DEFAULT']['data_folder']):
            raise FileNotFoundError(
                "Please setup monitizer first and download the data. You can run monitizer --setup "
                "DATASET1 DATASET2 to download the datasets.")

    print("### Monitizer is run with ###\n", args, "\n")

    run_monitizer(args.monitor_template, args.monitor_by_user, args.monitor_by_user_name,
                  args.monitor_config, args.neural_network, args.optimization_objective,
                  args.evaluation_criteria,
                  args.dataset, args.parameters,
                  args.optimize, args.evaluate,
                  args.output, args.output_latex, args.seed, args.confidence_intervals, args.evaluation_datasets)

if __name__ == "__main__":
    main()
