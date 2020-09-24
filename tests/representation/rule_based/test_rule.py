"""
Unit tests for Rules class
"""
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from leaf_common.representation.rule_based.rule import Rule
from leaf_common.representation.rule_based.rule_evaluator import RuleEvaluator
from leaf_common.representation.rule_based.rules_evaluation_constants \
    import RulesEvaluationConstants


class TestRule(TestCase):
    """
    Unit tests for Rules class
    """

    def __init__(self, *args, **kwargs):
        super(TestRule, self).__init__(*args, **kwargs)
        self.min_maxes = {
            ('0', RulesEvaluationConstants.MIN_KEY): 0,
            ('0', RulesEvaluationConstants.MAX_KEY): 10,
            ('1', RulesEvaluationConstants.MIN_KEY): 10,
            ('1', RulesEvaluationConstants.MAX_KEY): 20
        }
        self.domain_states = [
            {
                '0': 0.0,
                '1': 15.0
            },
            {
                '0': 0.5,
                '1': 16.0
            }
        ]

        self.evaluation_data = {
            RulesEvaluationConstants.OBSERVATION_HISTORY_KEY: self.domain_states,
            RulesEvaluationConstants.STATE_MIN_MAXES_KEY: self.min_maxes
        }

    @patch("leaf_common.representation.rule_based.rule_evaluator.ConditionEvaluator.evaluate",
           return_value=Mock())
    def test_parse_conditions_true(self, evaluate_mock):
        """
        Verify rule parsing when conditions return True
        """
        rule = self._create_rule(True, True)

        evaluate_mock.side_effect = [ True, True ]

        evaluator = RuleEvaluator()
        result = evaluator.evaluate(rule, self.evaluation_data)

        self.assertEqual('1', result[0])
        self.assertEqual(0, result[1])

    @patch("leaf_common.representation.rule_based.rule_evaluator.ConditionEvaluator.evaluate",
           return_value=Mock())
    def test_parse_conditions_false(self, evaluate_mock):
        """
        Verify rule parsing when conditions return mixture of True and False
        """
        rule = self._create_rule(True, False)

        evaluate_mock.side_effect = [ True, False ]

        evaluator = RuleEvaluator()
        result = evaluator.evaluate(rule, self.evaluation_data)

        self.assertEqual(RulesEvaluationConstants.NO_ACTION, result[0])
        self.assertEqual(0, result[1])

    @staticmethod
    def _create_rule(first_condition_true, second_condition_true):

        mock_condition_1 = MagicMock()
        mock_condition_1.parse.return_value = first_condition_true
        mock_condition_1.action = 'action1'
        mock_condition_1.get_str.return_value = 'condition1_str'

        mock_condition_2 = MagicMock()
        mock_condition_2.parse.return_value = second_condition_true
        mock_condition_2.action = 'action2'
        mock_condition_2.get_str.return_value = 'condition2_str'

        rule = Rule(actions={'0': 'action1', '1': 'action2'})
        rule.action = '1'
        rule.action_lookback = 0
        rule.conditions.append(mock_condition_1)
        rule.conditions.append(mock_condition_2)

        return rule
