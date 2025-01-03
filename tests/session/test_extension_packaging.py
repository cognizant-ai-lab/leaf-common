
# Copyright (C) 2019-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# leaf-common SDK Software in commercial settings.
#
# END COPYRIGHT
"""
Unit tests for ExtensionPackaging class
"""

from unittest import TestCase

from leaf_common.session.extension_packaging import ExtensionPackaging


class TestExtensionPackaging(TestCase):
    """
    Unit tests for ExtensionPackaging class
    """
    def test_str_to_extension_bytes_roundtrip(self):
        """
        Verify that we can convert to and from extension bytes
        """
        test_string = 'hello world'
        result = ExtensionPackaging().to_extension_bytes(test_string)
        self.assertEqual(bytes(test_string, 'utf-8'), result)

        result2 = ExtensionPackaging().from_extension_bytes(result, out_type=str)
        self.assertEqual(test_string, result2)
