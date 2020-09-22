""" Base class for rule representation """

import numpy

from leaf_common.representation.rule_based.rules_agent import RulesAgent
from leaf_common.representation.rule_based.rule_set_evaluator import RuleSetEvaluator
from leaf_common.representation.rule_based.rules_evaluation_constants import RulesEvaluationConstants


class RuleSetPrescriptor:
    """
    Prescriptor for RulesAgents
    """

    def __init__(self, rule_set: RulesAgent):
        self.rule_set = rule_set
        self.last_action = RulesEvaluationConstants.NO_ACTION

    def get_actions(self):
        return self.rule_set.actions

    def get_uid(self):
        return self.rule_set.uid

    def prescribe(self, context):
        """
        Prescribe actions for a list of states
        :param context: list of states
        :return: list of actions
        """
        context_vector = numpy.array(context).transpose()
        vector_size = context_vector.shape[0]
        actions = numpy.zeros((vector_size, len(self.rule_set.actions)))
        for i in range(vector_size):
            action = self.act(self.rule_set, context_vector[i, :], None, None)
            actions[i, :] = action
        return actions

    def act(self, observations, _reward, _done):
        """
        Act based on the observations
        :param observations: the input state
        :param _reward: Not used
        :param _done: Not used
        :return: an action
        """
        del _reward, _done

        for key in self.rule_set.states.keys():
            self.rule_set.state[key] = observations[int(key)]

        evaluator = RuleSetEvaluator()
        self.last_action = evaluator.evaluate(self.rule_set)

        self.rule_set.state[RulesEvaluationConstants.AGE_STATE_KEY] += 1
        action = numpy.array(list(self.last_action.values()))
        return action
