
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
Unit tests for SharedLoopAsyncioExecutor on a loop that rejects context=.

CPython's AbstractEventLoop.create_task takes context=, so every other test in
this suite exercises a loop that accepts it. This class borrows whatever loop
the host is running, though, and a hand-written loop need not implement the
full signature -- Pyodide's WebLoop is exactly such a loop, and it is this
class's main reason to exist.

The running loop's create_task is therefore replaced with one whose signature
omits context=, so the executor has to take its fallback path. Without it every
submission would raise TypeError on that platform.
"""

import asyncio
import contextvars
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from leaf_common.asyncio.shared_loop_asyncio_executor import SharedLoopAsyncioExecutor


class SharedLoopAsyncioExecutorContextFallbackTest(IsolatedAsyncioTestCase):
    """
    Tests SharedLoopAsyncioExecutor against a loop whose create_task() takes
    no context keyword.
    """

    async def asyncSetUp(self) -> None:
        """
        Note the running loop and its real create_task, so the stand-in can
        delegate to it.
        """
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self.real_create_task: Any = self.loop.create_task

    def _create_task_without_context(self, coro: Any, *, name: str = None) -> asyncio.Task:
        """
        Stand in for a loop whose create_task() has no context parameter.

        The signature is the point: the executor probes it to decide whether
        context= can be passed.

        :param coro: The coroutine to schedule
        :param name: The task name
        :return: A real Task, built without being told a context
        """
        return self.real_create_task(coro, name=name)

    async def test_probe_detects_a_loop_that_rejects_context(self) -> None:
        """
        The probe must read the stand-in's signature correctly, since every
        other assertion here depends on the fallback actually being taken.
        """
        # pylint: disable=protected-access
        self.assertTrue(SharedLoopAsyncioExecutor._takes_context(self.real_create_task))
        self.assertFalse(
            SharedLoopAsyncioExecutor._takes_context(self._create_task_without_context))

    async def test_submission_works_without_context_support(self) -> None:
        """
        The headline case: on such a loop the executor must still schedule
        work rather than raising TypeError on every submit.
        """
        with patch.object(self.loop, 'create_task', self._create_task_without_context):
            executor = SharedLoopAsyncioExecutor()
            executor.start()

            self.assertEqual(await executor.submit('a', lambda: 42), 42)
            self.assertEqual(await executor.submit('b', asyncio.sleep, 0, result=7), 7)
            # pylint: disable=protected-access
            self.assertFalse(executor._loop_takes_context)

            await executor.ashutdown()

    async def test_context_isolation_survives_the_fallback(self) -> None:
        """
        The fallback exists to keep per-request ContextVar isolation, which is
        the whole reason context= is passed in the first place. Entering the
        context around create_task() has to achieve the same thing.
        """
        marker: contextvars.ContextVar = contextvars.ContextVar('request', default='caller')

        with patch.object(self.loop, 'create_task', self._create_task_without_context):
            first = SharedLoopAsyncioExecutor()
            second = SharedLoopAsyncioExecutor()
            first.start()
            second.start()
            first.initialize(lambda: marker.set('first'))
            second.initialize(lambda: marker.set('second'))

            self.assertEqual(marker.get(), 'caller')
            self.assertEqual(await first.submit('a', marker.get), 'first')
            self.assertEqual(await second.submit('b', marker.get), 'second')

            await first.ashutdown()
            await second.ashutdown()

    async def test_ownership_marker_survives_the_fallback(self) -> None:
        """
        The self-cleanup guard rides in the same context, so it must still fire
        on the fallback path. If it did not, cleanup from owned work would
        cancel the caller instead of being refused.
        """
        with patch.object(self.loop, 'create_task', self._create_task_without_context):
            executor = SharedLoopAsyncioExecutor()
            executor.start()

            task = executor.submit('a', executor.ashutdown)
            with self.assertRaisesRegex(RuntimeError, 'outside'):
                await task

            # Never shut down, so still usable.
            self.assertEqual(await executor.submit('b', lambda: 1), 1)
            await executor.ashutdown()

    async def test_cleanup_still_drains_on_the_fallback_path(self) -> None:
        """
        Tasks created through the fallback must be owned like any other, so
        ashutdown() cancels them.
        """
        with patch.object(self.loop, 'create_task', self._create_task_without_context):
            executor = SharedLoopAsyncioExecutor()
            executor.start()
            cleaned: asyncio.Event = asyncio.Event()

            task = executor.submit('a', self._block_until_cancelled, cleaned)
            for _ in range(4):
                await asyncio.sleep(0)
            self.assertTrue(executor.has_pending_tasks())

            await executor.ashutdown()

            self.assertTrue(cleaned.is_set())
            self.assertTrue(task.cancelled())

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
