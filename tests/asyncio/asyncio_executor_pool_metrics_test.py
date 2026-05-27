
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
Unit tests for AsyncioExecutorPool.get_threads_metrics().

The pool aggregates per-executor (threads, running) tuples into a nested
dict with "used" and "available" sections. Each section reports the
number of executors plus the totals of their underlying thread counts.
These tests cover the empty pool, the used/available partitioning across
acquire/return state transitions in both reuse and non-reuse modes, and
the aggregation arithmetic.
"""
from typing import Tuple

from unittest import TestCase
from unittest.mock import MagicMock

from leaf_common.asyncio.asyncio_executor_pool import AsyncioExecutorPool


def make_metrics_executor(threads: int, running: int) -> MagicMock:
    """
    Build a mock AsyncioExecutor whose get_threads_metrics() returns
    the given (threads, running) tuple. Used to drive the aggregation
    arithmetic without depending on real thread scheduling.
    """
    mock = MagicMock()
    mock.get_threads_metrics.return_value: Tuple[int, int] = (threads, running)
    return mock


class AsyncioExecutorPoolMetricsTest(TestCase):
    """
    Verifies that get_threads_metrics() correctly partitions executors
    between the "used" and "available" buckets and sums their per-executor
    thread counts.
    """

    def tearDown(self):
        """
        Shutdown any real executors that may be live in the pool. Mock
        executors are no-ops on shutdown so the call is harmless either
        way.
        """
        if getattr(self, "pool", None) is None:
            return
        for executor in list(self.pool.pool_used) + list(self.pool.pool_available):
            try:
                executor.shutdown(wait=True)
            except Exception:  # pylint: disable=broad-exception-caught
                pass

    def test_metrics_on_empty_pool_report_all_zeros(self):
        """
        A freshly constructed pool has no executors in either bucket, so
        both sections report executors=0, work_threads=0, threads_running=0.
        """
        # pylint: disable=attribute-defined-outside-init
        self.pool = AsyncioExecutorPool(reuse_mode=True)
        metrics = self.pool.get_threads_metrics()
        self.assertEqual(
            {
                "used": {"executors": 0, "work_threads": 0, "threads_running": 0},
                "available": {"executors": 0, "work_threads": 0, "threads_running": 0},
            },
            metrics,
            f"Expected all-zero metrics on an empty pool; got {metrics}.",
        )

    def test_metrics_count_one_used_executor_and_zero_available(self):
        """
        After get_executor() the pool holds the new executor in pool_used;
        pool_available stays empty. Used.executors should be 1; available
        section should remain all-zero.
        """
        # pylint: disable=attribute-defined-outside-init
        self.pool = AsyncioExecutorPool(reuse_mode=True)
        # Replace the freshly-acquired real executor with a mock so the
        # threads/running counts are deterministic.
        self.pool.get_executor()
        self.pool.pool_used[0].shutdown(wait=True)
        self.pool.pool_used[0] = make_metrics_executor(threads=2, running=1)

        metrics = self.pool.get_threads_metrics()

        self.assertEqual(
            {
                "used": {"executors": 1, "work_threads": 2, "threads_running": 1},
                "available": {"executors": 0, "work_threads": 0, "threads_running": 0},
            },
            metrics,
            f"Expected metrics to count one used executor with its underlying "
            f"thread counts; got {metrics}.",
        )

    def test_metrics_after_return_in_reuse_mode_move_executor_to_available(self):
        """
        In reuse_mode=True, return_executor() moves the executor from
        pool_used to pool_available. The metrics should reflect the move:
        used.executors goes 1 -> 0, available.executors goes 0 -> 1.
        """
        # pylint: disable=attribute-defined-outside-init
        self.pool = AsyncioExecutorPool(reuse_mode=True)
        executor = self.pool.get_executor()
        # Swap in a mock with deterministic metrics, mirroring what would
        # happen if the real executor were idle after a return.
        self.pool.pool_used[0].shutdown(wait=True)
        mock_executor = make_metrics_executor(threads=2, running=0)
        self.pool.pool_used[0] = mock_executor

        self.pool.return_executor(mock_executor)

        metrics = self.pool.get_threads_metrics()
        self.assertEqual(
            {
                "used": {"executors": 0, "work_threads": 0, "threads_running": 0},
                "available": {"executors": 1, "work_threads": 2, "threads_running": 0},
            },
            metrics,
            f"Expected the returned executor to be visible in 'available' only; "
            f"got {metrics}.",
        )
        # The mock should still be the same instance, since reuse_mode keeps it.
        self.assertIs(
            mock_executor,
            self.pool.pool_available[0],
            "Returned executor should be the same instance held in pool_available.",
        )
        # Silence unused-local warning; executor is the original real one we already shut down.
        del executor

    def test_metrics_after_return_in_non_reuse_mode_drop_executor_from_pool(self):
        """
        In reuse_mode=False, return_executor() shuts the executor down
        and removes it entirely; neither bucket should hold it afterwards.
        """
        # pylint: disable=attribute-defined-outside-init
        self.pool = AsyncioExecutorPool(reuse_mode=False)
        executor = self.pool.get_executor()
        # Replace with a mock to make the assertion that shutdown() was
        # called clean and to avoid a real shutdown race.
        self.pool.pool_used[0].shutdown(wait=True)
        mock_executor = make_metrics_executor(threads=2, running=1)
        self.pool.pool_used[0] = mock_executor

        self.pool.return_executor(mock_executor)

        metrics = self.pool.get_threads_metrics()
        self.assertEqual(
            {
                "used": {"executors": 0, "work_threads": 0, "threads_running": 0},
                "available": {"executors": 0, "work_threads": 0, "threads_running": 0},
            },
            metrics,
            f"Expected the executor to disappear from both buckets in non-reuse "
            f"mode; got {metrics}.",
        )
        mock_executor.shutdown.assert_called_once()
        del executor

    def test_metrics_sum_thread_counts_across_multiple_used_executors(self):
        """
        With several executors in pool_used (and a separate one in
        pool_available), work_threads and threads_running should be the
        sums of the per-executor values, partitioned by bucket. This
        isolates the aggregation arithmetic from any threading flakiness
        by using mocks.
        """
        # pylint: disable=attribute-defined-outside-init
        self.pool = AsyncioExecutorPool(reuse_mode=True)
        self.pool.pool_used = [
            make_metrics_executor(threads=4, running=2),
            make_metrics_executor(threads=3, running=3),
            make_metrics_executor(threads=2, running=0),
        ]
        self.pool.pool_available = [
            make_metrics_executor(threads=5, running=0),
            make_metrics_executor(threads=1, running=0),
        ]

        metrics = self.pool.get_threads_metrics()

        self.assertEqual(
            {
                "used": {
                    "executors": 3,
                    "work_threads": 4 + 3 + 2,           # 9
                    "threads_running": 2 + 3 + 0,        # 5
                },
                "available": {
                    "executors": 2,
                    "work_threads": 5 + 1,               # 6
                    "threads_running": 0 + 0,            # 0
                },
            },
            metrics,
            f"Expected per-bucket sums of underlying executor metrics; got {metrics}.",
        )
