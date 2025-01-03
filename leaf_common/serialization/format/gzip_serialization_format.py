
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

import gzip
import os

from leaf_common.serialization.interface.serialization_format \
    import SerializationFormat


class GzipSerializationFormat(SerializationFormat):
    """
    A translating SerializationFormat implementation where the object
    being serialized is a byte stream from a file-like object,
    and the serialization format is gzip.
    from_object() is compression.
    to_object() is decompression.
    """

    def __init__(self, folder, base_name):
        """
        Constructor

        Note that even if we are not writing to a file,
        gzip uses a path as a header element.

        :param folder: directory where file is stored
        :param base_name: base file name for persistence
        """

        self.folder = folder
        self.base_name = base_name

    def from_object(self, obj):
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """
        fileobj = self._open_gzfileobj(obj, 'wb')
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
        obj = None

        if fileobj is not None:
            obj = self._open_gzfileobj(fileobj, 'rb')

        return obj

    def _open_gzfileobj(self, fileobj, mode):
        """
        :param fileobj: a fileobj receiving data from gzip
        :param mode: string representing how gzip should be confugured
                    (read or write). See convenience methods above for usage.
        :return: a fileobj from which g(un)zipped data can be read

        This method uses the string returned by get_path() as a filename to use
        in the gzip header.
        """
        # Even if not writing to a file, gzip uses the path as a header
        # element.
        filename = self.get_path()

        gzfileobj = gzip.GzipFile(filename=str(filename), mode=mode,
                                  fileobj=fileobj)

        return gzfileobj

    def get_path(self):
        """
        :return: the full path of the entity to store
        """
        path = os.path.join(self.folder, self.base_name)
        return path

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".gz"
