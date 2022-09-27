"""
Code relating to evaluation of Rule_based model.
"""
from typing import List, Any

from leaf_common.evaluation.component_evaluator import ComponentEvaluator
from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.data.rule_model import RuleModel
from leaf_common.representation.rule_based.data.rule_set_binding \
    import RuleSetBinding
from leaf_common.representation.rule_based.evaluation.rule_set_evaluator \
    import RuleSetEvaluator
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants


class RuleModelEvaluator(ComponentEvaluator):
    """
    A wrapper for rules-based model predictions computation
    """

    def evaluate(self, component: object, evaluation_data: object) -> object:
        """
        Evaluates the model against data and computes the decisions
        :param component: RuleModel instance
        :param evaluation_data: a multidimensional array containing the samples
        :return: actions as List[List[float]]
        """
        if component is None or not isinstance(component, RuleModel):
            return None
        model: RuleModel = component

        # our input data is actually a list of lists of some values
        data: List[List[Any]] = evaluation_data
        binding: RuleSetBinding = model.get_binding()

        evaluator: RuleSetEvaluator = RuleSetEvaluator(binding.states, binding.actions)
        sample_actions = []
        for data_index in range(len(data[0])):
            data_dictionary = dict(binding.states)
            keys = data_dictionary.keys()
            for key in keys:
                data_dictionary[key] = data[int(key)][data_index]
            actions_dict = evaluator.choose_action(model.get_rules(), data_dictionary)
            actions = []
            for action in actions_dict.values():
                if action[RulesConstants.ACTION_COUNT_KEY] > 0:
                    actions.append(action[RulesConstants.ACTION_COEFFICIENT_KEY] /
                                   action[RulesConstants.ACTION_COUNT_KEY])
                else:
                    actions.append(0.0)
            sample_actions.append(actions)
        return sample_actions
