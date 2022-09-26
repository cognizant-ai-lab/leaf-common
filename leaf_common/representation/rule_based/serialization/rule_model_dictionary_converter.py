
# Copyright (C) 2019-2022 Cognizant Digital Business, Evolutionary AI.
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

from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.data.rule_set_binding \
    import RuleSetBinding
from leaf_common.representation.rule_based.data.rule_model import RuleModel
from leaf_common.representation.rule_based.serialization.rule_set_dictionary_converter \
    import RuleSetDictionaryConverter
from leaf_common.serialization.interface.dictionary_converter import DictionaryConverter
from leaf_common.serialization.prep.pass_through_dictionary_converter \
    import PassThroughDictionaryConverter


class RuleModelDictionaryConverter(DictionaryConverter):
    """
    DictionaryConverter implementation for RuleModel objects.
    """

    def to_dict(self, obj: RuleModel) -> Dict[str, object]:
        """
        :param obj: The object of type RuleModel to be converted into a dictionary
        :return: A data-only dictionary that represents all the data for
                the given object, either in primitives
                (booleans, ints, floats, strings), arrays, or dictionaries.
                If obj is None, then the returned dictionary should also be
                None.  If obj is not the correct type, it is also reasonable
                to return None.
        """
        if obj is None:
            return None
        binding: RuleSetBinding = obj.get_binding()

        rules_converter = RuleSetDictionaryConverter()
        pass_through = PassThroughDictionaryConverter()

        obj_dict = {
            "key": RuleModel.RuleModelKey,
            "rules": rules_converter.to_dict(obj.get_rules()),
            "states": {
                "elements": pass_through.to_dict(binding.model_states)
            },
            "actions": {
                "elements": pass_through.to_dict(binding.model_actions)
            }
        }

        return obj_dict

    def from_dict(self, obj_dict: Dict[str, object]) -> RuleModel:
        """
        :param obj_dict: The data-only dictionary to be converted into an object
        :return: An object instance created from the given dictionary.
                If obj_dict is None, the returned object should also be None.
                If obj_dict is not the correct type, it is also reasonable
                to return None.
        """
        format_key = obj_dict.get("key", None)
        if format_key != RuleModel.RuleModelKey:
            msg: str = f"Expected object format {RuleModel.RuleModelKey} got {format_key}"
            raise ValueError(msg)

        rules_converter = RuleSetDictionaryConverter()
        pass_through = PassThroughDictionaryConverter()

        rules: RuleSet = rules_converter.from_dict(obj_dict.get("rules", None))
        actions = pass_through.from_dict(obj_dict.get("actions", None))
        if actions is not None:
            actions = actions.get("elements", None)
        states = pass_through.from_dict(obj_dict.get("states", None))
        if states is not None:
            states = states.get("elements", None)
        obj: RuleModel = RuleModel(rules, RuleSetBinding(states, actions))
        return obj
