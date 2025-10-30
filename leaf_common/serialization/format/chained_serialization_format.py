
# Copyright 2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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

import os

from leaf_common.serialization.interface.serialization_format \
    import SerializationFormat


class ChainedSerializationFormat(SerializationFormat):
    """
    An implementation of the SerializationFormat interface which chains
    serialization and deserialization through multiple stages.
    """

    def __init__(self):
        self.forward_chain = []

    def add_serialization_format(self, serialization_format):
        """
        :param serialization_format: The SerializationFormat to be
                added to the chain
        """

        if not isinstance(serialization_format, SerializationFormat):
            raise ValueError("Class mismatch in ChainedSerializationFormat")

        self.forward_chain.append(serialization_format)

    def from_object(self, obj):
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """

        fileobj = None

        if len(self.forward_chain) > 0:

            last_buffer = obj

            for serialization_format in self.forward_chain:

                # Convert the most recent buffer to a fileobj
                fileobj = serialization_format.from_object(last_buffer)

                # If the previous buffer was a file-like object, close it.
                if hasattr(last_buffer, 'close'):
                    last_buffer.close()

                last_buffer = fileobj

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

        if len(self.forward_chain) > 0:

            last_buffer = fileobj

            for serialization_format in reversed(self.forward_chain):

                # Convert the most recent buffer to a fileobj
                obj = serialization_format.to_object(last_buffer)

                # If the previous buffer was a file-like object, close it.
                if last_buffer is not None and \
                        hasattr(last_buffer, 'close'):

                    last_buffer.close()

                last_buffer = obj

        return obj

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization format, including the ".".
        """

        extension = ""

        if len(self.forward_chain) > 0:
            for serialization_format in self.forward_chain:
                extension += serialization_format.get_file_extension()

        return extension
