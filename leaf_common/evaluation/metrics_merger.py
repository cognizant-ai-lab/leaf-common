
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
See class comment for details
"""


class MetricsMerger():
    """
    A class to assist with incrementally merge metrics records.
    """

    def apply(self, original, incremental):
        """
        :param original: The original metrics Record/dictionary
                Can be None.
        :param incremental: The metrics Record/dictionary with the same
                keys/structure, but whose data is an incremental update
                to be (somehow) applied to the original.
                Can be None.
        :return: A new Record/dictionary with the incremental update performed.
        """
        raise NotImplementedError

    def reset(self, incremental):
        """
        :param incremental: The incremental structure whose metrics are to be reset
                in-place.
        """
        raise NotImplementedError
