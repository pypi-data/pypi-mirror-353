# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

import logging
from monitizer.monitors.Monitor import BaseMonitor
from monitizer.optimizers.optimization_config import OptimizationConfig
from monitizer.optimizers.objective import Objective


class OptimalForOODClass(Objective):
    """
    This class evaluates a monitor on one specific OOD-class.
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize the objective and store the configuration.
        Specify the relevant OOD-class on which the monitor should be evaluated.
        The monitor is evaluated on the validation set.
        """
        super().__init__(config)
        self.ood_class = config.additional_objective_info['ood_classes'].split(',')[0]
        logging.debug(f"The objective evaluates on the ood-class {self.ood_class}.")

    def __call__(self, monitor: BaseMonitor) -> float:
        """
        Evaluate a monitor on the defined OOD-class (validation set).
        :param monitor: the monitor to be evaluated
        :type monitor: BaseMonitor
        :rtype: float
        :return: accuracy of the monitor (i.e. percentage of correctly classified OOD inputs)
        """
        assert monitor.is_initialized()
        results = monitor.evaluate(monitor.data.get_OOD_val(self.ood_class))
        logging.debug(f"The monitor was evaluated on {self.ood_class} and it detected {sum(results)} / {len(results)}"
                      f" inputs correctly.")
        logging.debug(f"The value of the objective function is {sum(results) / len(results)}.")
        return sum(results) / len(results)


class OptimalForOODClassSubjectToFNR(Objective):
    """
   This class evaluates a monitor on one specific OOD-class given that the accuracy on the ID data is above a
    given threshold.
   """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize the objective and store the configuration.
        Specify the relevant OOD-class on which the monitor should be evaluated and the minimum accuracy on the ID data.
        The monitor is evaluated on the validation set.
        """
        super().__init__(config)
        self.ood_class = config.additional_objective_info['ood_classes'].split(',')[0]
        logging.debug(f"The objective evaluates on the ood-class {self.ood_class}")
        self.tnr_minimum = config.additional_objective_info.getint('tnr_minimum')
        logging.debug(f"The minimum accuracy on ID inputs is {self.tnr_minimum}.")

    def __call__(self, monitor: BaseMonitor) -> float:
        """
        Evaluate a monitor on the defined OOD-class (validation set) and on the ID-data.
        If the accuracy on the ID data is above the threshold, the result is only the accuracy on the OOD-data.
        Otherwise, a violation of the ID-accuracy is punished with (-10 + accuracy on ID).
        Note that the accuracy will range between 0 and 1.

        :param monitor: the monitor to be evaluated
        :type monitor: BaseMonitor
        :rtype: float
        :return: accuracy of the monitor (i.e. percentage of correctly classified OOD inputs)
        """
        assert monitor.is_initialized()
        id_result = monitor.evaluate(monitor.data.get_ID_val())
        logging.debug(f"The monitor was evaluated on ID and it detected {sum(id_result)} / {len(id_result)}"
                      f" inputs correctly.")
        id_result = (1 - (sum(id_result) / len(id_result)))
        results = monitor.evaluate(monitor.data.get_OOD_val(self.ood_class))
        logging.debug(f"The monitor was evaluated on {self.ood_class} and it detected {sum(results)} / {len(results)}"
                      f" inputs correctly.")
        if id_result * 100 < self.tnr_minimum:
            logging.debug(f"The value of the objective function is {(sum(results) / len(results)) - 10 + id_result}.")
            return (sum(results) / len(results)) - 10 + id_result
        else:
            logging.debug(f"The value of the objective function is {sum(results) / len(results)}.")
            return sum(results) / len(results)

class OptimalForAverageGeneratedOOD(Objective):
    """
    This class evaluates a monitor on one specific OOD-class.
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize the objective and store the configuration.
        Specify the relevant OOD-class on which the monitor should be evaluated.
        The monitor is evaluated on the validation set.
        """
        super().__init__(config)

    def __call__(self, monitor: BaseMonitor) -> float:
        """
        Evaluate a monitor on the defined OOD-class (validation set).
        :param monitor: the monitor to be evaluated
        :type monitor: BaseMonitor
        :rtype: float
        :return: accuracy of the monitor (i.e. percentage of correctly classified OOD inputs)
        """
        assert monitor.is_initialized()
        results = []
        for ood_class in monitor.data.get_generated_ood_names():
            result = monitor.evaluate(monitor.data.get_OOD_val(ood_class))
            results.append(sum(result) / len(result))
            logging.debug(f"The monitor was evaluated on {ood_class} and it detected {sum(result)} / {len(result)}"
                      f" inputs correctly.")

        logging.debug(f"The value of the objective function is {sum(results) / len(results)}.")
        return sum(results) / len(results)
