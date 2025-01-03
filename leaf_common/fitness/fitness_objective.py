
# Copyright (C) 2019-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# leaf-common SDK Software in commercial settings.
#
# END COPYRIGHT
"""
See class comment for details.
"""


class FitnessObjective():
    """
    A Data-only class which describes a single fitness objective.
    """

    def __init__(self, metric_name, maximize_fitness=True):
        """
        Constructor.

        :param metric_name: the String name of the field in a Metrics Record
                    whose value directly corresponds to this fitness
                    objective
        :param maximize_fitness: True when maximizing fitness.
                    False when minimizing. Default value is True.
        """
        self._metric_name = metric_name
        self._maximize_fitness = maximize_fitness

    def get_metric_name(self):
        """
        :return: the String name of the fitness metric
        """
        return self._metric_name

    def is_maximize_fitness(self):
        """
        :return: true if we are maximizing fitness.
                False otherwise.
        """
        return self._maximize_fitness
