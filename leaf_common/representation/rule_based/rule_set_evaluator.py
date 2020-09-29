"""
See class comment for details
"""

from copy import deepcopy
from typing import Dict
from typing import Tuple

import random

from leaf_common.candidates.constants import ACTION_MARKER
from leaf_common.evaluation.component_evaluator import ComponentEvaluator
from leaf_common.representation.rule_based.rule_evaluator import RuleEvaluator
from leaf_common.representation.rule_based.rules_agent import RulesAgent
from leaf_common.representation.rule_based.rules_evaluation_constants import RulesEvaluationConstants


class RuleSetEvaluator(ComponentEvaluator):
    """
    Rule-set evaluator class.

    This is a stateful evaluator in that calls to evaluate()
    keep some history as to the relevant evaluated_data/observations
    passed in so that time series offsets can be made.
    This state history is kept here in the Evaluator so that
    data does not go back to the service.

    As such we recommend one instance of this Evaluator be retained per RulesAgent.

    Also worth noting that invocation of the evaluate() method
    can result in the following fields on RulesAgent being changed:
        * times_applied
    Also each Rule's times_applied and age_state can change
    """

    def __init__(self, states: Dict[str, str], actions: Dict[str, str],
                 min_maxes: Dict[Tuple[str, str], float] = None):
        """
        Constructor

        :param states: XXX Need a good definition here
        :param actions: XXX Need a good definition here
        :param min_maxes: A dictionary of (state, "min"/"max") to a float value
                    which pre-calibrates the normalization of the conditions.
                    These values are copied and as evaluation proceeds, the
                    internal copy gets updated with new values should the
                    data encountered warrant it.  The default value is None,
                    indicating that we don't know enough about the data to
                    calibrate anything at the outset.
        """

        self.states = states
        self.actions = actions

        self.observation_history = []
        self.observation_history_size = 0

        # Initialize the min/maxes
        if self.state_min_maxes is not None:
            self.state_min_maxes = deepcopy(min_maxes)
        else:
            self.state_min_maxes = {}

        for state in self.states.keys():
            self.state_min_maxes[state, RulesEvaluationConstants.MIN_KEY] = 0
            self.state_min_maxes[state, RulesEvaluationConstants.MAX_KEY] = 0
            self.state_min_maxes[state, RulesEvaluationConstants.TOTAL_KEY] = 0

        # This evaluator itself is stateless, so its OK to just create one
        # as an optimization.
        self.rule_evaluator = RuleEvaluator(self.states)

        self.reset()

    def evaluate(self, component: RulesAgent, evaluation_data: object = None) -> object:
        rule_set = component

        # Set up a state dictionary distilling only the information needed from
        # observation/evaluation_data coming in. This will ultimately get stored
        # in the observation_history member so looking backwards in time is supported.
        #
        # 'current_observation' used to be RulesAgent.state, which was very confusing,
        # given that there is another member called 'states' which acts as a definition.
        current_observation = {}

        for key in self.states.keys():
            use_key = int(key)
            current_observation[key] = evaluation_data[use_key]

        action = self.choose_action(rule_set, current_observation)

        rule_set.age_state += 1

        return action

    def _revise_state_minmaxes(self, current_observation):
        """
        Get second state value
        Keep track of min and max for all states
        :param current_observation: the current state
        """
        for state in self.states.keys():
            self.state_min_maxes[state, RulesEvaluationConstants.TOTAL_KEY] = \
                self.state_min_maxes[state, RulesEvaluationConstants.TOTAL_KEY] + \
                current_observation[state]
            if current_observation[state] < self.state_min_maxes[state, RulesEvaluationConstants.MIN_KEY]:
                self.state_min_maxes[state, RulesEvaluationConstants.MIN_KEY] = current_observation[state]
            if current_observation[state] > self.state_min_maxes[state, RulesEvaluationConstants.MAX_KEY]:
                self.state_min_maxes[state, RulesEvaluationConstants.MAX_KEY] = current_observation[state]

    def get_min_maxes(self) -> Dict[Tuple[str, str], float]:
        """
        :return: the dictionary of min/max values encountered for each state.
            This in and of itself can be considered data which is "learned"
            by looking at the data set, but it is not evolved.  In some
            situations, these min/maxes can be essential calibration data
            when transfering a rule set into a predictive setting.
        """
        return self.state_min_maxes

    def _set_action_in_state(self, action, state):
        """
        Sets the action in state
        :param state: state
        :param action: action
        """
        for act in self.actions:
            state[ACTION_MARKER + act] = act == action

    def _get_action_in_state(self, state):
        """
        Extracts action from state
        :param state: state
        :return: the action
        """
        for action in self.actions:
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
        poll_dict = dict.fromkeys(self.actions.keys(), 0)
        nb_states = len(self.observation_history) - 1
        if self.observation_history:
            self._revise_state_minmaxes(self.observation_history[nb_states])
        if not rule_set.rules:
            raise RuntimeError("Fatal: an empty rule set detected")
        anyone_voted = False

        # Prepare the data going into the RuleEvaluator
        rule_evaluation_data = {
            RulesEvaluationConstants.OBSERVATION_HISTORY_KEY: self.observation_history,
            RulesEvaluationConstants.STATE_MIN_MAXES_KEY: self.state_min_maxes
        }
        for rule in rule_set.rules:
            result = self.rule_evaluator.evaluate(rule, rule_evaluation_data)
            action = result[RulesEvaluationConstants.ACTION_KEY]
            if action != RulesEvaluationConstants.NO_ACTION:
                if action in self.actions.keys():
                    poll_dict[action] += 1
                    anyone_voted = True
                if action == RulesEvaluationConstants.LOOK_BACK:
                    lookback = result[RulesEvaluationConstants.LOOKBACK_KEY]
                    poll_dict[self._get_action_in_state(self.observation_history[nb_states - lookback])] += 1
                    anyone_voted = True
        if not anyone_voted:
            rule_set.times_applied += 1
            poll_dict[rule_set.default_action] += 1
        return poll_dict

    def choose_action(self, rule_set: RulesAgent, current_observation: dict):
        """
        Choose an action
        :return: the chosen action
        """
        self.observation_history.append(current_observation)  # copy current state into history
        while len(self.observation_history) > self.observation_history_size:
            index_to_delete = 1
            del self.observation_history[index_to_delete]
        action_to_perform = self.parse_rules(rule_set)
        if action_to_perform == RulesEvaluationConstants.NO_ACTION:
            random_action = random.choice(list(self.actions.keys()))
            action_to_perform = random_action
        self._set_action_in_state(action_to_perform,
                                  self.observation_history[len(self.observation_history) - 1])
        return action_to_perform

    def reset(self):
        """
        Reset state per actions config
        """
        self.observation_history = []

        # It'd be nice if this MEM_FACTOR came from configuration
        self.observation_history_size = RulesEvaluationConstants.MEM_FACTOR * len(self.actions)
