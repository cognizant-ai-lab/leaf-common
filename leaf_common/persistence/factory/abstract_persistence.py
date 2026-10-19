
# Copyright © 2019-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# END COPYRIGHT
"""
See class comment for details.
"""

from typing import Any
from typing import IO

import io
import os
import shutil

from leaf_common.persistence.interface.persistence \
    import Persistence
from leaf_common.persistence.factory.override_file_extension_provider \
    import OverrideFileExtensionProvider
from leaf_common.persistence.interface.persistence_mechanism \
    import PersistenceMechanism
from leaf_common.serialization.interface.file_extension_provider \
    import FileExtensionProvider
from leaf_common.serialization.interface.serialization_format \
    import SerializationFormat


class AbstractPersistence(Persistence):
    """
    Partial implementation of the Persistence interface which
    saves some serialized data for an object via some persistence mechanism.

    Implementations should only need to override the method:
        get_serialization_format()
    """

    def __init__(self, persistence_mechanism: PersistenceMechanism, use_file_extension: str = None) -> None:
        """
        Constructor

        :param persistence_mechanism: the PersistenceMechanism to use
                for storage
        :param use_file_extension: Use the provided string instead of the
                standard file extension for the format. Default is None,
                indicating the standard file extension for the format should
                be used.
        """

        super().__init__()
        self._mechanism: PersistenceMechanism = persistence_mechanism
        self.use_file_extension: str = use_file_extension

    def get_serialization_format(self) -> SerializationFormat:
        """
        :return: The SerializationFormat instance to be used in persist()
                 and restore()
        """
        raise NotImplementedError

    def persist(self, obj: Any, file_reference: str = None) -> str:
        """
        Persists the object passed in.

        :param obj: an object to persist
        :param file_reference: An optional file reference string to override
                any file settings fixed at construct time. Default of None
                indicates to resort to implementation's fixed file reference
                settings.
        """

        serialization: SerializationFormat = self.get_serialization_format()
        file_extension_provider: FileExtensionProvider = self.get_file_extension_provider()

        buffer_fileobj: IO = serialization.from_object(obj)
        with buffer_fileobj:

            # Write contents from buffer.
            dest_fileobj: IO = self._mechanism.open_dest_for_write(buffer_fileobj,
                                                                   file_extension_provider,
                                                                   file_reference)
            if dest_fileobj is not None:
                with dest_fileobj:
                    shutil.copyfileobj(buffer_fileobj, dest_fileobj)

        path: str = self._mechanism.get_path(file_extension_provider=file_extension_provider,
                                             file_reference=file_reference)
        return path

    def restore(self, file_reference: str = None) -> object:
        """
        :param file_reference: An optional file reference string to override
                any file settings fixed at construct time. Default of None
                indicates to resort to implementation's fixed file reference
                settings.
        :return: an object from some persisted store
        """

        previous_state: Any = None
        serialization: SerializationFormat = self.get_serialization_format()
        file_extension_provider: FileExtensionProvider = self.get_file_extension_provider()

        buffer_fileobj: io.BytesIO
        with io.BytesIO() as buffer_fileobj:
            # Read data into buffer.
            source_fileobj: Any = self._mechanism.open_source_for_read(buffer_fileobj,
                                                                       file_extension_provider,
                                                                       file_reference)
            dest_obj: IO = None
            if source_fileobj is not None:

                # Check to see if the source_fileobj is a file-like object
                # If so copy into the buffer and set the seek pointer
                # to the start of the buffer
                if hasattr(source_fileobj, 'close'):
                    with source_fileobj:
                        shutil.copyfileobj(source_fileobj, buffer_fileobj)

                    # Set to the beginning of the memory buffer
                    # So next copy can work
                    buffer_fileobj.seek(0, os.SEEK_SET)
                else:
                    # We assume that open_source_for_read() has copied the
                    # data into the buffer_fileobj already
                    pass
                dest_obj = buffer_fileobj

            previous_state = serialization.to_object(dest_obj)

        return previous_state

    def get_file_reference(self, file_reference: str = None) -> str:
        """
        :param file_reference: An optional file reference string to override
                any file settings fixed at construct time. Default of None
                indicates to resort to implementation's fixed file reference
                settings.
        :return: A string reference to the file that would be accessed
                by this instance.
        """
        file_extension_provider: FileExtensionProvider = self.get_file_extension_provider()
        file_reference = self._mechanism.get_path(file_extension_provider,
                                                  file_reference)
        return file_reference

    def get_file_extension_provider(self) -> FileExtensionProvider:
        """
        :return: The appropriate FileExtensionProvider for the context
        """

        file_extension_provider: FileExtensionProvider = None
        if self.use_file_extension is not None:
            file_extension_provider = OverrideFileExtensionProvider(
                self.use_file_extension)
        else:
            file_extension_provider = self.get_serialization_format()

        return file_extension_provider
