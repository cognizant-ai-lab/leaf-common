
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

    def register(self, rep_type: RepresentationType, file_extension_provider: SerializationFormat):
        """
        Register a SerializationFormat implementation for a RepresentationType

        :param rep_type: A RepresentationType to use as a key
        :param file_extension_provider: A SerializationFormat implementation to use as a value
        """
        super().register(rep_type, file_extension_provider)
