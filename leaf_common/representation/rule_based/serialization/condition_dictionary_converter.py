
# Copyright 2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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
See class comment for details.
"""
from typing import Dict

from leaf_common.representation.rule_based.data.condition import Condition
from leaf_common.serialization.interface.dictionary_converter import DictionaryConverter


class ConditionDictionaryConverter(DictionaryConverter):
    """
    DictionaryConverter implementation for Condition objects.
    """

    def to_dict(self, obj: Condition) -> Dict[str, object]:
        """
        :param obj: The object to be converted into a dictionary
        :return: A data-only dictionary that represents all the data for
                the given object, either in primitives
                (booleans, ints, floats, strings), arrays, or dictionaries.
                If obj is None, then the returned dictionary should also be
                None.  If obj is not the correct type, it is also reasonable
                to return None.
        """
        if obj is None:
            return None

        obj_dict = {
            "first_state_lookback": int(obj.first_state_lookback),
            "first_state_key": str(obj.first_state_key),
            "first_state_coefficient": float(obj.first_state_coefficient),
            "first_state_exponent": obj.first_state_exponent,       # DEF: No type in data class

            "operator": str(obj.operator),

            "second_state_lookback": int(obj.second_state_lookback),
            "second_state_key": str(obj.second_state_key),
            "second_state_value": float(obj.second_state_value),
            "second_state_coefficient": float(obj.second_state_coefficient),
            "second_state_exponent": obj.second_state_exponent      # DEF: No type in data class
        }

        return obj_dict

    def from_dict(self, obj_dict: Dict[str, object]) -> Condition:
        """
        :param obj_dict: The data-only dictionary to be converted into an object
        :return: An object instance created from the given dictionary.
                If obj_dict is None, the returned object should also be None.
                If obj_dict is not the correct type, it is also reasonable
                to return None.
        """
        obj = Condition()

        obj.first_state_lookback = obj_dict.get("first_state_lookback", None)
        obj.first_state_key = obj_dict.get("first_state_key", None)
        obj.first_state_coefficient = obj_dict.get("first_state_coefficient", None)
        obj.first_state_exponent = obj_dict.get("first_state_exponent", None)

        obj.operator = obj_dict.get("operator", None)

        obj.second_state_lookback = obj_dict.get("second_state_lookback", None)
        obj.second_state_key = obj_dict.get("second_state_key", None)
        obj.second_state_value = obj_dict.get("second_state_value", None)
        obj.second_state_coefficient = obj_dict.get("second_state_coefficient", None)
        obj.second_state_exponent = obj_dict.get("second_state_exponent", None)

        return obj
