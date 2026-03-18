
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

from typing import Tuple


class BytesDecoder:
    """
    Utility class for decoding bytes to a string if bytes original encoding is unknown.
    By default, we will try for UTF-8 encoding, but if that fails, we go over the list
    of widely used encodings.
    """

    COMMON_ENCODINGS = [
        "utf-8",
        "cp1252",
        "latin-1"
    ]

    @staticmethod
    def decode_bytes(bytes_data, source_name: str = "") -> Tuple[str, str]:
        """
        Decodes the given bytes data to a string
        sequentially using the list of common encodings until one succeeds or all fail.

        :param bytes_data: The bytes data to decode.
        :source_name: Optional name of the source of the bytes data, used for logging purposes.
        :return: The tuple of decoded string and the encoding used for decoding.
        """
        for encoding in BytesDecoder.COMMON_ENCODINGS:
            try:
                return bytes_data.decode(encoding), encoding
            except UnicodeDecodeError:
                continue

        raise UnicodeDecodeError(f"Unable to decode bytes data from source '{source_name}'")
