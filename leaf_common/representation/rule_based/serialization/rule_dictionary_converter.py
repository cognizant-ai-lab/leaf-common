
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
See class comment for details.
"""
from typing import Dict

from leaf_common.representation.rule_based.data.rule import Rule
from leaf_common.representation.rule_based.serialization.condition_dictionary_converter \
    import ConditionDictionaryConverter
from leaf_common.serialization.interface.dictionary_converter import DictionaryConverter


class RuleDictionaryConverter(DictionaryConverter):
    """
    DictionaryConverter implementation for Rule objects.
    """

    def to_dict(self, obj: Rule) -> Dict[str, object]:
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
            "action": obj.action,
            "action_coefficient": obj.action_coefficient,
            "action_lookback": obj.action_lookback,
            "conditions": [],
            "times_applied": obj.times_applied
        }

        condition_converter = ConditionDictionaryConverter()
        for condition in obj.conditions:
            condition_dict = condition_converter.to_dict(condition)
            obj_dict["conditions"].append(condition_dict)

        return obj_dict

    def from_dict(self, obj_dict: Dict[str, object]) -> Rule:
        """
        :param obj_dict: The data-only dictionary to be converted into an object
        :return: An object instance created from the given dictionary.
                If obj_dict is None, the returned object should also be None.
                If obj_dict is not the correct type, it is also reasonable
                to return None.
        """
        obj = Rule()

        obj.action = obj_dict.get("action", None)
        obj.action_coefficient = obj_dict.get("action_coefficient", None)
        obj.action_lookback = obj_dict.get("action_lookback", None)
        obj.times_applied = obj_dict.get("times_applied", 0)

        condition_converter = ConditionDictionaryConverter()
        empty_list = []
        condition_dicts = obj_dict.get("conditions", empty_list)
        for condition_dict in condition_dicts:
            condition = condition_converter.from_dict(condition_dict)
            obj.conditions.append(condition)

        return obj
