
# Copyright © 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# END COPYRIGHT
"""
Unit tests for Rules class
"""
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from leaf_common.representation.rule_based.data.rule import Rule
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants

from leaf_common.representation.rule_based.evaluation.rule_evaluator import RuleEvaluator


class TestRule(TestCase):
    """
    Unit tests for Rules class
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_maxes = {
            '0': {
                RulesConstants.MIN_KEY: 0,
                RulesConstants.MAX_KEY: 10
            },
            '1': {
                RulesConstants.MIN_KEY: 10,
                RulesConstants.MAX_KEY: 20
            }
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
            RulesConstants.OBSERVATION_HISTORY_KEY: self.domain_states,
            RulesConstants.STATE_MIN_MAXES_KEY: self.min_maxes
        }

    @patch("leaf_common.representation.rule_based.evaluation.rule_evaluator.ConditionEvaluator.evaluate",
           return_value=Mock())
    def test_parse_conditions_true(self, evaluate_mock):
        """
        Verify rule parsing when conditions return True
        """
        rule = self._create_rule(True, True)

        evaluate_mock.side_effect = [True, True]

        evaluator = RuleEvaluator(None)
        result = evaluator.evaluate(rule, self.evaluation_data)

        self.assertEqual('1', result[RulesConstants.ACTION_KEY])
        self.assertEqual(0, result[RulesConstants.LOOKBACK_KEY])

    @patch("leaf_common.representation.rule_based.evaluation.rule_evaluator.ConditionEvaluator.evaluate",
           return_value=Mock())
    def test_parse_conditions_false(self, evaluate_mock):
        """
        Verify rule parsing when conditions return mixture of True and False
        """
        rule = self._create_rule(True, False)

        evaluate_mock.side_effect = [True, False]

        evaluator = RuleEvaluator(None)
        result = evaluator.evaluate(rule, self.evaluation_data)

        self.assertEqual(RulesConstants.NO_ACTION, result[RulesConstants.ACTION_KEY])
        self.assertEqual(0, result[RulesConstants.LOOKBACK_KEY])

    @staticmethod
    def _create_rule(first_condition_true, second_condition_true):

        mock_condition_1 = MagicMock()
        mock_condition_1.parse.return_value = first_condition_true
        mock_condition_1.action = 'action1'
        mock_condition_1.to_string.return_value = 'condition1_str'

        mock_condition_2 = MagicMock()
        mock_condition_2.parse.return_value = second_condition_true
        mock_condition_2.action = 'action2'
        mock_condition_2.to_string.return_value = 'condition2_str'

        rule = Rule()
        rule.action = '1'
        rule.action_lookback = 0
        rule.conditions.append(mock_condition_1)
        rule.conditions.append(mock_condition_2)

        return rule
