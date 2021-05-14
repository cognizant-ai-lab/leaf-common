
# Copyright (C) 2019-2021 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# leaf-common SDK Software in commercial settings.
#
# END COPYRIGHT

from unittest import TestCase

from servicecommon.fitness.fitness_objectives_from_config \
    import FitnessObjectivesFromConfig


class FitnessObjectivesFromConfigTest(TestCase):
    """
    Tests for the FitnessObjectivesFromConfig parser.
    Tests that the FitnessObjectives object that comes out of it
    is what we expect.
    """

    def setUp(self):

        self.parser = FitnessObjectivesFromConfig()

    def test_assumptions(self):

        self.assertIsNotNone(self.parser)

    def test_no_config_keys(self):

        # Test regular case
        config = {
            "my_config": {
            }
        }

        objectives = self.parser.create_fitness_objectives(config, "my_config")
        self.assertIsNotNone(objectives)

        n_obj = objectives.get_number_of_fitness_objectives()
        self.assertEqual(n_obj, 1)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "fitness")
        self.assertTrue(objective.is_maximize_fitness())

    def test_modern_single_string_value_fitness(self):

        # Test regular case
        config = {
            "my_config": {
                "fitness": "fitness"
            }
        }

        objectives = self.parser.create_fitness_objectives(config, "my_config")
        self.assertIsNotNone(objectives)

        n_obj = objectives.get_number_of_fitness_objectives()
        self.assertEqual(n_obj, 1)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "fitness")
        self.assertTrue(objective.is_maximize_fitness())

        # Test stripped metric names
        config = {
            "my_config": {
                "fitness": " my_metric_name "
            }
        }

        objectives = self.parser.create_fitness_objectives(config, "my_config")
        self.assertIsNotNone(objectives)

        n_obj = objectives.get_number_of_fitness_objectives()
        self.assertEqual(n_obj, 1)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "my_metric_name")
        self.assertTrue(objective.is_maximize_fitness())

    def test_modern_single_dict_value_fitness(self):

        # Test regular case
        config = {
            "my_config": {
                "fitness": {
                    "metric_name": "fitness",
                    "maximize": True
                 }
            }
        }

        objectives = self.parser.create_fitness_objectives(config, "my_config")
        self.assertIsNotNone(objectives)

        n_obj = objectives.get_number_of_fitness_objectives()
        self.assertEqual(n_obj, 1)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "fitness")
        self.assertTrue(objective.is_maximize_fitness())

        config = {
            "my_config": {
                "fitness": {
                    "metric_name": " my_metric_name ",
                    "maximize": False
                 }
            }
        }

        objectives = self.parser.create_fitness_objectives(config, "my_config")
        self.assertIsNotNone(objectives)

        n_obj = objectives.get_number_of_fitness_objectives()
        self.assertEqual(n_obj, 1)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "my_metric_name")
        self.assertFalse(objective.is_maximize_fitness())

    def test_modern_single_list_value_fitness(self):

        # Test regular case
        config = {
            "my_config": {
                "fitness": [
                    {
                        "metric_name": "fitness",
                        "maximize": False
                    }
                ]
            }
        }

        objectives = self.parser.create_fitness_objectives(config, "my_config")
        self.assertIsNotNone(objectives)

        n_obj = objectives.get_number_of_fitness_objectives()
        self.assertEqual(n_obj, 1)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "fitness")
        self.assertFalse(objective.is_maximize_fitness())

        config = {
            "my_config": {
                "fitness": ["my_metric_name"]
            }
        }

        objectives = self.parser.create_fitness_objectives(config, "my_config")
        self.assertIsNotNone(objectives)

        n_obj = objectives.get_number_of_fitness_objectives()
        self.assertEqual(n_obj, 1)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "my_metric_name")
        self.assertTrue(objective.is_maximize_fitness())

    def test_modern_multi_dict_value_fitness(self):

        # Test regular case
        config = {
            "my_config": {
                "fitness": [
                    {
                        "metric_name": "fitness",
                        "maximize": False
                    },
                    {
                        "metric_name": "  my_metric_name ",
                        "maximize": True
                    }
                ]
            }
        }

        objectives = self.parser.create_fitness_objectives(config, "my_config")
        self.assertIsNotNone(objectives)

        n_obj = objectives.get_number_of_fitness_objectives()
        self.assertEqual(n_obj, 2)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "fitness")
        self.assertFalse(objective.is_maximize_fitness())

        objective = objectives.get_fitness_objective(1)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "my_metric_name")
        self.assertTrue(objective.is_maximize_fitness())

    def test_modern_multi_string_value_fitness(self):

        # Test regular case
        config = {
            "my_config": {
                "fitness": [
                    "fitness",
                    " my_metric_name  "
                ]
            }
        }

        objectives = self.parser.create_fitness_objectives(config, "my_config")
        self.assertIsNotNone(objectives)

        n_obj = objectives.get_number_of_fitness_objectives()
        self.assertEqual(n_obj, 2)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "fitness")
        self.assertTrue(objective.is_maximize_fitness())

        objective = objectives.get_fitness_objective(1)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "my_metric_name")
        self.assertTrue(objective.is_maximize_fitness())

    def test_modern_multi_mixed_value_fitness(self):

        # Test regular case
        config = {
            "my_config": {
                "fitness": [
                    {
                        "metric_name": "fitness",
                        "maximize": False
                    },
                    " my_metric_name  "
                ]
            }
        }

        objectives = self.parser.create_fitness_objectives(config, "my_config")
        self.assertIsNotNone(objectives)

        n_obj = objectives.get_number_of_fitness_objectives()
        self.assertEqual(n_obj, 2)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "fitness")
        self.assertFalse(objective.is_maximize_fitness())

        objective = objectives.get_fitness_objective(1)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "my_metric_name")
        self.assertTrue(objective.is_maximize_fitness())

    def test_legacy_structure(self):

        config = {
            'fitness': {
                'metric': {
                    "name": "my_fitness",
                    "maximize": "false"
                }
            }
        }

        objectives = self.parser.create_fitness_objectives(config, None)
        self.assertIsNotNone(objectives)

        n_obj = objectives.get_number_of_fitness_objectives()
        self.assertEqual(n_obj, 1)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "my_fitness")
        self.assertFalse(objective.is_maximize_fitness())

    def test_legacy_fields(self):

        config = {
            'fitness_metrics_names': 'fitness, alt_objective',
            'fitness_metrics_maximize': 'false, true'
        }

        objectives = self.parser.create_fitness_objectives(config, None)
        self.assertIsNotNone(objectives)

        n_obj = objectives.get_number_of_fitness_objectives()
        self.assertEqual(n_obj, 2)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "fitness")
        self.assertFalse(objective.is_maximize_fitness())

        objective = objectives.get_fitness_objective(1)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), "alt_objective")
        self.assertTrue(objective.is_maximize_fitness())
