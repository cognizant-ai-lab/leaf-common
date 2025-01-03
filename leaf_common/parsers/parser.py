
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


class Parser():
    """
    Interface for classes that take an object as input and turn that
    object into some other construct
    """

    def parse(self, input_obj):
        """
        :param input_obj: the string (or other object) to parse

        :return: an object parsed from that string
        """
        raise NotImplementedError
