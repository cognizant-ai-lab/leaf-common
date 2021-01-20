
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


class PersistenceMechanism():
    """
    Interface for a particular mechanism of persistence.
    """

    def open_source_for_read(self, read_to_fileobj,
                             file_extension_provider=None):
        """
        :param read_to_fileobj: A fileobj to which we will send all data
                            read in from the persisted instance.
                            Implementations that choose to ignore this
                            must return non-None from this method.
        :param file_extension_provider:
                An implementation of the FileExtensionProvider interface
                which is often related to the Serialization implementation.
        :return: Either:
            1. None, indicating that the file desired does not exist.
            2. Some fileobj opened and ready to receive data which this class
                will fill and close in the restore() method.  Callers must
                use some form of copy() to get the all the data into any
                buffers backing the read_to_fileobj.
            3. The value 1, indicating to the parent class that the file exists,
               and the read_to_fileobj has been already filled with data by
               this call.
        """
        raise NotImplementedError

    def open_dest_for_write(self, send_from_fileobj,
                            file_extension_provider=None):
        """
        :param send_from_fileobj: A fileobj from which we will get all data
                            written out to the persisted instance.
                            Implementations that choose to ignore this
                            must return non-None from this method.
        :param file_extension_provider:
                An implementation of the FileExtensionProvider interface
                which is often related to the Serialization implementation.
        :return: Either:
            1. None, indicating to the parent class that the send_from_fileobj
               has been filled with data by this call.
            2. Some fileobj opened and ready to receive data which this class
                will fill and close in the persist() method.
        """
        raise NotImplementedError

    def must_exist(self):
        """
        :return: False if its OK for a file not to exist.
                 True if a file must exist.
        """
        raise NotImplementedError

    def get_path(self, file_extension_provider=None):
        """
        :param file_extension_provider:
                An implementation of the FileExtensionProvider interface
                which is often related to the Serialization implementation.
        :return: the full path of the entity to store
        """
        raise NotImplementedError
