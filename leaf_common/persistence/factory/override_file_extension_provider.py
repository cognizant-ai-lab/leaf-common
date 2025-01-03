
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
