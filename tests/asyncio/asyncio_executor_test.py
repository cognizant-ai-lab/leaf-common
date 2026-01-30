
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
Unit tests for AsyncioExecutor task item handling.
"""

import asyncio
import time
import threading

from asyncio import Task
from unittest import TestCase

from leaf_common.asyncio.asyncio_executor import AsyncioExecutor


# Module-level helper functions for testing

def dummy_sync_function():
    """
    Dummy synchronous function for testing.
    """

async def dummy_async_coroutine():
    """
    Dummy async coroutine for testing.
    """

def sample_function():
    """
    Sample function for testing get_function_name.
    """

async def async_sample():
    """
    Async sample function for testing get_function_name.
    """

class CallableClass:
    """
    Callable class for testing get_function_name with class instances.
    """

    def __call__(self):
        pass

def sync_function_with_result(result_holder, value):
    """
    Sync function that appends to result_holder.
    """
    result_holder.append(value)
    return value * 2

async def async_function_with_result(result_holder, value):
    """
    Async function that appends to result_holder after a delay.
    """
    await asyncio.sleep(0.1)
    result_holder.append(value)
    return value * 2

async def task_function_with_lock(results, lock, task_id):
    """
    Async task function that appends to results with lock protection.
    """
    await asyncio.sleep(0.1)
    with lock:
        results.append(task_id)

async def awaitable_function_with_result(result_holder):
    """
    Awaitable function that appends to result_holder.
    """
    await asyncio.sleep(0.1)
    result_holder.append("completed")

async def failing_async_function():
    """
    Async function that raises ValueError for testing exception handling.
    """
    raise ValueError("Test error")

async def simple_task_with_event(started):
    """
    Simple task that signals when started and sleeps.
    """
    started.set()
    await asyncio.sleep(1.0)

async def named_function():
    """
    Named function for testing task naming.
    """
    await asyncio.sleep(0.5)

async def long_running_task_with_cancel(started, cancelled, task_id):
    """
    Long running task that tracks cancellation.
    """
    started.set()
    try:
        await asyncio.sleep(10.0)
    except asyncio.CancelledError:
        cancelled.append(task_id)
        raise

async def long_task_with_locks(started_count, started_lock, cancelled, cancelled_lock, task_id):
    """
    Long running task with lock-protected counters for multi-task tests.
    """
    with started_lock:
        started_count[0] += 1
    try:
        await asyncio.sleep(10.0)
    except asyncio.CancelledError:
        with cancelled_lock:
            cancelled.append(task_id)
        raise

async def quick_task_with_event(completed):
    """
    Quick task that signals completion.
    """
    result = "done"
    completed.set()
    return result

async def cancellable_task_with_event(started):
    """
    Cancellable task that signals when started.
    """
    started.set()
    await asyncio.sleep(10.0)

async def exception_task():
    """
    Task that raises an exception for testing error handling.
    """
    raise ValueError("Intentional test error")

def init_function_with_result(init_result):
    """
    Init function that appends to result list.
    """
    init_result.append("initialized")

async def kwargs_function_with_result(result_holder, a, b, c=None):
    """
    Async function that tests kwargs handling.
    """
    result_holder.append((a, b, c))

def sync_with_args_and_result(result_holder, x, y, multiplier=1):
    """
    Sync function that tests args and kwargs handling.
    """
    result_holder.append((x + y) * multiplier)

async def callback_test_task_with_event(started):
    """
    Task for testing done callbacks.
    """
    started.set()
    await asyncio.sleep(0.5)
    return "result"

def custom_callback_with_event(callback_called, task):  # pylint: disable=unused-argument
    """
    Custom callback that signals when called.
    """
    callback_called.set()

async def thread_task_with_lock(results, results_lock, thread_id, task_id):
    """
    Task for concurrent thread testing.
    """
    await asyncio.sleep(0.1)
    with results_lock:
        results.append((thread_id, task_id))


class AsyncioExecutorTest(TestCase):  # pylint: disable=too-many-public-methods
    """
    Tests for AsyncioExecutor task item functionality.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        self.executor = AsyncioExecutor()
        self.executor.start()

    def tearDown(self):
        """
        Clean up after tests.
        """
        if self.executor:
            self.executor.shutdown(wait=True)

    def test_get_function_name_with_regular_function(self):
        """
        Test that get_function_name extracts name from regular function.
        """
        name = self.executor.get_function_name(sample_function, "test_submitter")
        self.assertIn("sample_function", name)
        self.assertIn("test_submitter", name)

    def test_get_function_name_with_async_function(self):
        """
        Test that get_function_name extracts name from async function.
        """
        name = self.executor.get_function_name(async_sample, "async_submitter")
        self.assertIn("async_sample", name)
        self.assertIn("async_submitter", name)

    def test_get_function_name_without_submitter_id(self):
        """
        Test that get_function_name works without submitter_id.
        """
        name = self.executor.get_function_name(sample_function, None)
        self.assertIn("sample_function", name)
        self.assertNotIn(":", name)

    def test_get_function_name_with_empty_submitter_id(self):
        """
        Test that get_function_name works with empty submitter_id.
        """
        name = self.executor.get_function_name(sample_function, "")
        self.assertIn("sample_function", name)

    def test_get_function_name_with_class_instance(self):
        """
        Test that get_function_name handles objects without __qualname__.
        """
        instance = CallableClass()
        name = self.executor.get_function_name(instance, "class_submitter")
        self.assertIn("CallableClass", name)
        self.assertIn("class_submitter", name)

    def test_in_executor_thread_from_main_thread(self):
        """
        Test that _in_executor_thread returns False from main thread.
        """
        # pylint: disable=protected-access
        result = self.executor._in_executor_thread()
        self.assertFalse(result)

    def test_submit_sync_function_returns_task(self):
        """
        Test that submit() returns a Task for sync functions.
        """
        result_holder = []
        task = self.executor.submit(
            "test_submitter",
            sync_function_with_result,
            result_holder,
            42
        )
        self.assertIsInstance(task, Task)
        time.sleep(0.5)
        self.assertEqual(result_holder, [42])

    def test_submit_async_function_returns_task(self):
        """
        Test that submit() returns a Task for async functions.
        """
        result_holder = []
        task = self.executor.submit(
            "test_submitter",
            async_function_with_result,
            result_holder,
            100
        )
        self.assertIsInstance(task, Task)
        time.sleep(0.5)
        self.assertEqual(result_holder, [100])

    def test_submit_multiple_tasks(self):
        """
        Test that multiple tasks can be submitted and tracked.
        """
        results = []
        lock = threading.Lock()

        tasks = []
        for i in range(5):
            task = self.executor.submit(
                f"submitter_{i}",
                task_function_with_lock,
                results,
                lock,
                i
            )
            tasks.append(task)

        self.assertEqual(len(tasks), 5)
        for task in tasks:
            self.assertIsInstance(task, Task)

        time.sleep(1.0)
        self.assertEqual(sorted(results), [0, 1, 2, 3, 4])

    def test_submit_raises_after_shutdown(self):
        """
        Test that submit() raises RuntimeError after shutdown.
        """
        self.executor.shutdown(wait=True)

        with self.assertRaises(RuntimeError) as context:
            self.executor.submit("test", dummy_async_coroutine)
        self.assertIn("Cannot schedule new tasks after shutdown", str(context.exception))
        self.executor = None

    def test_create_task_from_outside_executor_thread(self):
        """
        Test that create_task works from outside the executor thread.
        """
        result_holder = []
        coro = awaitable_function_with_result(result_holder)
        task = self.executor.create_task(coro, "external_submitter")
        self.assertIsInstance(task, Task)
        time.sleep(0.5)
        self.assertEqual(result_holder, ["completed"])

    def test_create_task_with_raise_exception_false(self):
        """
        Test that create_task with raise_exception=False handles exceptions silently.
        """
        coro = failing_async_function()
        task = self.executor.create_task(coro, "error_submitter", raise_exception=False)
        self.assertIsInstance(task, Task)
        time.sleep(0.5)

    def test_create_task_raises_after_shutdown(self):
        """
        Test that create_task() raises RuntimeError after shutdown.
        """
        self.executor.shutdown(wait=True)

        with self.assertRaises(RuntimeError) as context:
            self.executor.create_task(dummy_async_coroutine(), "test")
        self.assertIn("Cannot schedule new tasks after shutdown", str(context.exception))
        self.executor = None

    def test_track_task_adds_to_background_tasks(self):
        """
        Test that track_task properly adds task to background tasks dict.
        """
        started = threading.Event()
        task = self.executor.submit("track_test", simple_task_with_event, started)
        started.wait(timeout=2.0)
        task_id = id(task)
        # pylint: disable=protected-access
        self.assertIn(task_id, self.executor._background_tasks)

    def test_task_name_contains_submitter_and_function(self):
        """
        Test that task names contain submitter ID and function name.
        """
        task = self.executor.submit("my_submitter", named_function)
        task_name = task.get_name()
        self.assertIn("my_submitter", task_name)
        self.assertIn("named_function", task_name)

    def test_cancel_current_tasks(self):
        """
        Test that cancel_current_tasks cancels running tasks.
        """
        started = threading.Event()
        cancelled = []
        self.executor.submit(
            "cancel_test",
            long_running_task_with_cancel,
            started,
            cancelled,
            1
        )
        started.wait(timeout=2.0)
        time.sleep(0.2)

        self.executor.cancel_current_tasks(timeout=5.0)
        time.sleep(0.5)
        self.assertEqual(cancelled, [1])

    def test_cancel_current_tasks_multiple(self):
        """
        Test that cancel_current_tasks cancels multiple running tasks.
        """
        started_count = [0]
        started_lock = threading.Lock()
        cancelled = []
        cancelled_lock = threading.Lock()

        for i in range(3):
            self.executor.submit(
                f"cancel_test_{i}",
                long_task_with_locks,
                started_count,
                started_lock,
                cancelled,
                cancelled_lock,
                i
            )

        time.sleep(0.5)
        self.executor.cancel_current_tasks(timeout=5.0)
        time.sleep(0.5)
        self.assertEqual(sorted(cancelled), [0, 1, 2])

    def test_submission_done_removes_task_from_tracking(self):
        """
        Test that submission_done removes completed task from background_tasks.
        Verifies by checking that after shutdown, all tasks are cleaned up.
        """
        completed = threading.Event()
        task = self.executor.submit("tracking_test", quick_task_with_event, completed)
        completed.wait(timeout=2.0)
        self.assertTrue(task.done())

        self.executor.shutdown(wait=True)
        # pylint: disable=protected-access
        self.assertEqual(len(self.executor._background_tasks), 0)
        self.executor = None

    def test_submission_done_handles_cancelled_task(self):
        """
        Test that submission_done handles cancelled tasks gracefully.
        """
        started = threading.Event()
        task = self.executor.submit(
            "cancel_handling",
            cancellable_task_with_event,
            started
        )
        started.wait(timeout=2.0)
        self.executor.cancel_current_tasks(timeout=5.0)
        time.sleep(0.5)
        self.assertTrue(task.cancelled())

    def test_submission_done_handles_exception_in_task(self):
        """
        Test that submission_done handles tasks that raise exceptions.
        """
        task = self.executor.submit("exception_test", exception_task)
        time.sleep(0.5)
        self.assertTrue(task.done())

    def test_initialize_runs_function_in_loop(self):
        """
        Test that initialize() runs a function in the event loop.
        """
        init_result = []
        self.executor.initialize(lambda: init_function_with_result(init_result))
        self.assertEqual(init_result, ["initialized"])

    def test_initialize_raises_after_shutdown(self):
        """
        Test that initialize() raises RuntimeError after shutdown.
        """
        self.executor.shutdown(wait=True)

        with self.assertRaises(RuntimeError) as context:
            self.executor.initialize(dummy_sync_function)
        self.assertIn("Cannot schedule new calls after shutdown", str(context.exception))
        self.executor = None

    def test_get_event_loop_returns_loop(self):
        """
        Test that get_event_loop returns the internal event loop.
        """
        loop = self.executor.get_event_loop()
        self.assertIsNotNone(loop)
        self.assertTrue(loop.is_running())

    def test_shutdown_stops_loop(self):
        """
        Test that shutdown stops the event loop.
        """
        loop = self.executor.get_event_loop()
        self.assertTrue(loop.is_running())
        self.executor.shutdown(wait=True)
        time.sleep(0.2)
        self.assertFalse(loop.is_running())
        self.executor = None

    def test_start_is_idempotent(self):
        """
        Test that calling start() multiple times is safe.
        """
        # pylint: disable=protected-access
        original_thread = self.executor._thread
        self.executor.start()
        self.executor.start()
        self.assertIs(self.executor._thread, original_thread)

    def test_submit_with_kwargs(self):
        """
        Test that submit() correctly passes keyword arguments.
        """
        result_holder = []
        task = self.executor.submit(
            "kwargs_test",
            kwargs_function_with_result,
            result_holder,
            1,
            2,
            c=3
        )
        self.assertIsInstance(task, Task)
        time.sleep(0.5)
        self.assertEqual(result_holder, [(1, 2, 3)])

    def test_submit_sync_function_with_args_and_kwargs(self):
        """
        Test that submit() correctly passes args and kwargs to sync functions.
        """
        result_holder = []
        task = self.executor.submit(
            "sync_args_test",
            sync_with_args_and_result,
            result_holder,
            5,
            3,
            multiplier=2
        )
        self.assertIsInstance(task, Task)
        time.sleep(0.5)
        self.assertEqual(result_holder, [16])

    def test_task_done_callback_is_called(self):
        """
        Test that the done callback is properly registered and called.
        """
        callback_called = threading.Event()
        started = threading.Event()

        task = self.executor.submit("callback_test", callback_test_task_with_event, started)
        started.wait(timeout=2.0)

        task.add_done_callback(
            lambda t: custom_callback_with_event(callback_called, t)
        )
        callback_called.wait(timeout=2.0)
        self.assertTrue(callback_called.is_set())

    def test_concurrent_submits_from_multiple_threads(self):
        """
        Test that concurrent submits from multiple threads work correctly.
        """
        results = []
        results_lock = threading.Lock()
        threads_done = threading.Event()
        thread_count = 5
        tasks_per_thread = 3
        completed_threads = [0]

        def submit_from_thread(thread_id):
            for task_id in range(tasks_per_thread):
                self.executor.submit(
                    f"thread_{thread_id}",
                    thread_task_with_lock,
                    results,
                    results_lock,
                    thread_id,
                    task_id
                )
            with results_lock:
                completed_threads[0] += 1
                if completed_threads[0] == thread_count:
                    threads_done.set()

        threads = []
        for i in range(thread_count):
            t = threading.Thread(target=submit_from_thread, args=(i,))
            threads.append(t)
            t.start()

        threads_done.wait(timeout=5.0)
        for t in threads:
            t.join(timeout=2.0)

        time.sleep(1.0)
        self.assertEqual(len(results), thread_count * tasks_per_thread)


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
            executor.submit("test", dummy_async_coroutine)
        self.assertIn("Loop must be started", str(context.exception))

    def test_create_task_raises_when_loop_not_running(self):
        """
        Test that create_task() raises RuntimeError when loop is not running.
        """
        executor = AsyncioExecutor()

        with self.assertRaises(RuntimeError) as context:
            executor.create_task(dummy_async_coroutine(), "test")
        self.assertIn("Loop must be started", str(context.exception))

    def test_initialize_raises_when_loop_not_running(self):
        """
        Test that initialize() raises RuntimeError when loop is not running.
        """
        executor = AsyncioExecutor()

        with self.assertRaises(RuntimeError) as context:
            executor.initialize(dummy_sync_function)
        self.assertIn("Loop must be started", str(context.exception))

    def test_cancel_current_tasks_raises_when_loop_not_running(self):
        """
        Test that cancel_current_tasks() raises RuntimeError when loop is not running.
        """
        executor = AsyncioExecutor()

        with self.assertRaises(RuntimeError) as context:
            executor.cancel_current_tasks()
        self.assertIn("Loop must be running", str(context.exception))
