
# Copyright (C) 2019-2020 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# ENN-release SDK Software in commercial settings.
#
# END COPYRIGHT
"""
See class comment for details.
"""


class FileExtensionProvider():
    """
    Interface whose implementations give a file extension.
    """

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        raise NotImplementedError
