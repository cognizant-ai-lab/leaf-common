
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
Unit tests for SharedLoopAsyncioExecutor under a custom host task factory.

loop.create_task() may validly return any Future-compatible object when the
host loop has a task factory installed. On Python 3.12 such a result need not
be an asyncio.Task, and need not provide get_name(), get_coro() or get_stack().

These tests install a factory returning exactly that -- a Future that is not a
Task -- and assert the executor still owns, drains and reports the work. The
failure this guards against is specific: the factory schedules the work before
the executor ever sees the object, so a rejection at that point leaves the work
running untracked and outside shutdown.
"""

import asyncio
import contextvars
from typing import Any
from typing import Dict
from unittest import IsolatedAsyncioTestCase

from leaf_common.asyncio.shared_loop_asyncio_executor import SharedLoopAsyncioExecutor
from leaf_common.asyncio.shared_loop_asyncio_executor_pool import SharedLoopAsyncioExecutorPool


class NotATask(asyncio.Future):
    """
    A Future-compatible task-factory result that is deliberately not a Task.

    It drives the coroutine through an inner Task so the work really runs, and
    exposes none of get_name()/get_coro()/get_stack(), which is what makes it
    the useful adversary here. set_name() is present because create_task()
    calls it after the factory returns.
    """

    def __init__(self, coro: Any, *, loop: asyncio.AbstractEventLoop = None,
                 context: contextvars.Context = None):
        """
        Constructor

        :param coro: The coroutine the host loop asked to schedule
        :param loop: The loop to bind to
        :param context: The context create_task() forwarded, if any
        """
        super().__init__(loop=loop)
        self._name: str = None
        self._runner: asyncio.Task = asyncio.Task(coro, loop=loop, context=context)
        self._runner.add_done_callback(self._runner_done)

    def set_name(self, value: Any) -> None:
        """
        Accept the name create_task() applies after the factory returns.

        :param value: The name to record
        """
        self._name = str(value)

    def _runner_done(self, runner: asyncio.Task) -> None:
        """
        Mirror the inner task's outcome onto this Future.

        :param runner: The inner task that just finished
        """
        if self.done():
            return
        if runner.cancelled():
            self.cancel()
        elif runner.exception() is not None:
            self.set_exception(runner.exception())
        else:
            self.set_result(runner.result())

    # msg is part of Future.cancel()'s signature; this stand-in ignores it.
    # pylint: disable=unused-argument
    def cancel(self, msg: Any = None) -> bool:
        """
        Cancel the inner task as well as this Future.

        :param msg: Cancellation message, accepted for signature parity
        :return: True if cancellation was requested
        """
        self._runner.cancel()
        return super().cancel() if not self.done() else False


class SharedLoopAsyncioExecutorFactoryResultTest(IsolatedAsyncioTestCase):
    """
    Tests SharedLoopAsyncioExecutor against a host loop whose task factory
    returns a non-Task Future.
    """

    def setUp(self) -> None:
        """
        Record that no factory has been installed yet.
        """
        self.loop: asyncio.AbstractEventLoop = None

    async def asyncSetUp(self) -> None:
        """
        Install the adversarial task factory on the running host loop.
        """
        self.loop = asyncio.get_running_loop()
        self.loop.set_task_factory(self._factory)

    async def asyncTearDown(self) -> None:
        """
        Put the host loop's task factory back as it was.
        """
        self.loop.set_task_factory(None)

    @staticmethod
    def _factory(loop: asyncio.AbstractEventLoop, coro: Any, **kwargs: Any) -> NotATask:
        """
        Build a non-Task Future for the host loop.

        :param loop: The loop asking for a task
        :param coro: The coroutine to run
        :param kwargs: Whatever create_task() forwards, such as context
        :return: A NotATask wrapping the coroutine
        """
        return NotATask(coro, loop=loop, context=kwargs.get("context"))

    async def test_factory_result_is_owned_and_returns_its_value(self) -> None:
        """
        A non-Task factory result must be tracked and awaitable. Before the fix
        track_task() rejected it, after the factory had already scheduled it.
        """
        executor = SharedLoopAsyncioExecutor()
        executor.start()

        task = executor.submit('request', lambda: 42)
        self.assertFalse(isinstance(task, asyncio.Task))
        self.assertIsInstance(task, asyncio.Future)
        self.assertIn(task, executor.get_tracked_tasks())
        self.assertEqual(await task, 42)

        await executor.ashutdown()

    async def test_factory_result_is_drained_by_shutdown(self) -> None:
        """
        The leak the reviewer described: untracked work would survive cleanup.
        Owned work must be cancelled by ashutdown() instead.
        """
        executor = SharedLoopAsyncioExecutor()
        executor.start()
        cleaned: asyncio.Event = asyncio.Event()

        task = executor.submit('request', self._block_until_cancelled, cleaned)
        for _ in range(4):
            await asyncio.sleep(0)
        self.assertTrue(executor.has_pending_tasks())

        await executor.ashutdown()

        self.assertTrue(cleaned.is_set())
        self.assertTrue(task.cancelled())
        self.assertFalse(executor.has_pending_tasks())

    async def test_request_context_still_isolated(self) -> None:
        """
        create_task() forwards context to the factory, so per-request ContextVar
        isolation must survive a custom factory.
        """
        marker: contextvars.ContextVar = contextvars.ContextVar('request', default='caller')
        executor = SharedLoopAsyncioExecutor()
        executor.start()
        executor.initialize(lambda: marker.set('isolated'))

        self.assertEqual(marker.get(), 'caller')
        self.assertEqual(await executor.submit('a', marker.get), 'isolated')

        await executor.ashutdown()

    async def test_reporting_degrades_without_task_only_methods(self) -> None:
        """
        get_name()/get_coro()/get_stack() are Task-only. The pool's task dump
        must still render, since a dump is exactly what a caller reaches for
        when work will not go away.
        """
        pool = SharedLoopAsyncioExecutorPool()
        executor = pool.get_executor()
        cleaned: asyncio.Event = asyncio.Event()
        executor.submit('first', self._block_until_cancelled, cleaned)
        for _ in range(4):
            await asyncio.sleep(0)

        dump: Dict[str, Any] = pool.dump_tasks_in_used_executors()
        entry: Dict[str, Any] = dump[str(id(executor))]
        self.assertEqual(len(entry['tasks']), 1)
        reported: Dict[str, Any] = entry['tasks'][0]
        self.assertIsInstance(reported['name'], str)
        self.assertIsInstance(reported['coro'], str)
        self.assertEqual(reported['stack'], [])
        self.assertIn('NotATask', pool.format_task_dump(dump))

        await pool.areturn_executor(executor)
        self.assertTrue(cleaned.is_set())

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
