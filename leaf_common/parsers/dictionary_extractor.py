
# Copyright 2025 Cognizant Technology Solutions Corp, www.cognizant.com.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
