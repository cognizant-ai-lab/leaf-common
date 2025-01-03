
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

from typing import Any
from typing import Dict

from leaf_common.parsers.field_extractor import FieldExtractor


class DictionaryExtractor():
    """
    Policy class that pairs a specific dictionary instance with a FieldExtractor.
    """

    def __init__(self, dictionary: Dict[str, Any],
                 delimiter: str = "."):
        """
        Constructor

        :param dictionary: The dictionary to operate on.
        :param delimiter: a delimiting character for splitting deep-dictionary keys
        """
        self.my_dict: Dict[str, Any] = dictionary
        self.delimiter: str = delimiter
        self.extractor = FieldExtractor()

    def get(self, field_name, default_value=None):
        """
        :param field_name: the fully specified field name.
        :param default_value: a default value if the field is not found.
                Default is None
        :return: the value of the field in the dictionary or
            None if the field did not exist.
        """
        return self.extractor.get_field(self.my_dict, field_name, default_value=default_value,
                                        delimiter=self.delimiter)
