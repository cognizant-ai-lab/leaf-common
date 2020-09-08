""" Base class for rule representation """

import random

import numpy

from leaf_common.candidates.constants import ACTION_MARKER
from leaf_common.representation.rule_based.rules_evaluation_constants \
    import RulesEvaluationConstants


class RulesAgent:
    """
    Evolving Rule-based actor class.
    """

    # pylint: disable=too-many-instance-attributes
    # Nine is reasonable in this case.

    def __init__(self, states, actions, initial_state, uid="rule_based"):

        # State/Config needed for evaluation
        self.uid = uid
        self.domain_states = []
        self.last_action = RulesEvaluationConstants.NO_ACTION
        self.state = initial_state
        self.actions = actions
        self.states = states
        self.state_history_size = RulesEvaluationConstants.MEM_FACTOR * len(self.actions)
        self.state[RulesEvaluationConstants.AGE_STATE_KEY] = 0
        self.times_applied = 0
        self.state_min_maxes = {}
        for state in self.states.keys():
            self.state_min_maxes[state, RulesEvaluationConstants.MIN_KEY] = 0
            self.state_min_maxes[state, RulesEvaluationConstants.MAX_KEY] = 0
            self.state_min_maxes[state, RulesEvaluationConstants.TOTAL_KEY] = 0

        # Genetic Material
        self.default_action = None
        self.rules = []

    def __str__(self):
        rules_str = ""
        for rule in self.rules:
            rules_str = rules_str + rule.get_str(self.state_min_maxes) + "\n"
        times_applied = " <> "
        if self.times_applied > 0:
            times_applied = " <" + str(self.times_applied) + "> "
        rules_str = rules_str + times_applied + "Default Action: " + self.default_action + "\n"
        return rules_str

    def __repr__(self):
        # For now, just use __str__ for __repr__ output, even though they would generally be for different uses
        return self.__str__()

    def revise_state_minmaxes(self, current_state):  # Keep track of min and max for all states
        """
        Get second state value
        :param current_state: the current state
        """
        for state in self.states.keys():
            self.state_min_maxes[state, RulesEvaluationConstants.TOTAL_KEY] = \
                self.state_min_maxes[state, RulesEvaluationConstants.TOTAL_KEY] + \
                current_state[state]
            if current_state[state] < self.state_min_maxes[state, RulesEvaluationConstants.MIN_KEY]:
                self.state_min_maxes[state, RulesEvaluationConstants.MIN_KEY] = current_state[state]
            if current_state[state] > self.state_min_maxes[state, RulesEvaluationConstants.MAX_KEY]:
                self.state_min_maxes[state, RulesEvaluationConstants.MAX_KEY] = current_state[state]

    def remove_actions_from_state(self):
        """
        Removes actions from state
        :return: action-less state
        """
        keep = [key for key in self.domain_states[0] if not key.startswith(ACTION_MARKER)]
        new_states = []
        for state in self.domain_states:
            row = {new_key: state[new_key] for new_key in keep}
            new_states.append(row)
        return new_states

    def set_action_state(self, action):
        """
        Sets the action in state
        :param action: action
        """
        self.set_action_in_state(action, self.state)

    def set_action_in_state(self, action, state):
        """
        Sets the action in state
        :param state: state
        :param action: action
        """
        for act in self.actions:
            state[ACTION_MARKER + act] = act == action

    def get_action_state(self):
        """
        Return action in state
        :return: the action
        """
        return self.get_action_in_state(self.state)

    def get_action_in_state(self, state):
        """
        Extracts action from state
        :param state: state
        :return: the action
        """
        for action in self.actions:
            if state[ACTION_MARKER + action]:
                return action
        return RulesEvaluationConstants.NO_ACTION

    def parse_rules(self):
        """
        Parse rules
        :return: the chosen action
        """
        poll_dict = dict.fromkeys(self.actions.keys(), 0)
        nb_states = len(self.domain_states) - 1
        if self.domain_states:
            self.revise_state_minmaxes(self.domain_states[nb_states])
        if not self.rules:
            raise RuntimeError("Fatal: an empty rule set detected")
        anyone_voted = False
        for rule in self.rules:
            result = rule.parse(self.domain_states, self.state_min_maxes)
            if result[RulesEvaluationConstants.ACTION_KEY] != RulesEvaluationConstants.NO_ACTION:
                if result[RulesEvaluationConstants.ACTION_KEY] in self.actions.keys():
                    poll_dict[result[RulesEvaluationConstants.ACTION_KEY]] += 1
                    anyone_voted = True
                if result[RulesEvaluationConstants.ACTION_KEY] == RulesEvaluationConstants.LOOK_BACK:
                    lookback = result[RulesEvaluationConstants.LOOKBACK_KEY]
                    poll_dict[self.get_action_in_state(self.domain_states[nb_states - lookback])] += 1
                    anyone_voted = True
        if not anyone_voted:
            self.times_applied += 1
            poll_dict[self.default_action] += 1
        return poll_dict

    def choose_action(self):
        """
        Choose an action
        :return: the chosen action
        """
        current_state = dict(self.state)
        self.domain_states.append(current_state)  # copy current state into history
        while len(self.domain_states) > self.state_history_size:
            index_to_delete = 1
            del self.domain_states[index_to_delete]
        action_to_perform = self.parse_rules()
        if action_to_perform == RulesEvaluationConstants.NO_ACTION:
            random_action = random.choice(list(self.actions.keys()))
            action_to_perform = random_action
        self.set_action_in_state(action_to_perform, self.domain_states[len(self.domain_states) - 1])
        return action_to_perform

    def prescribe(self, context):
        """
        Prescribe actions for a list of states
        :param context: list of states
        :return: list of actions
        """
        context_vector = numpy.array(context).transpose()
        vector_size = context_vector.shape[0]
        actions = numpy.zeros((vector_size, len(self.actions)))
        for i in range(vector_size):
            action = self.act(context_vector[i, :], None, None)
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

        for key in self.states.keys():
            self.state[key] = observations[int(key)]
        self.last_action = self.choose_action()
        self.state[RulesEvaluationConstants.AGE_STATE_KEY] += 1
        action = numpy.array(list(self.last_action.values()))
        return action

    def reset(self):
        """
        Reset rules agent
        """
        self.domain_states = []
