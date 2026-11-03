# Copyright © 2023-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
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
from asyncio import Future

from unittest import IsolatedAsyncioTestCase

from typing_extensions import override

from leaf_common.asyncio.shared_loop_asyncio_executor import SharedLoopAsyncioExecutor

from tests.asyncio.task_executor_call_stacks import TaskExecutorCallStacks


class TestSharedLoopAsyncioExecutor(IsolatedAsyncioTestCase):
    """
    Unit tests for SharedLoopAsyncioExecutor.is_running_in_owned_loop(), called 1, 2 and 3 levels deep
    from threads with no running event loop, from a different event loop,
    and from the event loop that the executor borrows.
    The executor borrows the test's own event loop when it starts.
    Synchronous test methods run without an event loop on their thread.
    Async test methods run on the test's own event loop, which is the executor's loop.
    """

    @override
    async def asyncSetUp(self) -> None:
        """
        Creates the SharedLoopAsyncioExecutor and binds it to the test's event loop.
        """
        self.executor: SharedLoopAsyncioExecutor = SharedLoopAsyncioExecutor()
        self.executor.start()

    @override
    async def asyncTearDown(self) -> None:
        """
        Shuts down the SharedLoopAsyncioExecutor.
        """
        await self.executor.ashutdown()

    # No running event loop

    def test_no_loop_level_1(self) -> None:
        """
        Tests that a direct call from a thread with no running event loop returns False.
        """
        self.assertFalse(self.executor.is_running_in_owned_loop())
        self.assertFalse(TaskExecutorCallStacks.sync_level_1(self.executor))

    def test_no_loop_level_2(self) -> None:
        """
        Tests that a call 2 levels deep on a thread with no running event loop returns False.
        """
        self.assertFalse(TaskExecutorCallStacks.sync_level_2(self.executor))

    def test_no_loop_level_3(self) -> None:
        """
        Tests that a call 3 levels deep on a thread with no running event loop returns False.
        """
        self.assertFalse(TaskExecutorCallStacks.sync_level_3(self.executor))

    # Running event loop that is not the executor's

    async def test_other_loop(self) -> None:
        """
        Tests that a call 3 async levels deep on a different event loop returns False.
        """
        self.assertFalse(await TaskExecutorCallStacks.async_run_in_other_loop(self.executor))

    # Running event loop that is the executor's

    async def test_executor_loop_async_stacks(self) -> None:
        """
        Tests that async calls 1, 2 and 3 levels deep on the executor's event loop return True.
        """
        self.assertTrue(self.executor.is_running_in_owned_loop())
        self.assertTrue(await TaskExecutorCallStacks.async_level_1(self.executor))
        self.assertTrue(await TaskExecutorCallStacks.async_level_2(self.executor))
        self.assertTrue(await TaskExecutorCallStacks.async_level_3(self.executor))

    async def test_executor_loop_sync_stacks(self) -> None:
        """
        Tests that synchronous calls below an async method on the executor's event loop return True.
        """
        self.assertTrue(TaskExecutorCallStacks.sync_level_1(self.executor))
        self.assertTrue(TaskExecutorCallStacks.sync_level_3(self.executor))
        self.assertTrue(await TaskExecutorCallStacks.async_then_sync_level_3(self.executor))

    async def test_executor_loop_async_generator(self) -> None:
        """
        Tests that a call from an async generator on the executor's event loop returns True.
        """
        self.assertEqual([True], await TaskExecutorCallStacks.async_collect_generator(self.executor))

    async def test_executor_loop_submit(self) -> None:
        """
        Tests that a coroutine function given to submit() runs on the executor's event loop.
        """
        future: Future = self.executor.submit("test", TaskExecutorCallStacks.async_level_3, self.executor)
        self.assertTrue(await future)

    # Thread boundaries

    async def test_executor_thread_pool_is_not_loop(self) -> None:
        """
        Tests that a call made on a thread pool worker of the executor's event loop returns False,
        because the worker thread runs no event loop of its own.
        """
        self.assertFalse(await TaskExecutorCallStacks.async_run_in_thread_pool(self.executor))

    # Executor that is not started

    async def test_not_started(self) -> None:
        """
        Tests that an executor that is not started returns False, because it has no event loop yet.
        """
        executor: SharedLoopAsyncioExecutor = SharedLoopAsyncioExecutor()
        self.assertFalse(executor.is_running_in_owned_loop())
