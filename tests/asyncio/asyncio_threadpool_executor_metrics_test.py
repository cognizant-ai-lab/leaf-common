
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
Unit tests for AsyncioThreadPoolExecutor.get_threads_metrics().

The class wraps every submitted callable to count running tasks, so the
returned (num_threads, num_running) tuple should accurately reflect both
the lazy ThreadPoolExecutor worker-thread count and the count of
callables currently executing in those workers.
"""
import threading

from unittest import TestCase

from leaf_common.asyncio.asyncio_threadpool_executor import AsyncioThreadPoolExecutor


# Module-level helpers (no nested defs inside test methods).
def block_on_event(start_event: threading.Event,
                   release_event: threading.Event):
    """
    Helper task body: signals start_event when picked up by a worker thread,
    then blocks on release_event until the test side releases it. Used to
    pin one worker thread in the "running" state long enough for the test
    to observe the metric.
    """
    start_event.set()
    release_event.wait(timeout=5.0)


def quick_noop():
    """Helper task body: returns immediately. Used to force lazy worker creation."""


class AsyncioThreadPoolExecutorMetricsTest(TestCase):
    """
    Verifies that get_threads_metrics() returns an accurate (threads, running)
    tuple in each lifecycle state: empty, mid-task, post-task, and under
    multi-task concurrency.
    """

    def setUp(self):
        """Create a fresh executor sized so concurrency tests fit within it."""
        self.executor = AsyncioThreadPoolExecutor(max_workers=4)

    def tearDown(self):
        """Always shutdown the executor; tests may leave futures pending on failure."""
        self.executor.shutdown(wait=True)

    def test_metrics_on_fresh_executor_report_zero_running(self):
        """
        Before any work is submitted the executor has lazily created no
        worker threads and has nothing running, so both counts are 0.
        """
        num_threads, num_running = self.executor.get_threads_metrics()
        self.assertEqual(
            0, num_threads,
            f"Expected 0 worker threads on a fresh executor, got {num_threads}.",
        )
        self.assertEqual(
            0, num_running,
            f"Expected 0 running tasks on a fresh executor, got {num_running}.",
        )

    def test_metrics_report_one_running_during_task(self):
        """
        While a single submitted task is blocked inside its callable,
        get_threads_metrics() should report exactly 1 running task. The
        worker-thread count should be at least 1 (ThreadPoolExecutor
        lazily creates a worker on first submit).
        """
        start_event = threading.Event()
        release_event = threading.Event()
        future = self.executor.submit(block_on_event, start_event, release_event)
        # Wait until the worker has actually entered the wrapped callable.
        self.assertTrue(
            start_event.wait(timeout=5.0),
            "Helper task never entered its body within 5s; worker pool stuck?",
        )

        num_threads, num_running = self.executor.get_threads_metrics()

        # Release the task and wait for it to complete before asserting,
        # so a failure in the asserts does not leak a blocked worker.
        release_event.set()
        future.result(timeout=5.0)

        self.assertGreaterEqual(
            num_threads, 1,
            f"Expected at least 1 worker thread mid-task, got {num_threads}.",
        )
        self.assertEqual(
            1, num_running,
            f"Expected exactly 1 running task while the helper was blocked, "
            f"got {num_running}.",
        )

    def test_metrics_running_returns_to_zero_after_task_completes(self):
        """
        After a submitted task completes, running should fall back to 0.
        num_threads stays at whatever the pool grew to (typically 1).
        """
        future = self.executor.submit(quick_noop)
        future.result(timeout=5.0)

        num_threads, num_running = self.executor.get_threads_metrics()

        self.assertGreaterEqual(
            num_threads, 1,
            f"Expected at least 1 worker thread after first submit, got {num_threads}.",
        )
        self.assertEqual(
            0, num_running,
            f"Expected 0 running tasks after task completion, got {num_running}.",
        )

    def test_metrics_running_count_matches_concurrent_task_count(self):
        """
        Submitting N concurrent blocking tasks should result in
        num_running == N (up to max_workers, which is 4 here).
        Confirms the wrapper's increment/decrement is per-task, not a
        single boolean.
        """
        concurrent = 3
        start_events = [threading.Event() for _ in range(concurrent)]
        release_event = threading.Event()
        futures = [
            self.executor.submit(block_on_event, start_events[i], release_event)
            for i in range(concurrent)
        ]
        for i, start_event in enumerate(start_events):
            self.assertTrue(
                start_event.wait(timeout=5.0),
                f"Helper task {i} never entered its body within 5s.",
            )

        num_threads, num_running = self.executor.get_threads_metrics()

        # Release all tasks and wait for completion before asserting so
        # a failure does not leak blocked workers.
        release_event.set()
        for future in futures:
            future.result(timeout=5.0)

        self.assertGreaterEqual(
            num_threads, concurrent,
            f"Expected at least {concurrent} worker threads, got {num_threads}.",
        )
        self.assertEqual(
            concurrent, num_running,
            f"Expected {concurrent} running tasks while helpers were blocked, "
            f"got {num_running}.",
        )

    def test_metrics_handles_missing_threads_attribute_gracefully(self):
        """
        get_threads_metrics() reaches into the protected _threads member
        of ThreadPoolExecutor; if a future stdlib version removes it the
        method should fall back to 0 rather than raising. We simulate
        that by clearing the attribute via delattr.
        """
        # First submit one task so the executor would normally have threads.
        self.executor.submit(quick_noop).result(timeout=5.0)
        # Snapshot and remove _threads to simulate the missing-attribute
        # environment, then restore it in finally so tearDown's shutdown
        # (which also reads _threads) can still succeed.
        # pylint: disable=protected-access
        saved_threads = self.executor._threads
        del self.executor._threads
        try:
            num_threads, num_running = self.executor.get_threads_metrics()
        finally:
            self.executor._threads = saved_threads

        self.assertEqual(
            0, num_threads,
            f"Expected fallback of 0 worker threads when _threads is missing, "
            f"got {num_threads}.",
        )
        self.assertEqual(
            0, num_running,
            f"Expected 0 running tasks after the only submitted task finished, "
            f"got {num_running}.",
        )
