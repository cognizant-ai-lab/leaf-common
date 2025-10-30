
# Copyright © 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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

from unittest import TestCase

from leaf_common.parsers.canonical_multi_config_parser \
    import CanonicalMultiConfigParser


class CanonicalMultiConfigParserTest(TestCase):
    """
    Tests for the CanonicalMultiConfigParser.
    """

    def setUp(self):
        """
        Set up member variables for each test
        """

        self.key = "my_key"
        self.parser = CanonicalMultiConfigParser(name_key=self.key)

    def test_assumptions(self):
        """
        Test the assumptions the rest of the tests make
        """

        self.assertIsNotNone(self.parser)

    def test_none(self):
        """
        Tests None value
        """

        single_value = None
        canonical = self.parser.parse(single_value)
        self.assertIsNotNone(canonical)
        self.assertIsInstance(canonical, list)

        num = len(canonical)
        self.assertEqual(num, 0)

    def test_single_string(self):
        """
        Tests a single string
        """

        single_value = "Name1"
        canonical = self.parser.parse(single_value)

        self.assertIsNotNone(canonical)
        self.assertIsInstance(canonical, list)

        num = len(canonical)
        self.assertEqual(num, 1)

        first = canonical[0]
        self.assertIsNotNone(first)
        self.assertIsInstance(first, dict)

        name = first.get(self.key, None)
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)
        self.assertEqual(name, single_value)

    def test_list_of_strings(self):
        """
        Tests a list of strings
        """

        single_value = ["Name1", "Name2"]
        canonical = self.parser.parse(single_value)

        self.assertIsNotNone(canonical)
        self.assertIsInstance(canonical, list)

        num = len(canonical)
        self.assertEqual(num, 2)

        first = canonical[0]
        self.assertIsNotNone(first)
        self.assertIsInstance(first, dict)

        name = first.get(self.key, None)
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)
        self.assertEqual(name, "Name1")

        second = canonical[1]
        self.assertIsNotNone(second)
        self.assertIsInstance(second, dict)

        name = second.get(self.key, None)
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)
        self.assertEqual(name, "Name2")

    def test_single_dictionary(self):
        """
        Tests a single dictionary
        """

        single_value = {
            self.key: "Name1",
            "more_config": "tada!"
        }
        canonical = self.parser.parse(single_value)

        self.assertIsNotNone(canonical)
        self.assertIsInstance(canonical, list)

        num = len(canonical)
        self.assertEqual(num, 1)

        first = canonical[0]
        self.assertIsNotNone(first)
        self.assertIsInstance(first, dict)

        name = first.get(self.key, None)
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)
        self.assertEqual(name, "Name1")

        num_keys = len(first.keys())
        self.assertEqual(num_keys, 2)

    def test_multi_dictionary_dict(self):
        """
        Test a single structure of key/config dictionary pairs
        """

        single_value = {
            "Name1": {
                "more_config": True
            },
            "Name2": {
                "more_config": False
            }
        }
        canonical = self.parser.parse(single_value)

        self.assertIsNotNone(canonical)
        self.assertIsInstance(canonical, list)

        num = len(canonical)
        self.assertEqual(num, 2)

        first = canonical[0]
        self.assertIsNotNone(first)
        self.assertIsInstance(first, dict)

        name = first.get(self.key, None)
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)
        self.assertEqual(name, "Name1")

        num_keys = len(first.keys())
        self.assertEqual(num_keys, 2)
        value = first.get("more_config")
        self.assertTrue(value)

        second = canonical[1]
        self.assertIsNotNone(second)
        self.assertIsInstance(second, dict)

        name = second.get(self.key, None)
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)
        self.assertEqual(name, "Name2")

        num_keys = len(second.keys())
        self.assertEqual(num_keys, 2)
        value = second.get("more_config")
        self.assertFalse(value)

    def test_list_of_dictionaries(self):
        """
        Test a list of dictionaries
        """

        single_value = [
            {
                "Name1": {
                    "more_config": True
                }
            },
            {
                "Name2": {
                    "more_config": False
                }
            }
        ]
        canonical = self.parser.parse(single_value)

        self.assertIsNotNone(canonical)
        self.assertIsInstance(canonical, list)

        num = len(canonical)
        self.assertEqual(num, 2)

        first = canonical[0]
        self.assertIsNotNone(first)
        self.assertIsInstance(first, dict)

        name = first.get(self.key, None)
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)
        self.assertEqual(name, "Name1")

        num_keys = len(first.keys())
        self.assertEqual(num_keys, 2)
        value = first.get("more_config")
        self.assertTrue(value)

        second = canonical[1]
        self.assertIsNotNone(second)
        self.assertIsInstance(second, dict)

        name = second.get(self.key, None)
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)
        self.assertEqual(name, "Name2")

        num_keys = len(second.keys())
        self.assertEqual(num_keys, 2)
        value = second.get("more_config")
        self.assertFalse(value)

    def test_alt_list_of_dictionaries(self):
        """
        Tests list of dictionaries in another way
        """

        single_value = [
            {
                self.key: "Name1",
                "more_config": True
            },
            {
                self.key: "Name2",
                "more_config": False
            }
        ]
        canonical = self.parser.parse(single_value)

        self.assertIsNotNone(canonical)
        self.assertIsInstance(canonical, list)

        num = len(canonical)
        self.assertEqual(num, 2)

        first = canonical[0]
        self.assertIsNotNone(first)
        self.assertIsInstance(first, dict)

        name = first.get(self.key, None)
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)
        self.assertEqual(name, "Name1")

        num_keys = len(first.keys())
        self.assertEqual(num_keys, 2)
        value = first.get("more_config")
        self.assertTrue(value)

        second = canonical[1]
        self.assertIsNotNone(second)
        self.assertIsInstance(second, dict)

        name = second.get(self.key, None)
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)
        self.assertEqual(name, "Name2")

        num_keys = len(second.keys())
        self.assertEqual(num_keys, 2)
        value = second.get("more_config")
        self.assertFalse(value)
