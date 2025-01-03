
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

from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.serialization.rule_dictionary_converter \
    import RuleDictionaryConverter
from leaf_common.serialization.interface.dictionary_converter import DictionaryConverter
from leaf_common.serialization.interface.self_identifying_representation_error \
    import SelfIdentifyingRepresentationError


class RuleSetDictionaryConverter(DictionaryConverter):
    """
    DictionaryConverter implementation for RuleSet objects.
    """

    def __init__(self, verify_representation_type: bool = True):
        """
        Constructor

        :param verify_representation_type: When True, from_dict() will raise
                an error if the representation_type key does not match what we
                are expecting.  When False, no such error is raised.
                Default is True.
        """
        self._verify_representation_type = verify_representation_type

    def to_dict(self, obj: RuleSet) -> Dict[str, object]:
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
            # This key allows for self-identifying representations
            # when a common serialization format (like JSON) is shared
            # between multiple representations.
            "representation_type": RepresentationType.RuleBased.value,

            "age_state": obj.age_state,
            "default_action": obj.default_action,
            "default_action_coefficient": obj.default_action_coefficient,
            "min_maxes": obj.min_maxes,
            "rules": [],
            "times_applied": obj.times_applied
        }

        rule_converter = RuleDictionaryConverter()
        for rule in obj.rules:
            rule_dict = rule_converter.to_dict(rule)
            obj_dict["rules"].append(rule_dict)

        return obj_dict

    def from_dict(self, obj_dict: Dict[str, object]) -> RuleSet:
        """
        :param obj_dict: The data-only dictionary to be converted into an object
        :return: An object instance created from the given dictionary.
                If obj_dict is None, the returned object should also be None.
                If obj_dict is not the correct type, it is also reasonable
                to return None.
        """
        if self._verify_representation_type:
            representation_type = obj_dict.get("representation_type", None)
            if representation_type != RepresentationType.RuleBased.value:
                raise SelfIdentifyingRepresentationError(RepresentationType.RuleBased,
                                                         representation_type)

        min_maxes = obj_dict.get("min_maxes", None)
        obj = RuleSet(min_maxes=min_maxes)

        obj.age_state = obj_dict.get("age_state", 0)
        obj.default_action = obj_dict.get("default_action", None)
        obj.default_action_coefficient = obj_dict.get("default_action_coefficient", None)
        obj.times_applied = obj_dict.get("times_applied", 0)

        rule_converter = RuleDictionaryConverter()
        empty_list = []
        rule_dicts = obj_dict.get("rules", empty_list)
        for rule_dict in rule_dicts:
            rule = rule_converter.from_dict(rule_dict)
            obj.rules.append(rule)

        return obj
