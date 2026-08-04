
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

from leaf_common.serialization.format.hocon_serialization_format \
    import HoconSerializationFormat


class HoconSerializationFormatTest(TestCase):
    """
    Tests for HoconSerializationFormat.
    """

    HOCON_WITH_QUOTED_KEYS = """
    models {
        "llama3.1" = 1
        "llama3:8b" = 2
        plain_key = 3
    }
    """

    def setUp(self):
        """
        Set up members for tests
        """
        self.serialization = HoconSerializationFormat()
        self.sanitizing = HoconSerializationFormat(sanitize_keys=True)

    @staticmethod
    def as_fileobj(hocon_string):
        """
        :return: a file-like object containing the given HOCON string
        """
        return io.BytesIO(hocon_string.encode("utf-8"))

    def test_assumptions(self):
        """
        Tests serialization format got constructed
        """
        self.assertIsNotNone(self.serialization)

    def test_none_fileobj(self):
        """
        Tests that a None fileobj is handled correctly
        """
        obj = self.serialization.to_object(None)
        self.assertIsNone(obj)

    def test_keys_passed_through_by_default(self):
        """
        Tests that without sanitize_keys, keys come back in whatever form
        pyhocon stores them (historically, keys with forbidden characters
        keep the quotation marks pyhocon embeds in them).
        The comparison strips quotes so the test does not pin pyhocon's
        internal key representation across versions.
        """
        fileobj = self.as_fileobj(self.HOCON_WITH_QUOTED_KEYS)
        obj = self.serialization.to_object(fileobj)

        models = obj.get("models")
        self.assertEqual({"llama3.1", "llama3:8b", "plain_key"},
                         {key.strip('"') for key in models})

    def test_sanitize_keys(self):
        """
        Tests that with sanitize_keys=True on the constructor, keys with
        forbidden characters come back without embedded quotation marks.
        The constructor setting applies to plain to_object() calls, so it
        also reaches callers that invoke to_object() polymorphically
        (e.g. restore())
        """
        fileobj = self.as_fileobj(self.HOCON_WITH_QUOTED_KEYS)
        obj = self.sanitizing.to_object(fileobj)

        models = obj.get("models")
        self.assertEqual({"llama3.1": 1, "llama3:8b": 2, "plain_key": 3},
                         models)

    def test_sanitize_keys_returns_plain_dicts(self):
        """
        Tests that with sanitize_keys=True, nested structures come back
        as regular dicts, not ConfigTrees or OrderedDicts
        """
        hocon_string = """
        outer {
            "inner.quoted" {
                value = 1
            }
            some_list = [ { "key.with.dots" = 2 } ]
        }
        """
        fileobj = self.as_fileobj(hocon_string)
        obj = self.sanitizing.to_object(fileobj)

        outer = obj.get("outer")
        self.assertIs(type(outer), dict)
        self.assertIs(type(outer.get("inner.quoted")), dict)
        self.assertIs(type(outer.get("some_list")[0]), dict)
        self.assertEqual({"key.with.dots": 2}, outer.get("some_list")[0])

    def test_sanitize_keys_root_level_list(self):
        """
        Tests that sanitize_keys=True handles a root-level HOCON array,
        which pyhocon parses to a ConfigList rather than a ConfigTree
        """
        fileobj = self.as_fileobj('[1, 2, { "a.b" = 3 }]')
        obj = self.sanitizing.to_object(fileobj)
        self.assertEqual([1, 2, {"a.b": 3}], obj)
