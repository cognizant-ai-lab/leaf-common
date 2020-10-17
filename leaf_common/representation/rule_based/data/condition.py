"""
Base class for condition representation
"""

from typing import Dict
from typing import Tuple

from leaf_common.representation.rule_based.data.rules_constants import RulesConstants


class Condition:  # pylint: disable-msg=R0902
    """
    A class that encapsulates a binary condition with two operands (self.first_state and self.second_state)
    The operands used by the condition are randomly chosen at construction time from the list of states supplied
    from the Domain.
    An operator is randomly chosen from the `OPERATORS` list.
    """

    def __init__(self):

        # Genetic Material fields
        self.first_state_lookback: int = None
        self.first_state_key: str = None
        self.first_state_coefficient: float = None
        self.first_state_exponent = None
        self.operator: str = None
        self.second_state_lookback: int = None
        self.second_state_key: str = None
        self.second_state_value: float = None
        self.second_state_coefficient: float = None
        self.second_state_exponent = None

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__str__()

    # see https://github.com/PyCQA/pycodestyle/issues/753 for why next line needs noqa
    def to_string(self, states: Dict[str, str] = None,
                  min_maxes: Dict[Tuple[str, str], float] = None) -> str:  # noqa: E252
        """
        String representation for condition
        :param states: A dictionary of domain features
        :param min_maxes: A dictionary of domain features minimum and maximum values
        :return: condition.toString()
        """

        # Prepare 1st condition string
        first_condition = self._condition_part_to_string(self.first_state_coefficient,
                                                         self.first_state_key,
                                                         self.first_state_lookback,
                                                         self.first_state_exponent,
                                                         states)

        # Prepare 2nd condition string
        # Note: None or empty dictionaries both evaluate to false
        if states and self.second_state_key in states:
            second_condition = self._condition_part_to_string(self.second_state_coefficient,
                                                              self.second_state_key,
                                                              self.second_state_lookback,
                                                              self.second_state_exponent,
                                                              states)
        # Note: None or empty dictionaries both evaluate to false
        elif min_maxes:
            # Per evaluation code, min/max is based on the first_state_key
            min_value = min_maxes[self.first_state_key, RulesConstants.MIN_KEY]
            max_value = min_maxes[self.first_state_key, RulesConstants.MAX_KEY]
            second_condition_val = (min_value + self.second_state_value * (max_value - min_value))
            second_condition = \
                f'{second_condition_val:.{RulesConstants.DECIMAL_DIGITS}f} {{{min_value}..{max_value}}}'
        else:
            second_condition = f'{self.second_state_value:.{RulesConstants.DECIMAL_DIGITS}f}'

        return f'{first_condition} {self.operator} {second_condition}'

    # pylint: disable=no-self-use
    def _condition_part_to_string(self, coeff: float, key: str, lookback: int, exponent: int,
                                  states: Dict[str, str]) -> str:
        """
        Given features of a side of a condition inequality,
        return a string that describes the side, at least in a default capacity.
        (right side -- 2nd condition is not fully realized here in case of min/maxes)
        """
        del self
        use_key = key
        if states is not None and key in states:
            use_key = states[key]

        condition_part = f'{coeff:.{RulesConstants.DECIMAL_DIGITS}f}*{use_key}'
        if lookback > 0:
            condition_part = f'{condition_part}[{lookback}]'
        if exponent > 1:
            condition_part = f'{condition_part}^{exponent}'

        return condition_part
