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
""" Domain-specific binding for RuleModel context and actions."""

import copy
from typing import Dict, List

from leaf_common.representation.rule_based.config.rule_set_config_helper \
    import RuleSetConfigHelper


class RuleSetBinding:
    """
    Class representing some domain-specific context and actions
    (model inputs and outputs) which could be bound
    to some general model to perform model inference.
    """
    def __init__(self,
                 states: List[Dict[str, object]],
                 actions: List[Dict[str, object]]):
        """
        Creates a RulesModel
        :param states: model features
        :param actions: model actions
        """
        self.model_states = copy.deepcopy(states)
        self.model_actions = copy.deepcopy(actions)
        # Internally, "one-hot" encode our inputs and outputs
        # for use in model evaluator
        self.states = RuleSetConfigHelper.read_config_shape_var(self.model_states)
        self.actions = RuleSetConfigHelper.read_config_shape_var(self.model_actions)

    def to_string(self) -> str:
        """
        Returns string representing these states and actions
        :return: string representing this set of rules
        """
        return f"states: {repr(self.model_states)}\n" + \
               f"actions: {repr(self.model_actions)}\n"
