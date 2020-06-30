"""
Unit tests for Rules class
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock

from leaf_common.rule_based.condition import THE_MIN, THE_MAX
from leaf_common.rule_based.rule import Rule, NO_ACTION

MIN_MAXES = {('0', THE_MIN): 0, ('0', THE_MAX): 10, ('1', THE_MIN): 10, ('1', THE_MAX): 20}
DOMAIN_STATES = [{'0': 0.0, '1': 15.0}, {'0': 0.5, '1': 16.0}]


class TestRule(TestCase):
    """
    Unit tests for Rules class
    """

    def test_parse_conditions_true(self):
        """
        Verify rule parsing when conditions return True
        """
        rule = self._create_rule(True, True)
        result = rule.parse([{'0': 0.0, '1': 15.0}, {'0': 0.5, '1': 16.0}],
                            {('0', THE_MIN): 0, ('0', THE_MAX): 10, ('1', THE_MIN): 10, ('1', THE_MAX): 20})

        self.assertEqual('1', result[0])
        self.assertEqual(0, result[1])

    def test_parse_conditions_false(self):
        """
        Verify rule parsing when conditions return mixture of True and False
        """
        rule = self._create_rule(True, False)
        result = rule.parse(DOMAIN_STATES, MIN_MAXES)

        self.assertEqual(NO_ACTION, result[0])
        self.assertEqual(0, result[1])

    @staticmethod
    def _create_rule(first_condition_true, second_condition_true):
        with patch('leaf_common.rule_based.rule.Condition', autospec=True) as mock_condition:
            mock_condition_1 = MagicMock()
            mock_condition_1.parse.return_value = first_condition_true
            mock_condition_1.action = 'action1'
            mock_condition_1.get_str.return_value = 'condition1_str'
            mock_condition_2 = MagicMock()
            mock_condition_2.parse.return_value = second_condition_true
            mock_condition_2.action = 'action2'
            mock_condition_2.get_str.return_value = 'condition2_str'

            rule = Rule(actions={'0': 'action1', '1': 'action2'}, max_lookback=0)
            rule.action = '1'
            rule.action_lookback = 0
            rule.add_condition(mock_condition_1)
            rule.add_condition(mock_condition_2)

            return rule
