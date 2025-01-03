
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
See class comment for details
"""

from typing import Dict

from leaf_common.candidates.constants import ACTION_MARKER
from leaf_common.evaluation.component_evaluator import ComponentEvaluator
from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants
from leaf_common.representation.rule_based.evaluation.rule_evaluator import RuleEvaluator


class RuleSetEvaluator(ComponentEvaluator):
    """
    Rule-set evaluator class.

    This is a stateful evaluator in that calls to evaluate()
    keep some history as to the relevant evaluated_data/observations
    passed in so that time series offsets can be made.
    This state history is kept here in the Evaluator so that
    data does not go back to the service.

    As such we recommend one instance of this Evaluator be retained per RuleSet.

    Also worth noting that invocation of the evaluate() method
    can result in the following fields on RuleSet being changed:
        * times_applied
    Also each Rule's times_applied and age_state can change
    """

    def __init__(self, states: Dict[str, str], actions: Dict[str, str]):
        """
        Constructor

        :param states: XXX Need a good definition here
        :param actions: XXX Need a good definition here
        """

        self._states = states
        self._actions = actions

        self._observation_history = []
        self._observation_history_size = 0

        # This evaluator itself is stateless, so its OK to just create one
        # as an optimization.
        self._rule_evaluator = RuleEvaluator(self._states)

        self.reset()

    def evaluate(self, component: RuleSet, evaluation_data: Dict[str, str]) -> object:
        rule_set = component

        # Set up a state dictionary distilling only the information needed from
        # observation/evaluation_data coming in. This will ultimately get stored
        # in the observation_history member so looking backwards in time is supported.
        #
        # 'current_observation' used to be RuleSet.state, which was very confusing,
        # given that there is another member called 'states' which acts as a definition.
        current_observation = {}

        for key in self._states.keys():
            use_key = int(key)
            current_observation[key] = evaluation_data[use_key]

        action = self.choose_action(rule_set, current_observation)

        rule_set.age_state += 1

        return action

    def _revise_state_minmaxes(self, rule_set: RuleSet,
                               current_observation: Dict[str, str]) -> None:
        """
        Get second state value
        Keep track of min and max for all states
        :param current_observation: the current state
        """

        # Initialize the RuleSet's min/maxes if there is nothing in there.
        # Empty dictionaries evaluate to False, as does None.
        if not rule_set.min_maxes:
            rule_set.min_maxes = {}
            for state in self._states.keys():
                state_dict = {
                    RulesConstants.MIN_KEY: 0.0,
                    RulesConstants.MAX_KEY: 0.0,
                    RulesConstants.TOTAL_KEY: 0.0
                }
                rule_set.min_maxes[state] = state_dict

        empty_dict = {}
        for state in self._states.keys():

            state_dict = rule_set.min_maxes.get(state, empty_dict)
            state_dict[RulesConstants.TOTAL_KEY] = \
                state_dict[RulesConstants.TOTAL_KEY] + float(current_observation[state])

            state_min = state_dict.get(RulesConstants.MIN_KEY, 0.0)
            if current_observation[state] < state_min:
                state_dict[RulesConstants.MIN_KEY] = float(current_observation[state])

            state_max = state_dict.get(RulesConstants.MAX_KEY, 0.0)
            if current_observation[state] > state_max:
                state_dict[RulesConstants.MAX_KEY] = float(current_observation[state])

    def _set_action_in_state(self, action, state):
        """
        Sets the action in state
        :param state: state
        :param action: action
        """
        for act in self._actions:
            state[ACTION_MARKER + act] = act == action

    def _get_action_in_state(self, state):
        """
        Extracts action from state
        :param state: state
        :return: the action
        """
        for action in self._actions:
            if state[ACTION_MARKER + action]:
                return action
        return RulesConstants.NO_ACTION

    def parse_rules(self, rule_set: RuleSet):
        """
        Parse rules
        Used by tests and choose_action()

        :param rule_set: The RuleSet to evaluate
        :return: the chosen action
        """
        poll_dict = {}
        for key in self._actions.keys():
            poll_dict[key] = {RulesConstants.ACTION_COUNT_KEY: 0, RulesConstants.ACTION_COEFFICIENT_KEY: 0.0}
        nb_states = len(self._observation_history) - 1
        if self._observation_history:
            self._revise_state_minmaxes(rule_set, self._observation_history[nb_states])
        if not rule_set.rules:
            raise RuntimeError("Fatal: an empty rule set detected")
        anyone_voted = False

        # Prepare the data going into the RuleEvaluator
        rule_evaluation_data = {
            RulesConstants.OBSERVATION_HISTORY_KEY: self._observation_history,
            RulesConstants.STATE_MIN_MAXES_KEY: rule_set.min_maxes
        }
        for rule in rule_set.rules:
            result = self._rule_evaluator.evaluate(rule, rule_evaluation_data)
            action = result[RulesConstants.ACTION_KEY]
            if action != RulesConstants.NO_ACTION:
                if action in self._actions.keys():
                    poll_dict[action][RulesConstants.ACTION_COUNT_KEY] += 1
                    poll_dict[action][RulesConstants.ACTION_COEFFICIENT_KEY] += \
                        result[RulesConstants.ACTION_COEFFICIENT_KEY]
                    anyone_voted = True
                if action == RulesConstants.LOOKBACK_ACTION:
                    lookback = result[RulesConstants.LOOKBACK_KEY]
                    prev_actions = self._get_action_in_state(self._observation_history[nb_states - lookback])
                    for prev_action in prev_actions:
                        prev_action_poll = prev_action[RulesConstants.ACTION_COUNT_KEY]
                        poll_dict[prev_action][RulesConstants.ACTION_COUNT_KEY] += prev_action_poll
                        poll_dict[prev_action][RulesConstants.ACTION_COEFFICIENT_KEY] += \
                            prev_action[RulesConstants.ACTION_COEFFICIENT_KEY]
                    anyone_voted = True
        if not anyone_voted:
            rule_set.times_applied += 1
            poll_dict[rule_set.default_action][RulesConstants.ACTION_COUNT_KEY] = 1
            poll_dict[rule_set.default_action][RulesConstants.ACTION_COEFFICIENT_KEY] = \
                rule_set.default_action_coefficient
        return poll_dict

    def choose_action(self, rule_set: RuleSet, current_observation: Dict[str, str]):
        """
        Choose an action
        :return: the chosen action
        """
        self._observation_history.append(current_observation)  # copy current state into history
        while len(self._observation_history) > self._observation_history_size:
            index_to_delete = 1
            del self._observation_history[index_to_delete]
        action_to_perform = self.parse_rules(rule_set)
        self._set_action_in_state(action_to_perform,
                                  self._observation_history[len(self._observation_history) - 1])
        # Make sure the dict keys are sorted based on their numeric (and not string) values
        # E.g., we don't want a case where the keys are in this order: '1','10','2'
        # They should be in this order: '1', '2', '10', as, unfortunately, some upstream
        # logic relies on the numeric ordering
        action_to_perform = dict(sorted(action_to_perform.items(), key=lambda x: int(x[0])))
        return action_to_perform

    def reset(self) -> None:
        """
        Reset state per actions config
        """
        self._observation_history = []

        # It'd be nice if this MEM_FACTOR came from configuration
        self._observation_history_size = RulesConstants.MEM_FACTOR * len(self._actions)
