"""
Base class for rule representation
"""

import io
import random
import pickle

from leaf_common.rule_based.condition import Condition, condition_decode, condition_encode

RULE_ELEMENTS = ["condition", "action", "action_lookback"]
THE_LOOKBACK = 1
LOOK_BACK = "lb"
THE_ACTION = 0
NO_ACTION = -1
NUMBER_OF_BUILDING_BLOCK_CONDITIONS = 1


class Rule:
    """
    Rule representation based class.
    """

    def __init__(self, states, actions, max_lookback):
        self.states = states
        self.max_lookback = max_lookback
        self.actions = actions
        self.action = random.choice(list(actions.keys()))
        self.action_lookback = random.randint(0, self.max_lookback)
        self.times_applied = 0
        self.condition_string = []
        for _ in range(0, random.randint(1, NUMBER_OF_BUILDING_BLOCK_CONDITIONS)):
            condition = Condition(states, self.max_lookback)
            self.add_condition(condition)

    def __str__(self):
        return self.get_str(None)

    def get_str(self, min_maxes):
        """
        String representation for rule
        :param min_maxes: A dictionary of domain features minimum and maximum values
        :return: rule.toString()
        """
        if self.action_lookback > 0:
            the_action = " -->  Action[" + str(self.action_lookback) + "]"
        else:
            the_action = " -->  " + self.action
        condition_string = ""
        for condition in self.condition_string:
            condition_string = condition_string + "(" + condition.get_str(min_maxes) + ") "
        times_applied = "   < > "
        if self.times_applied > 0:
            times_applied = "  <" + str(self.times_applied) + "> "
        return times_applied + condition_string + the_action

    def parse(self, er_states, min_maxes):
        """
        Pars a rule
        :param er_states: list of domain states
        :param min_maxes: list of states min and max values
        :return: the result
        """

        for condition in self.condition_string:
            if not condition.parse(er_states, min_maxes):
                return [NO_ACTION, 0]
        nb_states = len(er_states) - 1
        if nb_states < self.action_lookback > 0:
            return [NO_ACTION, 0]
        self.times_applied += 1
        if self.action_lookback == 0:
            return [self.action, 0]
        return [LOOK_BACK, self.action_lookback]

    def copy(self, states, actions):
        """
        Copy a rule
        :param states: A dictionary of domain inputs
        :param actions: A dictionary of domain actions
        :return: the copied rule
        """
        rule = Rule(states, actions, self.max_lookback)
        rule.condition_string = []
        for condition in self.condition_string:
            rule.add_condition(condition.copy(states))
        rule.action = self.action
        rule.action_lookback = self.action_lookback
        return rule

    def add_condition(self, condition):
        """
        Add a condition to the rule in ascending order if not already exists
        :param condition: A condition
        :return: True if successful
        """
        if self.contains(condition):
            return False
        str_new_condition = condition.get_str(None)
        insertion_index = 0
        for i in range(len(self.condition_string)):
            str_condition = self.condition_string[i].get_str(None)
            if str_new_condition < str_condition:
                insertion_index += 1
            else:
                self.condition_string.insert(insertion_index, condition)
                return True
        self.condition_string.append(condition)
        return True

    def contains(self, condition):
        """
        Check if a condition is not already exist in the rule
        :param condition: A condition
        :return: True if exists, False otherwise
        """
        str_condition = "(" + condition.get_str(None) + ")"
        str_rule = self.get_str(None)
        if str_condition in str_rule:
            return True
        return False


def rule_decode(rule_bytes):
    """
    Converts a bag of bytes from a pickled dictionary into a rule
    :param rule_bytes: a bag of bytes
    :return: rule
    """
    rule_stream = io.BytesIO(rule_bytes)
    rule_dict = pickle.load(rule_stream)
    rule = Rule(rule_dict['states'], rule_dict['actions'], rule_dict['max_lookback'])
    rule.condition_string = []
    rule.action = rule_dict['action']
    rule.action_lookback = rule_dict['action_lookback']
    rule.times_applied = rule_dict['times_applied']
    encoded_conditions = rule_dict['condition_string']
    for encoded_condition in encoded_conditions:
        condition = condition_decode(encoded_condition)
        rule.condition_string.append(condition)
    return rule


def rule_encode(rule):
    """
    Converts a rule into bytes corresponding to a pickled dictionary
    :param rule: a rule
    :return: bag of bytes
    """
    rule_dict = {'states': rule.states,
                 'max_lookback': rule.max_lookback,
                 'actions': rule.actions,
                 'action': rule.action,
                 'action_lookback': rule.action_lookback,
                 'times_applied': rule.times_applied,
                 'condition_string': []
                 }
    for condition in rule.condition_string:
        rule_dict['condition_string'].append(condition_encode(condition))
    rule_bytes = pickle.dumps(rule_dict)
    return rule_bytes
