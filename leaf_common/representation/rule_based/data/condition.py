
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

from leaf_common.representation.rule_based.data.rules_constants import RulesConstants
from leaf_common.representation.rule_based.data.features import Features


class Condition:  # pylint: disable=too-many-instance-attributes
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
        self.first_state_exponent: int = None
        self.operator: str = None
        self.second_state_lookback: int = None
        self.second_state_key: str = None
        self.second_state_value: float = None
        self.second_state_coefficient: float = None
        self.second_state_exponent: int = None

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__str__()

    # see https://github.com/PyCQA/pycodestyle/issues/753 for why next line needs noqa
    def to_string(self, states: Dict[str, str] = None,
                  min_maxes: Dict[str, Dict[str, float]] = None) -> str:  # noqa: E252
        """
        FOR EXAMPLE:(for categorical)
        'race_is_category_Hispanic' becomes 'race is Hispanic'

        String representation for condition
        :param states: A dictionary of domain features
        :param min_maxes: A dictionary of domain features minimum and maximum values
        :return: condition.toString()
        """

        # Handle categorical conditions separately
        if states and Features.is_categorical(states[self.first_state_key]):
            the_string = self.categorical_to_string(states)
        else:
            the_string = self.continuous_to_string(min_maxes, states)

        return the_string

    def continuous_to_string(self, min_maxes: Dict[str, Dict[str, float]],
                             states: Dict[str, str]) -> str:
        """
        String representation for continuous condition
        :param min_maxes: A dictionary of domain features minimum and maximum values
        :param states: A dictionary of domain features
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
            empty_dict = {}
            state_dict = min_maxes.get(self.first_state_key, empty_dict)
            min_value = state_dict.get(RulesConstants.MIN_KEY)
            max_value = state_dict.get(RulesConstants.MAX_KEY)
            second_condition_val = min_value + self.second_state_value * (max_value - min_value)
            second_condition = \
                f'{second_condition_val:.{RulesConstants.DECIMAL_DIGITS}f} {{{min_value}..{max_value}}}'
        else:
            second_condition = f'{self.second_state_value:.{RulesConstants.DECIMAL_DIGITS}f}'
        the_string = f'{first_condition} {self.operator} {second_condition}'
        return the_string

    def categorical_to_string(self, states: Dict[str, str]) -> str:
        """
        FOR EXAMPLE:(for categorical)
        'race_is_category_Hispanic' becomes 'race is Hispanic'

        String representation for categorical condition
        :param states: A dictionary of domain features
        :return: condition.toString()
        """
        name = Features.extract_categorical_feature_name(states[self.first_state_key])
        category = Features.extract_categorical_feature_category(states[self.first_state_key])
        look_back = ''
        if self.first_state_lookback > 0:
            look_back = '[' + str(self.first_state_lookback) + ']'
        operator = "is"

        # The categorical data are coming in as one-hot, and we put 1.0 as the value to be compared to,
        # so LESS_THAN means "< 1" or zero (equivalent to False) and GREATER_THAN_EQUAL means ">= 1"
        # which is equivalent to one (True).
        if self.operator == RulesConstants.LESS_THAN:
            operator = operator + " not"
        the_string = f'{name}{look_back} {operator} {category}'
        return the_string

    # pylint: disable=too-many-arguments,too-many-positional-arguments
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
