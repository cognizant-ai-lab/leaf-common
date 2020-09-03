"""
See class comment for details.
"""

from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.serialization.interface.serialization_format import SerializationFormat

from leaf_common.representation.keras_nn.keras_nn_serialization_format import KerasNNSerializationFormat
from leaf_common.representation.rule_based.rules_agent_serialization_format import RulesAgentSerializationFormat
from leaf_common.representation.structure.structure_serialization_format import StructureSerializationFormat


class RepresentationSerializationFormatFactory():
    """
    Factory class which returns a leaf-common SerializationFormat class
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
        self.register(RepresentationType.KerasNN, KerasNNSerializationFormat(evaluator))
        self.register(RepresentationType.NNWeights, KerasNNSerializationFormat(evaluator))
        self.register(RepresentationType.Structure, StructureSerializationFormat())
        self.register(RepresentationType.RuleBased, RulesAgentSerializationFormat())

    def create_serialization_format(self, rep_type: RepresentationType) -> SerializationFormat:
        """
        Given a RepresentationType, return its register()-ed SerializationFormat
        implementation.

        :param rep_type: A RepresentationType to look up
        :return: A SerializationFormat implementation corresponding to the rep_type
        """

        serialization_format = self._map.get(rep_type, None)

        if serialization_format is None:
            raise ValueError(f"Unknown representation_type: {rep_type}")

        return serialization_format

    def register(self, rep_type: RepresentationType, serialization_format: SerializationFormat):
        """
        Register a SerializationFormat implementation for a RepresentationType

        :param rep_type: A RepresentationType to use as a key
        :param serialization_format: A SerializationFormat implementation to use as a value
        """
        self._map[rep_type] = serialization_format
