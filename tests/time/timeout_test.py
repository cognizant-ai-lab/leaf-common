
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
See class comment for details
"""

import time

from unittest import TestCase

from leaf_common.time.timeout import Timeout


class TimeoutTest(TestCase):
    """
    Test for Timeout object.
    """

    def setUp(self):
        """
        Common test set up
        """
        self.timeout = Timeout("test")

    def test_assumptions(self):
        """
        Test basic assumptions about the Timeout object
        """

        self.assertIsNotNone(self.timeout)
        self.assertTrue(self.timeout.get_limit_in_seconds() < 0)
        self.assertTrue(self.timeout.get_remaining_time_in_seconds() < 0)

    def test_timeout_name(self):
        """
        Tests that timeout will set and return its name correctly.
        """
        self.timeout.set_name("abcd")
        self.timeout.set_name("xyz")
        self.assertTrue(self.timeout.get_name() == "xyz")

        self.timeout.set_name("rtyu")
        self.assertTrue(self.timeout.get_name() == "rtyu")

        self.timeout.set_limit_in_seconds(2)
        self.assertTrue(self.timeout.get_name() == "rtyu")

    def test_timeout_reached(self):
        """
        Tests that set timeout will be reached.
        """
        self.timeout.set_limit_in_seconds(2)
        self.assertFalse(self.timeout.is_reached())
        time.sleep(2.5)
        self.assertTrue(self.timeout.is_reached())
        time.sleep(1)
        self.assertTrue(self.timeout.is_reached())
        # Reset the timeout and do it again
        self.timeout.set_limit_in_seconds(3)
        self.assertFalse(self.timeout.is_reached())
        time.sleep(3.3)
        self.assertTrue(self.timeout.is_reached())
        time.sleep(1)
        self.assertTrue(self.timeout.is_reached())

    def test_timeout_time_remaining(self):
        """
        Tests that timeout remaining time is reported corerctly
        """
        self.timeout.set_limit_in_seconds(-1)
        time_remain1 = self.timeout.get_remaining_time_in_seconds()
        self.assertTrue(time_remain1 < 0)
        time.sleep(2)
        time_remain = self.timeout.get_remaining_time_in_seconds()
        self.assertTrue(time_remain == time_remain1)

        self.timeout.set_limit_in_seconds(5)
        time_remain = self.timeout.get_remaining_time_in_seconds()
        self.assertTrue(4 < time_remain <= 5)

        time.sleep(1)
        time_remain = self.timeout.get_remaining_time_in_seconds()
        self.assertTrue(3 < time_remain <= 4)

        time.sleep(2)
        time_remain = self.timeout.get_remaining_time_in_seconds()
        self.assertTrue(1 < time_remain <= 2)

        # Reset the timeout and do it again
        self.timeout.set_limit_in_seconds(10)
        time_remain = self.timeout.get_remaining_time_in_seconds()
        self.assertTrue(9 < time_remain <= 10)

        time.sleep(1)
        time_remain = self.timeout.get_remaining_time_in_seconds()
        self.assertTrue(8 < time_remain <= 9)

        time.sleep(2)
        time_remain = self.timeout.get_remaining_time_in_seconds()
        self.assertTrue(6 < time_remain <= 7)
