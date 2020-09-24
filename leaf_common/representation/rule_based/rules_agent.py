""" Base class for rule representation """


class RulesAgent:
    """
    Evolving Rule-based actor class.
    """

    # pylint: disable=too-many-instance-attributes
    # Nine is reasonable in this case.

    def __init__(self, states, actions, uid="rule_based"):

        # We might be able to leave uid to the service infrastructure
        # for enclosing candidates
        self.uid = uid

        # These might be able to come from config as opposed to
        # being trucked around by each individual over the wire
        self.actions = actions
        self.states = states

        # Evaluation Metrics used in reproduction
        self.times_applied = 0
        self.age_state = 0

        # Honest-to-goodness Genetic Material
        self.default_action = None
        self.rules = []

    def get_str(self, state_min_maxes=None):
        rules_str = ""
        for rule in self.rules:
            rules_str = rules_str + rule.get_str(state_min_maxes) + "\n"
        times_applied = " <> "
        if self.times_applied > 0:
            times_applied = " <" + str(self.times_applied) + "> "
        rules_str = rules_str + times_applied + "Default Action: " + self.default_action + "\n"
        return rules_str

    def __str__(self):
        return self.get_str()

    def __repr__(self):
        # For now, just use __str__ for __repr__ output, even though they would generally be for different uses
        return self.__str__()
