
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


def cmp_to_key(comparator):
    """
    Helper method to convert a comparison function into
    a key function for python's list sort() method.
    This is useful to keep things on the up-and-up for Python 3
    where we still want to use the Comparator interface.
    """

    class CmpToKey():
        'Convert a cmp= function into a key= function'

        def __init__(self, obj):
            self.obj = obj

        def __lt__(self, other):
            return comparator.compare(self.obj, other.obj) < 0

        def __gt__(self, other):
            return comparator.compare(self.obj, other.obj) > 0

        def __eq__(self, other):
            return comparator.compare(self.obj, other.obj) == 0

        def __le__(self, other):
            return comparator.compare(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return comparator.compare(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return comparator.compare(self.obj, other.obj) != 0

    return CmpToKey
