"""
Unit tests for `Condition` class
"""
from unittest import TestCase
from unittest.mock import patch

from leaf_common.rule_based.condition import Condition, THE_MIN, THE_MAX


class TestCondition(TestCase):
    """
    Unit tests for `Condition` class
    """
    @patch('leaf_common.rule_based.condition.random.randint', autospec=True)
    @patch('leaf_common.rule_based.condition.random.choice', autospec=True)
    def test_greater_true(self, mock_random_choice, mock_random_int):
        """
        Make sure '>' works when evaluation is true
        """
        condition = self._create_condition(mock_random_choice, mock_random_int, '>')
        result = condition.parse([{'0': 3, '1': 1}], {THE_MIN: 0, THE_MAX: 10})
        self.assertTrue(result)

    @patch('leaf_common.rule_based.condition.random.randint', autospec=True)
    @patch('leaf_common.rule_based.condition.random.choice', autospec=True)
    def test_greater_false(self, mock_random_choice, mock_random_int):
        """
        Make sure '>' works when evaluation is false
        """
        condition = self._create_condition(mock_random_choice, mock_random_int, '>')
        result = condition.parse([{'0': 3, '1': 4}], {THE_MIN: 0, THE_MAX: 10})
        self.assertFalse(result)

    @patch('leaf_common.rule_based.condition.random.randint', autospec=True)
    @patch('leaf_common.rule_based.condition.random.choice', autospec=True)
    def test_less_true(self, mock_random_choice, mock_random_int):
        """
        Make sure '<' works when evaluation is true
        """
        condition = self._create_condition(mock_random_choice, mock_random_int, '<')
        result = condition.parse([{'0': 1, '1': 2}], {THE_MIN: 0, THE_MAX: 10})
        self.assertTrue(result)

    @patch('leaf_common.rule_based.condition.random.randint', autospec=True)
    @patch('leaf_common.rule_based.condition.random.choice', autospec=True)
    def test_less_false(self, mock_random_choice, mock_random_int):
        """
        Make sure '<' works when evaluation is false
        """
        condition = self._create_condition(mock_random_choice, mock_random_int, '<')
        result = condition.parse([{'0': 3, '1': 1}], {THE_MIN: 0, THE_MAX: 10})
        self.assertFalse(result)

    @patch('leaf_common.rule_based.condition.random.randint', autospec=True)
    @patch('leaf_common.rule_based.condition.random.choice', autospec=True)
    def test_ge_true(self, mock_random_choice, mock_random_int):
        """
        Make sure '>=' works when evaluation is true
        """
        condition = self._create_condition(mock_random_choice, mock_random_int, '<')
        result = condition.parse([{'0': 3, '1': 1}], {THE_MIN: 0, THE_MAX: 10})
        self.assertFalse(result)

    @patch('leaf_common.rule_based.condition.random.randint', autospec=True)
    @patch('leaf_common.rule_based.condition.random.choice', autospec=True)
    def test_ge_equality(self, mock_random_choice, mock_random_int):
        """
        Make sure '>=' works when evaluation is true and values are equal (edge case)
        """
        condition = self._create_condition(mock_random_choice, mock_random_int, '<')
        result = condition.parse([{'0': 2, '1': 1}], {THE_MIN: 0, THE_MAX: 10})
        self.assertFalse(result)

    @patch('leaf_common.rule_based.condition.random.randint', autospec=True)
    @patch('leaf_common.rule_based.condition.random.choice', autospec=True)
    def test_le_true(self, mock_random_choice, mock_random_int):
        """
        Make sure '<=' works when evaluation is true
        """
        condition = self._create_condition(mock_random_choice, mock_random_int, '<=')
        result = condition.parse([{'0': 1, '1': 2}], {THE_MIN: 0, THE_MAX: 10})
        self.assertTrue(result)

    @patch('leaf_common.rule_based.condition.random.randint', autospec=True)
    @patch('leaf_common.rule_based.condition.random.choice', autospec=True)
    def test_le_false(self, mock_random_choice, mock_random_int):
        """
        Make sure '<=' works when evaluation is false
        """
        condition = self._create_condition(mock_random_choice, mock_random_int, '<=')
        result = condition.parse([{'0': 3, '1': 1}], {THE_MIN: 0, THE_MAX: 10})
        self.assertFalse(result)

    @patch('leaf_common.rule_based.condition.random.randint', autospec=True)
    @patch('leaf_common.rule_based.condition.random.choice', autospec=True)
    def test_to_string(self, mock_random_choice, mock_random_int):
        """
        Verify behavior of `get_str()` method
        """

        # With lookbacks
        condition = self._create_condition(mock_random_choice, mock_random_int, '<=', 1, 2)
        condition_string = condition.get_str()
        self.assertEqual('0.42*S_0[1] <= 0.84*S_1[2]', condition_string)

        # Different operator, no lookbacks
        condition = self._create_condition(mock_random_choice, mock_random_int, '>')
        condition_string = condition.get_str()
        self.assertEqual('0.42*S_0 > 0.84*S_1', condition_string)

    @staticmethod
    def _create_condition(mock_random_choice, mock_random_int, condition_type, lookback1=0, lookback2=0):
        # We simulate two states, keys '0' and '1'
        states = {'0': 'S_0', '1': 'S_1'}

        # Set up canned random numbers to express: 0.42*S_0 <condition> 0.69*S_1
        mock_random_choice.side_effect = [list(states)[0], condition_type, list(states)[1]]
        mock_random_int.side_effect = [
            lookback1,  # first_state_lookback
            42,         # first_state_coefficient
            lookback2,  # second_state_lookback
            32,         # second_state_value
            84          # second_state_coefficient
        ]
        condition = Condition(states, max_lookback=5)
        return condition
