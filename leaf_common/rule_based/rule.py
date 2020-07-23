"""
Base class for rule representation
"""

from typing import Dict
from typing import List
from typing import Tuple

from leaf_common.rule_based.condition import Condition
from leaf_common.rule_based.rules_evaluation_constants \
    import RulesEvaluationConstants


class Rule:
    """
    Rule representation based class.
    """

    def __init__(self, actions: Dict[str, str]):

        # State/Config needed for evaluation
        self.actions = actions
        self.times_applied = 0

        # Genetic Material
        self.action = None
        self.action_lookback = None
        self.conditions: List[Condition] = []

    def __str__(self):
        return self.get_str()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    # see https://github.com/PyCQA/pycodestyle/issues/753 for why next line needs noqa
    def get_str(self, min_maxes: Dict[Tuple[str, str], float] = None) -> str:  # noqa: E252
        """
        String representation for rule
        :param min_maxes: A dictionary of domain features minimum and maximum values
        :return: rule.toString()
        """
        if self.action_lookback > 0:
            the_action = " -->  Action[" + str(self.action_lookback) + "]"
        else:
            the_action = " -->  " + self.action
        condition_string = ""
        for condition in self.conditions:
            condition_string = condition_string + "(" + condition.get_str(min_maxes) + ") "
        times_applied = "   < > "
        if self.times_applied > 0:
            times_applied = "  <" + str(self.times_applied) + "> "
        return times_applied + condition_string + the_action

    def parse(self, domain_states: List[Dict[str, float]], min_maxes: Dict[Tuple[str, str], float]) -> List[object]:
        """
        Parse a rule
        :param domain_states: list of domain states
        :param min_maxes: list of states min and max values
        :return: A list containing an action indicator, and a lookback value or 0 for no lookback
        """

        for condition in self.conditions:
            if not condition.parse(domain_states, min_maxes):
                return [RulesEvaluationConstants.NO_ACTION, 0]
        nb_states = len(domain_states) - 1

        # If the lookback is greater than the number of states we have, we can't evaluate the condition so
        # default to RulesEvaluationConstants.NO_ACTION
        if nb_states < self.action_lookback:
            return [RulesEvaluationConstants.NO_ACTION, 0]
        self.times_applied += 1
        if self.action_lookback == 0:
            return [self.action, 0]
        return [RulesEvaluationConstants.LOOK_BACK, self.action_lookback]
