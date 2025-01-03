
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

from leaf_common.parsers.parser import Parser


class StringParser(Parser):
    """
    Parser implementation getting a string from an object.
    """

    def parse(self, input_obj):
        """
        :param input_obj: the object to parse

        :return: a string parsed from that input object
        """
        return str(input_obj)
