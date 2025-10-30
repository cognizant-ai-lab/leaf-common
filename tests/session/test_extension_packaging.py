
# Copyright 2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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
