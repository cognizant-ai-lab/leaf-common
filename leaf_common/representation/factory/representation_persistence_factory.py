"""
See class comment for details.
"""

from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.persistence.interface.persistence import Persistence

from leaf_common.representation.keras_nn.keras_nn_file_persistence import KerasNNFilePersistence
from leaf_common.representation.rule_based.rules_agent_file_persistence import RulesAgentFilePersistence
from leaf_common.representation.structure.structure_file_persistence import StructureFilePersistence


class RepresentationPersistenceFactory():
    """
    Factory class which returns a leaf-common Persistence class
    for the RepresentationType
    """

    def __init__(self, evaluator=None):
        """
        Constructor.

        :param evaluator: optional Evaluator implementation for KerasNN
        """

        # Initialize the map
        self._map = {}

        # Do some simple registrations
        self.register(RepresentationType.KerasNN, KerasNNFilePersistence(evaluator))
        self.register(RepresentationType.NNWeights, KerasNNFilePersistence(evaluator))
        self.register(RepresentationType.Structure, StructureFilePersistence())
        self.register(RepresentationType.RuleBased, RulesAgentFilePersistence())

    def create_persistence(self, rep_type: RepresentationType) -> Persistence:
        """
        Given a RepresentationType, return its register()-ed Persistence
        implementation.

        :param rep_type: A RepresentationType to look up
        :return: A Persistence implementation corresponding to the rep_type
        """

        persistence = self._map.get(rep_type, None)

        if persistence is None:
            raise ValueError(f"Unknown representation_type: {rep_type}")

        return persistence

    def register(self, rep_type: RepresentationType, persistence: Persistence):
        """
        Register a Persistence implementation for a RepresentationType

        :param rep_type: A RepresentationType to use as a key
        :param persistence: A Persistence implementation to use as a value
        """
        self._map[rep_type] = persistence
