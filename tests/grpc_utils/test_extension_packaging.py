"""
Unit tests for ExtensionPackaging class
"""

from unittest import TestCase

from leaf_common.grpc_utils.extension_packaging import ExtensionPackaging


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
