
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

from leaf_common.fitness.fitness_objective import FitnessObjective

from leaf_common.fitness.reversed_comparator import ReversedComparator

from leaf_common.fitness.fitness_objectives import FitnessObjectives
from leaf_common.fitness.metrics_based_individual_comparator \
    import MetricsBasedIndividualComparator

from leaf_common.parsers.list_parser import ListParser
from leaf_common.parsers.boolean_list_parser import BooleanListParser


class FitnessObjectivesBuilder():
    """
    Class which keeps track of all the Fitness Objective data for
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
    """

    DEFAULT_MAXIMIZE_FITNESS = True

    def __init__(self, metric_names=None,
                 maximize_fitnesses=None,
                 objective_dictionary_list=None):
        """
        Constructor.

        :param metric_names: a single space-delimited string containing
                the one or more field names of the Metrics Record
                that correspond to fitness objectives.
        :param maximize_fitnesses: a single space-delimited string containing
                one or more booleans which describe whether the metric name
                in the same list position should be maximized.

                Components that are marked as true are maximized.
                Components that are marked as false are minimized.

                If this list contains fewer components than the metric_names
                list, a value of true will be filled in for any missing
                component, starting at the end of the exhausted list of
                metric names.  Any extra components are ignored.

        :param objective_dictionary_list: a list of dictionaries that
                fully describe any and all fitness objectives.  As this is
                an alternate means of specifying what is to be built,
                when specified, we expect metric_names and maximize_fitnesses
                to both be None.
        """

        self._string_list_parser = ListParser()
        self._boolean_list_parser = BooleanListParser()
        self._metric_names = metric_names
        self._maximize_fitnesses = maximize_fitnesses
        self._objective_dictionary_list = objective_dictionary_list

    def build(self):
        """
        :return: a FitnessObjectives instance given the constructor arguments.
        """

        # Create the immutable list we will be handing back to
        # clients of this object.
        objectives = self.parse_fitness_objectives()
        objectives_list = copy.copy(objectives)

        comparators = self.create_ranking_comparators(objectives_list)
        ranking_comparators = copy.copy(comparators)

        fitness_objectives = FitnessObjectives(objectives_list,
                                               ranking_comparators)
        return fitness_objectives

    def parse_fitness_objectives(self):
        """
        Called from build().

        :return: a List of FitnessObjective-s parsed from the two passed
                Strings
        """

        if self._objective_dictionary_list is not None:
            objectives = self.parse_from_dictionaries()
        else:
            objectives = self.parse_from_strings()

        return objectives

    def parse_from_strings(self):
        """
        :return: FitnessObjectives structure built from legacy parsing
                of multiple strings.
        """

        # Parse the string arguments into lists of primitives
        metrics = self._string_list_parser.parse_list(self._metric_names)
        maximizes = self._boolean_list_parser.parse_list(self._maximize_fitnesses)

        # Assembles the lists of primitives into FitnessObjective-s.
        objectives = []
        for i, metric in enumerate(metrics):

            maximize = self.DEFAULT_MAXIMIZE_FITNESS
            if i < len(maximizes):
                maximize = maximizes[i]

            objective = FitnessObjective(metric, maximize)
            objectives.append(objective)

        return objectives

    def parse_from_dictionaries(self):
        """
        :return: FitnessObjectives structure built from more modern parsing
                of a list of dictionaries.
        """

        # Assembles the lists of primitives into FitnessObjective-s.
        objectives = []
        for objective_dict in self._objective_dictionary_list:

            metric = objective_dict.get("metric_name", "fitness")
            maximize = objective_dict.get("maximize", self.DEFAULT_MAXIMIZE_FITNESS)

            objective = FitnessObjective(metric, maximize)
            objectives.append(objective)

        return objectives

    def create_ranking_comparators(self, objectives):
        """
        Called from build().

        :param objectives: a List of FitnessObjectives
        :return: a List of Comparators of MetricsProviders (Individuals)
            for each fitness objective in the already-parsed list.
        """

        comparators = []

        for objective in objectives:

            metric_name = objective.get_metric_name()
            maximize_fitness = objective.is_maximize_fitness()

            ranking_comparator = MetricsBasedIndividualComparator(metric_name)
            if maximize_fitness:
                ranking_comparator = ReversedComparator(ranking_comparator)

            comparators.append(ranking_comparator)

        return comparators
