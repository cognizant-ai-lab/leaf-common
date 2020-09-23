"""
Base class for rule representation
"""

from typing import Dict
from typing import List
from typing import Tuple

from leaf_common.representation.rule_based.condition import Condition


class Rule:
    """
    Rule representation based class.
    """

    def __init__(self, actions: Dict[str, str]):

        # State/Config needed for evaluation
        # Note: Not actually used in evaluation at rule level
        #       Probably just here to pass a long to condition evaluation
        #       Perhaps better off coming from config
        self.actions = actions

        # Evaluation Metrics used during reproduction
        self.times_applied = 0

        # Genetic Material
        self.action = None
        self.action_lookback = None
        self.conditions: List[Condition] = []

    def __str__(self):
        return self.get_str()

    def __repr__(self):
        return self.__str__()

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
