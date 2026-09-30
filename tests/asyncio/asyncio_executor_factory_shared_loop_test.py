
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
Unit tests for AsyncioExecutorFactory's SHARED_LOOP type.

These assert the property the browser depends on: nothing the factory builds for
that type starts a thread. threading.Thread.start is patched to fail rather than
merely counted, so a regression shows up as a test failure at the point of the
call rather than as a count mismatch later.
"""

import asyncio
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from leaf_common.asyncio.asyncio_executor_factory import AsyncioExecutorFactory
from leaf_common.asyncio.asyncio_executor_types import AsyncioExecutorTypes
from leaf_common.asyncio.shared_loop_asyncio_executor import SharedLoopAsyncioExecutor


class AsyncioExecutorFactorySharedLoopTest(IsolatedAsyncioTestCase):
    """
    Tests that the SHARED_LOOP type really is thread-free, which is the whole
    reason for it to exist.
    """

    async def test_shared_loop_type_starts_no_threads(self) -> None:
        """
        Building a shared-loop pool and using the executor it hands out touches
        no thread, and borrows the loop the caller is already on.
        """
        with patch("threading.Thread.start", side_effect=AssertionError("No threads")):
            pool = AsyncioExecutorFactory.create_pool(AsyncioExecutorTypes.SHARED_LOOP,
                                                      max_workers=4)
            executor = pool.get_executor()
            self.assertIsInstance(executor, SharedLoopAsyncioExecutor)
            self.assertIs(executor.get_event_loop(), asyncio.get_running_loop())
            self.assertEqual(await executor.submit("request", lambda: 42), 42)
            pool.return_executor(executor)
            await executor.ashutdown(cancel_futures=False)
