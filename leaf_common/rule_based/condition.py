"""
Base class for condition representation
"""
import random
from typing import Dict, List

import math

OPERATORS = [">=", "<=", ">", "<"]
CONDITION_ELEMENTS = [
    "first_state", "first_state_coefficient", "first_state_exponent", "first_state_lookback", "operator",
    "second_state", "second_state_coefficient", "second_state_exponent", "second_state_lookback", "second_state_value"
]
THE_VALUE = "value"
THE_ACTION = 0
THE_MIN = "min"
THE_MAX = "max"
THE_TOTAL = "total"
GRANULARITY = 100
DECIMAL_DIGITS = int(math.log10(GRANULARITY))
FLOAT_FORMAT = "." + str(DECIMAL_DIGITS) + "f"
MAX_EXPONENT = 3


class Condition:  # pylint: disable-msg=R0902
    """
    A class that encapsulates a binary condition with two operands (self.first_state and self.second_state)
    The operands used by the condition are randomly chosen at construction time from the list of states supplied
    from the Domain.
    An operator is randomly chosen from the `OPERATORS` list.
    """

    def __init__(self, states: Dict[str, str], max_lookback: int):
        self.states = states
        self.max_lookback = max_lookback
        self.first_state_lookback = random.randint(0, self.max_lookback)
        self.first_state: str = random.choice(list(states.keys()))
        self.first_state_coefficient = random.randint(0, GRANULARITY) / GRANULARITY
        self.first_state_exponent = 1
        self.operator = random.choice(OPERATORS)
        self.second_state_lookback = random.randint(0, self.max_lookback)
        choices = list(states.keys()) + [THE_VALUE]
        if self.first_state_lookback == self.second_state_lookback:
            choices.remove(self.first_state)
        self.second_state = random.choice(choices)
        self.second_state_value = random.randint(0, GRANULARITY) / GRANULARITY
        self.second_state_coefficient = random.randint(0, GRANULARITY) / GRANULARITY
        self.second_state_exponent = 1

    def __str__(self):
        return self.get_str()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def get_str(self, min_maxes: Dict[(str, str)]=None) -> str:
        """
        String representation for condition
        :param min_maxes: A dictionary of domain features minimum and maximum values
        :return: condition.toString()
        """
        first_condition = format(self.first_state_coefficient, FLOAT_FORMAT) + '*' + str(self.states[self.first_state])
        if self.first_state_lookback > 0:
            first_condition = first_condition + "[" + str(self.first_state_lookback) + "]"
        if self.first_state_exponent > 1:
            first_condition = first_condition + '^' + str(self.first_state_exponent)
        if self.second_state in self.states:
            second_condition = format(self.second_state_coefficient, FLOAT_FORMAT) + \
                               '*' + self.states[self.second_state]
            if self.second_state_lookback > 0:
                second_condition = second_condition + "[" + str(self.second_state_lookback) + "]"
            if self.second_state_exponent > 1:
                second_condition = second_condition + '^' + str(self.second_state_exponent)
        elif min_maxes:
            min_value = min_maxes[self.first_state, THE_MIN]
            max_value = min_maxes[self.first_state, THE_MAX]
            second_condition = format((min_value + self.second_state_value * (max_value - min_value)), FLOAT_FORMAT)
            second_condition = second_condition + " {" + str(min_value) + ".." + str(max_value) + "}"
        else:
            second_condition = format(self.second_state_value, FLOAT_FORMAT)

        return first_condition + " " + self.operator + " " + second_condition

    def get_second_state_value(self, domain_states: List[Dict[str, float]], nb_states: int,
                               min_maxes: Dict[(str, str)]) -> float:
        """
        Get second state value
        :param domain_states: list of domain states
        :param nb_states: the number of domain states
        :param min_maxes: list of states min and max values
        :return: the second state
        """
        if self.second_state in self.states.keys():
            second_state_idx = nb_states - self.second_state_lookback
            second_state = domain_states[second_state_idx][self.second_state]
            second_state = (second_state ** self.second_state_exponent) * self.second_state_coefficient
        else:
            the_min = min_maxes[self.first_state, THE_MIN]
            the_max = min_maxes[self.first_state, THE_MAX]
            the_range = the_max - the_min
            second_state = the_min + the_range * self.second_state_value

        return second_state

    def parse(self, domain_states: List[Dict[str, float]], min_maxes: Dict[(str, str)]) -> bool:
        """
        Parse a condition
        :param domain_states: list of domain states
        :param min_maxes: list of min and max values, one pair per state
        :return: A boolean indicating whether this condition is satisfied by the given domain states
        """
        nb_states = len(domain_states) - 1
        if nb_states < self.first_state_lookback or nb_states < self.second_state_lookback:
            return False
        domain_state_idx = nb_states - self.first_state_lookback
        domain_state_value = domain_states[domain_state_idx][self.first_state]
        operand_1 = (domain_state_value ** self.first_state_exponent) * self.first_state_coefficient
        operand_2 = self.get_second_state_value(domain_states, nb_states, min_maxes)
        condition = (
            (self.operator == ">=" and operand_1 >= operand_2) or
            (self.operator == "<=" and operand_1 <= operand_2) or
            (self.operator == ">" and operand_1 > operand_2) or
            (self.operator == "<" and operand_1 < operand_2)
        )
        return condition

    def copy(self, states):
        """
        Copy a condition
        :param states: A dictionary of domain inputs
        :return: the copied condition
        """
        condition = Condition(states, self.max_lookback)
        condition.first_state = self.first_state
        condition.first_state_coefficient = self.first_state_coefficient
        condition.first_state_exponent = self.first_state_exponent
        condition.first_state_lookback = self.first_state_lookback
        condition.operator = self.operator
        condition.second_state = self.second_state
        condition.second_state_coefficient = self.second_state_coefficient
        condition.second_state_exponent = self.second_state_exponent
        condition.second_state_lookback = self.second_state_lookback
        condition.second_state_value = self.second_state_value
        return condition
