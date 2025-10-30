
# Copyright 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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

import io
import gzip
import os

from leaf_common.serialization.format.gzip_serialization_format \
    import GzipSerializationFormat


class BufferedGzipSerializationFormat(GzipSerializationFormat):
    """
    A slightly different SerializationFormat for Gzip where the
    serialization goes into a buffer.

    from_object() is compression.
    to_object() is decompression.
    """

    def from_object(self, obj):
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """

        my_byte_array = bytearray(obj.read())
        compressed_bytes = gzip.compress(my_byte_array)
        fileobj = io.BytesIO(compressed_bytes)
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

        my_byte_array = bytearray(fileobj.read())
        decompressed_bytes = gzip.decompress(my_byte_array)
        new_fileobj = io.BytesIO(decompressed_bytes)
        new_fileobj.seek(0, os.SEEK_SET)

        return new_fileobj
