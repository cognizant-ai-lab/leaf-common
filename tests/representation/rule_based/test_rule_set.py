"""
Unit tests for RuleSet
"""
import os
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.evaluation.rule_set_evaluator \
    import RuleSetEvaluator
from leaf_common.representation.rule_based.persistence.rule_set_file_persistence \
    import RuleSetFilePersistence
from leaf_common.representation.rule_based.data.rules_evaluation_constants \
    import RulesEvaluationConstants


class TestRuleSet(TestCase):
    """
    Unit tests for RuleSet
    """

    def __init__(self, *args, **kwargs):
        super(TestRuleSet, self).__init__(*args, **kwargs)
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

    def test_complex_rule_set_roundtrip(self):
        """
        Verify roundtrip with persisted rule_set "from the field" (gen 50 Flappy Bird)
        """
        rules_file = os.path.join(self.fixtures_path, 'saved_rule_set.rules')
        persistence = RuleSetFilePersistence()
        rule_set = persistence.restore(rules_file)

        with tempfile.NamedTemporaryFile('w') as saved_rule_set_file:
            persistence = RuleSetFilePersistence()
            persistence.persist(rule_set, saved_rule_set_file.name)
            reloaded_rule_set = persistence.restore(saved_rule_set_file.name)

        self.assertIsNot(rule_set, reloaded_rule_set)

    @patch("leaf_common.representation.rule_based.rule_set_evaluator.RuleEvaluator.evaluate",
           return_value=Mock())
    def test_parse_rules_agree(self, evaluate_mock):
        """
        Verify correct parsing of rules
        """

        # Set it up so mock rules agree on action1
        rule_set, num_rules = self._create_rules_rule_set(
            rule1_action={RulesEvaluationConstants.ACTION_KEY: 'action1'},
            rule2_action={RulesEvaluationConstants.ACTION_KEY: 'action1'})

        self.assertEqual(num_rules, len(rule_set.rules))

        evaluate_mock.side_effect = [
            {RulesEvaluationConstants.ACTION_KEY: 'action1'},
            {RulesEvaluationConstants.ACTION_KEY: 'action1'}
        ]

        evaluator = RuleSetEvaluator(self.states, self.actions)
        result = evaluator.parse_rules(rule_set)

        self.assertEqual(num_rules, len(result))
        self.assertTrue('action1' in result)
        self.assertTrue('action2' in result)
        self.assertEqual(num_rules, result['action1'])
        self.assertEqual(0, result['action2'])

    @patch("leaf_common.representation.rule_based.rule_set_evaluator.RuleEvaluator.evaluate",
           return_value=Mock())
    def test_parse_rules_disagree(self, evaluate_mock):
        """
        Verify correct parsing of rules
        """

        # Set it up so mock rules vote differently -- 1 for action1, 1 for action2
        rule_set, num_rules = self._create_rules_rule_set(
            rule1_action={RulesEvaluationConstants.ACTION_KEY: 'action1'},
            rule2_action={RulesEvaluationConstants.ACTION_KEY: 'action2'})

        self.assertEqual(num_rules, len(rule_set.rules))

        evaluate_mock.side_effect = [
            {RulesEvaluationConstants.ACTION_KEY: 'action1'},
            {RulesEvaluationConstants.ACTION_KEY: 'action2'}
        ]

        evaluator = RuleSetEvaluator(self.states, self.actions)
        result = evaluator.parse_rules(rule_set)

        print("test result = ", str(result))
        self.assertEqual(num_rules, len(result))
        self.assertTrue('action1' in result)
        self.assertTrue('action2' in result)
        self.assertEqual(1, result['action1'])
        self.assertEqual(1, result['action2'])

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
