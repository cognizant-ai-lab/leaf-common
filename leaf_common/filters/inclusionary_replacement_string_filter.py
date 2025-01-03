
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
class InclusionaryReplacementStringFilter(StringFilter):
    """
    Implementation of the StringFilter interface which replaces all
    instances of any single character *not* in a specified string with one
    single common substring.
    """

    def __init__(self, valid_chars: str, replace_invalid_with: str):
        """
        Constructor

        :param valid_chars: The string specifying the valid characters to keep
        :param replace_invalid_with: The string to replace invalid characters wherever they are found
                A value of None here implies no replacement at all (a null operation)
                An empty string here implies omission of invalid characters
        """
        self._valid_chars = valid_chars
        self._replace_invalid_with = replace_invalid_with

        if self._valid_chars is None:
            # There are no valid chars
            self._valid_chars = ""

    def filter(self, in_string: str) -> str:
        """
        :param in_string: an input string to filter
        :return: a filtered version of the in_string, according to implementation policy
        """
        # Nothing to replace
        if in_string is None or self._replace_invalid_with is None:
            return in_string

        accumulator = in_string
        for one_char in in_string:
            if one_char not in self._valid_chars:
                accumulator = accumulator.replace(one_char, self._replace_invalid_with)

        return accumulator
