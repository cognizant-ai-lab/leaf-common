
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


class BooleanParser(Parser):
    """
    Parser implementation getting a boolean from an object.
    """

    def parse(self, input_obj):
        """
        :param input_obj: the object to parse

        :return: a boolean parsed from that object
        """

        if input_obj is None:
            return False

        if isinstance(input_obj, str):
            lower = input_obj.lower()

            true_values = ['true', '1', 'on', 'yes']
            if lower in true_values:
                return True

            false_values = ['false', '0', 'off', 'no']
            if lower in false_values:
                return False

            return False

        return bool(input_obj)
