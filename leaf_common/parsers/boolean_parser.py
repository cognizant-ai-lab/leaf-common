
# Copyright © 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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
