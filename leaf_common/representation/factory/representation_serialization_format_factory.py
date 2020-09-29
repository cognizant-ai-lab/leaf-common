"""
See class comment for details.
"""

from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.serialization.interface.serialization_format import SerializationFormat

from leaf_common.representation.rule_based.rule_set_serialization_format import RuleSetSerializationFormat
from leaf_common.representation.structure.structure_serialization_format import StructureSerializationFormat


class RepresentationSerializationFormatFactory():
    """
    Factory class which returns a leaf-common SerializationFormat class
    for the RepresentationType
    """

    def __init__(self):
        """
        Constructor.
        """

        # Initialize the map
        self._type_map = {}
        self._extension_map = {}

        # Do some simple registrations
        self.register(RepresentationType.Structure, StructureSerializationFormat())
        self.register(RepresentationType.RuleBased, RuleSetSerializationFormat())

    def create_from_representation_type(self, rep_type: RepresentationType) -> SerializationFormat:
        """
        Given a RepresentationType, return its register()-ed SerializationFormat
        implementation.

        :param rep_type: A RepresentationType to look up
        :return: A SerializationFormat implementation corresponding to the rep_type
        """

        serialization_format = self._type_map.get(rep_type, None)

        if serialization_format is None:
            raise ValueError(f"Unknown representation_type: {rep_type}")

        return serialization_format

    def create_from_filename(self, filename: str) -> SerializationFormat:
        """
        Given a filename, return its register()-ed SerializationFormat
        implementation.

        :param filename: A string filename whose file extension is used as a key for look up
        :return: A SerializationFormat implementation corresponding to the filename
        """

        serialization_format = None
        found_key = None

        for key, value in self._extension_map.items():

            use_key = filename is not None and filename.endswith(key)
            if use_key:
                # Use the longest match of the file extension keys
                # Assume this means more specific
                if found_key is not None and len(key) < len(found_key):
                    use_key = False

            if use_key:
                found_key = key
                serialization_format = value

        if serialization_format is None:
            raise ValueError(f"Unknown file extension in file name: {filename}")

        return serialization_format

    def register(self, rep_type: RepresentationType, serialization_format: SerializationFormat):
        """
        Register a SerializationFormat implementation for a RepresentationType

        :param rep_type: A RepresentationType to use as a key
        :param serialization_format: A SerializationFormat implementation to use as a value
        """
        self._type_map[rep_type] = serialization_format

        extension = serialization_format.get_file_extension()
        self._extension_map[extension] = serialization_format
