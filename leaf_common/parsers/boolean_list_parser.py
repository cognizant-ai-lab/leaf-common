
# Copyright 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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
