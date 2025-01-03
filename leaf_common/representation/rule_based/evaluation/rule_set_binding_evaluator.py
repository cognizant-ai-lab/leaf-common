
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
Code relating to evaluation of RuleSet bound to domain-specific context/actions.
"""
from typing import List, Any

from leaf_common.evaluation.component_evaluator import ComponentEvaluator
from leaf_common.representation.rule_based.data.rule_set_binding \
    import RuleSetBinding
from leaf_common.representation.rule_based.evaluation.rule_set_evaluator \
    import RuleSetEvaluator
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants


class RuleSetBindingEvaluator(ComponentEvaluator):
    """
    A wrapper for rules-based model predictions computation

    Also worth noting that invocation of the evaluate() method
    can result in the following fields on RuleSet being changed:
        * times_applied
    Also each Rule's times_applied and age_state can change.
    """

    def evaluate(self, component: object, evaluation_data: object) -> object:
        """
        Evaluates the model against data and computes the decisions
        :param component: RuleSetBinding instance
        :param evaluation_data: a multidimensional array containing the samples
        :return: actions as List[List[float]]
        """
        # pylint: disable=too-many-locals
        if component is None or not isinstance(component, RuleSetBinding):
            return None
        model: RuleSetBinding = component

        # our input data is actually a list of lists of some values
        data: List[List[Any]] = evaluation_data

        # Our inputs and outputs are "one-hot" encoded
        # for use in RuleSet evaluator
        encoded_states = model.states
        encoded_actions = model.actions

        evaluator: RuleSetEvaluator = RuleSetEvaluator(encoded_states, encoded_actions)
        sample_actions = []
        for data_index in range(len(data[0])):
            data_dictionary = dict(encoded_states)
            keys = data_dictionary.keys()
            for key in keys:
                data_dictionary[key] = data[int(key)][data_index]
            actions_dict = evaluator.choose_action(model.rules, data_dictionary)
            actions = []
            for action in actions_dict.values():
                if action[RulesConstants.ACTION_COUNT_KEY] > 0:
                    actions.append(action[RulesConstants.ACTION_COEFFICIENT_KEY] /
                                   action[RulesConstants.ACTION_COUNT_KEY])
                else:
                    actions.append(0.0)
            sample_actions.append(actions)
        return sample_actions
