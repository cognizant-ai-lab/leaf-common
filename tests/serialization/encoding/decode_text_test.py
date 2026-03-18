
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
See class comment for details
"""

import io
from unittest import TestCase

from leaf_common.serialization.util.bytes_decoder import BytesDecoder


class DecodeTextTest(TestCase):
    """
    Test class for the BytesDecoder utility class,
    which is responsible for decoding bytes data to strings when the original encoding is unknown.
    """

    def test_decode_utf8_first(self):
        """
        Test that UTF-8 is attempted first and succeeds when the bytes are UTF-8 encoded.
        """
        original_text = 'include "base.conf"\nkey = "Привет"\n'
        fileobj = io.BytesIO(original_text.encode("utf-8"))

        decoded_text, used_encoding = BytesDecoder.decode_bytes(fileobj.read())

        self.assertEqual(decoded_text, original_text)
        self.assertEqual(used_encoding, "utf-8")

    def test_fallback_to_windows_cp1252(self):
        """
        Test that if UTF-8 decoding fails, the decoder falls back to trying Windows-1252 encoding.
        This test uses characters that are valid in Windows-1252 but not in UTF-8 to ensure
        that the fallback is working correctly.
        """
        original_text = 'include "base.conf"\nkey = "café €"\n'
        fileobj = io.BytesIO(original_text.encode("cp1252"))

        decoded_text, used_encoding = BytesDecoder.decode_bytes(fileobj.read())

        self.assertEqual(decoded_text, original_text)
        self.assertEqual(used_encoding, "cp1252")

    def test_fallback_to_latin(self):
        """
        Test that if UTF-8 and Windows-1252 decoding both fail, the decoder falls back to trying Latin-1 encoding.
        This test uses bytes that are valid in Latin-1 but not in UTF-8 or Windows-1252 to ensure
        """
        fileobj = io.BytesIO(b"\x81\x8d\x8f\x90\x9d")

        _, used_encoding = BytesDecoder.decode_bytes(fileobj.read())

        self.assertEqual(used_encoding, "latin-1")

    def test_decode_hocon_windows_cp1252(self):
        """
        Test that a HOCON file encoded in Windows-1252 is correctly decoded,
        and that the resulting text contains the expected HOCON content.
        This test ensures that the decoder can handle real-world HOCON files that may be encoded in Windows-1252,
        which is common for files containing certain special characters.
        """
        hocon_text = (
            'include "base.conf"\n'
            'app {\n'
            '  name = "café"\n'
            '  currency = "€"\n'
            '}\n'
        )

        fileobj = io.BytesIO(hocon_text.encode("cp1252"))

        decoded_text, used_encoding = BytesDecoder.decode_bytes(fileobj.read())

        self.assertEqual(decoded_text, hocon_text)
        self.assertEqual(used_encoding, "cp1252")
        self.assertIn('include "base.conf"', decoded_text)
        self.assertIn('name = "café"', decoded_text)
        self.assertIn('currency = "€"', decoded_text)
