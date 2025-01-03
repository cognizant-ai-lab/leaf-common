
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
Unit tests for RuleSet
"""
import os
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from leaf_common.representation.rule_based.config.rule_set_config_helper \
    import RuleSetConfigHelper
from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.data.rule_set_binding \
    import RuleSetBinding
from leaf_common.representation.rule_based.evaluation.rule_set_evaluator \
    import RuleSetEvaluator
from leaf_common.representation.rule_based.persistence.rule_set_file_persistence \
    import RuleSetFilePersistence
from leaf_common.representation.rule_based.persistence.rule_set_binding_file_persistence \
    import RuleSetBindingFilePersistence
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants


class TestRuleSet(TestCase):
    """
    Unit tests for RuleSet
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        root_dir = os.path.dirname(os.path.abspath(__file__))
        self.fixtures_path = os.path.join(root_dir, '../..', 'fixtures')
        self.states = {
            'k1': 'value1',
            'k2': 'value2'
        }
        self.actions = {
            'action1': 'action_value1',
            'action2': 'action_value2'
        }

    def test_rule_set_config_helper_weird_values(self):
        """
        Verify extracting states and actions from config when values do not correspond with size
        """
        config = {"network": {"inputs": [
            {
                "name": "observations",
                "size": 4,
                "values": [
                    "float"
                ]
            }], "argmax_on_outputs": True,
            "hidden_layers": [
                {"layer_name": "hidden_1",
                 "layer_type": "Dense",
                 "layer_params": {
                     "units": 32,
                     "activation": "tanh",
                     "use_bias": True
                 }
                 }
            ],
            "outputs": [
                {
                    "name": "Action",
                    "size": 2,
                    "activation": "softmax",
                    "use_bias": True,
                    "values": [
                        "Push cart to the left",
                        "Push cart to the right"
                    ]
                }
            ]
        },
            "evolution": {
                "nb_generations": 160,
                "early_stop": True,
                "population_size": 50,
                "nb_elites": 5,
                "parent_selection": "tournament",
                "fitness": [
                    {"metric_name": "score", "maximize": True, "target": 195}
                ],
                "remove_population_pct": 0.8,
                "mutation_type": "gaussian_noise_percentage",
                "mutation_probability": 0.1,
                "mutation_factor": 0.1,
                "initialization_distribution": "orthogonal",
                "initialization_range": 1
            },
            "esp_rl_loop": {
                "domain_name": "OpenAIGym.CartPole-v0",
                "predictor_type": "NN",
                "nb_predictor_eval_gens": -1,
                "nb_episodes": 5,
                "nb_episodes_to_consider_solved": 100,
                "max_nb_frames": 200,
                "record_video": False,
                "random_agent_init": True,
                "nb_rf_estimators": 100,
                "data_cutoff_rows": 1000000,
                "decay": 0.9
            },
            "LEAF": {
                "esp_host_official": "v1.esp.evolution.ml",
                "esp_host": "localhost",
                "esp_port": 50051,
                "representation": "NNWeights",
                "experiment_id": "ESP-CartPole-Olivier-DE",
                "reevaluate_elites": True,
                "version": "0.0.1",
                "persistence_dir": "trained_agents/",
                "candidates_to_persist": "elites"
            }
        }
        states = RuleSetConfigHelper.get_states(config)
        self.assertEqual(len(states), 4)
        self.assertEqual(states['0'], 'observations_is_category_io_0')
        actions = RuleSetConfigHelper.get_actions(config)
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions['1'], 'Action_is_category_Push cart to the right')

    def test_rule_set_config_helper_no_inputs(self):
        """
        Verify extracting states and actions from config when values is missing
        This config is similar to what we construct based on OpenAI Gym envs
        """
        config = {"network": {"inputs": [
            {
                "name": "observations",
                "size": 4,
            }],
         "hidden_layers": [
            {"layer_name": "hidden_1",
             "layer_type": "Dense",
             "layer_params": {
                 "units": 128,
                 "activation": "tanh",
                 "use_bias": True
                 }
             }], "outputs": [
            {
                "name": "Action",
                "activation": "softmax",
                "size": 3,
                "use_bias": True
            }], }, "evolution": {
            "nb_generations": 9,
            "early_stop": True,
            "population_size": 20,
            "nb_elites": 1,
            "parent_selection": "tournament",
            "fitness": [
                {"metric_name": "score", "maximize": True, "target": 195}],
            "remove_population_pct": 0.8,
            "mutation_type": "gaussian_noise_percentage",
            "mutation_probability": 0.8,
            "mutation_factor": 0.1,
            "initialization_distribution": "orthogonal",
            "initialization_range": 1
        },
            "esp_rl_loop": {
            "domain_name": "OpenAIGym.CartPole-v0",
            "nb_esp_loop_iterations": 100,
            "predictor_type": "RFR",
            "nb_predictor_eval_gens": 3,
            "nb_rf_estimators": 100,
            "nb_episodes": 2,
            "nb_episodes_to_consider_solved": 1,
            "max_nb_frames": 200,
            "data_cutoff_rows": 10000,
            "decay": 0.9,
            "random_agent_init": True,
            "record_video": False
        },
            "LEAF": {
                "esp_port": 50051,
                "representation": "RuleBased",
                "reevaluate_elites": True,
                "version": "0.0.1",
                "persistence_dir": "trained_agents/",
                "candidates_to_persist": "elites"
            }
        }
        states = RuleSetConfigHelper.get_states(config)
        self.assertEqual(len(states), 4)
        self.assertEqual(states['3'], 'observations_is_category_io_3')
        actions = RuleSetConfigHelper.get_actions(config)
        self.assertEqual(len(actions), 3)
        self.assertEqual(actions['1'], 'Action_is_category_io_1')

    def test_serialize_roundtrip(self):
        """
        Verify simple roundtrip with serializer
        """
        rule_set = RuleSet()

        with tempfile.NamedTemporaryFile('w') as saved_rule_set_file:
            persistence = RuleSetFilePersistence()
            persistence.persist(rule_set, saved_rule_set_file.name)
            reloaded_rule_set = persistence.restore(saved_rule_set_file.name)

        self.assertIsNot(rule_set, reloaded_rule_set)

    def test_rulesmodel_serialize_roundtrip(self):
        """
        Verify simple roundtrip with rules model serializer
        """
        rules_model = RuleSetBinding(RuleSet(), [], [])

        with tempfile.NamedTemporaryFile('w') as saved_rules_model_file:
            persistence = RuleSetBindingFilePersistence()
            persistence.persist(rules_model, saved_rules_model_file.name)
            reloaded_rules_model = persistence.restore(saved_rules_model_file.name)

        self.assertIsNot(rules_model, reloaded_rules_model)

    def test_complex_rule_set_roundtrip(self):
        """
        Verify roundtrip with persisted rule_set "from the field" (gen 50 Flappy Bird)
        """
        rules_file = os.path.join(self.fixtures_path, 'saved_rule_set')
        persistence = RuleSetFilePersistence()
        rule_set = persistence.restore(rules_file)

        with tempfile.NamedTemporaryFile('w') as saved_rule_set_file:
            persistence = RuleSetFilePersistence()
            persistence.persist(rule_set, saved_rule_set_file.name)
            reloaded_rule_set = persistence.restore(saved_rule_set_file.name)

        self.assertIsNot(rule_set, reloaded_rule_set)

    def test_complex_rules_model_roundtrip(self):
        """
        Verify roundtrip with persisted rules model "from the field"
        """
        rules_model_path = os.path.join(self.fixtures_path, 'saved_rules_model')
        persistence = RuleSetBindingFilePersistence()
        rules_model = persistence.restore(rules_model_path)

        with tempfile.NamedTemporaryFile('w') as saved_rules_model_file:
            persistence = RuleSetBindingFilePersistence()
            persistence.persist(rules_model, saved_rules_model_file.name)
            reloaded_rules_model = persistence.restore(saved_rules_model_file.name)

        self.assertIsNot(rules_model, reloaded_rules_model)

    @patch("leaf_common.representation.rule_based.evaluation.rule_set_evaluator.RuleEvaluator.evaluate",
           return_value=Mock())
    def test_parse_rules_agree(self, evaluate_mock):
        """
        Verify correct parsing of rules
        """

        # Set it up so mock rules agree on action1
        rule_set, num_rules = self._create_rules_rule_set(
            rule1_action={RulesConstants.ACTION_KEY: 'action1'},
            rule2_action={RulesConstants.ACTION_KEY: 'action1'})

        self.assertEqual(num_rules, len(rule_set.rules))

        evaluate_mock.side_effect = [
            {RulesConstants.ACTION_KEY: 'action1', RulesConstants.ACTION_COEFFICIENT_KEY: 0.5},
            {RulesConstants.ACTION_KEY: 'action1', RulesConstants.ACTION_COEFFICIENT_KEY: 0.9}
        ]

        evaluator = RuleSetEvaluator(self.states, self.actions)
        result = evaluator.parse_rules(rule_set)

        self.assertEqual(num_rules, len(result))
        self.assertTrue('action1' in result)
        self.assertTrue('action2' in result)
        self.assertEqual(num_rules, result['action1'].get(RulesConstants.ACTION_COUNT_KEY))
        self.assertEqual(0, result['action2'].get(RulesConstants.ACTION_COUNT_KEY))
        self.assertEqual(1.4, result['action1'].get(RulesConstants.ACTION_COEFFICIENT_KEY))
        self.assertEqual(0.0, result['action2'].get(RulesConstants.ACTION_COEFFICIENT_KEY))

    @patch("leaf_common.representation.rule_based.evaluation.rule_set_evaluator.RuleEvaluator.evaluate",
           return_value=Mock())
    def test_parse_rules_disagree(self, evaluate_mock):
        """
        Verify correct parsing of rules
        """

        # Set it up so mock rules vote differently -- 1 for action1, 1 for action2
        rule_set, num_rules = self._create_rules_rule_set(
            rule1_action={RulesConstants.ACTION_KEY: 'action1'},
            rule2_action={RulesConstants.ACTION_KEY: 'action2'})

        self.assertEqual(num_rules, len(rule_set.rules))

        evaluate_mock.side_effect = [
            {RulesConstants.ACTION_KEY: 'action1', RulesConstants.ACTION_COEFFICIENT_KEY: 0.5},
            {RulesConstants.ACTION_KEY: 'action2', RulesConstants.ACTION_COEFFICIENT_KEY: 0.1}
        ]

        evaluator = RuleSetEvaluator(self.states, self.actions)
        result = evaluator.parse_rules(rule_set)

        print("test result = ", str(result))
        self.assertEqual(num_rules, len(result))
        self.assertTrue('action1' in result)
        self.assertTrue('action2' in result)
        self.assertEqual(1, result['action1'].get(RulesConstants.ACTION_COUNT_KEY))
        self.assertEqual(1, result['action2'].get(RulesConstants.ACTION_COUNT_KEY))
        self.assertEqual(0.5, result['action1'].get(RulesConstants.ACTION_COEFFICIENT_KEY))
        self.assertEqual(0.1, result['action2'].get(RulesConstants.ACTION_COEFFICIENT_KEY))

    @staticmethod
    def _create_rules_rule_set(rule1_action, rule2_action):
        mock_rule_1 = MagicMock()
        mock_rule_2 = MagicMock()
        mock_rule_1.conditions = [MagicMock()]
        mock_rule_2.conditions = [MagicMock()]
        mock_rule_1.parse.return_value = rule1_action
        mock_rule_2.parse.return_value = rule2_action
        rule_set = RuleSet()
        rule_set.rules.append(mock_rule_1)
        rule_set.rules.append(mock_rule_2)
        return rule_set, len(rule_set.rules)
