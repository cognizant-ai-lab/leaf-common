
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
Unit tests for AsyncioExecutor.get_threads_metrics().

The method delegates to the executor's internal AsyncioThreadPoolExecutor
when one is present, or returns (0, 0) otherwise. The behavior of the
threadpool itself is covered in asyncio_threadpool_executor_metrics_test;
this module isolates AsyncioExecutor's delegation logic.
"""
import threading

from unittest import TestCase

from leaf_common.asyncio.asyncio_executor import AsyncioExecutor


# Module-level helper (no nested defs inside test methods).
def block_on_event(start_event: threading.Event,
                   release_event: threading.Event):
    """
    Helper task body: signals start_event when picked up by a worker thread,
    then blocks on release_event until the test side releases it. Used to
    pin one worker thread in the "running" state long enough for the test
    to observe the metric via the AsyncioExecutor wrapper.
    """
    start_event.set()
    release_event.wait(timeout=5.0)


class AsyncioExecutorMetricsTest(TestCase):
    """
    Verifies that AsyncioExecutor.get_threads_metrics() returns the same
    (threads, running) tuple as the underlying AsyncioThreadPoolExecutor,
    and that the fallback path returns (0, 0) when no threadpool is set.
    """

    def setUp(self):
        """Create and start a fresh executor."""
        self.executor = AsyncioExecutor()
        self.executor.start()

    def tearDown(self):
        """Always shutdown so the event-loop thread terminates cleanly."""
        if self.executor is not None:
            self.executor.shutdown(wait=True)

    def test_metrics_on_idle_executor_report_zero(self):
        """
        Immediately after start(), no work has been dispatched to the
        threadpool, so both counts are zero.
        """
        num_threads, num_running = self.executor.get_threads_metrics()
        self.assertEqual(
            0, num_threads,
            f"Expected 0 worker threads on an idle executor, got {num_threads}.",
        )
        self.assertEqual(
            0, num_running,
            f"Expected 0 running tasks on an idle executor, got {num_running}.",
        )

    def test_metrics_reflect_work_dispatched_to_internal_threadpool(self):
        """
        AsyncioExecutor.get_threads_metrics() delegates to its internal
        AsyncioThreadPoolExecutor. Submit work directly to that threadpool
        (the same one the executor's event loop dispatches sync work to via
        run_in_executor) and verify the delegated metrics reflect it.
        """
        start_event = threading.Event()
        release_event = threading.Event()

        # pylint: disable=protected-access
        threadpool = self.executor._threadpool_executor
        future = threadpool.submit(block_on_event, start_event, release_event)
        self.assertTrue(
            start_event.wait(timeout=5.0),
            "Helper task never entered its body within 5s.",
        )

        num_threads, num_running = self.executor.get_threads_metrics()

        # Release and drain before asserting, so failures do not leak
        # a blocked worker.
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

    def test_metrics_return_zero_tuple_when_threadpool_is_absent(self):
        """
        AsyncioExecutor.get_threads_metrics() short-circuits to (0, 0) if
        the internal _threadpool_executor reference is falsy. Simulate
        that branch by clearing the attribute. Avoids needing a real
        environment where the threadpool failed to construct.
        """
        # pylint: disable=protected-access
        self.executor._threadpool_executor = None

        num_threads, num_running = self.executor.get_threads_metrics()

        self.assertEqual(
            0, num_threads,
            f"Expected fallback of 0 worker threads when threadpool is absent, "
            f"got {num_threads}.",
        )
        self.assertEqual(
            0, num_running,
            f"Expected 0 running tasks when threadpool is absent, "
            f"got {num_running}.",
        )
