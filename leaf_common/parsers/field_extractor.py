
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


class FieldExtractor():
    """
    A policy class that will extract a given field by name
    from a given dictionary.  Field names with '.'-delimited
    values imply nested dictionary lookup.
    """

    def get_field(self, dictionary, field_name, default_value=None,
                  delimiter="."):
        """
        :param dictionary: the dictionary in which the field
            is supposed exist.
        :param field_name: the fully specified field name.
        :param default_value: a default value if the field is not found.
                Default is None
        :param delimiter: a delimiting character for splitting deep-dictionary
                keys
        :return: the value of the field in the dictionary or
            None if the field did not exist.
        """

        # Handle the case of no dictionary
        if dictionary is None or \
                not isinstance(dictionary, dict) or \
                field_name is None:
            return default_value

        # Handle case where field_name is not a string
        # Just do the lookup anyway.
        if field_name is None or \
                not isinstance(field_name, str):
            return dictionary.get(field_name, default_value)

        # Handle the simple case of no delimited key
        if delimiter not in field_name:
            return dictionary.get(field_name, default_value)

        # Handle the more complex case of a delimited key
        field_split = field_name.split(delimiter)
        use_field_name = field_split[0]

        # Get the value for the segment of the field name
        # If it's not a dictionary, return the default value,
        # as we know we have more to look for.
        value = dictionary.get(use_field_name, None)
        if value is None or \
                not isinstance(value, dict):
            return default_value

        # We know the value is a dictionary.
        # Get the remaining bit of the delimited field
        # into its own string for recursion
        remaining_split = field_split[1:len(field_split)+1]
        remaining_field = delimiter.join(remaining_split)

        deep_value = self.get_field(value, remaining_field,
                                    default_value, delimiter)
        return deep_value
