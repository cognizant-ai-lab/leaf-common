
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

from leaf_common.filters.string_filter import StringFilter


# pylint: disable=too-few-public-methods
class StripWhitespaceStringFilter(StringFilter):
    """
    Implementation of the StringFilter interface which removes all
    leading or trailing whitespace.
    """

    def filter(self, in_string: str) -> str:
        """
        :param in_string: an input string to filter
        :return: a filtered version of the in_string, according to implementation policy
        """
        replacement = None
        if in_string is not None:
            replacement = in_string.strip()

        return replacement
