
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
import logging
import os

from leaf_common.persistence.mechanism.abstract_persistence_mechanism \
    import AbstractPersistenceMechanism


class LocalFilePersistenceMechanism(AbstractPersistenceMechanism):
    """
    Implementation of AbstractPersistenceMechanism which
    saves objects to a local file.
    """

    def open_source_for_read(self, read_to_fileobj,
                             file_extension_provider=None,
                             file_reference: str = None):
        """
        :param read_to_fileobj: A fileobj into which we will put all data
                            read in from the persisted instance.
        :param file_extension_provider:
                An implementation of the FileExtensionProvider interface
                which is often related to the Serialization implementation.
        :param file_reference: An optional file reference string to override
                any file settings fixed at construct time. Default of None
                indicates to resort to implementation's fixed file reference
                settings.
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
        path = self.get_path(file_extension_provider, file_reference)
        logger = logging.getLogger(__name__)
        logger.info("Reading %s", str(path))

        fileobj = None
        try:
            # pylint: disable=consider-using-with
            fileobj = open(path, 'rb')
        except FileNotFoundError as ex:
            if self.must_exist():
                raise ex

        return fileobj

    def open_dest_for_write(self, send_from_fileobj,
                            file_extension_provider=None,
                            file_reference: str = None):
        """
        :param send_from_fileobj: A fileobj from which we will get all data
                            written out to the persisted instance.
        :param file_extension_provider:
                An implementation of the FileExtensionProvider interface
                which is often related to the Serialization implementation.
        :param file_reference: An optional file reference string to override
                any file settings fixed at construct time. Default of None
                indicates to resort to implementation's fixed file reference
                settings.
        :return: the fileobj representing the local file, indicating to the
                parent class that the send_from_fileobj has not yet been filled
                with data by this call.
        """
        path = self.get_path(file_extension_provider, file_reference)
        logger = logging.getLogger(__name__)
        logger.info("Writing %s", str(path))

        dirs = os.path.dirname(path)
        os.makedirs(dirs, exist_ok=True)

        # Allow for string or bytes as input
        writestyle = "wb"
        if isinstance(send_from_fileobj, io.StringIO):
            writestyle = "w"

        return open(path, writestyle)
