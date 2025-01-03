
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


class RawBytesSerializationFormat(SerializationFormat):
    """
    An implementation of the SerializationFormat interface which provides
    a Serializer and a Deserializer implementations under one roof
    for taking an object back and forth from its raw bytes.

    We expect this to be called largely with image data.
    """

    def from_object(self, obj):
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """

        # Make a file-like object out of the input object's bytes
        fileobj = obj
        if not isinstance(obj, io.BytesIO):
            my_bytes = obj
            if not isinstance(obj, bytes) and \
               not isinstance(obj, bytearray):
                if isinstance(obj, str):
                    my_bytes = bytes(obj, 'utf-8')
                else:
                    my_bytes = bytes(obj)

            fileobj = io.BytesIO(my_bytes)

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

        # DEF:Need to figure this out for full symmetry,
        #     but not urgent given that we care mostly about writing image data
        raise NotImplementedError

    def get_file_extension(self):
        """
        There are no standard extensions for raw bytes, so
        we leave it to the caller to supply the extension.

        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ""
