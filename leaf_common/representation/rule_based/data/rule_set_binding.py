
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
""" Domain-specific binding for RuleSet context and actions."""

from typing import Dict

from leaf_common.representation.rule_based.data.rule_set import RuleSet


class RuleSetBinding:
    """
    Class representing some domain-specific context and actions
    (model inputs and outputs) which could be bound
    to some general model to perform model inference.
    """
    def __init__(self,
                 rules: RuleSet,
                 states: Dict[str, str],
                 actions: Dict[str, str]):
        """
        Creates a binding for given RuleSet

        :param rules: The RuleSet to bind to states and actions.
                Note: If you care about immutability during evaluation,
                      consider doing a deepcopy() before passing in this argument.
                      If you go this route, consider using the RuleSetMetricsMerger
                      to properly update metrics during evaluation.
        :param states: model features encoded w.r.t. categorical values
        :param actions: model actions encoded w.r.t. categorical values
        """
        self.rules = rules
        self.states = states
        self.actions = actions
        self.key = RuleSetBinding.RuleSetBindingKey

    # Class-specific key for verification of persist/restore operations
    RuleSetBindingKey = "RuleSetBinding-1.0"

    def to_string(self) -> str:
        """
        Returns string representing rules together with bound states and actions
        :return: string representing this RuleSetBinding instance
        """
        rules_str: str = self.rules.to_string(self.states, self.actions)
        return f"rules: {rules_str}\n states: {repr(self.states)}\n" + \
               f"actions: {repr(self.actions)}\n"

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        # For now, just use __str__ for __repr__ output, even though
        # they would generally be for different uses
        return self.__str__()
