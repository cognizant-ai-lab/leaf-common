"""
See class comment for details.
"""

from leaf_common.persistence.factory.simple_file_persistence import SimpleFilePersistence
from leaf_common.representation.rule_based.rule_set_serialization_format import RuleSetSerializationFormat
from leaf_common.serialization.interface.serialization_format import SerializationFormat


class RuleSetFilePersistence(SimpleFilePersistence):
    """
    Implementation of the leaf-common Persistence interface which
    saves/restores a RuleSet to a file.
    """

    def __init__(self, serialization_format: SerializationFormat = None):
        """
        Constructor.

        :param serialization_format: A means of serializing a RuleSet
                by default this is None and a RuleSetSerializationFormat is used
        """
        use_format = serialization_format
        if use_format is None:
            use_format = RuleSetSerializationFormat()
        super(RuleSetFilePersistence, self).__init__(use_format)
