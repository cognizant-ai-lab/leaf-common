""" Base class for rule representation """

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
        self.state = initial_state
        self.state[RulesEvaluationConstants.AGE_STATE_KEY] = 0
        self.actions = actions
        self.states = states
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
