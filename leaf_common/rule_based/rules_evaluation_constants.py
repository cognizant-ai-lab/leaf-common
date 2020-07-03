"""
See class comment
"""

import math

from leaf_common.candidates.constants import ACTION_MARKER


class RulesEvaluationConstants():
    """
    Constants for various aspects of Rules evaluation
    """

    # Rules stuff
    RULE_FILTER_FACTOR = 1
    AGE_STATE = "age"
    MEM_FACTOR = 100  # max memory cells required
    THE_TOTAL = "total"

    # Rule stuff
    RULE_ELEMENTS = ["condition", "action", "action_lookback"]
    THE_LOOKBACK = 1
    LOOK_BACK = "lb"
    THE_ACTION = 0
    NO_ACTION = -1

    # Condition stuff
    CONDITION_ELEMENTS = [
        "first_state",
        "first_state_coefficient",
        "first_state_exponent",
        "first_state_lookback",
        "operator",
        "second_state",
        "second_state_coefficient",
        "second_state_exponent",
        "second_state_lookback",
        "second_state_value"
    ]
    THE_MIN = "min"
    THE_MAX = "max"
    GRANULARITY = 100
    DECIMAL_DIGITS = int(math.log10(GRANULARITY))

    # Condition operator strings
    LESS_THAN = "<"
    LESS_THAN_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_EQUAL = ">="

    ACTION_MARKER = ACTION_MARKER
