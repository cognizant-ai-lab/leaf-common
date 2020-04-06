""" Base class for rule representation """

import random
import sys

import jsonpickle
import numpy

from leaf_common.rule_based.condition import THE_MIN, THE_MAX, THE_TOTAL
from leaf_common.rule_based.rule import NO_ACTION, Rule, THE_ACTION, LOOK_BACK, THE_LOOKBACK

RULE_FILTER_FACTOR = 1
MAX_LOOKBACK = 0
NUMBER_OF_BUILDING_BLOCK_RULES = 3
ACTION_MARKER = "a_"
AGE_STATE = "age"
MEM_FACTOR = 100  # max memory cells required


class RulesAgent:
    """
    Evolving Rule-based actor class.
    """

    # pylint: disable=too-many-instance-attributes
    # Nine is reasonable in this case.

    def __init__(self, states, actions, initial_state, uid="rule_based"):
        self.uid = uid
        self.er_states = []
        self.last_action = NO_ACTION
        self.state = initial_state
        self.actions = actions
        self.states = states
        self.state_history_size = MEM_FACTOR * len(self.actions)
        self.state[AGE_STATE] = 0
        self.default_action = random.choice(list(self.actions.keys()))
        self.times_applied = 0
        self.state_min_maxes = {}
        for state in self.states.keys():
            self.state_min_maxes[state, THE_MIN] = 0
            self.state_min_maxes[state, THE_MAX] = 0
            self.state_min_maxes[state, THE_TOTAL] = 0
        self.rules = []
        for _ in range(0, random.randint(1, NUMBER_OF_BUILDING_BLOCK_RULES)):
            rule = Rule(states, actions, MAX_LOOKBACK)
            self.add_rule(rule)

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

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def revise_state_minmaxes(self, current_state):  # Keep track of min and max for all states
        """
        Get second state value
        :param current_state: the current state
        """
        for state in self.states.keys():
            self.state_min_maxes[state, THE_TOTAL] = self.state_min_maxes[state, THE_TOTAL] + current_state[state]
            if current_state[state] < self.state_min_maxes[state, THE_MIN]:
                self.state_min_maxes[state, THE_MIN] = current_state[state]
            if current_state[state] > self.state_min_maxes[state, THE_MAX]:
                self.state_min_maxes[state, THE_MAX] = current_state[state]

    def remove_actions_from_state(self):
        """
        Removes actions from state
        :return: action-less state
        """
        keep = [key for key in self.er_states[0] if not key.startswith(ACTION_MARKER)]
        new_states = []
        for state in self.er_states:
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
        return NO_ACTION

    def parse_rules(self):
        """
        Parse rules
        :return: the chosen action
        """
        poll_dict = dict.fromkeys(self.actions.keys(), 0)
        nb_states = len(self.er_states) - 1
        self.revise_state_minmaxes(self.er_states[nb_states])
        if not self.rules:
            print("Fatal: an empty rule set detected")
            sys.exit(1)
        anyone_voted = False
        for rule in self.rules:
            result = rule.parse(self.er_states, self.state_min_maxes)
            if result[THE_ACTION] != NO_ACTION:
                if result[THE_ACTION] in self.actions.keys():
                    poll_dict[result[THE_ACTION]] += 1
                    anyone_voted = True
                if result[THE_ACTION] == LOOK_BACK:
                    lookback = result[THE_LOOKBACK]
                    poll_dict[self.get_action_in_state(self.er_states[nb_states - lookback])] += 1
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
        self.er_states.append(current_state)  # copy current state into history
        while len(self.er_states) > self.state_history_size:
            index_to_delete = 1
            del self.er_states[index_to_delete]
        action_to_perform = self.parse_rules()
        if action_to_perform == NO_ACTION:
            random_action = random.choice(list(self.actions.keys()))
            action_to_perform = random_action
        self.set_action_in_state(action_to_perform, self.er_states[len(self.er_states) - 1])
        return action_to_perform

    def copy_rules(self, rules):
        """
        Copies a rule set
        :param rules: the source
        :return: the cloned rule
        """
        self.rules = []
        for rule in rules:
            self.add_rule(rule.copy(self.states, self.actions))

    def clone_agent(self, reference_actor):
        """
        Clones a rules_agent
        :param reference_actor: source agent
        :return: cloned rules_agent
        """
        self.state_history_size = reference_actor.state_history_size
        self.default_action = reference_actor.default_action
        self.state_min_maxes = dict(reference_actor.state_min_maxes)
        self.copy_rules(reference_actor.rules)

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

    def act(self, observations, reward, done):
        """
        Act based on the observations
        :param observations: the input state
        :param reward: Not used
        :param done: Not used
        :return: an action
        """
        del reward, done

        for key in self.states.keys():
            self.state[key] = observations[int(key)]
        self.last_action = self.choose_action()
        self.state[AGE_STATE] += 1
        action = numpy.array(list(self.last_action.values()))
        return action

    def reset(self):
        """
        Reset rules agent
        """
        self.er_states = []

    def add_rule(self, rule):
        """
        Add a rule if it's not already exist in the rule set
        :param rule: A rule
        :return: True if successful
        """
        if self.contains(rule):
            return False
        self.rules.append(rule)
        return True

    def contains(self, rule):
        """
        Check to see if a rule set already contains a rule
        :param rule: A rule to be checked
        :return: True if the rule exists in the rule set
        """
        for i in range(len(self.rules)):
            if len(self.rules[i].condition_string) == len(rule.condition_string):
                shortcut = True
                for j in range(len(self.rules[i].condition_string)):
                    if self.rules[i].condition_string[j].get_str(None) != \
                            rule.condition_string[j].get_str(None):
                        shortcut = False
                if shortcut:
                    return True
        return False

    @staticmethod
    def decode(rules_agent_string: str) -> 'RulesAgent':
        """
        Converts a RulesAgent in the form of a JSON string to an instance of RulesAgent.

        :param String containing RulesAgent's state.
        :return: An instance of `RulesAgent` populated from the supplied JSON string.
        """

        return jsonpickle.decode(rules_agent_string, keys=True)

    def encode(self) -> str:
        """
        Converts an individual into a human-readable JSON string
        :return: String containing RulesAgent's state
        """
        return jsonpickle.encode(self, keys=True)

    def save(self, file_name: str) -> None:
        """
        Save this rules agent (and associated members) to a file in JSON format.

        :param file_name: A string containing a reference to a writeable file. The file will be overwritten.
        :return None but current state of this object is dumped as JSON to the file provided.
        """
        json_string = self.encode()
        with open(file_name, 'w') as output_file:
            output_file.write(json_string)

    @staticmethod
    def load(file_name: str) -> 'RulesAgent':
        """
        Load a rules agent from a JSON file

        :param file_name: A string containing a reference to a readable file that contains the agent in serialized
        JSON format
        :return An instance of `RulesAgent` populated from the given file
        """
        with open(file_name, 'r') as input_file:
            return RulesAgent.decode(input_file.read())
