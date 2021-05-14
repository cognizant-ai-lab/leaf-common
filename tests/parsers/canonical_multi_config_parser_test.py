
# Copyright (C) 2019-2021 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# leaf-common SDK Software in commercial settings.
#
# END COPYRIGHT

from unittest import TestCase

from servicecommon.parsers.canonical_multi_config_parser \
    import CanonicalMultiConfigParser


class CanonicalMultiConfigParserTest(TestCase):
    """
    Tests for the CanonicalMultiConfigParser.
    """

    def setUp(self):

        self.key = "my_key"
        self.parser = CanonicalMultiConfigParser(name_key=self.key)


    def test_assumptions(self):

        self.assertIsNotNone(self.parser)


    def test_none(self):
        single_value = None
        canonical = self.parser.parse(single_value)
        self.assertIsNotNone(canonical)
        self.assertIsInstance(canonical, list)

        num = len(canonical)
        self.assertEqual(num, 0)


    def test_single_string(self):

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
