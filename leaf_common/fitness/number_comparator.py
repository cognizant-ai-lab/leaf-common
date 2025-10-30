
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


from leaf_common.fitness.none_comparator import NoneComparator


class NumberComparator(NoneComparator):
    """
    An implementation of the Comparator interface for
    comparing two numbers.
    """

    def compare(self, obj1, obj2):
        """
        :param obj1: The first object offered for comparison
        :param obj2: The second object offered for comparison
        :return:  A negative integer, zero, or a positive integer as the first
                argument is less than, equal to, or greater than the second.
        """

        comparison = super().compare(obj1, obj2)
        if comparison is not None:
            return comparison

        if obj1 < obj2:
            return -1
        if obj1 > obj2:
            return 1

        return 0
