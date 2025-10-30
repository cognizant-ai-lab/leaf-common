
# Copyright 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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
Base class for rule representation
"""

from typing import Dict

from leaf_common.evaluation.component_evaluator import ComponentEvaluator
from leaf_common.representation.rule_based.data.rule import Rule
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants
from leaf_common.representation.rule_based.evaluation.condition_evaluator \
    import ConditionEvaluator


class RuleEvaluator(ComponentEvaluator):
    """
    ComponentEvaluator implementation for the Rule class

    Upon exit from evaluate() the following fields in Rule might be modified:
        * times_applied
    """

    def __init__(self, states: Dict[str, str]):
        # The ConditionEvaluator itself is stateless, so it's OK to just create
        # one here as an optimization
        self.condition_evaluator = ConditionEvaluator(states)

    def evaluate(self, component: Rule,
                 evaluation_data: Dict[str, object]) -> Dict[str, object]:
        """
        :return: A list containing an action indicator, an action coefficient,
                    and a lookback value or 0 for no lookback
        """

        rule = component

        for condition in rule.conditions:
            condition_result = self.condition_evaluator.evaluate(condition, evaluation_data)
            if not condition_result:
                return {RulesConstants.ACTION_KEY: RulesConstants.NO_ACTION,
                        RulesConstants.ACTION_COEFFICIENT_KEY: rule.action_coefficient,
                        RulesConstants.LOOKBACK_KEY: 0}

        observation_history = evaluation_data[RulesConstants.OBSERVATION_HISTORY_KEY]
        nb_states = len(observation_history) - 1

        # If the lookback is greater than the number of states we have, we can't evaluate the condition so
        # default to RulesConstants.NO_ACTION
        if nb_states < rule.action_lookback:
            return {RulesConstants.ACTION_KEY: RulesConstants.NO_ACTION,
                    RulesConstants.ACTION_COEFFICIENT_KEY: rule.action_coefficient,
                    RulesConstants.LOOKBACK_KEY: 0}

        rule.times_applied += 1
        if rule.action_lookback == 0:
            return {RulesConstants.ACTION_KEY: rule.action,
                    RulesConstants.ACTION_COEFFICIENT_KEY: rule.action_coefficient,
                    RulesConstants.LOOKBACK_KEY: 0}

        return {RulesConstants.ACTION_KEY: RulesConstants.LOOKBACK_ACTION,
                RulesConstants.ACTION_COEFFICIENT_KEY: rule.action_coefficient,
                RulesConstants.LOOKBACK_KEY: rule.action_lookback}
