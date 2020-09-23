"""
Base class for condition representation
"""

from typing import Dict
from typing import List
from typing import Tuple

from leaf_common.evaluation.component_evaluator import ComponentEvaluator
from leaf_common.representation.rule_based.condition import Condition
from leaf_common.representation.rule_based.rules_evaluation_constants \
    import RulesEvaluationConstants


class ConditionEvaluator(ComponentEvaluator):  # pylint: disable-msg=R0902
    """
    ComponentEvaluator implementation for Conditions

    The evaluate() method can be seen as a Pure Function, with no side effects
    on an instance of this class, and no side effects on any of the arguments.
    """

    def evaluate(self, component: Condition,
                 evaluation_data: Dict[str, object] = None) -> bool:

        condition = component

        observation_history = evaluation_data[RulesEvaluationConstants.OBSERVATION_HISTORY_KEY]
        min_maxes = evaluation_data[RulesEvaluationConstants.STATE_MIN_MAXES_KEY]

        result = self.parse(condition, observation_history, min_maxes)
        return result

    def parse(self, condition: Condition, observation_history: List[Dict[str, float]],
              min_maxes: Dict[Tuple[str, str], float]) -> bool:
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
        operand_1 = domain_state_value * condition.first_state_coefficient
        operand_2 = self.get_second_state_value(condition, observation_history, nb_states, min_maxes)
        result = (
            (condition.operator == RulesEvaluationConstants.GREATER_THAN_EQUAL and operand_1 >= operand_2) or
            (condition.operator == RulesEvaluationConstants.LESS_THAN_EQUAL and operand_1 <= operand_2) or
            (condition.operator == RulesEvaluationConstants.GREATER_THAN and operand_1 > operand_2) or
            (condition.operator == RulesEvaluationConstants.LESS_THAN and operand_1 < operand_2)
        )
        return result

    def get_second_state_value(self, condition: Condition,
                               observation_history: List[Dict[str, float]],
                               nb_states: int,
                               min_maxes: Dict[Tuple[str, str], float]) -> float:
        """
        Get second state value
        :param observation_history: list of domain states
        :param nb_states: the number of domain states
        :param min_maxes: list of states min and max values
        :return: the second state
        """
        if condition.second_state_key in condition.states.keys():
            second_state_idx = nb_states - condition.second_state_lookback
            second_state = observation_history[second_state_idx][condition.second_state_key]
            second_state *= condition.second_state_coefficient
        else:
            the_min = min_maxes[condition.first_state_key, RulesEvaluationConstants.MIN_KEY]
            the_max = min_maxes[condition.first_state_key, RulesEvaluationConstants.MAX_KEY]
            the_range = the_max - the_min
            second_state = the_min + the_range * condition.second_state_value

        return second_state
