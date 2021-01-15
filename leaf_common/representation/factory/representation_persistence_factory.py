
# Copyright (C) 2019-2020 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# leaf-common SDK Software in commercial settings.
#
# END COPYRIGHT
"""
See class comment for details.
"""
from typing import List

from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.persistence.interface.persistence import Persistence

from leaf_common.representation.factory.representation_file_extension_provider_factory \
    import RepresentationFileExtensionProviderFactory
from leaf_common.representation.rule_based.persistence.rule_set_file_persistence \
    import RuleSetFilePersistence
from leaf_common.representation.structure.structure_file_persistence import StructureFilePersistence


class RepresentationPersistenceFactory(RepresentationFileExtensionProviderFactory):
    """
    Factory class which returns a leaf-common Persistence class
    for the RepresentationType
    """

    def __init__(self):
        """
        Constructor.
        """

        super().__init__()

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
        return super().create_from_representation_type(rep_type)

    def lookup_from_filename(self, filename: str) -> List[Persistence]:
        """
        Given a filename, return a list of potential register()-ed Persistence
        implementations.

        Note that this implementation does not actually open the file
        to examine any self-identifying aspects of the contents, and as
        a single file type (like JSON) has the potential to contain a
        number of different possibilities, this method returns a list
        if it finds anything.

        :param filename: A string filename whose file extension is used as a key for look up
        :return: A list of potential Persistence implementations corresponding to the filename
                 or None if no Persistence implementations are found for the filename
        """
        return super().lookup_from_filename(filename)

    def register(self, rep_type: RepresentationType, persistence: Persistence):
        """
        Register a Persistence implementation for a RepresentationType

        :param rep_type: A RepresentationType to use as a key
        :param persistence: A Persistence implementation to use as a value
        """
        super().register(rep_type, persistence)
