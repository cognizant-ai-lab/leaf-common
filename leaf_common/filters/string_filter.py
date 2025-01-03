
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
Copyright (C) 2021-2023 Cognizant Digital Business, Evolutionary AI.
All Rights Reserved.
Issued under the Academic Public License.

You can be released from the terms, and requirements of the Academic Public
License by purchasing a commercial license.
Purchase of a commercial license is mandatory for any use of the
unileaf-util SDK Software in commercial settings.

END COPYRIGHT
"""


# pylint: disable=too-few-public-methods
class StringFilter:
    """
    Interface whose filter() method takes one string and returns another string
    which is a filtered version of the input.

    These kinds of things are necessary for the following reasons:
    * Tensorflow only likes column names with certain characters in them
    * HTML UI sometimes only likes certain characters in strings.
    """

    def filter(self, in_string: str) -> str:
        """
        :param in_string: an input string to filter
        :return: a filtered version of the in_string, according to implementation policy
        """
        raise NotImplementedError
