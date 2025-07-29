# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import math, logging
from monitizer.benchmark.dataset import Dataset
from monitizer.monitors.Monitor import BaseMonitor
import pandas as pd
import plotly.express as px
import matplotlib
import matplotlib.pyplot as plt
import numpy as np


#: Literal['test', 'full', 'short', 'auroc']
def evaluate(optimized_monitor: BaseMonitor, evaluation_criteria: list, dataset: Dataset,
             output_file: str, output_latex=False, get_confidences: bool = False, evaluation_datasets: list = None) -> pd.DataFrame:
    """
    Evaluates a given monitor.

    :param optimized_monitor: an (optimized) monitor (can also be initialized with parameters as input)
    :type optimized_monitor: BaseMonitor
    :param evaluation_criteria: possible criteria for evaluation, currently "full" or "short"/"test", and "auroc".
     "full" evaluates on all OOD classes, "short"/"test" only on the first 3 (whatever they may be)
     "auroc" evalutes the AUROC instead of the prediction rate on OOD classes
    :type evaluation_criteria: str
    :param dataset: the ID-dataset, necessary to get all possible OOD-sets
    :type dataset: Dataset
    :param output_file: location where the output should be stored
    :type output_file: str
    :param output_latex: whether to additionally output latex-tables, defaults to False
    :type output_latex: bool
    :param get_confidences: whether to compute confidence intervals for accuracy/AUROC
    :type get_confidences: bool
    :param evaluation_datasets: list of datasets on which to evaluate (must be implemented!)
    :type evaluation_datasets: list

    :rtype: None
    :return: evaluates a monitor on all ("full") or 3 ("test"/"short") OOD classes and stores the results in a file
    """
    if "full" in evaluation_criteria:
        logging.debug("Performing full evaluation")
        results = evaluate_on(optimized_monitor, dataset, dataset.get_all_subset_names(), output_latex, output_file,
                              get_confidences)
    elif "auroc" in evaluation_criteria:
        logging.debug("Compute only the auroc")
        if "short" in evaluation_criteria:
            logging.debug(
                f"Performing evaluation only on a subset, i.e., {dataset.get_all_subset_names()[:min(len(dataset.get_all_subset_names()), 3)]}")
            results = evaluate_auroc(optimized_monitor, dataset,
                                     dataset.get_all_subset_names()[:min(len(dataset.get_all_subset_names()), 3)],
                                     output_latex, output_file, get_confidences)
        else:
            results = evaluate_auroc(optimized_monitor, dataset, evaluation_datasets, output_latex,
                                     output_file, get_confidences)
    elif "short" in evaluation_criteria or "test" in evaluation_criteria:
        logging.debug(
            f"Performing evaluation only on a subset, i.e., {dataset.get_all_subset_names()[:min(len(dataset.get_all_subset_names()), 3)]}")
        results = evaluate_on(optimized_monitor, dataset,
                              dataset.get_all_subset_names()[:min(len(dataset.get_all_subset_names()), 3)],
                              output_latex,
                              output_file, get_confidences)
    else:
        if evaluation_datasets is None:
            results = evaluate_on(optimized_monitor, dataset, dataset.get_all_subset_names(), output_latex, output_file,
                                  get_confidences)
        else:
            results = evaluate_on(optimized_monitor, dataset, evaluation_datasets, output_latex, output_file,
                              get_confidences)
    return results


def show_results_multi_objective(data: pd.DataFrame, output_file: str = 'multi-objective-pareto-frontier'):
    """
    Plots the pareto front for multi-objective optimization.

    :param data: the performance of the monitor for different weightings of the objectives
    :type data: pd.DataFrame, columns are "weight-X1, weight-X2, ..., result-X1, result-X2, ..."
    :param output_file: location wehere to store the resulting figure
    :type output_file: str
    :rtype: None
    """
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['font.family'] = 'STIXGeneral'
    output_file += '.png'
    objectives = [i for i in data.columns if i.startswith('weight')]
    num_objectives = len(objectives)
    fig = plt.figure(figsize=(5, 3))
    ax = plt.subplot(111)
    if num_objectives == 2:
        lines = [i for i in data.columns if i.startswith('result')]
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']
        # draw the pareto frontier
        # the weights give the direction, the resulting value is the length of the line
        for i, r in data.iterrows():
            w1 = r[objectives[0]]
            w2 = r[objectives[1]]
            if not w1 == 0 and not w2 == 0:
                m = r[objectives[0]] / r[objectives[1]]
                x = [i for i in range(100) if m / 100 * i < 1]
                y = [m * i for i in x if m * i < 100]
                ax.plot(x, y, color='gray', linestyle='dashed', alpha=0.2)
                t = ax.text(y[-1] / m, y[-1], f"({w1:4.2f},{w2:4.2f})")
                t.set_alpha(0.2)
        for j, line in enumerate(lines):
            xs = []
            ys = []
            for i, r in data.iterrows():
                value = r[line] * 100
                if r[objectives[1]] == 0:
                    xs.append(0)
                    ys.append(value)
                    ax.text(0, value, str(round(value, 2)), color=colors[j])
                else:
                    m = r[objectives[0]] / r[objectives[1]]
                    xs.append(value * math.cos(math.atan(m)))
                    ys.append(value * math.sin(math.atan(m)))
                    ax.text(xs[-1], ys[-1], str(round(value, 2)), color=colors[j])
            if 'id' in line:
                lab = "ID"
            else:
                lab = line
            ax.plot(xs, ys, label=lab.replace('result-', ''), alpha=0.7, color=colors[j])
        # plt.title("Pareto-frontier", fontsize=25)
        plt.xlabel(objectives[1].replace("weight-", ""))
        plt.ylabel(objectives[0].replace("weight-", ""))
        plt.legend(loc='upper right')
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        ax.spines[['right', 'top']].set_visible(False)
        # ax.set_axisbelow(True)
        # ax.yaxis.grid(color='gray', linestyle='dashed')
        # ax.xaxis.grid(color='gray', linestyle='dashed')
        plt.savefig(output_file, bbox_inches="tight", pad_inches=0.2)


def evaluate_auroc(optimized_monitor: BaseMonitor, dataset: Dataset, subsets: list = None, latex=False, output_file="",
                   get_confidences=True) -> pd.DataFrame:
    """
    Evaluate the monitor on all datasets specified (subsets) and compute the AUROC

    :param optimized_monitor: an (optimized) monitor (can also be initialized with parameters as input)
    :type optimized_monitor: BaseMonitor
    :param dataset: the ID-dataset, necessary to get all possible OOD-sets
    :type dataset: Dataset
    :param subsets: names of the OOD classes that shall be evaluated
    :type subsets: list(str)
    :param latex: whether to output the results as latex-tables, defaults to False
    :type latex: bool
    :param output_file: location where to store the tables and figures
    :type output_file: str
    :param get_confidences: whether to compute confidence intervals for accuracy/AUROC
    :type get_confidences: bool
    :rtype: pd.DataFrame
    :return: the resulting table (dataset + AUROC)
    """
    logging.debug(f"Getting all AUROCS for the OOD sets")
    aurocs = optimized_monitor.get_auroc_scores_all_test(subsets, get_confidences=get_confidences)
    if get_confidences:
        results = pd.DataFrame(columns=['data', 'AUROC', 'confidence-min', 'confidence-max'])
    else:
        results = pd.DataFrame(columns=['data', 'AUROC'])
    if subsets is None:
        results['data'] = dataset.get_all_subset_names()
    else:
        results['data'] = subsets
    if get_confidences:
        results['AUROC'] = aurocs[0]
        results['confidence-min'] = aurocs[1]
        results['confidence-max'] = aurocs[2]
    else:
        results['AUROC'] = aurocs
    results.to_csv(f"{output_file}-auroc.csv", index=False)
    logging.debug(f"Stored the AUROC-results at {output_file}-auroc.csv")
    if latex:
        results.to_latex(f"{output_file}-auroc.tex", index=False, float_format="%3.2f")
        logging.debug(f"Stored the AUROC-results at {output_file}-auroc.tex")
    print(results.to_markdown())
    return results


def evaluate_on(optimized_monitor: BaseMonitor, dataset: Dataset, subsets: list, latex=False, output_file="",
                get_confidences=True) -> pd.DataFrame:
    """
    Evaluate the monitor on all datasets specified (subsets).

    :param optimized_monitor: an (optimized) monitor (can also be initialized with parameters as input)
    :type optimized_monitor: BaseMonitor
    :param dataset: the ID-dataset, necessary to get all possible OOD-sets
    :type dataset: Dataset
    :param subsets: names of the OOD classes that shall be evaluated
    :type subsets: list(str)
    :param latex: whether to output the results as latex-tables, defaults to False
    :type latex: bool
    :param output_file: location where to store the tables and figures
    :type output_file: str
    :param get_confidences: whether to compute confidence intervals for accuracy/AUROC
    :type get_confidences: bool
    :return: the table with the results (TPR, TNR, FNR, FPR, confidences for each dataset)
    :rtype: pd.DataFrame
    """

    # Evaluate on ID data
    current_set = dataset.get_ID_test()
    id_prediction = optimized_monitor.evaluate(current_set)
    result = sum(id_prediction) / len(current_set.dataset)
    confidence_width = 1.96 * np.sqrt((result * (1 - result)) / len(current_set.dataset))
    confidences = (result + confidence_width, result - confidence_width)
    logging.debug(
        f"On ID the number of detected ID-inputs is {sum(id_prediction)} of {len(current_set.dataset)} total.")
    logging.debug(f"That results in a FPR of {result}.")
    if get_confidences:
        id_results = pd.DataFrame(columns=["data", "FPR", "FPR-confidence-min", "FPR-confidence-max"])
        id_results.loc[0] = ["ID", result * 100, confidences[0] * 100, confidences[1] * 100]
        id_results["FPR"] = id_results["FPR"].astype(float).round(6)
        id_results["FPR-confidence-min"] = id_results["FPR-confidence-min"].astype(float).round(6)
        id_results["FPR-confidence-max"] = id_results["FPR-confidence-max"].astype(float).round(6)
    else:
        id_results = pd.DataFrame(columns=["data", "TNR", "FPR"])
        id_results.loc[0] = ["ID", (1 - result) * 100, result * 100]
        id_results["TNR"] = id_results["TNR"].astype(float).round(6)
        id_results["FPR"] = id_results["FPR"].astype(float).round(6)
    id_results.to_csv(f"{output_file}-id.csv", index=False)
    logging.debug(f"Stored the ID-results at {output_file}-id.csv")
    if latex:
        logging.debug(f"Stored the ID-results at {output_file}-id.tex")
        id_results.to_latex(f"{output_file}-id.tex", index=False, float_format="%3.2f")

    stored = []
    if get_confidences:
        ood_results = pd.DataFrame(
            columns=["data", "FNR", "FNR-confidence-min", "FNR-confidence-max", "TPR", "TPR-confidence-min",
                     "TPR-confidence-max", "Precision", "Recall"])
    else:
        ood_results = pd.DataFrame(columns=["data", "FNR", "TPR", "Precision", "Recall"])
    stored.append(f"{'ID accuracy:':<50} {(1 - result) * 100:5.2f}%")

    # Evaluate on OOD data
    for subset in subsets:
        logging.debug(f"Evaluating {subset}...")
        current_set = dataset.get_OOD_test(subset)
        ood_prediction = optimized_monitor.evaluate(current_set)
        result = sum(ood_prediction) / len(current_set.dataset)
        confidence_width = 1.96 * np.sqrt((result * (1 - result)) / len(current_set.dataset))
        confidences = (result + confidence_width, result - confidence_width)
        fnr_result = 1 - result
        confidence_width_fnr = 1.96 * np.sqrt((fnr_result * (1 - fnr_result)) / len(current_set.dataset))
        confidences_fnr = (fnr_result + confidence_width_fnr, fnr_result - confidence_width_fnr)
        logging.debug(
            f"On OOD of type {subset}, the number of detected OOD-inputs is {sum(ood_prediction)} "
            f"of {len(current_set.dataset)} total.")
        logging.debug(f"That results in a TPR of {result}.")
        safe_val = (sum(ood_prediction) + sum(id_prediction)) if (sum(ood_prediction) + sum(id_prediction)) > 0 else 1
        if get_confidences:
            ood_results.loc[len(ood_results)] = [subset, (1 - result) * 100, confidences_fnr[0] * 100,
                                                 confidences_fnr[1] * 100, result * 100, confidences[0] * 100,
                                                 confidences[1] * 100, sum(ood_prediction) / safe_val * 100,
                                                 result * 100]
            ood_results["FNR-confidence-min"] = ood_results["FNR-confidence-min"].astype(float).round(6)
            ood_results["FNR-confidence-max"] = ood_results["FNR-confidence-max"].astype(float).round(6)
            ood_results["TPR-confidence-min"] = ood_results["TPR-confidence-min"].astype(float).round(6)
            ood_results["TPR-confidence-max"] = ood_results["TPR-confidence-max"].astype(float).round(6)
        else:
            ood_results.loc[len(ood_results)] = [subset, (1 - result) * 100, result * 100,
                                                 sum(ood_prediction) / safe_val * 100, result * 100]
        stored.append(f"{f'OOD {subset} accuracy:':<50} {result * 100:5.2f}%")
    ood_results["FNR"] = ood_results["FNR"].astype(float).round(6)
    ood_results["TPR"] = ood_results["TPR"].astype(float).round(6)
    ood_results.to_csv(f"{output_file}-ood.csv", index=False)
    logging.debug(f"Stored the OOD-results at {output_file}-ood.csv")

    combined = pd.merge(id_results, ood_results, "outer")
    combined = combined.fillna('-')
    combined.to_csv(f"{output_file}.csv", index=False)
    logging.debug(f"Stored the combined results at {output_file}.csv")
    if latex:
        ood_results.to_latex(f"{output_file}-ood.tex", index=False, float_format="%3.2f")
        logging.debug(f"Stored the OOD-results at {output_file}-ood.tex")
        combined.to_latex(f"{output_file}.tex", index=False, float_format="%3.2f")
        logging.debug(f"Stored the combined results at {output_file}.tex")

    com = pd.DataFrame(ood_results[["data", "TPR"]])
    com.loc[len(com)] = ["ID", 100 - id_results["FPR"][0]]
    com = com.rename(columns={"TPR": "accuracy"})

    logging.debug("Create spider plot...")
    create_spider_plot(com, output_file)
    logging.debug("Create parallel coordinates plot...")
    #logging.getLogger().setLevel(logging.INFO)
    create_line_plot(com, output_file)
    #logging.getLogger().setLevel(logging.DEBUG)
    print(combined.to_markdown())
    return combined


def create_spider_plot(data: pd.DataFrame, output_file: str):
    """
    Given a dataset with the relevant information (i.e. 'accuracy' of the monitor on OOD-classes and ID-data), generate
     a spider plot.

    :param data: the outcome of the monitor on the OOD-classes and ID-input
    :type data: pd.DataFrame, column 'data' contains the names of the datasets, 'accuracy' the accuracy of the monitor
    :param output_file: location where to store the figure
    :type output_file: str
    :rtype: None
    """
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['font.family'] = 'STIXGeneral'
    fig = px.line_polar(data, r='accuracy', theta="data", line_close=True, range_r=(0, 100))
    fig.update_traces(fill="toself")
    fig.write_image(f"{output_file}-spider-plot.png")


def create_line_plot(df: pd.DataFrame, output_file: str):
    """
    Given a dataset with the relevant information (i.e. 'accuracy' of the monitor on OOD-classes and ID-data), generate
     a spider plot.

    :param df: the outcome of the monitor on the OOD-classes and ID-input
    :type df: pd.DataFrame, column 'data' contains the names of the datasets, 'accuracy' the accuracy of the monitor
    :param output_file: location where to store the figure
    :type output_file: str
    :rtype: None
    """
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['font.family'] = 'STIXGeneral'
    N = len(df)
    data = df['data'].tolist()
    values = df['accuracy'].tolist()

    fig, axs = plt.subplots(1, N - 1)
    for i in range(N - 1):
        axs[i].set_xlim(i, i + 1)
        axs[i].set_ylim(0, 105)
        if i < N - 2:
            axs[i].set_xticks([i])
            axs[i].set_xticklabels([data[i]], rotation=45, ha='right')
        else:
            axs[i].set_xticks([i, i + 1])
            axs[i].set_xticklabels([data[i], data[i + 1]], rotation=45, ha='right')
        if 0 < i < N - 2:
            axs[i].set_yticks([])
        if i == N - 2:
            axs[i].yaxis.tick_right()
            axs[i].yaxis.set_label_position("right")

        axs[i].plot([i, i + 1], [values[i], values[i + 1]],
                    color=(0.98, 0.52, 0, 1))
        axs[i].fill_between([i, i + 1], [values[i], values[i + 1]], color=(0.98, 0.52, 0, 1), alpha=0.2)
    plt.subplots_adjust(wspace=0)

    plt.savefig(f"{output_file}-parallel-line-plot.png", bbox_inches='tight')
