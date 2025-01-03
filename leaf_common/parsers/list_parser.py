
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

import re

from leaf_common.parsers.parser import Parser
from leaf_common.parsers.string_parser import StringParser


class ListParser(Parser):
    """
    Class which can parse a list of the values from
    a list in a single String, returning a List as the result.

    The bigger idea here is that an instance of this class can be used to
    parse a String value of a property and use the resulting List from
    the parse_list() method as a value in some other data class.

    This class works as-is with parsing lists of Strings, but subclasses
    can provide specific type_type parsers to get specific type values
    back from each list-element string passed in there.

    The delimiter regular expression to use for the list can be specified
    in the constructor.
    """

    DEFAULT_DELIMITER = "[, ]"

    def __init__(self, delimiter_regex=None, type_parser=None):
        """
        Constructor.

        :param delimiter_regex: the delimiter_regex used to separate
                string names of values in a parsed string.
                By default the delimiters are commas *and* spaces.
        :param type_parser: a Parser implementation that turns a string
            (at least) into the desired list element type.
            The default is None, implying that a StringParser is used
            turning each element into a String.
        """

        self._delimiter_regex = delimiter_regex
        if self._delimiter_regex is None:
            self._delimiter_regex = self.DEFAULT_DELIMITER

        self._type_parser = type_parser
        if self._type_parser is None:
            self._type_parser = StringParser()

    def parse(self, input_obj):
        """
        Fulfills the Parser interface

        :param input_obj: the string to parse
        :return: an list object parsed from that object
        """
        return self.parse_list(input_obj)

    def parse_list(self, input_obj):        # noqa: C901
        """
        :param input_obj: a String representing a
                delimiter_regex-separated list of values
                or an object that is already a list.
        :return: an List containing the parsed values of the type found
            in the delimiter_regex-separated list provided by the input_obj.
            Warnings will be issued when a component of the list cannot be
            parsed.
        """

        value_list = []

        # A None string on input is OK.
        # We just return an empty set then.
        if input_obj is None:
            return value_list

        split_list = None

        # If the object coming in is already a list, just use it.
        if isinstance(input_obj, list):
            split_list = input_obj

        if isinstance(input_obj, str):
            # Split the input string into components that we parse one by one.
            trimmed_list = input_obj.strip()
            split_list = re.split(self._delimiter_regex, trimmed_list)

        if split_list is not None and \
                len(split_list) > 0:

            # Parse each component of the list
            for one_element in split_list:

                # Skip over empty strings
                if one_element is None:
                    continue

                if isinstance(one_element, str):
                    # Remove preceding or trailing whitespace
                    one_element = one_element.strip()

                    # Skip over empties
                    if len(one_element) == 0:
                        continue

                # Skip over empties
                if one_element is None:
                    continue

                # Defer to implementation for parsing
                one_value = self._type_parser.parse(one_element)

                # Skip over values that did not parse
                if one_value is None:
                    continue

                value_list.append(one_value)

        return value_list
