
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

from unittest import TestCase

from leaf_common.serialization.prep.redactor_dictionary_converter \
    import RedactorDictionaryConverter


class RedactorDictionaryConverterTest(TestCase):
    """
    Tests for RedactorDictionaryConverter.
    """

    def setUp(self):
        """
        Set up member for tests
        """
        self.converter = RedactorDictionaryConverter()

    def test_assumptions(self):
        """
        Tests converter got constructed
        """
        self.assertIsNotNone(self.converter)

    @staticmethod
    def is_redacted(safe_dict, key):
        """
        :return: True if the value for the key in the dictionary is redacted
        """
        value = safe_dict.get(key, None)
        is_redacted = value == "<redacted>"
        return is_redacted

    def test_none(self):
        """
        Tests that the None value is handled correctly
        """
        unsafe_dict = None
        safe_dict = self.converter.to_dict(unsafe_dict)
        self.assertIsNone(safe_dict)

    def test_empty(self):
        """
        Tests that an empty dictionary value is handled correctly
        """
        unsafe_dict = {}
        safe_dict = self.converter.to_dict(unsafe_dict)
        self.assertIsNotNone(safe_dict)
        self.assertEqual(len(safe_dict.keys()), 0)

    def test_simple(self):
        """
        Tests redaction in a simple dictionary
        """

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
        """
        Tests redaction in nested dictionary
        """

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
        """
        Tests redaction in a list
        """

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
                []
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
