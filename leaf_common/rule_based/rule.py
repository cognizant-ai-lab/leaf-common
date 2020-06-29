"""
Base class for rule representation
"""

from typing import Dict
from typing import List
from typing import Tuple

from leaf_common.rule_based.condition import Condition

RULE_ELEMENTS = ["condition", "action", "action_lookback"]
THE_LOOKBACK = 1
LOOK_BACK = "lb"
THE_ACTION = 0
NO_ACTION = -1


class Rule:
    """
    Rule representation based class.
    """

    def __init__(self, states: Dict[str, str], actions: Dict[str, str], max_lookback: int):
        self.max_lookback = max_lookback
        self.actions = actions
        self.action = None
        self.action_lookback = None
        self.times_applied = 0
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
                return [NO_ACTION, 0]
        nb_states = len(domain_states) - 1

        # If the lookback is greater than the number of states we have, we can't evaluate the condition so
        # default to NO_ACTION
        if nb_states < self.action_lookback:
            return [NO_ACTION, 0]
        self.times_applied += 1
        if self.action_lookback == 0:
            return [self.action, 0]
        return [LOOK_BACK, self.action_lookback]

    def copy(self, states, actions):
        """
        Copy a rule
        :param states: A dictionary of domain inputs
        :param actions: A dictionary of domain actions
        :return: the copied rule
        """
        rule = Rule(states, actions, self.max_lookback)
        rule.conditions = []
        for condition in self.conditions:
            rule.add_condition(condition.copy(states))
        rule.action = self.action
        rule.action_lookback = self.action_lookback
        return rule

    def add_condition(self, condition: Condition):
        """
        Add a condition to the rule in ascending order if not already exists
        :param condition: A condition
        :return: True if successful
        """
        if self.contains(condition):
            return False
        str_new_condition = condition.get_str()
        insertion_index = 0
        for i in range(len(self.conditions)):
            str_condition = self.conditions[i].get_str()
            if str_new_condition < str_condition:
                insertion_index += 1
            else:
                self.conditions.insert(insertion_index, condition)
                return True
        self.conditions.append(condition)
        return True

    def contains(self, condition):
        """
        Check if a condition is not already exist in the rule
        :param condition: A condition
        :return: True if exists, False otherwise
        """
        str_condition = "(" + condition.get_str(None) + ")"
        str_rule = self.get_str()
        return str_condition in str_rule
