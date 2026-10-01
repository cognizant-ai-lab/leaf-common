
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
"""Shared-loop executor behavior; these scenarios also run in Pyodide."""
import asyncio
import contextvars
from typing import Any
from typing import Coroutine
from typing import Dict
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from leaf_common.asyncio.shared_loop_asyncio_executor import SharedLoopAsyncioExecutor

from tests.asyncio.structural_future import StructuralFuture


class SharedLoopAsyncioExecutorTest(IsolatedAsyncioTestCase):
    """
    Tests SharedLoopAsyncioExecutor against a real running loop.
    """

    async def test_results_without_threads_or_loop_changes(self) -> None:
        """
        Results come back with no thread started and the host loop left as it was.
        """
        loop = asyncio.get_running_loop()
        factory, handler = loop.get_task_factory(), loop.get_exception_handler()
        with patch('threading.Thread.start', side_effect=AssertionError('No threads')):
            executor = SharedLoopAsyncioExecutor()
            executor.start()
            executor.start()
            self.assertEqual(await executor.submit('request', lambda value: value + 1, 4), 5)
            self.assertEqual(await executor.submit('request', asyncio.sleep, 0, result=7), 7)
            self.assertEqual(await executor.create_task(asyncio.sleep(0, result=8), 'request'), 8)
            future = loop.create_future()
            future.set_result(9)
            self.assertEqual(await executor.create_task(future, 'request'), 9)
            await executor.ashutdown()
        self.assertIs(loop.get_task_factory(), factory)
        self.assertIs(loop.get_exception_handler(), handler)
        self.assertTrue(loop.is_running())
        self.assertEqual(executor.get_threads_metrics(), (0, 0))

    async def test_request_context_isolation(self) -> None:
        """
        Each executor carries its own ContextVar copy, isolated from the caller's.
        """
        marker = contextvars.ContextVar('request', default='caller')
        first, second = SharedLoopAsyncioExecutor(), SharedLoopAsyncioExecutor()
        first.start()
        second.start()
        first.initialize(lambda: marker.set('first'))
        second.initialize(lambda: marker.set('second'))
        self.assertEqual(marker.get(), 'caller')
        self.assertEqual(await first.submit('a', marker.get), 'first')
        self.assertEqual(await second.submit('b', marker.get), 'second')
        await first.ashutdown()
        await second.ashutdown()

    async def test_cancellation_isolated_and_reusable(self) -> None:
        """
        Cancelling one executor's tasks spares another's, and leaves it reusable.
        """
        first, second = SharedLoopAsyncioExecutor(), SharedLoopAsyncioExecutor()
        first.start()
        second.start()
        cleaned: asyncio.Event = asyncio.Event()
        cancelled = first.submit('a', self._block_until_cancelled, cleaned)
        survivor = second.submit('b', asyncio.sleep, 100)
        await asyncio.sleep(0)
        await first.cancel_current_tasks()
        self.assertTrue(cancelled.cancelled())
        self.assertTrue(cleaned.is_set())
        self.assertFalse(survivor.done())
        self.assertEqual(await first.submit('a', lambda: 42), 42)
        await first.ashutdown()
        await second.ashutdown()

    async def test_lifecycle_and_nonblocking_shutdown(self) -> None:
        """
        Submissions are rejected before start() and after shutdown, and shutdown(wait=True) refuses to block.
        """
        executor = SharedLoopAsyncioExecutor()
        with self.assertRaises(RuntimeError):
            executor.submit('a', lambda: None)
        executor.start()
        task = executor.submit('a', asyncio.sleep, 100)
        with self.assertRaisesRegex(RuntimeError, 'ashutdown'):
            executor.shutdown()
        executor.shutdown(wait=False, cancel_futures=True)
        await executor.ashutdown()
        self.assertTrue(task.cancelled())
        with self.assertRaises(RuntimeError):
            executor.submit('a', lambda: None)
        with self.assertRaises(RuntimeError):
            executor.start()

    async def test_exceptions_propagate_and_report(self) -> None:
        """
        Failures raise when awaited, and raise_exception=True also reports them to the loop handler.
        """
        executor = SharedLoopAsyncioExecutor()
        executor.start()

        with self.assertRaises(ValueError):
            executor.initialize(lambda: (_ for _ in ()).throw(ValueError('init')))
        with patch.object(asyncio.get_running_loop(), 'call_exception_handler') as report:
            task = executor.create_task(self._fail(), 'a', raise_exception=True)
            with self.assertRaises(ValueError):
                await task
            await asyncio.sleep(0)
            self.assertEqual(report.call_count, 1)
        await executor.ashutdown()
        self.assertFalse(executor._tasks)  # pylint: disable=protected-access

    async def test_timeout_retains_tasks_for_later_cleanup(self) -> None:
        """
        A task that outlasts the cancellation timeout stays owned rather than being dropped.
        """
        executor = SharedLoopAsyncioExecutor()
        executor.start()
        release: asyncio.Event = asyncio.Event()
        task = executor.submit('a', self._resist_cancellation, release)
        await asyncio.sleep(0)
        with self.assertRaises(TimeoutError):
            await executor.cancel_current_tasks(timeout=0.01)
        self.assertIn(task, executor._tasks)  # pylint: disable=protected-access
        release.set()
        await executor.ashutdown(cancel_futures=False)

    async def test_self_cleanup_rejected_without_deadlock(self) -> None:
        """
        Cleanup awaited from inside an owned task is refused instead of deadlocking.
        """
        executor = SharedLoopAsyncioExecutor()
        executor.start()
        task = executor.submit('a', executor.ashutdown)
        with self.assertRaisesRegex(RuntimeError, 'outside'):
            await task
        await executor.ashutdown()

    async def test_structural_future_from_another_loop_is_rejected_unscheduled(self) -> None:
        """
        A Future-compatible object that is not an asyncio.Future subclass must
        still get the loop check. With a subclass check it slipped past, was
        scheduled, and failed only once _consume() awaited it -- by which point
        its underlying work was running outside this executor's cleanup.
        """
        executor = SharedLoopAsyncioExecutor()
        executor.start()
        other_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        try:
            foreign: StructuralFuture = StructuralFuture(other_loop)
            self.assertTrue(asyncio.isfuture(foreign))
            self.assertNotIsInstance(foreign, asyncio.Future)

            with self.assertRaisesRegex(ValueError, 'another event loop'):
                executor.create_task(foreign, 'a')

            # Rejected before anything was scheduled or owned.
            self.assertEqual(executor.get_tracked_tasks(), [])
            self.assertFalse(foreign.done())
        finally:
            other_loop.close()

        await executor.ashutdown()

    async def test_cancelling_the_wrapper_cancels_a_structural_future(self) -> None:
        """
        Cancelling our wrapping task must reach the awaitable it wraps, even
        when the wrapper is cancelled before its first step -- _consume() never
        awaits the awaitable at all in that case, so without the hand-off the
        work behind it would keep running untracked.
        """
        executor = SharedLoopAsyncioExecutor()
        executor.start()
        wrapped: StructuralFuture = StructuralFuture(asyncio.get_running_loop())

        task = executor.create_task(wrapped, 'a')
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        for _ in range(4):
            await asyncio.sleep(0)

        self.assertEqual(wrapped.cancel_calls, 1)
        self.assertTrue(wrapped.cancelled())

        await executor.ashutdown()

    async def test_cleanup_from_a_detached_child_after_its_root_finishes(self) -> None:
        """
        An untracked child is never drained, cancelled or reported, so cleanup
        from it cannot wait on itself and must be allowed once the owned root
        it descends from has finished.

        The child inherits the root marker through its context, so a guard
        keyed on the executor alone refused this even with nothing pending --
        contradicting the rule that only submitted or tracked tasks are owned.
        """
        executor = SharedLoopAsyncioExecutor()
        executor.start()
        gate: asyncio.Event = asyncio.Event()
        finished: asyncio.Event = asyncio.Event()
        outcome: Dict[str, Any] = {}

        child: Coroutine = self._cleanup_when_released(executor, gate, outcome, finished)
        self.assertEqual(await executor.submit('parent', self._spawn_child_then_return, child),
                         'parent done')

        # The root has finished, so nothing owned is pending any more.
        self.assertEqual([task for task in executor.get_tracked_tasks() if not task.done()], [])

        gate.set()
        await finished.wait()
        self.assertEqual(outcome['result'], 'allowed')

    async def test_cleanup_from_a_child_of_a_pending_root_is_refused(self) -> None:
        """
        The other half: while the owned root is still pending, draining it from
        a descendant would wait on work the descendant is holding up. That must
        stay refused, or the fix above would trade one bug for a deadlock.
        """
        executor = SharedLoopAsyncioExecutor()
        executor.start()
        gate: asyncio.Event = asyncio.Event()
        gate.set()
        release: asyncio.Event = asyncio.Event()
        finished: asyncio.Event = asyncio.Event()
        outcome: Dict[str, Any] = {}

        child: Coroutine = self._cleanup_when_released(executor, gate, outcome, finished)
        parent = executor.submit('parent', self._spawn_child_then_wait, child, release)

        await finished.wait()
        self.assertIn('refused', outcome['result'])

        release.set()
        await parent
        await executor.ashutdown()

    @staticmethod
    async def _spawn_child_then_return(child: Coroutine) -> str:
        """
        Spawn a detached child task and finish, leaving the child running.

        :param child: The coroutine to run as an untracked child task
        :return: A sentinel the caller can assert on
        """
        asyncio.create_task(child)
        return 'parent done'

    @staticmethod
    async def _spawn_child_then_wait(child: Coroutine, release: asyncio.Event) -> None:
        """
        Spawn a detached child task and stay pending until released.

        :param child: The coroutine to run as an untracked child task
        :param release: The event that lets this finish
        """
        asyncio.create_task(child)
        await release.wait()

    @staticmethod
    async def _cleanup_when_released(executor: SharedLoopAsyncioExecutor,
                                     gate: asyncio.Event,
                                     outcome: Dict[str, Any],
                                     finished: asyncio.Event) -> None:
        """
        Wait for the gate, then try to clean the executor up and record what
        happened. Runs as an untracked child of whoever spawned it.

        :param executor: The executor to attempt cleanup on
        :param gate: The event that lets this proceed
        :param outcome: Dict to record 'allowed' or the refusal into
        :param finished: The event set once the attempt is done
        """
        await gate.wait()
        try:
            await executor.ashutdown()
            outcome['result'] = 'allowed'
        except RuntimeError as exc:
            outcome['result'] = f'refused: {exc}'
        finally:
            finished.set()

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

    @staticmethod
    async def _resist_cancellation(release: asyncio.Event) -> None:
        """
        Swallow the first cancellation and keep waiting, so a bounded
        cancel_current_tasks() times out on it.

        :param release: The event that finally lets this finish
        """
        try:
            await release.wait()
        except asyncio.CancelledError:
            await release.wait()

    @staticmethod
    async def _fail() -> Any:
        """
        Raise, so exception propagation and reporting can be observed.

        :return: Never returns
        """
        raise ValueError('expected')
