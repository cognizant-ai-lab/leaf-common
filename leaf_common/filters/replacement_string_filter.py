
# Copyright © 2019-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
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
Copyright (C) 2021-2023 Cognizant Digital Business, Evolutionary AI.
All Rights Reserved.
Issued under the Academic Public License.

You can be released from the terms, and requirements of the Academic Public
License by purchasing a commercial license.
Purchase of a commercial license is mandatory for any use of the
unileaf-util SDK Software in commercial settings.

END COPYRIGHT
"""

from leaf_common.filters.string_filter import StringFilter


# pylint: disable=too-few-public-methods
class ReplacementStringFilter(StringFilter):
    """
    Implementation of the StringFilter interface which replaces all
    instances of one substring with another.
    """

    def __init__(self, find: str, replace_with: str):
        """
        Constructor

        :param find: The source string to find
        :param replace_with: The string to replace the 'find' string wherever it is found
        """
        self._find = find
        self._replace_with = replace_with

    def filter(self, in_string: str) -> str:
        """
        :param in_string: an input string to filter
        :return: a filtered version of the in_string, according to implementation policy
        """
        replacement = None
        if in_string is not None:
            replacement = in_string.replace(self._find, self._replace_with)

        return replacement
