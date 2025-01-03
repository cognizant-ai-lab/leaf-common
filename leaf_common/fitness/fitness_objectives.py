
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

import copy
import math

from typing import List

from leaf_common.fitness.comparator import Comparator
from leaf_common.fitness.fitness_objective import FitnessObjective


class FitnessObjectives():
    """
    Data class which keeps track of all the Fitness Objective data for
    an experiment.

    The idea behind this class is that this guy:

    1. Parses fitness information from common injected properties
    2. Centralizes the access to fitness information
    3. Is dependency injected into other policy classes' constructors
       as this information is needed.
    4. Provides ranking Comparators for each fitness objective.
       Ranking comparators put more-fit Individuals closer to the start
       of a list sorted by them, and less-fit Individuals closer to the end.
       (Note that this is the reverse of what most folks might expect
        out of a Comparator, but tends to be the most useful for selection.)

    In general we expect a single instance of this class to be provided to
    all consumers of this information for any single scope of evolution.
    (Meaning coevolution might have > 1)
    """

    def __init__(self, objectives: List[FitnessObjective],
                 ranking_comparators: List[Comparator]):
        """
        Constructor.

        :param objectives: the list of FitnessObjectives.
                Able to handle multi-objective definitions.
        :param ranking_comparators: an immutable list of ranking Comparators.
            Each Comparator corresponds to a single FitnessObjective.
            In sorting a List of MetricsProviders (Individuals),
            Ranking comparators put more-fit Individuals closer to the start
            of the list, and less-fit Individuals closer to the end.
            (Note that this is the reverse of what most folks might expect
             out of a Comparator.)
        """
        self._fitness_objectives = copy.copy(objectives)
        if self._fitness_objectives is None:
            self._fitness_objectives = []

        self._ranking_comparators = copy.copy(ranking_comparators)
        if self._ranking_comparators is None:
            self._ranking_comparators = []

    def get_fitness_objectives(self) -> List[FitnessObjective]:
        """
        :return: the immutable list of FitnessObjective data
        """
        return copy.copy(self._fitness_objectives)

    def get_ranking_comparators(self) -> List[Comparator]:
        """
        :return: the ImmutableList of ranking Comparators.
            Each Comparator corresponds to a single FitnessObjective.
            In sorting a List of MetricsProviders (Individuals),
            Ranking comparators put more-fit Individuals closer to the start
            of the list, and less-fit Individuals closer to the end.
            (Note that this is the reverse of what most folks might expect
             out of a Comparator.)
        """
        return copy.copy(self._ranking_comparators)

    def get_number_of_fitness_objectives(self) -> int:
        """
        :return: the number of fitness objectives
        """
        return len(self._fitness_objectives)

    def get_fitness_objective(self, index: int) -> FitnessObjective:
        """
        :param index: the index of FitnessObjective to return
        :return: the index-th FitnessObjective
        """
        if index < 0 or \
                index >= self.get_number_of_fitness_objectives():
            return None
        return self._fitness_objectives[index]

    def get_ranking_comparator(self, index: int) -> Comparator:
        """
        :param index: the index of the ranking comparator to return
        :return: the index-th ranking Comparator.
        """
        if index < 0 or \
                index >= self.get_number_of_fitness_objectives():
            return None
        return self._ranking_comparators[index]

    def get_lowest_value(self, index: int):
        """
        :param index: the index of the ranking comparator to return
        :return: the index-th comparator's lowest value.
        """
        if index < 0 or \
                index >= self.get_number_of_fitness_objectives():
            return None

        fitness_objective = self.get_fitness_objective(index)
        is_maximize = fitness_objective.is_maximize_fitness()

        lowest_value = -math.inf
        if not is_maximize:
            lowest_value = math.inf

        return lowest_value

    def get_highest_value(self, index: int):
        """
        :param index: the index of the ranking comparator to return
        :return: the index-th comparator's highest value.
        """

        if index < 0 or \
                index >= self.get_number_of_fitness_objectives():
            return None

        lowest_value = self.get_lowest_value(index)
        if lowest_value is None:
            return None

        # Can't get pylint to shut up.
        # pylint: disable=invalid-unary-operand-type
        return -lowest_value

    def get_value_from_metrics_provider(self, metrics_provider, index: int):
        """
        :param metrics_provider: An implementation of the MetricsProvider
                interface
        :param index: the index of FitnessObjective value to return
        :return: The value of the fitness metric, or None if it does not exist
        """
        comparator = self.get_ranking_comparator(index)
        metric_value = comparator.get_basis_value(metrics_provider)
        return metric_value
