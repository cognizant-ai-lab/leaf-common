
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
from leaf_common.serialization.interface.serialization_format import SerializationFormat

from leaf_common.representation.factory.representation_file_extension_provider_factory \
    import RepresentationFileExtensionProviderFactory
from leaf_common.representation.rule_based.serialization.rule_set_serialization_format \
    import RuleSetSerializationFormat
from leaf_common.representation.structure.structure_serialization_format import StructureSerializationFormat


class RepresentationSerializationFormatFactory(RepresentationFileExtensionProviderFactory):
    """
    Factory class which returns a leaf-common SerializationFormat class
    for the RepresentationType
    """

    def __init__(self):
        """
        Constructor.
        """

        super().__init__()

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
        return super().create_from_representation_type(rep_type)

    def lookup_from_filename(self, filename: str) -> List[SerializationFormat]:
        """
        Given a filename, return a list of potential register()-ed
        SerializationFormat implementations.

        Note that this implementation does not actually open the file
        to examine any self-identifying aspects of the contents, and as
        a single file type (like JSON) has the potential to contain a
        number of different possibilities, this method returns a list
        if it finds anything.

        :param filename: A string filename whose file extension is used as a key
                 for look up
        :return: A SerializationFormat implementation corresponding to the filename
        :return: A list of potential SerializationFormat implementations
                 corresponding to the filename or None if no Persistence
                 implementations are found for the filename
        """
        return super().lookup_from_filename(filename)

    def register(self, rep_type: RepresentationType, serialization_format: SerializationFormat):
        """
        Register a SerializationFormat implementation for a RepresentationType

        :param rep_type: A RepresentationType to use as a key
        :param serialization_format: A SerializationFormat implementation to use as a value
        """
        super().register(rep_type, serialization_format)
