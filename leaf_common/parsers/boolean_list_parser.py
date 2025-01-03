
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


from leaf_common.parsers.boolean_parser import BooleanParser
from leaf_common.parsers.list_parser import ListParser


class BooleanListParser(ListParser):
    """
    A ListParser implementation that parses lists of boolean values
    from a string.
    """

    def __init__(self, delimiter_regex=None):
        """
        Constructor

        :param delimiter_regex: the delimiter_regex used to separate
                string names of values in a parsed string.
                By default the delimiters are commas *and* spaces.
        """
        super().__init__(delimiter_regex, BooleanParser())
