
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
from copy import deepcopy
from typing import Dict
from typing import List

from leaf_common.filters.string_filter import StringFilter
from leaf_common.filters.tensorflow_field_name_filter import TensorFlowFieldNameFilter


class SanitizeUtil():
    """
    Utility methods for sanitizing special characters in data source column names
    """

    @staticmethod
    def sanitize_dict_keys(fields: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        'Sanitizes' the keys in the fields mapping per Keras/TensorFlow requirements

        :param fields: The original fields mapping to potentially sanitize
            This is not modified on output at all.
        :return: A potentially sanitized copy of the fields mapping
        """
        # Sanitize dictionary keys (dictionary values are unchanged), while specifically not modifying the input
        sanitized_fields = {}
        fields_copy = deepcopy(fields)

        sanitizer = TensorFlowFieldNameFilter()

        field_names = fields.keys()
        # sanitize_column_names() takes a list of column names as input, and
        # returns a dictionary as output. The keys in the dictionary are column names, and
        # the values in the dictionary are (potentially) sanitized column names
        field_names_sanitized = SanitizeUtil.sanitize_column_names(field_names, sanitizer)

        # This code block populates a new dictionary, whose keys are (potentially) sanitized
        # version of the input dictionary and whose values are unchanged.
        #
        # Iterate over field names
        #   Get the sanitized version of field name
        #   Get the value for the (unsanitized) field name from fields_copy
        #   Push the value you got above in the dictionary using the sanitized field name
        for field_name in field_names:
            sanitized_field_name = field_names_sanitized[field_name]
            # Don't want to modify the input dictionary, hence, we use a
            # copy of the input dictionary here to pop values
            sanitized_fields[sanitized_field_name] = fields_copy.pop(field_name)

        return sanitized_fields

    @staticmethod
    def sanitize_list(input_list: list[str]) -> list[str]:
        """
        'Sanitizes' the given list per Keras/TensorFlow requirements

        :param input_list: The original list to potentially sanitize
            This is not modified on output at all.
        :return: A potentially sanitized copy of the input_list
        """
        # Sanitize while specifically not modifying the input
        # Create a copy of the input_list. Then update the list
        # entries that are sanitized below
        sanitized_input = deepcopy(input_list)

        sanitizer = TensorFlowFieldNameFilter()

        # sanitize_column_names() takes a list of column names as input, and
        # returns a dictionary as output. The keys in the dictionary are column names, and
        # the values in the dictionary are (potentially) sanitized column names
        sanitized_input_dict = SanitizeUtil.sanitize_column_names(input_list, sanitizer)

        # Iterate over input list and update the output list entries that are sanitized
        for idx, item in enumerate(input_list):
            sanitized_input[idx] = sanitized_input_dict[item]

        return sanitized_input

    @staticmethod
    def sanitize_column_names(column_names: List[str],
                              sanitizer: StringFilter) -> Dict[str, str]:
        """
        Creates a dictionary of unsanitized column names to sanitized column
        names where the column name values are sanitized by some specified
        criteria.

        :param column_names: A List of column names to sanitize.
        :param sanitizer: A StringFilter implementation that will sanitize
                        the column name.
        :return: A new dictionary where the keys are old column names and the
                 values are new sanitized column names.  If no sanitization
                 needs to be done, then the value will be the same as they key.
        """

        # Per https://stackoverflow.com/questions/39980323/are-dictionaries-ordered-in-python-3-6
        # Dictionary keys are returned in the order they are inserted, so if we do depend on
        # ordering of the new dictionary we should be ok.
        sanitized = {}
        for column_name in column_names:
            sanitized_column_name = sanitizer.filter(column_name)
            sanitized[column_name] = sanitized_column_name

        return sanitized
