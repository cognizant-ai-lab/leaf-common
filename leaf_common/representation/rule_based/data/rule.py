
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
