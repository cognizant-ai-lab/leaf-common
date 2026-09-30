
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
"""Contract checks for the uncached shared-loop pool."""
import asyncio
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from leaf_common.asyncio.shared_loop_asyncio_executor_pool import SharedLoopAsyncioExecutorPool


class SharedLoopAsyncioExecutorPoolTest(IsolatedAsyncioTestCase):
    """
    Tests the contract SharedLoopAsyncioExecutorPool shares with AsyncioExecutorPool.
    """

    async def test_fresh_executors_without_threads(self) -> None:
        """
        Every acquisition builds a new executor, with no reuse and no thread.
        """
        with patch('threading.Thread.start', side_effect=AssertionError('No threads')):
            pool = SharedLoopAsyncioExecutorPool(True, idle_timeout_seconds=0,
                                                 gc_sweep_interval_seconds=0,
                                                 max_workers=2)
            first = pool.get_executor()
            self.assertIs(first.get_event_loop(), asyncio.get_running_loop())
            self.assertEqual(await first.submit('a', lambda: 42), 42)
            pool.return_executor(first)
            second = pool.get_executor()
            self.assertIsNot(first, second)
            self.assertEqual(pool.pool_available, [])
            self.assertFalse(pool.reuse_mode)
            pool.return_executor(second)
            pool.shutdown()
            pool.shutdown(wait=False)

    async def test_return_cancels_only_returned_executor(self) -> None:
        """
        Returning one executor cancels its work alone and leaves other executors running.
        """
        pool = SharedLoopAsyncioExecutorPool()
        first, second = pool.get_executor(), pool.get_executor()
        cleaned: asyncio.Event = asyncio.Event()
        task = first.submit('first', self._block_until_cancelled, cleaned)
        other = second.submit('second', asyncio.Event().wait)
        await asyncio.sleep(0)
        pool.return_executor(first)
        await first.ashutdown(cancel_futures=False)
        self.assertTrue(task.cancelled())
        self.assertTrue(cleaned.is_set())
        self.assertFalse(other.done())
        with self.assertRaises(RuntimeError):
            first.submit('a', lambda: None)
        pool.return_executor(second)
        await second.ashutdown(cancel_futures=False)
        self.assertTrue(asyncio.get_running_loop().is_running())

    async def test_invalid_returns_and_pool_shutdown(self) -> None:
        """
        Returning a foreign or already-returned executor raises, and pool shutdown leaves checked-out executors usable.
        """
        pool, foreign = SharedLoopAsyncioExecutorPool(), SharedLoopAsyncioExecutorPool()
        executor = pool.get_executor()
        with self.assertRaises(ValueError):
            foreign.return_executor(executor)
        pool.shutdown()
        self.assertEqual(await executor.submit('a', lambda: 1), 1)
        pool.return_executor(executor)
        with self.assertRaises(ValueError):
            pool.return_executor(executor)

    async def test_metrics_and_task_dump_are_request_scoped(self) -> None:
        """
        Metrics and the task dump attribute tasks to the executor that owns them, not to the shared loop.
        """
        pool = SharedLoopAsyncioExecutorPool()
        first, second = pool.get_executor(), pool.get_executor()
        first.submit('first', asyncio.Event().wait)
        second.submit('second', asyncio.Event().wait)
        dump = pool.dump_tasks_in_used_executors()
        self.assertEqual(len(dump[str(id(first))]['tasks']), 1)
        self.assertTrue(dump[str(id(first))]['tasks'][0]['name'].startswith('first:'))
        self.assertTrue(dump[str(id(second))]['tasks'][0]['name'].startswith('second:'))
        self.assertIn('first:', pool.format_task_dump(dump))
        self.assertEqual(pool.get_threads_metrics(), {
            'used': {'executors': 2, 'work_threads': 0, 'threads_running': 0},
            'available': {'executors': 0, 'work_threads': 0, 'threads_running': 0},
        })
        for executor in (first, second):
            pool.return_executor(executor)
            await executor.ashutdown(cancel_futures=False)
        self.assertEqual(pool.format_task_dump(pool.dump_tasks_in_used_executors()), '(no used executors)')

    @staticmethod
    async def _block_until_cancelled(cleaned: asyncio.Event) -> None:
        """
        Block forever, flagging the given event once cancellation unwinds it.

        :param cleaned: The event to set from the finally block
        """
        try:
            await asyncio.Event().wait()
        finally:
            cleaned.set()
