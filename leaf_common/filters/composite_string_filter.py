
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
from typing import List

from leaf_common.filters.string_filter import StringFilter


class CompositeStringFilter(StringFilter):
    """
    An implementation of the StringFilter interface which puts together
    multiple string filter operations in a certain order
    """

    def __init__(self, filters: List[StringFilter] = None):
        """
        Constructor

        :param filter_classes: A list of StringFilter class instances
                                to apply in order
        """

        self._filters = []

        if filters is not None:
            for one_filter in filters:
                self.add_filter(one_filter)

    def add_filter(self, new_filter: StringFilter):
        """
        :param new_filter: The StringFilter to be added to the list to be applied
        """
        self._filters.append(new_filter)

    def filter(self, in_string: str) -> str:
        """
        :param in_string: an input string to filter
        :return: a filtered version of the in_string, according to implementation policy
        """
        accumulator = in_string
        for string_filter in self._filters:
            accumulator = string_filter.filter(accumulator)
        return accumulator
