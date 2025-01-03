
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

from leaf_common.serialization.interface.deserializer import Deserializer
from leaf_common.serialization.interface.serializer import Serializer
from leaf_common.serialization.interface.file_extension_provider \
    import FileExtensionProvider


class SerializationFormat(Serializer, Deserializer, FileExtensionProvider):
    """
    An interface which combines implementation aspects of a Serializer
    and a Deserializer with a format name for registration.
    """

    def from_object(self, obj):
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """
        raise NotImplementedError

    def to_object(self, fileobj):
        """
        :param fileobj: The file-like object to deserialize.
                It is expected that the file-like object be open
                and be pointing at the beginning of the data
                (ala seek to the beginning).

                After calling this method, the seek pointer
                will be at the end of the data. Closing of the
                fileobj is left to the caller.
        :return: the deserialized object
        """
        raise NotImplementedError

    def get_file_extension(self) -> str:
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".

                While the parent interface allows for returning
                lists, a SerializationFormat implementation should
                only ever have a single file extension associated
                with it.
        """
        raise NotImplementedError
