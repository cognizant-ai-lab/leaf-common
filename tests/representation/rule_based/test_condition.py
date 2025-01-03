
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
Unit tests for `Condition` class
"""
from unittest import TestCase

from leaf_common.representation.rule_based.data.condition import Condition
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants

from leaf_common.representation.rule_based.evaluation.condition_evaluator \
    import ConditionEvaluator


class TestCondition(TestCase):
    """
    Unit tests for `Condition` class
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_max = {
            RulesConstants.MIN_KEY: 0,
            RulesConstants.MAX_KEY: 10
        }
        self.evaluation_data = {
            RulesConstants.STATE_MIN_MAXES_KEY: self.min_max
        }

        # We simulate two states, keys '0' and '1'
        self.states = {'0': 'S_0', '1': 'S_1'}
        self.evaluator = ConditionEvaluator(self.states)

    def test_greater_true(self):
        """
        Make sure '>' works when evaluation is true
        """
        condition = self._create_condition('>')

        self.evaluation_data[RulesConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 3, '1': 1}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertTrue(result)

    def test_greater_false(self):
        """
        Make sure '>' works when evaluation is false
        """
        condition = self._create_condition('>')

        self.evaluation_data[RulesConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 3, '1': 4}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertFalse(result)

    def test_less_true(self):
        """
        Make sure '<' works when evaluation is true
        """
        condition = self._create_condition('<')

        self.evaluation_data[RulesConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 1, '1': 2}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertTrue(result)

    def test_less_false(self):
        """
        Make sure '<' works when evaluation is false
        """
        condition = self._create_condition('<')

        self.evaluation_data[RulesConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 3, '1': 1}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertFalse(result)

    def test_ge_true(self):
        """
        Make sure '>=' works when evaluation is true
        """
        condition = self._create_condition('<')

        self.evaluation_data[RulesConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 3, '1': 1}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertFalse(result)

    def test_ge_equality(self):
        """
        Make sure '>=' works when evaluation is true and values are equal (edge case)
        """
        condition = self._create_condition('<')

        self.evaluation_data[RulesConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 2, '1': 1}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)

        self.assertFalse(result)

    def test_le_true(self):
        """
        Make sure '<=' works when evaluation is true
        """
        condition = self._create_condition('<=')

        self.evaluation_data[RulesConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 1, '1': 2}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)
        self.assertTrue(result)

        # Make it false with exponent
        condition.second_state_exponent = 2
        condition.second_state_coefficient = 0.1
        result = self.evaluator.evaluate(condition, self.evaluation_data)
        self.assertFalse(result)

        # Make it true with exponent
        condition.second_state_coefficient = 0.12
        result = self.evaluator.evaluate(condition, self.evaluation_data)
        self.assertTrue(result)

    def test_le_false(self):
        """
        Make sure '<=' works when evaluation is false
        """
        condition = self._create_condition('<=')

        self.evaluation_data[RulesConstants.OBSERVATION_HISTORY_KEY] = \
            [{'0': 3, '1': 1}]
        result = self.evaluator.evaluate(condition, self.evaluation_data)
        self.assertFalse(result)

        # Make it false with exponent
        condition.first_state_exponent = 3
        condition.first_state_coefficient = 0.1
        result = self.evaluator.evaluate(condition, self.evaluation_data)
        self.assertFalse(result)

        # Make it true with exponent
        condition.first_state_coefficient = 0.03
        result = self.evaluator.evaluate(condition, self.evaluation_data)
        self.assertTrue(result)

    def test_to_string(self):
        """
        Verify behavior of `to_string()` method
        """

        # With lookbacks
        condition = self._create_condition('<=', 1, 2)
        condition_string = condition.to_string(states=self.states)
        self.assertEqual('0.42*S_0[1] <= 0.84*S_1[2]', condition_string)

        # With exponent on the left side
        condition.first_state_exponent = 2
        condition_string = condition.to_string(states=self.states)
        self.assertEqual('0.42*S_0[1]^2 <= 0.84*S_1[2]', condition_string)

        # Different operator, no lookbacks
        condition = self._create_condition('>')
        condition_string = condition.to_string(states=self.states)
        self.assertEqual('0.42*S_0 > 0.84*S_1', condition_string)

        # With exponent on the right side
        condition.second_state_exponent = 3
        condition_string = condition.to_string(states=self.states)
        self.assertEqual('0.42*S_0 > 0.84*S_1^3', condition_string)

    def _create_condition(self, condition_type, lookback1=0, lookback2=0):

        # Set up canned random numbers to express: 0.42*S_0 <condition> 0.69*S_1
        condition = Condition()
        condition.first_state_lookback = lookback1
        condition.first_state_key = list(self.states)[0]
        condition.first_state_coefficient = 0.42
        condition.first_state_exponent = 1
        condition.operator = condition_type
        condition.second_state_lookback = lookback2
        condition.second_state_key = list(self.states)[1]
        condition.second_state_value = 0.32
        condition.second_state_coefficient = 0.84
        condition.second_state_exponent = 1
        return condition
