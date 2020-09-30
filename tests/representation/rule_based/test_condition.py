"""
Unit tests for `Condition` class
"""
from unittest import TestCase

from leaf_common.representation.rule_based.condition import Condition
from leaf_common.representation.rule_based.condition_evaluator import ConditionEvaluator
from leaf_common.representation.rule_based.rules_evaluation_constants \
    import RulesEvaluationConstants


class TestCondition(TestCase):
    """
    Unit tests for `Condition` class
    """

    def __init__(self, *args, **kwargs):
        super(TestCondition, self).__init__(*args, **kwargs)
        self.min_max = {
            RulesEvaluationConstants.MIN_KEY: 0,
            RulesEvaluationConstants.MAX_KEY: 10
        }
        self.evaluation_data = {
            RulesEvaluationConstants.STATE_MIN_MAXES_KEY: self.min_max
        }
        self.evaluator = ConditionEvaluator()

    def test_greater_true(self):
        """
        Make sure '>' works when evaluation is true
        """
        condition = self._create_condition('>')

        self.evaluation_data[RulesEvaluationConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 3, '1': 1}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertTrue(result)

    def test_greater_false(self):
        """
        Make sure '>' works when evaluation is false
        """
        condition = self._create_condition('>')

        self.evaluation_data[RulesEvaluationConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 3, '1': 4}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertFalse(result)

    def test_less_true(self):
        """
        Make sure '<' works when evaluation is true
        """
        condition = self._create_condition('<')

        self.evaluation_data[RulesEvaluationConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 1, '1': 2}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertTrue(result)

    def test_less_false(self):
        """
        Make sure '<' works when evaluation is false
        """
        condition = self._create_condition('<')

        self.evaluation_data[RulesEvaluationConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 3, '1': 1}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertFalse(result)

    def test_ge_true(self):
        """
        Make sure '>=' works when evaluation is true
        """
        condition = self._create_condition('<')

        self.evaluation_data[RulesEvaluationConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 3, '1': 1}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertFalse(result)

    def test_ge_equality(self):
        """
        Make sure '>=' works when evaluation is true and values are equal (edge case)
        """
        condition = self._create_condition('<')

        self.evaluation_data[RulesEvaluationConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 2, '1': 1}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertFalse(result)

    def test_le_true(self):
        """
        Make sure '<=' works when evaluation is true
        """
        condition = self._create_condition('<=')

        self.evaluation_data[RulesEvaluationConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 1, '1': 2}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertTrue(result)

    def test_le_false(self):
        """
        Make sure '<=' works when evaluation is false
        """
        condition = self._create_condition('<=')

        self.evaluation_data[RulesEvaluationConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 3, '1': 1}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertFalse(result)

    def test_to_string(self):
        """
        Verify behavior of `get_str()` method
        """

        # With lookbacks
        condition = self._create_condition('<=', 1, 2)
        condition_string = condition.get_str()
        self.assertEqual('0.42*S_0[1] <= 0.84*S_1[2]', condition_string)

        # Different operator, no lookbacks
        condition = self._create_condition('>')
        condition_string = condition.get_str()
        self.assertEqual('0.42*S_0 > 0.84*S_1', condition_string)

    @staticmethod
    def _create_condition(condition_type, lookback1=0, lookback2=0):
        # We simulate two states, keys '0' and '1'
        states = {'0': 'S_0', '1': 'S_1'}

        # Set up canned random numbers to express: 0.42*S_0 <condition> 0.69*S_1
        condition = Condition(states)
        condition.first_state_lookback = lookback1
        condition.first_state_key = list(states)[0]
        condition.first_state_coefficient = 0.42
        condition.operator = condition_type
        condition.second_state_lookback = lookback2
        condition.second_state_key = list(states)[1]
        condition.second_state_value = 0.32
        condition.second_state_coefficient = 0.84
        return condition
