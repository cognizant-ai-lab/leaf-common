
# Copyright 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
