
# Copyright (C) 2019-2021 Cognizant Digital Business, Evolutionary AI.
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

from leaf_common.serialization.prep.redactor_dictionary_converter \
    import RedactorDictionaryConverter


class RedactorDictionaryConverterTest(TestCase):
    """
    Tests for RedactorDictionaryConverter.
    """

    def setUp(self):
        self.converter = RedactorDictionaryConverter()

    def test_assumptions(self):
        self.assertIsNotNone(self.converter)

    def is_redacted(self, safe_dict, key):
        value = safe_dict.get(key, None)
        is_redacted = (value == "<redacted>")
        return is_redacted

    def test_none(self):
        unsafe_dict = None
        safe_dict = self.converter.to_dict(unsafe_dict)
        self.assertIsNone(safe_dict)

    def test_empty(self):
        unsafe_dict = {}
        safe_dict = self.converter.to_dict(unsafe_dict)
        self.assertIsNotNone(safe_dict)
        self.assertEquals(len(safe_dict.keys()), 0)

    def test_simple(self):

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

        safe_dict = self.converter.to_dict(unsafe_dict)
        self.assertFalse(self.is_redacted(safe_dict, "unredacted"))

        self.assertTrue(self.is_redacted(safe_dict, "ENN_AUTH_CLIENT_ID"))
        self.assertTrue(self.is_redacted(safe_dict, "ENN_AUTH_CLIENT_PASS"))
        self.assertTrue(self.is_redacted(safe_dict, "ENN_LOGIN_USER"))
        self.assertTrue(self.is_redacted(safe_dict, "ENN_USERNAME"))
        self.assertTrue(self.is_redacted(safe_dict, "CF_ACCOUNT"))
        self.assertTrue(self.is_redacted(safe_dict, "CF_API_KEY"))
        self.assertTrue(self.is_redacted(safe_dict, "AWS_ACCESS_KEY_ID"))
        self.assertTrue(self.is_redacted(safe_dict, "AWS_SECRET_ACCESS_KEY"))

    def test_nested(self):

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

        unsafe_dict = {
            "dict": unsafe_dict
        }

        outer_safe_dict = self.converter.to_dict(unsafe_dict)
        safe_dict = outer_safe_dict["dict"]
        self.assertFalse(self.is_redacted(safe_dict, "unredacted"))

        self.assertTrue(self.is_redacted(safe_dict, "ENN_AUTH_CLIENT_ID"))
        self.assertTrue(self.is_redacted(safe_dict, "ENN_AUTH_CLIENT_PASS"))
        self.assertTrue(self.is_redacted(safe_dict, "ENN_LOGIN_USER"))
        self.assertTrue(self.is_redacted(safe_dict, "ENN_USERNAME"))
        self.assertTrue(self.is_redacted(safe_dict, "CF_ACCOUNT"))
        self.assertTrue(self.is_redacted(safe_dict, "CF_API_KEY"))
        self.assertTrue(self.is_redacted(safe_dict, "AWS_ACCESS_KEY_ID"))
        self.assertTrue(self.is_redacted(safe_dict, "AWS_SECRET_ACCESS_KEY"))


    def test_list(self):

        unsafe_dict = {
            "list": [
                0,
                "password",
                {
                    "unredacted": "value in the clear",
                    "ENN_AUTH_CLIENT_ID": "oh this is sooo secret",
                    "ENN_AUTH_CLIENT_PASS": "oh this is sooo secret",
                    "ENN_LOGIN_USER": "oh this is sooo secret",
                    "ENN_USERNAME": "oh this is sooo secret",
                    "CF_ACCOUNT": "oh this is sooo secret",
                    "CF_API_KEY": "oh this is sooo secret",
                    "AWS_ACCESS_KEY_ID": "oh this is sooo secret",
                    "AWS_SECRET_ACCESS_KEY": "oh this is sooo secret",
                    "COMPLETION_SERVICE_SOURCE_CREDENTIALS": "oh this is sooo secret"
                },
                [ ]
            ]
        }

        outer_safe_dict = self.converter.to_dict(unsafe_dict)
        safe_list = outer_safe_dict["list"]
        safe_dict = safe_list[2]
        
        self.assertFalse(self.is_redacted(safe_dict, "unredacted"))

        self.assertTrue(self.is_redacted(safe_dict, "ENN_AUTH_CLIENT_ID"))
        self.assertTrue(self.is_redacted(safe_dict, "ENN_AUTH_CLIENT_PASS"))
        self.assertTrue(self.is_redacted(safe_dict, "ENN_LOGIN_USER"))
        self.assertTrue(self.is_redacted(safe_dict, "ENN_USERNAME"))
        self.assertTrue(self.is_redacted(safe_dict, "CF_ACCOUNT"))
        self.assertTrue(self.is_redacted(safe_dict, "CF_API_KEY"))
        self.assertTrue(self.is_redacted(safe_dict, "AWS_ACCESS_KEY_ID"))
        self.assertTrue(self.is_redacted(safe_dict, "AWS_SECRET_ACCESS_KEY"))
