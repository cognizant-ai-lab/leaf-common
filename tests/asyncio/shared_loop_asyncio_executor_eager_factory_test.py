
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
Unit tests for SharedLoopAsyncioExecutor under an eager task factory.

asyncio.eager_task_factory runs a coroutine's first step inside create_task()
itself, before the task object is handed back. That opens a window in which the
executor is running its own submitted work while that work is neither in _tasks
nor recorded as an owned root yet.

Preserving a host's eager factory is one of this class's stated reasons for not
constructing asyncio.Task directly, so the window has to be handled rather than
assumed away: without it, work that cleans up in its first step shuts the
executor down and the caller sees a misleading "Cannot schedule new tasks after
shutdown" instead of the guard's refusal.
"""

import asyncio
from typing import Any
from typing import Dict
from unittest import IsolatedAsyncioTestCase

from leaf_common.asyncio.shared_loop_asyncio_executor import SharedLoopAsyncioExecutor


class SharedLoopAsyncioExecutorEagerFactoryTest(IsolatedAsyncioTestCase):
    """
    Tests SharedLoopAsyncioExecutor on a host loop running eager tasks.
    """

    async def asyncSetUp(self) -> None:
        """
        Install the eager task factory on the running host loop.
        """
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self.loop.set_task_factory(asyncio.eager_task_factory)

    async def asyncTearDown(self) -> None:
        """
        Put the host loop's task factory back as it was.
        """
        self.loop.set_task_factory(None)

    async def test_ordinary_work_runs_under_an_eager_factory(self) -> None:
        """
        The baseline: preserving the host's eager factory has to actually work,
        since that is the reason given for not building Tasks directly.
        """
        executor = SharedLoopAsyncioExecutor()
        executor.start()

        self.assertEqual(await executor.submit('a', lambda: 42), 42)
        self.assertEqual(await executor.submit('b', asyncio.sleep, 0, result=7), 7)

        await executor.ashutdown()

    async def test_self_cleanup_during_the_eager_first_step_is_refused(self) -> None:
        """
        Work that cleans up in its first step runs before create_task() returns,
        so it is not in _tasks and its owned root is not yet recorded.

        It must still be recognised as this executor's own work. Otherwise the
        executor shuts itself down and the caller gets "Cannot schedule new
        tasks after shutdown" from track_task() -- a confusing error for an
        already-mistaken call, and a dead executor besides.
        """
        executor = SharedLoopAsyncioExecutor()
        executor.start()
        outcome: Dict[str, Any] = {}

        task = executor.submit('a', self._clean_up_and_record, executor, outcome)
        with self.assertRaisesRegex(RuntimeError, 'outside'):
            await task

        self.assertIn('refused', outcome['result'])
        # Never shut down, so still usable.
        self.assertEqual(await executor.submit('b', lambda: 1), 1)
        await executor.ashutdown()

    async def test_cleanup_from_outside_is_unaffected(self) -> None:
        """
        The eager window must not make the guard fire for a caller that is not
        inside the executor's work at all.
        """
        executor = SharedLoopAsyncioExecutor()
        executor.start()
        cleaned: asyncio.Event = asyncio.Event()

        executor.submit('a', self._block_until_cancelled, cleaned)
        for _ in range(4):
            await asyncio.sleep(0)

        await executor.ashutdown()
        self.assertTrue(cleaned.is_set())

    @staticmethod
    async def _clean_up_and_record(executor: SharedLoopAsyncioExecutor,
                                   outcome: Dict[str, Any]) -> str:
        """
        Attempt executor cleanup as the very first thing this work does, so it
        happens inside the eager first step, and re-raise so the caller sees it.

        :param executor: The executor to attempt cleanup on
        :param outcome: Dict to record the refusal into
        :return: A sentinel, never reached while the guard holds
        """
        try:
            await executor.ashutdown()
        except RuntimeError as exc:
            outcome['result'] = f'refused: {exc}'
            raise
        outcome['result'] = 'allowed'
        return 'shut itself down'

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
