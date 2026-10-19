
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

from leaf_common.serialization.interface.file_extension_provider \
    import FileExtensionProvider


class PersistenceMechanism():
    """
    Interface for a particular mechanism of persistence.
    """

    def open_source_for_read(self, read_to_fileobj: IO,
                             file_extension_provider: FileExtensionProvider = None,
                             file_reference: str = None) -> Any:
        """
        :param read_to_fileobj: A fileobj to which we will send all data
                            read in from the persisted instance.
                            Implementations that choose to ignore this
                            must return non-None from this method.
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
        raise NotImplementedError

    def open_dest_for_write(self, send_from_fileobj: IO,
                            file_extension_provider: FileExtensionProvider = None,
                            file_reference: str = None) -> IO:
        """
        :param send_from_fileobj: A fileobj from which we will get all data
                            written out to the persisted instance.
                            Implementations that choose to ignore this
                            must return non-None from this method.
        :param file_extension_provider:
                An implementation of the FileExtensionProvider interface
                which is often related to the Serialization implementation.
        :param file_reference: An optional file reference string to override
                any file settings fixed at construct time. Default of None
                indicates to resort to implementation's fixed file reference
                settings.
        :return: Either:
            1. None, indicating to the parent class that the send_from_fileobj
               has been filled with data by this call.
            2. Some fileobj opened and ready to receive data which this class
                will fill and close in the persist() method.
        """
        raise NotImplementedError

    def must_exist(self) -> bool:
        """
        :return: False if its OK for a file not to exist.
                 True if a file must exist.
        """
        raise NotImplementedError

    def get_path(self, file_extension_provider: FileExtensionProvider = None, file_reference: str = None) -> str:
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
        raise NotImplementedError
