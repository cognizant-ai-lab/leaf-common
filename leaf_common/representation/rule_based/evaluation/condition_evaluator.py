
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
Base class for condition representation
"""

from typing import Dict
from typing import List

from leaf_common.evaluation.component_evaluator import ComponentEvaluator
from leaf_common.representation.rule_based.data.condition import Condition
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants


class ConditionEvaluator(ComponentEvaluator):  # pylint: disable-msg=R0902
    """
    ComponentEvaluator implementation for Conditions

    The evaluate() method can be seen as a Pure Function, with no side effects
    on an instance of this class, and no side effects on any of the arguments.
    """

    def __init__(self, states: Dict[str, str]):
        self.states = states

    def evaluate(self, component: Condition,
                 evaluation_data: Dict[str, object]) -> bool:

        condition = component

        observation_history = evaluation_data[RulesConstants.OBSERVATION_HISTORY_KEY]
        min_maxes = evaluation_data.get(RulesConstants.STATE_MIN_MAXES_KEY)

        result = self.parse(condition, observation_history, min_maxes)
        return result

    def parse(self, condition: Condition, observation_history: List[Dict[str, float]],
              min_maxes: Dict[str, Dict[str, float]]) -> bool:
        """
        Parse a condition
        :param observation_history: list of domain states
        :param min_maxes: list of min and max values, one pair per state
        :return: A boolean indicating whether this condition is satisfied by the given domain states
        """
        nb_states = len(observation_history) - 1

        # If we don't have sufficient history for the requested lookback, just return False
        if nb_states < condition.first_state_lookback or nb_states < condition.second_state_lookback:
            return False

        domain_state_idx = nb_states - condition.first_state_lookback
        domain_state_value = observation_history[domain_state_idx][condition.first_state_key]
        operand_1 = condition.first_state_coefficient * (domain_state_value ** condition.first_state_exponent)
        operand_2 = self.get_second_state_value(condition, observation_history, nb_states, min_maxes)
        result = (
            (condition.operator == RulesConstants.GREATER_THAN_EQUAL and operand_1 >= operand_2) or
            (condition.operator == RulesConstants.LESS_THAN_EQUAL and operand_1 <= operand_2) or
            (condition.operator == RulesConstants.GREATER_THAN and operand_1 > operand_2) or
            (condition.operator == RulesConstants.LESS_THAN and operand_1 < operand_2)
        )
        return result

    def get_second_state_value(self, condition: Condition,
                               observation_history: List[Dict[str, float]],
                               nb_states: int,
                               min_maxes: Dict[str, Dict[str, float]]) -> float:
        """
        Get second state value
        :param observation_history: list of domain states
        :param nb_states: the number of domain states
        :param min_maxes: list of states min and max values
        :return: the second state
        """
        if condition.second_state_key in self.states.keys():
            second_state_idx = nb_states - condition.second_state_lookback
            second_state = observation_history[second_state_idx][condition.second_state_key]
            second_state = second_state ** condition.second_state_exponent
            second_state *= condition.second_state_coefficient
        else:
            empty_dict = {}
            state_dict = min_maxes.get(condition.first_state_key, empty_dict)
            the_min = state_dict.get(RulesConstants.MIN_KEY)
            the_max = state_dict.get(RulesConstants.MAX_KEY)
            the_range = the_max - the_min
            second_state = the_min + the_range * condition.second_state_value

        return second_state
