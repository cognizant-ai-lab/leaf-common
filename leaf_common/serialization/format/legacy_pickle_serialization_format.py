
# Copyright (C) 2019-2020 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# ENN-release SDK Software in commercial settings.
#
# END COPYRIGHT

import io
import os

# Python 3
import pickle

from leaf_common.serialization.interface.serialization_format \
    import SerializationFormat

from leaf_common.serialization.format.gzip_serialization_format \
    import GzipSerializationFormat


class LegacyPickleSerializationFormat(SerializationFormat):
    """
    Implementation of the SerializationFormat interface which
    (de/)serializes pickled data and the file extension is non-existent.

    We really don't want to use this any more especially since the
    file extension does not tell anyone what the file really is.
    """

    def __init__(self, folder, base_name, must_exist=True,
                    pickle_protocol=2):
        """
        Constructor

        :param folder: directory where file is stored
        :param base_name: base file name for persistence
        :param must_exist: Default True.  When False, if the file does
                not exist upon restore() no exception is raised.
                When True, an exception is raised.
        :param pickle_protocol: the pickle protocol version to use.
                    Default is 2. (Whatever that really means.)
        """

        super().__init__()
        self._must_exist = must_exist
        self._pickle_protocol = pickle_protocol
        self._gzip = GzipSerializationFormat(folder, base_name)


    def from_object(self, obj):
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """

        fileobj = io.BytesIO()

        # Dump gzipped pickle into buffer.
        with self._gzip.from_object(fileobj) as gzfileobj:
            # Write gzipped pickle to buffer
            pickle.dump(obj, gzfileobj, protocol=self._pickle_protocol)

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

        deserialized_object = None

        # un-Gzip from buffer.
        # Then un-pickle from gzip
        with self._gzip.to_object(fileobj) as gzfileobj:
            try:
                deserialized_object = pickle.load(gzfileobj)
            except Exception:
                if not self.must_exist():
                    # If we get an EOFError, that's OK. That just means
                    # the file did not exist yet.
                    pass
                else:
                    raise

        return deserialized_object

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
        # ENN's aboriginal serialization implementation assumed no
        # file extension and gzipped pickle.
        return ""
