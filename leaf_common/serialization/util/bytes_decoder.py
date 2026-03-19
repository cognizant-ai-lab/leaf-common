
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
    Utility class for best-effort decoding of bytes to a string when the original encoding is
    unknown. The encodings listed in ``COMMON_ENCODINGS`` are tried in order until one
    succeeds.

    Note that the default list includes ``latin-1``, which can decode any byte sequence.
    This means decoding is expected to always succeed, but the resulting text may be
    meaningless if the input was not actually text or used an unexpected encoding.
    """

    COMMON_ENCODINGS = [
        "utf-8",
        "cp1252",
        "latin-1"
    ]

    @staticmethod
    def decode_bytes(bytes_data, source_name: str = "") -> Tuple[str, str]:
        """
        Decodes the given bytes data to a string by sequentially trying the encodings listed
        in :attr:`COMMON_ENCODINGS` and returning as soon as one succeeds.

        With the default encodings (including ``latin-1``), this method is expected to always
        return a decoded string, although the content may be garbled for non-text or
        unexpectedly encoded inputs. The final ``UnicodeDecodeError`` is only raised if none
        of the configured encodings can decode the data.

        :param bytes_data: The bytes data to decode.
        :param source_name: Optional name of the source of the bytes data, used for logging purposes.
        :return: The tuple of decoded string and the encoding used for decoding.
        """
        for encoding in BytesDecoder.COMMON_ENCODINGS:
            try:
                return bytes_data.decode(encoding), encoding
            except UnicodeDecodeError:
                continue

        raise UnicodeError(f"Unable to decode bytes data from source '{source_name}'")
