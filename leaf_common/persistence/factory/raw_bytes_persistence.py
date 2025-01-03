
# Copyright (C) 2019-2025 Cognizant Digital Business, Evolutionary AI.
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

from leaf_common.persistence.factory.abstract_persistence \
    import AbstractPersistence
from leaf_common.serialization.format.raw_bytes_serialization_format \
    import RawBytesSerializationFormat


class RawBytesPersistence(AbstractPersistence):
    """
    Implementation of the AbstractPersistence class which
    saves raw bytes data of an object via some persistence mechanism.
    """

    def __init__(self, persistence_mechanism, use_file_extension=None):
        """
        Constructor

        :param persistence_mechanism: the PersistenceMechanism to use
                for storage
        :param use_file_extension: Use the provided string instead of the
                standard file extension for the format. Default is None,
                indicating the standard file extension for the format should
                be used.
        """

        super().__init__(persistence_mechanism,
                         use_file_extension=use_file_extension)
        self._serialization = RawBytesSerializationFormat()

    def get_serialization_format(self):
        return self._serialization

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".",
                *or* a list of these strings that are considered valid
                file extensions.
        """
        return self._serialization.get_file_extension()
