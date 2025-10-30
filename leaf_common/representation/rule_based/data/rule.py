
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
Base class for rule representation
"""

from typing import Dict
from typing import List
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants

from leaf_common.representation.rule_based.data.condition import Condition


class Rule:
    """
    Rule representation based class.
    """

    def __init__(self):

        # Evaluation Metrics used during reproduction
        self.times_applied = 0

        # Genetic Material
        self.action = None
        self.action_lookback = None
        self.action_coefficient: float = None
        self.conditions: List[Condition] = []

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__str__()

    # see https://github.com/PyCQA/pycodestyle/issues/753 for why next line needs noqa
    def to_string(self, states: Dict[str, str] = None,
                  min_maxes: Dict[str, Dict[str, float]] = None,
                  actions: Dict[str, str] = None) -> str:  # noqa: E252
        """
        String representation for rule
        :param states: An optional dictionary of state definitions seen during evaluation.
        :param actions: An optional dictionary of action definitions seen during evaluation.
        :param min_maxes: A dictionary of domain features minimum and maximum values
        :return: rule.toString()
        """
        action_name = str(self.action)
        if actions is not None and self.action in actions:
            action_name = actions[self.action]
        coefficient_part = f'{self.action_coefficient:.{RulesConstants.DECIMAL_DIGITS}f}*'
        if self.action_lookback > 0:
            the_action = " -->  Action[" + str(self.action_lookback) + "]"
        else:
            the_action = " -->  " + coefficient_part + action_name
        condition_string = ""
        for condition in self.conditions:
            condition_string = condition_string + "(" + \
                               condition.to_string(states=states, min_maxes=min_maxes) + ") "
        times_applied = "   < > "
        if self.times_applied > 0:
            times_applied = "  <" + str(self.times_applied) + "> "
        return times_applied + condition_string + the_action
