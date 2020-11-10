"""
See class comment for details.
"""

from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.persistence.interface.persistence import Persistence

from leaf_common.representation.rule_based.persistence.rule_set_file_persistence \
    import RuleSetFilePersistence
from leaf_common.representation.structure.structure_file_persistence import StructureFilePersistence


class RepresentationPersistenceFactory():
    """
    Factory class which returns a leaf-common Persistence class
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
        self.register(RepresentationType.Structure, StructureFilePersistence())
        self.register(RepresentationType.RuleBased, RuleSetFilePersistence())

    def create_from_representation_type(self, rep_type: RepresentationType) -> Persistence:
        """
        Given a RepresentationType, return its register()-ed Persistence
        implementation.

        :param rep_type: A RepresentationType to look up
        :return: A Persistence implementation corresponding to the rep_type
        """

        persistence = self._type_map.get(rep_type, None)

        if persistence is None:
            raise ValueError(f"Unknown representation_type: {rep_type}")

        return persistence

    def representation_type_from_filename(self, filename: str) -> RepresentationType:
        """
        Given a filename, return its register()-ed RepresentationType

        :param filename: A string filename whose file extension is used as a key for look up
        :return: A RepresentationType corresponding to the filename
        """

        persistence = self.create_from_filename(filename)

        for representation_type, value in self._type_map.items():

            if value == persistence:
                return representation_type
        return None

    def create_from_filename(self, filename: str) -> Persistence:
        """
        Given a filename, return its register()-ed Persistence
        implementation.

        :param filename: A string filename whose file extension is used as a key for look up
        :return: A Persistence implementation corresponding to the filename
        """

        persistence = None
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
                persistence = value

        if persistence is None:
            raise ValueError(f"Unknown file extension in file name: {filename}")

        return persistence

    def register(self, rep_type: RepresentationType, persistence: Persistence):
        """
        Register a Persistence implementation for a RepresentationType

        :param rep_type: A RepresentationType to use as a key
        :param persistence: A Persistence implementation to use as a value
        """
        self._type_map[rep_type] = persistence

        extension = persistence.get_file_extension()
        self._extension_map[extension] = persistence
