
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

from leaf_common.serialization.interface.file_extension_provider \
    import FileExtensionProvider


class OverrideFileExtensionProvider(FileExtensionProvider):
    """
    Implementation of the FileExtensionProvider interface
    that gives a custom file extension
    """

    def __init__(self, file_extension):
        """
        :param file_extension: Use the provided string instead of the
                standard file extension for the format.
        """
        self.file_extension = file_extension

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return self.file_extension
