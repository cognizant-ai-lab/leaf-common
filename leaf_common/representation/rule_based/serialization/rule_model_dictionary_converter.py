
# Copyright (C) 2019-2021 Cognizant Digital Business, Evolutionary AI.
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
from leaf_common.representation.rule_based.data.rules_model import RulesModel
from leaf_common.representation.rule_based.serialization.rule_set_dictionary_converter \
    import RuleSetDictionaryConverter
from leaf_common.serialization.interface.dictionary_converter import DictionaryConverter
from leaf_common.serialization.prep.pass_through_dictionary_converter \
    import PassThroughDictionaryConverter
from leaf_common.serialization.interface.self_identifying_representation_error \
    import SelfIdentifyingRepresentationError


class RulesModelDictionaryConverter(DictionaryConverter):
    """
    DictionaryConverter implementation for RuleModel objects.
    """

    def  __init__(self, verify_representation_type: bool = True):
        """
        Constructor

        :param verify_representation_type: When True, from_dict() will raise
                an error if the representation_type key does not match what we
                are expecting.  When False, no such error is raised.
                Default is True.
        """
        self._verify_representation_type = verify_representation_type

    def to_dict(self, obj: RulesModel) -> Dict[str, object]:
        """
        :param obj: The object of type RulesModel to be converted into a dictionary
        :return: A data-only dictionary that represents all the data for
                the given object, either in primitives
                (booleans, ints, floats, strings), arrays, or dictionaries.
                If obj is None, then the returned dictionary should also be
                None.  If obj is not the correct type, it is also reasonable
                to return None.
        """
        if obj is None:
            return None

        rules_converter = RuleSetDictionaryConverter()
        pass_through = PassThroughDictionaryConverter()

        obj_dict = {
            # This key allows for self-identifying representations
            # when a common serialization format (like JSON) is shared
            # between multiple representations.
            "representation_type": RepresentationType.RulesModel.value,

            "rules": rules_converter.to_dict(obj.candidate),
            "states": pass_through.to_dict(obj.states),
            "actions": pass_through.to_dict(obj.actions)
        }

        return obj_dict

    def from_dict(self, obj_dict: Dict[str, object]) -> RulesModel:
        """
        :param obj_dict: The data-only dictionary to be converted into an object
        :return: An object instance created from the given dictionary.
                If obj_dict is None, the returned object should also be None.
                If obj_dict is not the correct type, it is also reasonable
                to return None.
        """
        if self._verify_representation_type:
            representation_type = obj_dict.get("representation_type", None)
            if representation_type != RepresentationType.RulesModel.value:
                raise SelfIdentifyingRepresentationError(RepresentationType.RulesModel,
                                                         representation_type)

        rules_converter = RuleSetDictionaryConverter()
        pass_through = PassThroughDictionaryConverter()

        rules: RuleSet = rules_converter.from_dict(obj_dict.get("rules", None))
        actions = pass_through.from_dict(obj_dict.get("actions", None))
        states = pass_through.from_dict(obj_dict.get("states", None))
        obj: RulesModel = RulesModel(rules, states, actions)
        return obj
