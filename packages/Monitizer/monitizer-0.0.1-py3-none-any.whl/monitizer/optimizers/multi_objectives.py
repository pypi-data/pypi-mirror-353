# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

from monitizer.monitors.Monitor import BaseMonitor
from monitizer.optimizers.optimization_config import OptimizationConfig
from monitizer.optimizers.objective import Objective
from abc import abstractmethod
import logging


class MultiObjective(Objective):
    """
    This class describes the multi-objective as an extension of the normal objective.
    It contains additionally the possibility to store weights for each objective and to get the number of objectives.
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize the objective. Same as for the general case.
        """
        super().__init__(config)
        self.weights = None

    def set_weights(self, weights: tuple):
        """
        Set the weights for each objective.

        :param weights: the weights for each objective
        :type weights: tuple
        :rtype: None
        """
        assert len(weights) == self.get_num_objectives()
        self.weights = weights

    @abstractmethod
    def get_num_objectives(self) -> int:
        """
        Return the number of objectives.
        """
        pass

    @abstractmethod
    def evaluate(self, monitor):
        """
        Evaluate the monitor on the objectives and weight them according to the weights.
        """
        pass

    @abstractmethod
    def get_columns(self) -> list:
        """
        Get the column names for this objective, i.e., "weight-1, weight-2, ..., result-1, result-2", such that
         the results can be stored in a table.
        """
        pass

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


class OptimalForOODClasses(MultiObjective):
    """
    This class evaluates a monitor on several specified OOD-classes.
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize the objective and store the configuration.
        Specify the relevant OOD-classes on which the monitor should be evaluated.
        The monitor is evaluated on the validation set.
        """
        super().__init__(config)
        self.ood_classes = [x.strip() for x in config.additional_objective_info['ood_classes'].split(',')]
        logging.debug(f"The objective evaluates on the ood-classes {self.ood_classes}.")

    def get_columns(self) -> list:
        """
        Get the column names for this objective, i.e., "weight-1, weight-2, ..., result-1, result-2", such that
         the results can be stored in a table.

        :rtype: list
        :return: the columns for a pandas.DataFrame
        """
        columns = [f"weight-{ood_class}" for ood_class in self.ood_classes]
        columns += [f"result-{ood_class}" for ood_class in self.ood_classes]
        return columns

    def get_num_objectives(self) -> int:
        """
        Return the number of objectives.

        :rtype: int
        :return: the number of objectives, in this case the number of OOD-classes
        """
        return len(self.ood_classes)

    def evaluate(self, monitor: BaseMonitor) -> (list, list):
        """
        Evaluates the monitor on all OOD-classes.

        :param monitor: the monitor to be evaluated
        :type monitor: BaseMonitor
        :rtype: tuple(list, list)
        :return: (weights and accuracy of the monitor (i.e. percentage of correctly classified OOD inputs) for each OOD-class, accuracy of the monitor for each OOD-class)
        """
        assert monitor.is_initialized()
        result = []
        for ood_class in self.ood_classes:
            logging.debug(f"Evaluate the monitor on {ood_class}...")
            all_results = monitor.evaluate(monitor.data.get_OOD_val(ood_class))
            logging.debug(f"The monitor detected {sum(all_results)} / {len(all_results)} inputs correctly.")
            result.append(sum(all_results) / len(all_results))
        vals = [self.weights[i] for i in range(len(self.weights))]
        vals += result
        return vals, result

    def __call__(self, monitor: BaseMonitor) -> float:
        """
        Evaluates the monitor on all OOD-classes and accumulate the result.

        :param monitor: the monitor to be evaluated
        :type monitor: BaseMonitor
        :rtype: float
        :return: value of the objective
        """
        _, result = self.evaluate(monitor)
        logging.debug(f"Value of the objective is {sum([result[i] * self.weights[i] for i in range(len(result))])}.")
        return sum([result[i] * self.weights[i] for i in range(len(result))])


class OptimalForOODClassesSubjectToFNR(MultiObjective):
    """
    This class evaluates a monitor on several specified OOD-classes given that the accuracy on the ID data is above a
     given threshold.
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize the objective and store the configuration.
        Specify the relevant OOD-classes on which the monitor should be evaluated.
        The monitor is evaluated on the validation set.
        """
        super().__init__(config)
        self.ood_classes = [x.strip() for x in config.additional_objective_info['ood_classes'].split(',')]
        logging.debug(f"The objective evaluates on the ood-classes {self.ood_classes}.")
        self.tnr_minimum = config.additional_objective_info.getint('tnr_minimum')
        logging.debug(f"The minimum accuracy on ID inputs is {self.tnr_minimum}.")

    def get_columns(self) -> list:
        """
        Get the column names for this objective, i.e., "weight-1, weight-2, ..., result-1, result-2", such that
         the results can be stored in a table.

        :rtype: list
        :return: the columns for a pandas.DataFrame
        """
        columns = [f"weight-{ood_class}" for ood_class in self.ood_classes]
        columns += ["result-id"]
        columns += [f"result-{ood_class}" for ood_class in self.ood_classes]
        return columns

    def get_num_objectives(self) -> int:
        """
        Return the number of objectives.

        :rtype: int
        :return: the number of objectives, in this case the number of OOD-classes
        """
        return len(self.ood_classes)

    def evaluate(self, monitor: BaseMonitor) -> (list, list):
        """
        Evaluates the monitor on all OOD-classes.

        :param monitor: the monitor to be evaluated
        :type monitor: BaseMonitor
        :rtype: tuple(list, list)
        :return: (weights and accuracy of the monitor (i.e. percentage of correctly classified OOD inputs) for each OOD-class, accuracy of the monitor for each OOD-class)
        """
        assert monitor.is_initialized()
        id_result = monitor.evaluate(monitor.data.get_ID_val())
        logging.debug(f"The monitor was evaluated on ID and it detected {sum(id_result)} / {len(id_result)}"
                      f" inputs correctly.")
        id_result = (1 - (sum(id_result) / len(id_result)))
        result = []
        for ood_class in self.ood_classes:
            logging.debug(f"Evaluate the monitor on {ood_class}...")
            all_results = monitor.evaluate(monitor.data.get_OOD_val(ood_class))
            logging.debug(f"The monitor detected {sum(all_results)} / {len(all_results)} inputs correctly.")
            result.append(sum(all_results) / len(all_results))
        vals = [self.weights[i] for i in range(len(self.weights))]
        vals += [id_result]
        vals += result
        return vals, result, id_result

    def __call__(self, monitor: BaseMonitor) -> float:
        """
        Evaluate a monitor on the defined OOD-classes (validation set) and on the ID-data.
        If the accuracy on the ID data is above the threshold, the result is only the accuracy on the OOD-data.
        Otherwise, a violation of the ID-accuracy is punished with (-10 + accuracy on ID).
        Note that the accuracy will range between 0 and 1.

        :param monitor: the monitor to be evaluated
        :type monitor: BaseMonitor
        :rtype: float
        :return: value of the objective
        """
        _, result, id_result = self.evaluate(monitor)
        if id_result * 100 < self.tnr_minimum:
            logging.debug(
                f"The value of the objective function is {sum([result[i] * self.weights[i] for i in range(len(result))]) - 10 + id_result}.")
            return sum([result[i] * self.weights[i] for i in range(len(result))]) - 10 + id_result
        else:
            logging.debug(
                f"The value of the objective function is {sum([result[i] * self.weights[i] for i in range(len(result))])}.")
            return sum([result[i] * self.weights[i] for i in range(len(result))])
