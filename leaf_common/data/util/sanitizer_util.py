from copy import deepcopy
from typing import Dict

from leaf_common.data.profiling.column_name_sanitizer_transformation \
    import ColumnNameSanitizerTransformation
from leaf_common.filters.tensorflow_field_name_filter import TensorFlowFieldNameFilter


class SanitizeUtil:
    """
    Utility methods for sanitizing special characters per Keras/TensorFlow requirements
    """

    @staticmethod
    def sanitize_cao_mapping(cao_mapping: Dict[str, list[str]]) -> Dict[str, list[str]]:
        """
        'Sanitizes' the given CAO mapping per Keras/TensorFlow requirements

        :param cao_mapping: The original cao_mapping to potentially sanitize
            This is not modified on output at all.
        :return: A potentially sanitized copy of the cao_mapping
        """
        # Sanitize while specifically not modifying the input
        sanitized_cao_mapping = deepcopy(cao_mapping)

        # Sanitize context/actions/outcomes lists and place them in the output dictionary
        sanitized_cao_mapping['context'] = SanitizeUtil.sanitize_list(cao_mapping['context'])
        sanitized_cao_mapping['actions'] = SanitizeUtil.sanitize_list(cao_mapping['actions'])
        sanitized_cao_mapping['outcomes'] = SanitizeUtil.sanitize_list(cao_mapping['outcomes'])

        return sanitized_cao_mapping

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
        field_names_sanitized = ColumnNameSanitizerTransformation.sanitize_column_names(field_names, sanitizer)

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
        sanitized_input_dict = ColumnNameSanitizerTransformation.sanitize_column_names(input_list, sanitizer)

        # Iterate over input list and update the output list entries that are sanitized
        for idx, item in enumerate(input_list):
            sanitized_input[idx] = sanitized_input_dict[item]

        return sanitized_input
