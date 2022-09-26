
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
""" Base class for rules-based model representation """

from copy import deepcopy

from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.data.rule_set_binding \
    import RuleSetBinding


class RuleModel:
    """
    Class representing complete rules-based model:
    set of rules developed for this model and
    rules set binding defining domain-specific context and actions
    """
    # pylint: disable=too-many-instance-attributes
    # Nine is reasonable in this case.

    def __init__(self, rules: RuleSet, binding: RuleSetBinding):
        """
        Constructor
        """
        self.rules = deepcopy(rules)
        self.rules_binding = deepcopy(binding)
        self.key = RuleModel.RuleModelKey

    # Class-specific key for verification of persist/restore operations
    RuleModelKey = "RuleModel-1.0"

    def get_rules(self):
        return self.rules

    def get_binding(self):
        return self.rules_binding

    def to_string(self) -> str:
        rules_str: str = self.rules.to_string(
            self.rules_binding.states,
            self.rules_binding.actions)
        return RuleModel.RuleModelKey+": rules: " + rules_str +\
            " binding: "+self.rules_binding.to_string()

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        # For now, just use __str__ for __repr__ output, even though
        # they would generally be for different uses
        return self.__str__()