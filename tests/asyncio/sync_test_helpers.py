
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
Synchronous helper functions for AsyncioExecutor unit tests.
"""


class SyncTestHelpers:
    """
    Container class for synchronous test helper functions.
    """

    @staticmethod
    def dummy_sync_function():
        """
        Dummy synchronous function for testing.
        """

    @staticmethod
    def sample_function():
        """
        Sample function for testing get_function_name.
        """

    @staticmethod
    def sync_function_with_result(result_holder, value):
        """
        Sync function that appends to result_holder.
        """
        result_holder.append(value)
        return value * 2

    @staticmethod
    def init_function_with_result(init_result):
        """
        Init function that appends to result list.
        """
        init_result.append("initialized")

    @staticmethod
    def sync_with_args_and_result(result_holder, x, y, multiplier=1):
        """
        Sync function that tests args and kwargs handling.
        """
        result_holder.append((x + y) * multiplier)

    @staticmethod
    def custom_callback_with_event(callback_called, task):  # pylint: disable=unused-argument
        """
        Custom callback that signals when called.
        """
        callback_called.set()
