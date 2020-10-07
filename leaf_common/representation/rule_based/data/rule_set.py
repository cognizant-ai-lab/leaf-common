""" Base class for rule representation """

from typing import Dict
from typing import Tuple


class RuleSet:
    """
    Evolving Rule-based actor class.
    """

    # pylint: disable=too-many-instance-attributes
    # Nine is reasonable in this case.

    def __init__(self, min_maxes: Dict[Tuple[str, str], float] = None):
        """
        Constructor

        :param min_maxes: A dictionary of (state, "min"/"max") to a float value
                    which pre-calibrates the normalization of the conditions.
                    These values are copied and as evaluation proceeds, the
                    internal copy gets updated with new values should the
                    data encountered warrant it.  The default value is None,
                    indicating that we don't know enough about the data to
                    calibrate anything at the outset.
        """

        # Evaluation Metrics used in reproduction
        self.times_applied = 0
        self.age_state = 0

        # Honest-to-goodness Genetic Material
        self.default_action = None
        self.rules = []

        # Initialize the min/maxes
        if min_maxes is not None:
            self.min_maxes = deepcopy(min_maxes)
        else:
            self.min_maxes = {}

    # see https://github.com/PyCQA/pycodestyle/issues/753 for why next line needs noqa
    def to_string(self, states: Dict[str, str] = None) -> str:      # noqa: E252
        """
        String representation for rule

        :param states: An optional dictionary of state definitions seen during evaluation.
        :return: RuleSet.toString()
        """
        rules_str = ""
        for rule in self.rules:
            rules_str = rules_str + rule.to_string(states, self.min_maxes) + "\n"
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
