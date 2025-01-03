
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
""" Base class for rule representation """

from copy import deepcopy
from typing import Dict

from leaf_common.representation.rule_based.data.rules_constants import RulesConstants


class RuleSet:
    """
    Evolving Rule-based actor class.
    """

    # pylint: disable=too-many-instance-attributes
    # Nine is reasonable in this case.

    def __init__(self, min_maxes: Dict[str, Dict[str, float]] = None):
        """
        Constructor

        :param min_maxes: A dictionary of dictionaries, where the
                    outer dictionary keys are states whose values are
                    the inner dictionaries. Each inner dictionary has
                    at least two keys: "min" and "max" and each key has
                    float values which pre-calibrate the normalization
                    of the conditions.

                    These values are copied and as evaluation proceeds, the
                    internal copy gets updated with new values should the
                    data encountered warrant it.  The default value is None,
                    indicating that we don't know enough about the data to
                    calibrate anything at the outset.
        """

        # Evaluation Metrics used in reproduction
        self.times_applied = 0
        self.age_state = 0

        # Honest-to-goodness Genetic Material
        self.default_action = None
        self.default_action_coefficient: float = None
        self.rules = []

        # Initialize the min/maxes
        self.min_maxes = {}
        if min_maxes is not None:
            self.min_maxes = deepcopy(min_maxes)

    # see https://github.com/PyCQA/pycodestyle/issues/753 for why next line needs noqa
    def to_string(self, states: Dict[str, str] = None, actions: Dict[str, str] = None) -> str:      # noqa: E252
        """
        String representation for rule
        EXAMPLE:
          <7315> (race is Hispanic)  -->  0.20*nateglinide_is_category_Yes
          <100174> (diag_1 is circulatory)  -->  0.60*repaglinide_is_category_Yes
          <154742> (gender is Male)  -->  0.44*insulin_is_category_Yes
          <279049> Default Action: 0.76*glyburide_is_category_No


        :param states: An optional dictionary of state definitions seen during evaluation.
        :param actions: An optional dictionary of action definitions seen during evaluation.
        :return: RuleSet.toString()
        """
        action_name = str(self.default_action)
        if actions is not None and self.default_action in actions:
            action_name = actions[self.default_action]
        rules_str = ""
        for rule in self.rules:
            rules_str = rules_str + rule.to_string(states=states, actions=actions, min_maxes=self.min_maxes) + "\n"
        times_applied = " <> "
        if self.times_applied > 0:
            times_applied = " <" + str(self.times_applied) + "> "
        coefficient_part = f'{self.default_action_coefficient:.{RulesConstants.DECIMAL_DIGITS}f}*'
        rules_str = rules_str + times_applied + "Default Action: " + coefficient_part + action_name + "\n"
        return rules_str

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        # For now, just use __str__ for __repr__ output, even though they would generally be for different uses
        return self.__str__()
