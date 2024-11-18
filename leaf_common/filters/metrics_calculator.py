
# Copyright (C) 2021-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# unileaf-util SDK Software in commercial settings.
#
# END COPYRIGHT
from abc import ABC
from abc import abstractmethod

from typing import Dict


class MetricsCalculator(ABC):
    """
    This class implements a contract for implementations
    to calculate a certain kind of metric.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of this metric
        :return: a string
        """

    def __str__(self):
        return self.name

    @staticmethod
    @abstractmethod
    def compute(ground_truth, predictions, filtered_metric_params: Dict = None):
        """
        This function computes the metrics.
        :param ground_truth: Array or DataFrame
        :param predictions: Array or DataFrame of the same format as ground_truth
        :param filtered_metric_params: Dictionary containing the parameters of the metric if any
        :return measurement: A score representing the metric.
        """

    @staticmethod
    @abstractmethod
    def get_default_params() -> Dict:
        """
        This function should return the default Parameters of
        the metric as Dictionary along with a description.
        :return default_model_params: Dictionary
        Format: {
            "parameter_name": {
                "default_value": "",
                "description": ""
            },
        }
        """
