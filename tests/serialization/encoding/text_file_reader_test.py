
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

import asyncio
import os
import tempfile
from unittest import TestCase

from leaf_common.serialization.util.text_file_reader import TextFileReader


# ---------------------------------------------------------------------------
# Encoding fixtures
#
# BytesDecoder tries the encodings utf-8, cp1252, latin-1 in that order and
# returns as soon as one succeeds. The byte sequences below are chosen so
# that each encoding's branch is exercised exactly once:
#
#   * utf-8     : valid UTF-8 multibyte sequence (E2 80 99 -> U+2019)
#   * cp1252    : 0x92 -- invalid as standalone UTF-8, valid in cp1252 (U+2019)
#   * latin-1   : 0x81 -- invalid in UTF-8 *and* in strict cp1252, valid in latin-1 (U+0081)
# ---------------------------------------------------------------------------

UTF8_BYTES = "hello ’world’".encode("utf-8")
UTF8_EXPECTED = "hello ’world’"

CP1252_BYTES = b"hello \x92world\x92"
CP1252_EXPECTED = "hello ’world’"

LATIN1_BYTES = b"hello \x81world\x81"
LATIN1_EXPECTED = LATIN1_BYTES.decode("latin-1")


class TextFileReaderTest(TestCase):
    """
    Test class for the TextFileReader utility, covering both the synchronous
    and asynchronous read methods over all three encodings tried by BytesDecoder
    (utf-8, cp1252, latin-1).
    """

    def setUp(self):
        """Create a fresh temporary directory for each test."""
        # pylint: disable=consider-using-with
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = self._tmp_dir.name

    def tearDown(self):
        """Clean up the temporary directory created in setUp."""
        self._tmp_dir.cleanup()

    def _write_bytes(self, content: bytes, filename: str = "sample.txt") -> str:
        """Write raw bytes to a file in the per-test temp directory and return its path."""
        path = os.path.join(self.tmp_path, filename)
        with open(path, "wb") as fileobj:
            fileobj.write(content)
        return path

    # -----------------------------------------------------------------------
    # read_text_file (synchronous)
    # -----------------------------------------------------------------------

    def test_read_text_file_decodes_utf8(self):
        """A UTF-8 encoded file is decoded via the utf-8 branch."""
        path = self._write_bytes(UTF8_BYTES)
        self.assertEqual(TextFileReader.read_text_file(path), UTF8_EXPECTED)

    def test_read_text_file_decodes_cp1252(self):
        """A cp1252-only byte sequence falls through utf-8 and is decoded as cp1252."""
        path = self._write_bytes(CP1252_BYTES)
        self.assertEqual(TextFileReader.read_text_file(path), CP1252_EXPECTED)

    def test_read_text_file_decodes_latin1(self):
        """A latin-1-only byte sequence falls through utf-8 and cp1252, decoded as latin-1."""
        path = self._write_bytes(LATIN1_BYTES)
        self.assertEqual(TextFileReader.read_text_file(path), LATIN1_EXPECTED)

    def test_read_text_file_empty_file_returns_empty_string(self):
        """An empty file decodes to an empty string."""
        path = self._write_bytes(b"")
        self.assertEqual(TextFileReader.read_text_file(path), "")

    def test_read_text_file_raises_file_not_found(self):
        """A missing file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            TextFileReader.read_text_file(os.path.join(self.tmp_path, "does_not_exist.txt"))

    # -----------------------------------------------------------------------
    # async_read_text_file
    # -----------------------------------------------------------------------

    def test_async_read_text_file_decodes_utf8(self):
        """A UTF-8 encoded file is decoded via the utf-8 branch (async)."""
        path = self._write_bytes(UTF8_BYTES)
        result = asyncio.run(TextFileReader.async_read_text_file(path))
        self.assertEqual(result, UTF8_EXPECTED)

    def test_async_read_text_file_decodes_cp1252(self):
        """A cp1252-only byte sequence falls through utf-8 and is decoded as cp1252 (async)."""
        path = self._write_bytes(CP1252_BYTES)
        result = asyncio.run(TextFileReader.async_read_text_file(path))
        self.assertEqual(result, CP1252_EXPECTED)

    def test_async_read_text_file_decodes_latin1(self):
        """A latin-1-only byte sequence falls through utf-8 and cp1252, decoded as latin-1 (async)."""
        path = self._write_bytes(LATIN1_BYTES)
        result = asyncio.run(TextFileReader.async_read_text_file(path))
        self.assertEqual(result, LATIN1_EXPECTED)

    def test_async_read_text_file_empty_file_returns_empty_string(self):
        """An empty file decodes to an empty string (async)."""
        path = self._write_bytes(b"")
        result = asyncio.run(TextFileReader.async_read_text_file(path))
        self.assertEqual(result, "")

    def test_async_read_text_file_raises_file_not_found(self):
        """A missing file raises FileNotFoundError (async)."""
        with self.assertRaises(FileNotFoundError):
            asyncio.run(
                TextFileReader.async_read_text_file(
                    os.path.join(self.tmp_path, "does_not_exist.txt")
                )
            )
