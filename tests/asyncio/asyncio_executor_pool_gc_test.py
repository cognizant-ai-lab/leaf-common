
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
Unit tests for AsyncioExecutorPool's active idle-executor garbage
collection.

The GC runs on a dedicated daemon thread which periodically calls
_sweep_once(): identify executors in pool_available whose idle period
exceeds idle_timeout_seconds, remove them, and shut them down. Most
tests drive _sweep_once() directly with a synthetic `now` to verify
behavior deterministically without waiting on real time; one end-to-end
test exercises the periodic thread with a tight sweep interval.
"""
import threading
import time

from unittest import TestCase
from unittest.mock import MagicMock

from leaf_common.asyncio.asyncio_executor_pool import AsyncioExecutorPool


class AsyncioExecutorPoolGcTest(TestCase):
    """
    Verifies the active idle-executor GC: the sweep correctly partitions
    stale vs fresh executors, the periodic GC thread runs sweeps on its
    own schedule, and the lifecycle (start / shutdown / exception safety)
    is robust.
    """

    def tearDown(self):
        """
        Stop the background GC thread and shut down any real executors
        lingering in the pool. Mocks are no-ops.
        """
        if getattr(self, "pool", None) is None:
            return
        self.pool.shutdown()
        for executor in list(self.pool.pool_used) + list(self.pool.pool_available):
            try:
                executor.shutdown(wait=True)
            except Exception:  # pylint: disable=broad-exception-caught
                pass

    def test_sweep_collects_idle_executor_after_timeout(self):
        """
        _sweep_once() removes and shuts down an executor whose idle period
        exceeds idle_timeout_seconds.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=True, idle_timeout_seconds=10.0)
        self.pool.shutdown()  # stop background GC; this test drives _sweep_once() manually
        mock_executor = MagicMock()
        self.pool.pool_available = [mock_executor]
        self.pool._returned_at[id(mock_executor)] = 100.0

        # Simulate 100 seconds elapsed (> 10s threshold).
        self.pool._sweep_once(now=200.0)

        self.assertEqual(
            [], self.pool.pool_available,
            "Expected the stale executor to be removed from pool_available."
        )
        self.assertEqual(
            {}, self.pool._returned_at,
            "Expected the stale executor's timestamp to be cleared."
        )
        mock_executor.shutdown.assert_called_once_with(wait=True)

    def test_sweep_preserves_fresh_executor_within_timeout(self):
        """
        An executor whose idle time is below idle_timeout_seconds is left
        in pool_available and not shut down.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=True, idle_timeout_seconds=10.0)
        self.pool.shutdown()  # stop background GC; this test drives _sweep_once() manually
        mock_executor = MagicMock()
        self.pool.pool_available = [mock_executor]
        self.pool._returned_at[id(mock_executor)] = 100.0

        # 5 seconds elapsed (< 10s threshold).
        self.pool._sweep_once(now=105.0)

        self.assertEqual(
            [mock_executor], self.pool.pool_available,
            "Expected the fresh executor to remain in pool_available."
        )
        self.assertIn(
            id(mock_executor), self.pool._returned_at,
            "Expected the fresh executor's timestamp to remain recorded."
        )
        mock_executor.shutdown.assert_not_called()

    def test_sweep_preserves_fresh_executors_following_stale_ones(self):
        """
        With a mix of stale and fresh executors in pool_available (oldest
        first), the sweep removes the stale prefix and stops at the first
        fresh entry. Fresh executors after a fresh one are also preserved.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=True, idle_timeout_seconds=10.0)
        self.pool.shutdown()  # stop background GC; this test drives _sweep_once() manually
        stale_a = MagicMock(name="stale_a")
        stale_b = MagicMock(name="stale_b")
        fresh_c = MagicMock(name="fresh_c")
        fresh_d = MagicMock(name="fresh_d")
        self.pool.pool_available = [stale_a, stale_b, fresh_c, fresh_d]
        self.pool._returned_at = {
            id(stale_a): 100.0,
            id(stale_b): 101.0,
            id(fresh_c): 195.0,
            id(fresh_d): 198.0,
        }

        # now=200.0: stale_a idle 100s, stale_b idle 99s, fresh_c idle 5s, fresh_d idle 2s.
        self.pool._sweep_once(now=200.0)

        self.assertEqual(
            [fresh_c, fresh_d], self.pool.pool_available,
            "Expected only the fresh executors to remain, in order."
        )
        self.assertEqual(
            {id(fresh_c): 195.0, id(fresh_d): 198.0}, self.pool._returned_at,
            "Expected timestamps only for the surviving fresh executors."
        )
        stale_a.shutdown.assert_called_once_with(wait=True)
        stale_b.shutdown.assert_called_once_with(wait=True)
        fresh_c.shutdown.assert_not_called()
        fresh_d.shutdown.assert_not_called()

    def test_sweep_is_noop_in_non_reuse_mode(self):
        """
        In reuse_mode=False, _sweep_once() is a no-op and no GC thread is
        started.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=False, idle_timeout_seconds=10.0)
        mock_executor = MagicMock()
        self.pool.pool_available = [mock_executor]
        self.pool._returned_at[id(mock_executor)] = 100.0

        self.pool._sweep_once(now=10_000.0)

        self.assertEqual(
            [mock_executor], self.pool.pool_available,
            "Expected non-reuse mode to skip GC entirely; pool_available untouched."
        )
        mock_executor.shutdown.assert_not_called()
        self.assertIsNone(
            self.pool._gc_thread,
            "Expected no GC thread to be started in non-reuse mode."
        )

    def test_get_and_return_do_not_sweep(self):
        """
        get_executor() and return_executor() must not perform a sweep -
        sweeping is the GC thread's exclusive responsibility. A stale
        executor sitting in pool_available is not shut down by caller-side
        calls.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        # Long sweep interval so the GC thread doesn't race the assertions.
        self.pool = AsyncioExecutorPool(
            reuse_mode=True,
            idle_timeout_seconds=10.0,
            gc_sweep_interval_seconds=3600.0,
        )

        stale_executor = MagicMock(name="stale")
        self.pool.pool_available = [stale_executor]
        self.pool._returned_at[id(stale_executor)] = -10_000.0

        # Stop the GC thread so it doesn't interfere with the test
        self.pool.shutdown()

        # Put a different executor through the get/return cycle.
        returning = MagicMock(name="returning")
        self.pool.pool_used = [returning]
        self.pool.return_executor(returning)

        # The stale executor is still there: no caller-side sweep.
        self.assertIn(
            stale_executor, self.pool.pool_available,
            "Expected return_executor() not to sweep the stale executor."
        )
        stale_executor.shutdown.assert_not_called()

        # get_executor() can reuse a stale entry, but still does not shut it down.
        # FIFO order: stale_executor was added first, so it's at the head.
        result = self.pool.get_executor()
        self.assertIs(
            result, stale_executor,
            "Expected get_executor() to reuse the head entry without sweeping."
        )
        stale_executor.shutdown.assert_not_called()

    def test_active_gc_thread_collects_idle_executor_on_its_own_schedule(self):
        """
        With no get_executor() / return_executor() activity, the GC thread
        still wakes on its interval and collects stale executors.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        # Tight schedule: any stale executor is collected within tens of ms.
        self.pool = AsyncioExecutorPool(
            reuse_mode=True,
            idle_timeout_seconds=0.001,        # 1 ms -> any backdated entry is stale
            gc_sweep_interval_seconds=0.01,    # sweep every 10 ms
        )

        mock_executor = MagicMock()
        with self.pool.lock:
            self.pool.pool_available = [mock_executor]
            # Backdate the entry so it's stale immediately.
            self.pool._returned_at[id(mock_executor)] = 0.0

        # Wait long enough for the GC thread to tick at least once after we
        # inserted the entry. 200 ms is generous; the typical case clears
        # the entry on the next ~10 ms tick.
        deadline = time.monotonic() + 0.5
        while time.monotonic() < deadline:
            if not self.pool.pool_available:
                break
            time.sleep(0.01)

        self.assertEqual(
            [], self.pool.pool_available,
            "Expected the active GC thread to collect the stale executor on its own."
        )
        mock_executor.shutdown.assert_called_once_with(wait=True)

    def test_default_config_values_are_set(self):
        """
        A pool constructed without overrides picks up the documented
        class-level defaults for both idle timeout and sweep interval.
        """
        # pylint: disable=attribute-defined-outside-init
        self.pool = AsyncioExecutorPool(reuse_mode=True)
        self.assertEqual(
            AsyncioExecutorPool.DEFAULT_IDLE_TIMEOUT_SECONDS,
            self.pool.idle_timeout_seconds,
            "Expected the default idle timeout to be DEFAULT_IDLE_TIMEOUT_SECONDS."
        )
        self.assertEqual(
            AsyncioExecutorPool.DEFAULT_GC_SWEEP_INTERVAL_SECONDS,
            self.pool.gc_sweep_interval_seconds,
            "Expected the default sweep interval to be DEFAULT_GC_SWEEP_INTERVAL_SECONDS."
        )

    def test_shutdown_stops_gc_thread(self):
        """
        pool.shutdown() signals the stop event and joins the GC thread.
        After shutdown(), the thread is not alive.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        # Long sweep interval to make sure shutdown actually interrupts the wait.
        self.pool = AsyncioExecutorPool(
            reuse_mode=True,
            gc_sweep_interval_seconds=3600.0,
        )
        gc_thread = self.pool._gc_thread
        self.assertIsNotNone(gc_thread, "Expected GC thread to be started in reuse mode.")
        self.assertTrue(gc_thread.is_alive(), "Expected GC thread to be alive after construction.")

        self.pool.shutdown()

        self.assertFalse(gc_thread.is_alive(), "Expected GC thread to exit after shutdown().")
        self.assertIsNone(self.pool._gc_thread, "Expected _gc_thread to be cleared after shutdown().")
        # Second shutdown() call is idempotent.
        self.pool.shutdown()

    def test_gc_thread_survives_sweep_exception(self):
        """
        If a per-executor shutdown raises during sweep, the GC thread
        logs and continues; subsequent stale executors are still
        collected on the same sweep.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=True, idle_timeout_seconds=10.0)

        bad_executor = MagicMock(name="bad")
        bad_executor.shutdown.side_effect = RuntimeError("simulated shutdown failure")
        good_executor = MagicMock(name="good")

        base = time.monotonic()
        with self.pool.lock:
            self.pool.pool_available = [bad_executor, good_executor]
            self.pool._returned_at = {
                id(bad_executor): base,
                id(good_executor): base,
            }

        # Drive sweep synchronously on the test thread with a synthetic time.
        self.pool._sweep_once(now=base + self.pool.idle_timeout_seconds + 1.0)

        bad_executor.shutdown.assert_called_once_with(wait=True)
        good_executor.shutdown.assert_called_once_with(wait=True)
        self.assertEqual([], self.pool.pool_available)
        self.assertTrue(
            self.pool._gc_thread.is_alive(),
            "Expected the GC thread itself to remain alive."
        )

    def test_no_gc_threads_leak_across_pools(self):
        """
        Each pool starts exactly one GC thread; shutdown() reliably stops
        it. Constructing and shutting down many pools must not leak
        threads.
        """
        baseline_gc_threads = {
            t.name for t in threading.enumerate()
            if t.name.startswith("AsyncioExecutorPool-GC-") and t.is_alive()
        }
        pools = [AsyncioExecutorPool(reuse_mode=True) for _ in range(5)]
        for pool in pools:
            pool.shutdown()
        live_gc_threads = [
            t for t in threading.enumerate()
            if t.name.startswith("AsyncioExecutorPool-GC-") and t.is_alive() and t.name not in baseline_gc_threads
        ]
        self.assertEqual(
            [], live_gc_threads,
            f"Expected no new GC threads to remain after shutdown(); found {live_gc_threads}."
        )
