
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

from leaf_common.fitness.fitness_objectives_builder \
    import FitnessObjectivesBuilder

from leaf_common.parsers.field_extractor import FieldExtractor
from leaf_common.parsers.canonical_multi_config_parser \
    import CanonicalMultiConfigParser


class FitnessObjectivesFromConfig():
    """
    Helper class to create a ChromosomeDataFitnessObjectives instance
    by reading the relevant config files.
    """

    def __init__(self):
        """
        Constructor.
        """

        # Gets the relevant fields from the config dict
        self.extractor = FieldExtractor()

    def create_fitness_objectives(self, config, nested_config=None):
        """
        :param config: The Config dictionary containing
                the LEAF-style fitness specification.
                This should either be a master config or a builder config.
        :param nested_config: The name of the nested config that fitness values
                should come from. The default is None, indicating that
                we should find the fields on the dictionary passed in.
        :return: The LEAF FitnessObjectives object parsed from that config
        """

        basis_config = self.find_basis_config(config, nested_config)

        builder = self.find_modern_specification(basis_config)
        if builder is None:
            builder = self.find_legacy_fields(basis_config)

        # Build the FitnessObjectives object
        fitness_objectives = builder.build()

        # Alter the Comparator objects if the implementation allows
        fitness_objectives = self.alter_comparators(fitness_objectives)

        return fitness_objectives

    def find_basis_config(self, config, nested_config):
        """
        :param config: The config object/dictionary to extract
                    fitness information from
        :param nested_config: The key which will get to the
                    sub-dictionary within the config that will
                    have the fitness information
        :return: The basis config dictionary expected to contain
                fitness information
        """

        # Get the config as a dictionary
        basis_config = config
        if config is None:
            basis_config = {}
        elif hasattr(config, 'config'):
            # Allow for Config objects
            basis_config = config.config

        if nested_config is not None:
            # If the config was a master config, get the nested config out of it
            nested_config_dict = self.extractor.get_field(basis_config,
                                                          nested_config, None)
            if nested_config_dict is not None and \
                    isinstance(nested_config_dict, dict):
                basis_config = nested_config_dict

        return basis_config

    def find_legacy_fields(self, config_dict):
        """
        :param config_dict: The configuration dictionary containing fitness
                    information
        :return: A FitnessObjectivesBuilder object populated from legacy
                 fitness key/value rules.
        """

        # Default to single objective, maximization, if not specified.
        default_fitness_names = 'fitness'
        default_maximize_fitness = 'true'

        # Check for multi-objective
        alt_obj_strength = self.extractor.get_field(config_dict, 'alt_obj_strength', 0)
        coevo_alt_obj_strength = self.extractor.get_field(config_dict,
                                                          'coevo_alt_obj_str', 0)
        # Either of these not being 0 means that the alt objective is used
        # for ParetoSort either in Species or Coevolution, so we need the
        # other objective defined.
        if alt_obj_strength != 0 or coevo_alt_obj_strength != 0:
            default_fitness_names = 'fitness, alt_objective'
            default_maximize_fitness = 'true, true'

        # Try the nested fitness dict first
        metric_names = self.extractor.get_field(config_dict,
                                                'fitness.metric.name',
                                                default_fitness_names)
        maximize_fitnesses = self.extractor.get_field(config_dict,
                                                      'fitness.metric.maximize',
                                                      default_maximize_fitness)

        # Now try the flattened name
        metric_names = self.extractor.get_field(config_dict,
                                                'fitness_metrics_names',
                                                metric_names)
        maximize_fitnesses = self.extractor.get_field(config_dict,
                                                      'fitness_metrics_maximize',
                                                      maximize_fitnesses)

        # Build the FitnessObjectives object
        builder = FitnessObjectivesBuilder(metric_names=metric_names,
                                           maximize_fitnesses=maximize_fitnesses)
        return builder

    def find_modern_specification(self, config_dict):
        """
        :param config_dict: The configuration dictionary containing fitness
                    information
        :return: A FitnessObjectivesBuilder object populated from more modern
                 and cleanly extensible fitness key/value rules.
        """

        fitness_objectives = None

        # The main key for all this is "fitness"
        fitness = self.extractor.get_field(config_dict, 'fitness', None)
        fitness = self.parse_into_list(fitness)
        if fitness is None:
            return None

        fitness_objectives = self.parse_list(fitness)
        if fitness_objectives is None:
            return None

        # Build the FitnessObjectives object
        builder = FitnessObjectivesBuilder(
                            objective_dictionary_list=fitness_objectives)

        return builder

    def parse_into_list(self, fitness):
        """
        :param fitness: The raw value of the fitness field to parse.
            This value can be:
                ... for single objective fitness:
                    1   A single string denoting a single fitness metric name
                        that is (by default) to be maximized
                    2.  A single dictionary of the structure:
                        {
                            "metric_name": "<your_metric_name>",
                            "maximize": True/False
                        }
                ... for multi objective fitness:
                    3.  A list of one or more entries for single objective
                        fitness (above)
        :return: A single list-normalized (but not component-normalized) version
                 of the entries for fitness.

                 Even if a single objective was specified, we return a list
                 with a single element in it.
        """

        if fitness is None:
            return None

        # Parse values that are not lists
        if isinstance(fitness, dict):
            metric_value = fitness.get('metric', None)
            if metric_value is not None:
                # Assumption is the legacy style.
                # Let the legacy method handle it.
                return None

            # Make a list out of the single dict and continue
            fitness = [fitness]

        elif isinstance(fitness, str):
            # Assumption is that only fitness metric name is specified
            # Make a list out of the single string and continue
            fitness = [fitness]

        elif isinstance(fitness, (bool, float, int)):
            # Damn fool specification.
            # We don't know what they are thinking.
            # Use legacy.
            return None

        return fitness

    def parse_list(self, fitness):
        """
        :param fitness: The list-normalized, not component-normalize
            value of the fitness field
            The component values can be:
                    1   A single string denoting a single fitness metric name
                        that is (by default) to be maximized
                    2.  A single dictionary of the structure:
                        {
                            "metric_name": "<your_metric_name>",
                            "maximize": True/False
                        }
                ... for each component of the list.
        :return: A single fully normalized list of the entries for fitness.
                 Even if a single objective was specified, we return a list
                 with a single element in it.
        """

        if len(fitness) == 0:
            return None

        parser = CanonicalMultiConfigParser(name_key="metric_name")
        objective_dictionary_list = parser.parse(fitness)

        # Strip the fitness names
        for one_dict in objective_dictionary_list:
            value = one_dict.get("metric_name")
            stripped = value.strip()
            one_dict["metric_name"] = stripped

        return objective_dictionary_list

    def alter_comparators(self, fitness_objectives):
        """
        Method to allow for alteration of the comparators to reflect
        implementation details of fitness handling.

        :param fitness_objectives: A FitnessObjectives object
        :return: a potentially alternate version of the FitnessObjectives
        """

        # By default, this implementation does nothing
        return fitness_objectives
