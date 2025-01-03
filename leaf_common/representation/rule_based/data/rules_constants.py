
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
See class comment
"""

import math


class RulesConstants:
    """
    Constants for various aspects of the Rule-based representation
    """

    # Rules stuff
    MEM_FACTOR = 100  # max memory cells required
    TOTAL_KEY = "total"

    CONDITION_KEY = "condition"
    ACTION_KEY = "action"
    ACTION_COUNT_KEY = "action_count"
    ACTION_COEFFICIENT_KEY = "action_coefficient"
    LOOKBACK_KEY = "action_lookback"

    # Rule stuff
    RULE_ELEMENTS = [CONDITION_KEY, ACTION_KEY, ACTION_COEFFICIENT_KEY, LOOKBACK_KEY]
    LOOKBACK_ACTION = "lb"
    NO_ACTION = -1

    # pylint: disable=fixme
    # XXX If these are used as a keys, they would be better off as a strings
    #       Think: More intelligible in JSON.

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
    MIN_KEY = "min"
    MAX_KEY = "max"
    GRANULARITY = 100
    DECIMAL_DIGITS = int(math.log10(GRANULARITY))

    # Condition operator strings
    LESS_THAN = "<"
    LESS_THAN_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_EQUAL = ">="

    # Evaluation Data dictionary keys
    OBSERVATION_HISTORY_KEY = "observation_history"
    STATE_MIN_MAXES_KEY = "min_maxes"

    # marker added to categorical attribute names upon data flattening
    CATEGORY_EXPLAINABLE_MARKER = "_is_category_"
