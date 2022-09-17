"""
Code relating to evaluation of Rule_based prescriptor.
It has been implemented  to mitigate the high level of dependancy our current domain has on Keras models
"""
import copy
from typing import Dict, List
import numpy as np

from leaf_common.representation.rule_based.evaluation.rule_set_evaluator import RuleSetEvaluator
from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants

class RulesModel:
    """
    A wrapper for rule_set to do predictions
    """
    def __init__(self, candidate: RuleSet,
                       states: List[Dict[str, object]],
                       actions: List[Dict[str, object]]):
        """
        Creates a RulesModel
        :param candidate: rule set
        :param states: model features
        :param actions: model actions
        """
        self.candidate = candidate
        self.states = copy.deepcopy(states)
        self.actions = copy.deepcopy(actions)

    def predict(self, data: np.array) -> np.array:
        """
        Evaluates the model against data and computes the decisions
        :param data: a multidimensional numpy array containing the samples
        :return: actions
        """
        evaluator = RuleSetEvaluator(self.states, self.actions)
        sample_actions = []
        for data_index in range(data.shape[1]):
            data_dictionary = dict(self.states)
            keys = data_dictionary.keys()
            for key in keys:
                data_dictionary[key] = data[int(key)][data_index]
            actions_dict = evaluator.choose_action(self.candidate, data_dictionary)
            actions = []
            for action in actions_dict.values():
                if action[RulesConstants.ACTION_COUNT_KEY] > 0:
                    actions.append(action[RulesConstants.ACTION_COEFFICIENT_KEY] /
                                   action[RulesConstants.ACTION_COUNT_KEY])
                else:
                    actions.append(0.0)
            sample_actions.append(actions)
        return_actions = np.array(sample_actions)
        return return_actions

    def to_string(self) -> str:
        """
        Returns string representing this set of rules
        :return: string representing this set of rules
        """
        return self.candidate.to_string(states=self.states, actions=self.actions)
