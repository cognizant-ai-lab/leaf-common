
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
from typing import List

from unittest import TestCase

from leaf_common.parsers.boolean_parser import BooleanParser


class BooleanParserTest(TestCase):
    """
    Tests for the BooleanParser.

    Covers the None case, clean truthy/falsy strings, case-insensitivity,
    strings padded with leading/trailing whitespace (GitHub issue #182),
    unrecognized strings, and non-string input.
    """

    def setUp(self) -> None:
        """
        Set up member variables for each test
        """

        self.parser: BooleanParser = BooleanParser()

    def test_assumptions(self) -> None:
        """
        Test the assumptions the rest of the tests make
        """

        self.assertIsNotNone(self.parser)

    def test_none(self) -> None:
        """
        Tests that None parses as False
        """

        result: bool = self.parser.parse(None)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_clean_true_strings(self) -> None:
        """
        Tests that each recognized truthy spelling parses as True
        when there is no surrounding whitespace.
        """

        true_strings: List[str] = ['true', '1', 'on', 'yes']
        for one_string in true_strings:
            with self.subTest(value=one_string):
                result: bool = self.parser.parse(one_string)
                self.assertIsInstance(result, bool)
                self.assertTrue(result)

    def test_clean_false_strings(self) -> None:
        """
        Tests that each recognized falsy spelling parses as False
        when there is no surrounding whitespace.
        """

        false_strings: List[str] = ['false', '0', 'off', 'no']
        for one_string in false_strings:
            with self.subTest(value=one_string):
                result: bool = self.parser.parse(one_string)
                self.assertIsInstance(result, bool)
                self.assertFalse(result)

    def test_mixed_case_strings(self) -> None:
        """
        Tests that matching is case-insensitive.
        """

        true_strings: List[str] = ['True', 'TRUE', 'tRuE', 'Yes', 'YES', 'On', 'ON']
        for one_string in true_strings:
            with self.subTest(value=one_string):
                self.assertTrue(self.parser.parse(one_string))

        false_strings: List[str] = ['False', 'FALSE', 'fAlSe', 'No', 'NO', 'Off', 'OFF']
        for one_string in false_strings:
            with self.subTest(value=one_string):
                self.assertFalse(self.parser.parse(one_string))

    def test_true_strings_with_whitespace(self) -> None:
        """
        Tests that truthy spellings padded with leading and/or trailing
        whitespace still parse as True.

        This is the regression test for GitHub issue #182, where
        parse("true ") and parse(" 1") used to return False.
        """

        padded_true_strings: List[str] = [
            'true ',            # trailing space (the case from the issue)
            ' 1',               # leading space (the case from the issue)
            ' on ',             # both sides
            '\tyes',            # leading tab
            'true\n',           # trailing newline, as from a .env line
            '\r\nyes\r\n',      # Windows line endings
            '   TRUE   ',       # padding combined with mixed case
            ' \t 1 \n ',        # mixed whitespace characters
        ]
        for one_string in padded_true_strings:
            with self.subTest(value=repr(one_string)):
                result: bool = self.parser.parse(one_string)
                self.assertIsInstance(result, bool)
                self.assertTrue(result)

    def test_false_strings_with_whitespace(self) -> None:
        """
        Tests that falsy spellings padded with leading and/or trailing
        whitespace still parse as False, and remain a bool.
        """

        padded_false_strings: List[str] = [
            'false ',
            ' 0',
            ' off ',
            '\tno',
            'false\n',
            '\r\nno\r\n',
            '   FALSE   ',
            ' \t 0 \n ',
        ]
        for one_string in padded_false_strings:
            with self.subTest(value=repr(one_string)):
                result: bool = self.parser.parse(one_string)
                self.assertIsInstance(result, bool)
                self.assertFalse(result)

    def test_unrecognized_strings(self) -> None:
        """
        Tests that strings which match neither the truthy nor the falsy
        set parse as False, regardless of whitespace.

        Note that only *surrounding* whitespace is stripped; whitespace
        inside a value (e.g. "tru e") still prevents a match.
        """

        unrecognized_strings: List[str] = [
            '',                 # empty
            ' ',                # whitespace-only
            '\t\n',             # whitespace-only, other characters
            'maybe',
            'tru e',            # internal whitespace is not stripped
            'yes please',
            'true false',
            '2',
            '-1',
            'truthy',
            'none',
            'null',
        ]
        for one_string in unrecognized_strings:
            with self.subTest(value=repr(one_string)):
                result: bool = self.parser.parse(one_string)
                self.assertIsInstance(result, bool)
                self.assertFalse(result)

    def test_non_string_objects(self) -> None:
        """
        Tests that non-string, non-None input falls back to Python truthiness.
        """

        truthy_objects: List[Any] = [True, 1, 2, -1, 1.5, [1], {'a': 1}, (0,), 'x'.encode()]
        for one_object in truthy_objects:
            with self.subTest(value=repr(one_object)):
                result: bool = self.parser.parse(one_object)
                self.assertIsInstance(result, bool)
                self.assertTrue(result)

        falsy_objects: List[Any] = [False, 0, 0.0, [], {}, (), b'']
        for one_object in falsy_objects:
            with self.subTest(value=repr(one_object)):
                result: bool = self.parser.parse(one_object)
                self.assertIsInstance(result, bool)
                self.assertFalse(result)
