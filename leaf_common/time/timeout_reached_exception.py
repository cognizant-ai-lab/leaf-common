
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
See class comment for details
"""


class TimeoutReachedException(Exception):
    """
    Exception raised by the Timeout.check_timeout() method.
    """

    def __init__(self, timeout: object):
        """
        Constructor.
        Store timeout information to pass it
        to anyone who will handle this exception.

        :param timeout: The Timeout object which reached the timeout.
                Note we do not type this to prevent circular dependencies
        """

        Exception.__init__(self)
        self.timeout = timeout
