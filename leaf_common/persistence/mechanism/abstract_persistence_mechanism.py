
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

import os

from leaf_common.persistence.interface.persistence_mechanism \
    import PersistenceMechanism


class AbstractPersistenceMechanism(PersistenceMechanism):
    """
    Abstract class for a particular mechanism of persistence.

    Implementations should only need to override the two methods:
        open_source_for_read(read_to_fileobj)
        open_dest_for_write(send_from_fileobj)
    """

    def __init__(self, folder, base_name, must_exist=True):
        """
        Constructor

        :param folder: directory where file is stored
        :param base_name: base file name for persistence
        :param must_exist: Default True.  When False, if the file does
                not exist upon restore() no exception is raised.
                When True, an exception is raised.
        """

        super().__init__()

        self.folder = folder
        self.base_name = base_name
        self._must_exist = must_exist

    def open_source_for_read(self, read_to_fileobj,
                             file_extension_provider=None,
                             file_reference: str = None):
        """
        See PersistenceMechanism.open_source_for_read() for details.
        """
        raise NotImplementedError

    def open_dest_for_write(self, send_from_fileobj,
                            file_extension_provider=None,
                            file_reference: str = None):
        """
        See PersistenceMechanism.open_source_for_read() for details.
        """
        raise NotImplementedError

    def must_exist(self):
        """
        :return: False if its OK for a file not to exist.
                 True if a file must exist.
        """
        return self._must_exist

    def get_path(self, file_extension_provider=None, file_reference: str = None):
        """
        :param file_extension_provider:
                An implementation of the FileExtensionProvider interface
                which is often related to the Serialization implementation.
        :param file_reference: An optional file reference string to override
                any file settings fixed at construct time. Default of None
                indicates to resort to implementation's fixed file reference
                settings.
        :return: the full path of the entity to store
        """
        # First determine the path from any fixed settings
        fixed_settings_path = self.folder
        if self.base_name is not None:
            fixed_settings_path = os.path.join(self.folder, self.base_name)

        file_extension = ""
        if file_extension_provider is not None:
            file_extension = file_extension_provider.get_file_extension()

        path = fixed_settings_path + file_extension

        # Examine the optional file reference to see which fixed pieces
        # we need to adopt
        if file_reference is not None:

            file_reference_path = file_reference
            if not file_reference.startswith("/"):
                # Not an Absolute path. Use our folder
                file_reference_path = os.path.join(self.folder, file_reference)

            if not file_reference_path.endswith(file_extension):
                # No file extension, only basename. Use ours
                file_reference_path = file_reference_path + file_extension

            path = file_reference_path

        return path
