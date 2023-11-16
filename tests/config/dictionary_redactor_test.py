
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# leaf-distributed SDK Software in commercial settings.
#
# END COPYRIGHT

from unittest import TestCase

from leaf_common.config.dictionary_redactor import DictionaryRedactor


class DictionaryRedactorTest(TestCase):
    """
    Tests for redacting "sensitive" keys in a data structure
    """

    def setUp(self):
        self.redactor = DictionaryRedactor()

    def test_assumptions(self):
        self.assertIsNotNone(self.redactor)

    def is_redacted(self, safe_dict, key):
        value = safe_dict.get(key, None)
        is_redacted = value == "<redacted>"
        return is_redacted

    def test_redact_dictionary(self):

        unsafe_dict = {
            "unredacted": "value in the clear",
            "ENN_AUTH_CLIENT_ID": "oh this is sooo secret",
            "ENN_AUTH_CLIENT_PASS": "oh this is sooo secret",
            "ENN_LOGIN_USER": "oh this is sooo secret",
            "ENN_USERNAME": "oh this is sooo secret",
            "CF_ACCOUNT": "oh this is sooo secret",
            "CF_API_KEY": "oh this is sooo secret",
            "AWS_ACCESS_KEY_ID": "oh this is sooo secret",
            "AWS_SECRET_ACCESS_KEY": "oh this is sooo secret",
            "COMPLETION_SERVICE_SOURCE_CREDENTIALS": "oh this is sooo secret",
        }

        safe_dict = self.redactor.redact(unsafe_dict)
        self.assertFalse(self.is_redacted(safe_dict, "unredacted"))

        self.assertTrue(self.is_redacted(safe_dict, "ENN_AUTH_CLIENT_ID"))
        self.assertTrue(self.is_redacted(safe_dict, "ENN_AUTH_CLIENT_PASS"))
        self.assertTrue(self.is_redacted(safe_dict, "ENN_LOGIN_USER"))
        self.assertTrue(self.is_redacted(safe_dict, "ENN_USERNAME"))
        self.assertTrue(self.is_redacted(safe_dict, "CF_ACCOUNT"))
        self.assertTrue(self.is_redacted(safe_dict, "CF_API_KEY"))
        self.assertTrue(self.is_redacted(safe_dict, "AWS_ACCESS_KEY_ID"))
        self.assertTrue(self.is_redacted(safe_dict, "AWS_SECRET_ACCESS_KEY"))
        self.assertTrue(self.is_redacted(safe_dict, "COMPLETION_SERVICE_SOURCE_CREDENTIALS"))

    def test_redact_tree(self):

        unsafe_tree = {
            "unredacted": "value in the clear",
            "part1": [
                {"ENN_AUTH_CLIENT_ID": "oh this is sooo secret",
                "ENN_AUTH_CLIENT_PASS": "oh this is sooo secret"}
            ],
            "ENN_LOGIN_USER": "oh this is sooo secret",
            "ENN_USERNAME": "oh this is sooo secret",
            "part2": [
                [
                    [{"CF_ACCOUNT": "oh this is sooo secret"}, 1],
                    {"CF_ACCOUNT1": {"data": "oh this is sooo secret"}},
                    2,
                    {"unredacted": "value in the clear"}
                ]
            ],
            "CF_API_KEY": "oh this is sooo secret",
            "AWS_ACCESS_KEY_ID": "oh this is sooo secret",
            "AWS_SECRET_ACCESS_KEY": "oh this is sooo secret",
            "COMPLETION_SERVICE_SOURCE_CREDENTIALS": "oh this is sooo secret",
        }

        safe_tree = self.redactor.redact(unsafe_tree)
        self.assertFalse(self.is_redacted(safe_tree, "unredacted"))

        self.assertTrue(self.is_redacted(safe_tree["part1"][0], "ENN_AUTH_CLIENT_ID"))
        self.assertTrue(self.is_redacted(safe_tree["part1"][0], "ENN_AUTH_CLIENT_PASS"))
        self.assertTrue(self.is_redacted(safe_tree, "ENN_LOGIN_USER"))
        self.assertTrue(self.is_redacted(safe_tree, "ENN_USERNAME"))
        self.assertTrue(self.is_redacted(safe_tree["part2"][0][0][0], "CF_ACCOUNT"))
        self.assertEqual(safe_tree["part2"][0][0][1], 1)
        self.assertTrue(self.is_redacted(safe_tree["part2"][0][1], "CF_ACCOUNT1"))
        self.assertEqual(safe_tree["part2"][0][2], 2)
        self.assertFalse(self.is_redacted(safe_tree["part2"][0][3], "unredacted"))

        self.assertTrue(self.is_redacted(safe_tree, "CF_API_KEY"))
        self.assertTrue(self.is_redacted(safe_tree, "AWS_ACCESS_KEY_ID"))
        self.assertTrue(self.is_redacted(safe_tree, "AWS_SECRET_ACCESS_KEY"))
        self.assertTrue(self.is_redacted(safe_tree, "COMPLETION_SERVICE_SOURCE_CREDENTIALS"))

        
