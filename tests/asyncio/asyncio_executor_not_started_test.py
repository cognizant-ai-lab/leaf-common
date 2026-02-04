
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
Unit tests for AsyncioExecutor when not started.
"""

from unittest import TestCase

from leaf_common.asyncio.asyncio_executor import AsyncioExecutor
from tests.asyncio.async_test_helpers import AsyncTestHelpers
from tests.asyncio.sync_test_helpers import SyncTestHelpers


class AsyncioExecutorNotStartedTest(TestCase):
    """
    Tests for AsyncioExecutor when not started.
    """

    def test_submit_raises_when_loop_not_running(self):
        """
        Test that submit() raises RuntimeError when loop is not running.
        """
        executor = AsyncioExecutor()

        with self.assertRaises(RuntimeError) as context:
            executor.submit("test", AsyncTestHelpers.dummy_async_coroutine)
        self.assertIn("Loop must be started", str(context.exception))

    def test_create_task_raises_when_loop_not_running(self):
        """
        Test that create_task() raises RuntimeError when loop is not running.
        """
        executor = AsyncioExecutor()

        with self.assertRaises(RuntimeError) as context:
            executor.create_task(AsyncTestHelpers.dummy_async_coroutine, "test")
        self.assertIn("Loop must be started", str(context.exception))

    def test_initialize_raises_when_loop_not_running(self):
        """
        Test that initialize() raises RuntimeError when loop is not running.
        """
        executor = AsyncioExecutor()

        with self.assertRaises(RuntimeError) as context:
            executor.initialize(SyncTestHelpers.dummy_sync_function)
        self.assertIn("Loop must be started", str(context.exception))

    def test_cancel_current_tasks_raises_when_loop_not_running(self):
        """
        Test that cancel_current_tasks() raises RuntimeError when loop is not running.
        """
        executor = AsyncioExecutor()

        with self.assertRaises(RuntimeError) as context:
            executor.cancel_current_tasks()
        self.assertIn("Loop must be running", str(context.exception))
