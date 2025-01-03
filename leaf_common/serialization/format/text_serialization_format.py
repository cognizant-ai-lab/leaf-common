
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

import io
import os

from leaf_common.serialization.interface.serialization_format \
    import SerializationFormat


class TextSerializationFormat(SerializationFormat):
    """
    Implementation of the SerializationFormat interface which
    (de/)serializes from text data.
    """

    def __init__(self, must_exist=True):
        """
        Constructor

        :param must_exist: Default True.  When False, if the file does
                not exist upon restore() no exception is raised.
                When True, an exception is raised.
        """

        super().__init__()
        self._must_exist = must_exist

    def from_object(self, obj):
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """

        obj_str = str(obj)
        fileobj = io.BytesIO(bytearray(obj_str, 'UTF-8'))

        # Set to the beginning of the memory buffer
        # So next copy can work
        fileobj.seek(0, os.SEEK_SET)

        return fileobj

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

        if fileobj is None:
            return None

        # By default, bytes are returned as string object.
        obj = fileobj.read()
        return obj

    def must_exist(self):
        """
        :return: False if its OK for a file not to exist.
                 True if a file must exist.
        """
        return self._must_exist

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".txt"
