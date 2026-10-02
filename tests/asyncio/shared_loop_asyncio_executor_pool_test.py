
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
            'retiring': {'executors': 0, 'work_threads': 0, 'threads_running': 0},
        })
        for executor in (first, second):
            pool.return_executor(executor)
            await executor.ashutdown(cancel_futures=False)
        self.assertEqual(pool.format_task_dump(pool.dump_tasks_in_used_executors()), '(no used executors)')

    async def test_sync_return_keeps_ownership_of_unfinished_work(self) -> None:
        """
        A task that catches CancelledError outlives return_executor(). The pool
        must keep reporting the executor rather than dropping it while it runs.
        """
        pool = SharedLoopAsyncioExecutorPool()
        executor = pool.get_executor()
        release: asyncio.Event = asyncio.Event()
        executor.submit('a', self._resist_cancellation, release)
        await self._settle()

        pool.return_executor(executor)
        await self._settle()

        metrics = pool.get_threads_metrics()
        self.assertEqual(metrics['used']['executors'], 0)
        self.assertEqual(metrics['retiring']['executors'], 1)

        dump = pool.dump_tasks_in_used_executors()
        self.assertTrue(dump[str(id(executor))]['retiring'])
        self.assertEqual(len(dump[str(id(executor))]['tasks']), 1)

        release.set()
        await pool.ashutdown()

    async def test_sync_return_of_finished_work_retains_nothing(self) -> None:
        """
        The happy path must not accumulate: an executor with no pending work is
        released outright rather than parked as retiring.
        """
        pool = SharedLoopAsyncioExecutorPool()
        executor = pool.get_executor()
        self.assertEqual(await executor.submit('a', lambda: 42), 42)

        pool.return_executor(executor)

        metrics = pool.get_threads_metrics()
        self.assertEqual(metrics['used']['executors'], 0)
        self.assertEqual(metrics['retiring']['executors'], 0)
        self.assertEqual(pool.dump_tasks_in_used_executors(), {})
        pool.shutdown()

    async def test_areturn_executor_completes_cleanup(self) -> None:
        """
        The awaitable path drains the work and only then gives up ownership,
        which is the guarantee the native pool's return_executor() provides.
        """
        pool = SharedLoopAsyncioExecutorPool()
        executor = pool.get_executor()
        cleaned: asyncio.Event = asyncio.Event()
        executor.submit('a', self._block_until_cancelled, cleaned)
        await self._settle()

        await pool.areturn_executor(executor)

        self.assertTrue(cleaned.is_set())
        self.assertFalse(executor.has_pending_tasks())
        metrics = pool.get_threads_metrics()
        self.assertEqual(metrics['used']['executors'], 0)
        self.assertEqual(metrics['retiring']['executors'], 0)
        pool.shutdown()

    async def test_shutdown_refuses_to_abandon_retiring_work(self) -> None:
        """
        shutdown(wait=True) cannot drain the shared loop, so it says so instead
        of silently losing the executor. wait=False opts out of the check.
        """
        pool = SharedLoopAsyncioExecutorPool()
        executor = pool.get_executor()
        release: asyncio.Event = asyncio.Event()
        executor.submit('a', self._resist_cancellation, release)
        await self._settle()
        pool.return_executor(executor)
        await self._settle()

        with self.assertRaisesRegex(RuntimeError, 'ashutdown'):
            pool.shutdown()
        pool.shutdown(wait=False)

        release.set()
        await pool.ashutdown()

    async def test_pool_ashutdown_drains_retiring_executors(self) -> None:
        """
        await ashutdown() is the recovery point for anything left retiring by a
        synchronous return.
        """
        pool = SharedLoopAsyncioExecutorPool()
        first, second = pool.get_executor(), pool.get_executor()
        first_cleaned: asyncio.Event = asyncio.Event()
        second_cleaned: asyncio.Event = asyncio.Event()
        first.submit('first', self._block_until_cancelled, first_cleaned)
        second.submit('second', self._block_until_cancelled, second_cleaned)
        await self._settle()
        pool.return_executor(first)
        pool.return_executor(second)

        await pool.ashutdown()

        self.assertTrue(first_cleaned.is_set())
        self.assertTrue(second_cleaned.is_set())
        self.assertEqual(pool.get_threads_metrics()['retiring']['executors'], 0)
        pool.shutdown()

    async def test_areturn_timeout_keeps_the_executor_retiring(self) -> None:
        """
        A task that outlasts the timeout must not be dropped. The pool keeps
        the executor so metrics still show it and ashutdown() can retry.
        """
        pool = SharedLoopAsyncioExecutorPool()
        executor = pool.get_executor()
        release: asyncio.Event = asyncio.Event()
        executor.submit('a', self._resist_cancellation, release)
        await self._settle()

        with self.assertRaises(TimeoutError):
            await pool.areturn_executor(executor, timeout=0.01)

        self.assertEqual(pool.get_threads_metrics()['retiring']['executors'], 1)
        self.assertTrue(pool.dump_tasks_in_used_executors()[str(id(executor))]['retiring'])

        release.set()
        await pool.ashutdown()
        self.assertEqual(pool.get_threads_metrics()['retiring']['executors'], 0)

    async def test_areturn_from_an_owned_task_keeps_pool_ownership(self) -> None:
        """
        ashutdown() refuses to run when called from one of the executor's own
        tasks, and that executor is left fully usable -- _shutdown is never
        set, because _pending() raises first. So the pool must still own it.

        The bug this guards against was delayed: the executor was retired
        before ashutdown() was consulted, so once the calling task ended
        _prune_retired() forgot it, leaving a usable executor with no owner.
        """
        pool = SharedLoopAsyncioExecutorPool()
        executor = pool.get_executor()

        task = executor.submit('a', pool.areturn_executor, executor)
        with self.assertRaisesRegex(RuntimeError, 'outside'):
            await task

        # Still checked out, not retiring, right after the refusal.
        metrics = pool.get_threads_metrics()
        self.assertEqual(metrics['used']['executors'], 1)
        self.assertEqual(metrics['retiring']['executors'], 0)

        # And still checked out after the calling task has ended and a prune
        # has run -- this is where the old behavior lost it.
        await self._settle()
        metrics = pool.get_threads_metrics()
        self.assertEqual(metrics['used']['executors'], 1)
        self.assertEqual(metrics['retiring']['executors'], 0)
        self.assertIn(str(id(executor)), pool.dump_tasks_in_used_executors())

        # The executor was never shut down, so it still works and can still
        # be returned properly.
        self.assertEqual(await executor.submit('b', lambda: 42), 42)
        await pool.areturn_executor(executor)
        self.assertEqual(pool.get_threads_metrics()['used']['executors'], 0)
        pool.shutdown()

    async def test_areturn_of_a_foreign_executor_raises(self) -> None:
        """
        An executor this pool never handed out is an error, and checking that
        must not disturb the pool that does own it.
        """
        pool = SharedLoopAsyncioExecutorPool()
        foreign = SharedLoopAsyncioExecutorPool()
        executor = pool.get_executor()

        with self.assertRaises(ValueError):
            await foreign.areturn_executor(executor)

        self.assertEqual(pool.get_threads_metrics()['used']['executors'], 1)
        await pool.areturn_executor(executor)
        pool.shutdown()
        foreign.shutdown()

    async def test_cancelling_areturn_retires_the_executor(self) -> None:
        """
        If the task awaiting areturn_executor() is cancelled mid-drain, the
        executor's shutdown flag is already set, so it is unusable. It must not
        be left checked out: pool.ashutdown() drains only retiring executors,
        so cancellation-resistant work would otherwise survive pool cleanup
        with nothing left to retry the drain.
        """
        pool = SharedLoopAsyncioExecutorPool()
        executor = pool.get_executor()
        release: asyncio.Event = asyncio.Event()
        executor.submit('a', self._resist_cancellation, release)
        await self._settle()

        returner = asyncio.create_task(pool.areturn_executor(executor))
        await self._settle()
        returner.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await returner

        self.assertTrue(executor.is_shutdown())
        metrics = pool.get_threads_metrics()
        self.assertEqual(metrics['used']['executors'], 0)
        self.assertEqual(metrics['retiring']['executors'], 1)

        # And the pool can now finish what the cancelled call started.
        release.set()
        await pool.ashutdown()
        self.assertEqual(pool.get_threads_metrics()['retiring']['executors'], 0)
        self.assertFalse(executor.has_pending_tasks())

    async def test_refused_cleanup_leaves_the_executor_checked_out(self) -> None:
        """
        The other side of the same decision: when ashutdown() refuses before
        beginning, the executor was never shut down and must stay checked out
        and usable. Keying on the executor's own state has to preserve that,
        not just the cancellation case.
        """
        pool = SharedLoopAsyncioExecutorPool()
        executor = pool.get_executor()

        task = executor.submit('a', pool.areturn_executor, executor)
        with self.assertRaisesRegex(RuntimeError, 'outside'):
            await task
        await self._settle()

        self.assertFalse(executor.is_shutdown())
        metrics = pool.get_threads_metrics()
        self.assertEqual(metrics['used']['executors'], 1)
        self.assertEqual(metrics['retiring']['executors'], 0)

        self.assertEqual(await executor.submit('b', lambda: 9), 9)
        await pool.areturn_executor(executor)
        pool.shutdown()

    @staticmethod
    async def _settle() -> None:
        """
        Yield to the loop enough times for a cancellation to be delivered and,
        where the task swallows it, for the task to resume and park again.
        """
        for _ in range(4):
            await asyncio.sleep(0)

    @staticmethod
    async def _resist_cancellation(release: asyncio.Event) -> None:
        """
        Swallow the first cancellation and keep waiting. This is the adversary
        the retiring lifecycle exists for.

        :param release: The event that finally lets this finish
        """
        try:
            await release.wait()
        except asyncio.CancelledError:
            await release.wait()

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
