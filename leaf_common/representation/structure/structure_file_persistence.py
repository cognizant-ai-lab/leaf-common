
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

from leaf_common.persistence.factory.simple_file_persistence import SimpleFilePersistence
from leaf_common.representation.structure.structure_serialization_format import StructureSerializationFormat
from leaf_common.serialization.interface.serialization_format import SerializationFormat


class StructureFilePersistence(SimpleFilePersistence):
    """
    Implementation of the leaf-common Persistence interface which
    saves/restores an evaluated structure to a file.
    """

    def __init__(self, serialization_format: SerializationFormat = None):
        """
        Constructor.

        :param serialization_format: A means of serializing an evolved structure
                by default this is None and a StructureSerializationFormat is used
        """
        use_format = serialization_format
        if use_format is None:
            use_format = StructureSerializationFormat()
        super().__init__(use_format)
