""" Base class for rule representation """

from typing import Dict
from typing import Tuple


class RuleSet:
    """
    Evolving Rule-based actor class.
    """

    # pylint: disable=too-many-instance-attributes
    # Nine is reasonable in this case.

    def __init__(self):

        # Evaluation Metrics used in reproduction
        self.times_applied = 0
        self.age_state = 0

        # Honest-to-goodness Genetic Material
        self.default_action = None
        self.rules = []

    # see https://github.com/PyCQA/pycodestyle/issues/753 for why next line needs noqa
    def to_string(self, states: Dict[str, str] = None,
                state_min_maxes: Dict[Tuple[str, str], float] = None) -> str:  # noqa: E252
        """
        String representation for rule
        :param min_maxes: A dictionary of domain features minimum and maximum values
        :return: RuleSet.toString()
        """
        rules_str = ""
        for rule in self.rules:
            rules_str = rules_str + rule.to_string(states, state_min_maxes) + "\n"
        times_applied = " <> "
        if self.times_applied > 0:
            times_applied = " <" + str(self.times_applied) + "> "
        rules_str = rules_str + times_applied + "Default Action: " + self.default_action + "\n"
        return rules_str

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        # For now, just use __str__ for __repr__ output, even though they would generally be for different uses
        return self.__str__()
