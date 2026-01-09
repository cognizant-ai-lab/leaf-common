
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
See class comment for details.
"""


from leaf_common.fitness.comparator import Comparator


class NoneComparator(Comparator):
    """
    An implementation of the Comparator interface for
    comparing two objects which might be None.
    """

    def compare(self, obj1, obj2):
        """
        :param obj1: The first object offered for comparison
        :param obj2: The second object offered for comparison
        :return:  0 if both objects are None.
                  -1 if obj1 is None only
                  1 if obj2 is None only
                  None if both are not None. This allows a return value
                  for a composite Comparator to know it has to do something.
        """

        if obj1 is None and obj2 is None:
            return 0

        if obj1 is None:
            return -1

        if obj2 is None:
            return 1

        return None
