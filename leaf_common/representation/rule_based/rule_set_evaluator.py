""" Base class for rule representation """

import random

from leaf_common.candidates.constants import ACTION_MARKER
from leaf_common.evaluation.component_evaluator import ComponentEvaluator
from leaf_common.representation.rule_based.rules_agent import RulesAgent
from leaf_common.representation.rule_based.rules_evaluation_constants import RulesEvaluationConstants


class RuleSetEvaluator(ComponentEvaluator):
    """
    Rule-set evaluator class.
    """

    def __init__(self, rule_set: RulesAgent = None):

        self.domain_states = []
        self.state_history_size = 0

        if rule_set is not None:
            self.reset(rule_set)

    def evaluate(self, component: RulesAgent, evaluation_data: object = None) -> object:
        rule_set = component
        action = self.choose_action(rule_set)
        return action

    # pylint: disable=no-self-use
    def _revise_state_minmaxes(self, rule_set: RulesAgent, current_state):
        """
        Get second state value
        Keep track of min and max for all states
        :param current_state: the current state
        """
        for state in rule_set.states.keys():
            rule_set.state_min_maxes[state, RulesEvaluationConstants.TOTAL_KEY] = \
                rule_set.state_min_maxes[state, RulesEvaluationConstants.TOTAL_KEY] + \
                current_state[state]
            if current_state[state] < rule_set.state_min_maxes[state, RulesEvaluationConstants.MIN_KEY]:
                rule_set.state_min_maxes[state, RulesEvaluationConstants.MIN_KEY] = current_state[state]
            if current_state[state] > rule_set.state_min_maxes[state, RulesEvaluationConstants.MAX_KEY]:
                rule_set.state_min_maxes[state, RulesEvaluationConstants.MAX_KEY] = current_state[state]

    # pylint: disable=no-self-use
    def _set_action_in_state(self, rule_set: RulesAgent, action, state):
        """
        Sets the action in state
        :param state: state
        :param action: action
        """
        for act in rule_set.actions:
            state[ACTION_MARKER + act] = act == action

    # pylint: disable=no-self-use
    def _get_action_in_state(self, rule_set: RulesAgent, state):
        """
        Extracts action from state
        :param state: state
        :return: the action
        """
        for action in rule_set.actions:
            if state[ACTION_MARKER + action]:
                return action
        return RulesEvaluationConstants.NO_ACTION

    def parse_rules(self, rule_set: RulesAgent):
        """
        Parse rules
        Used by tests and choose_action()

        :param rule_set: The RulesAgent to evaluate
        :return: the chosen action
        """
        poll_dict = dict.fromkeys(rule_set.actions.keys(), 0)
        nb_states = len(self.domain_states) - 1
        if self.domain_states:
            self._revise_state_minmaxes(rule_set, self.domain_states[nb_states])
        if not rule_set.rules:
            raise RuntimeError("Fatal: an empty rule set detected")
        anyone_voted = False
        for rule in rule_set.rules:
            result = rule.parse(self.domain_states, rule_set.state_min_maxes)
            if result[RulesEvaluationConstants.ACTION_KEY] != RulesEvaluationConstants.NO_ACTION:
                if result[RulesEvaluationConstants.ACTION_KEY] in rule_set.actions.keys():
                    poll_dict[result[RulesEvaluationConstants.ACTION_KEY]] += 1
                    anyone_voted = True
                if result[RulesEvaluationConstants.ACTION_KEY] == RulesEvaluationConstants.LOOK_BACK:
                    lookback = result[RulesEvaluationConstants.LOOKBACK_KEY]
                    poll_dict[self._get_action_in_state(rule_set,
                                                        self.domain_states[nb_states - lookback])] += 1
                    anyone_voted = True
        if not anyone_voted:
            rule_set.times_applied += 1
            poll_dict[rule_set.default_action] += 1
        return poll_dict

    def choose_action(self, rule_set: RulesAgent):
        """
        Choose an action
        :return: the chosen action
        """
        current_state = dict(rule_set.state)
        self.domain_states.append(current_state)  # copy current state into history
        while len(self.domain_states) > self.state_history_size:
            index_to_delete = 1
            del self.domain_states[index_to_delete]
        action_to_perform = self.parse_rules(rule_set)
        if action_to_perform == RulesEvaluationConstants.NO_ACTION:
            random_action = random.choice(list(rule_set.actions.keys()))
            action_to_perform = random_action
        self._set_action_in_state(rule_set, action_to_perform,
                                  self.domain_states[len(self.domain_states) - 1])
        return action_to_perform

    def reset(self, rule_set: RulesAgent):
        """
        Reset state per rules agent
        """
        self.domain_states = []
        self.state_history_size = RulesEvaluationConstants.MEM_FACTOR * len(rule_set.actions)
