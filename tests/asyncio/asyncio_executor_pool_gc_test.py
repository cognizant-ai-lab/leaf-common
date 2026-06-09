
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
Unit tests for AsyncioExecutorPool's idle-executor garbage collection.

The pool keeps a parallel _returned_at timestamp per executor in
pool_available. A passive sweep (_collect_idle_executors) runs on every
get_executor() and return_executor() call. The sweep removes any executor
whose idle time exceeds idle_timeout_seconds and enqueues it on the
background GC thread for shutdown. Tests drive _collect_idle_executors
with an explicit `now` to avoid real-time waits, and use _gc_queue.join()
to wait for the GC thread to finish before asserting on shutdown.
"""
import threading
import time

from unittest import TestCase
from unittest.mock import MagicMock

from leaf_common.asyncio.asyncio_executor_pool import AsyncioExecutorPool


class AsyncioExecutorPoolGcTest(TestCase):
    """
    Verifies the idle-executor GC policy: stale executors are removed
    synchronously and shut down asynchronously on the background GC
    thread; fresh ones are kept; non-reuse mode is unaffected.
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

    def test_idle_executor_collected_after_timeout(self):
        """
        An executor returned to the pool whose idle time exceeds
        idle_timeout_seconds is removed from pool_available synchronously
        and shut down asynchronously by the GC thread.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=True, idle_timeout_seconds=10.0)
        mock_executor = MagicMock()
        self.pool.pool_available = [mock_executor]
        self.pool._returned_at[id(mock_executor)] = 100.0

        # Simulate 100 seconds elapsed (> 10s threshold).
        self.pool._collect_idle_executors(now=200.0)

        # Sync side-effects are visible immediately.
        self.assertEqual(
            [], self.pool.pool_available,
            "Expected the stale executor to be removed from pool_available."
        )
        self.assertEqual(
            {}, self.pool._returned_at,
            "Expected the stale executor's timestamp to be cleared."
        )
        # Shutdown happens on the GC thread; wait for it.
        self.pool._gc_queue.join()
        mock_executor.shutdown.assert_called_once_with(wait=True)

    def test_fresh_executor_not_collected_within_timeout(self):
        """
        An executor whose idle time is below idle_timeout_seconds is left
        in pool_available, never enqueued for shutdown.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=True, idle_timeout_seconds=10.0)
        mock_executor = MagicMock()
        self.pool.pool_available = [mock_executor]
        self.pool._returned_at[id(mock_executor)] = 100.0

        # 5 seconds elapsed (< 10s threshold).
        self.pool._collect_idle_executors(now=105.0)
        self.pool._gc_queue.join()

        self.assertEqual(
            [mock_executor], self.pool.pool_available,
            "Expected the fresh executor to remain in pool_available."
        )
        self.assertIn(
            id(mock_executor), self.pool._returned_at,
            "Expected the fresh executor's timestamp to remain recorded."
        )
        mock_executor.shutdown.assert_not_called()

    def test_gc_preserves_fresh_executors_following_stale_ones(self):
        """
        With a mix of stale and fresh executors in pool_available (oldest
        first), GC removes the stale prefix and stops at the first fresh
        entry. Fresh executors after a fresh one are also preserved.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=True, idle_timeout_seconds=10.0)
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
        self.pool._collect_idle_executors(now=200.0)
        self.pool._gc_queue.join()

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

    def test_gc_runs_on_return_executor(self):
        """
        Calling return_executor triggers the passive GC sweep. A stale
        executor sitting in pool_available is collected when another
        executor is returned.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=True, idle_timeout_seconds=10.0)

        stale_executor = MagicMock(name="stale")
        self.pool.pool_available = [stale_executor]
        self.pool._returned_at[id(stale_executor)] = -10_000.0

        returning_executor = MagicMock(name="returning")
        self.pool.pool_used = [returning_executor]

        self.pool.return_executor(returning_executor)
        self.pool._gc_queue.join()

        self.assertEqual(
            [returning_executor], self.pool.pool_available,
            "Expected the stale executor to be GC'd and only the returning one to remain."
        )
        stale_executor.shutdown.assert_called_once_with(wait=True)

    def test_gc_runs_on_get_executor(self):
        """
        Calling get_executor triggers the passive GC sweep. If the only
        executor in pool_available is stale, it is collected and
        get_executor falls through to construct a fresh one.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=True, idle_timeout_seconds=10.0)

        stale_executor = MagicMock(name="stale")
        self.pool.pool_available = [stale_executor]
        self.pool._returned_at[id(stale_executor)] = -10_000.0

        result = self.pool.get_executor()
        self.pool._gc_queue.join()

        self.assertIsNot(
            result, stale_executor,
            "Expected get_executor to skip the stale entry rather than reuse it."
        )
        self.assertNotIn(
            stale_executor, self.pool.pool_available,
            "Expected the stale executor to be removed from pool_available."
        )
        stale_executor.shutdown.assert_called_once_with(wait=True)
        # Tidy up the real executor get_executor() just constructed.
        self.pool.pool_used.remove(result)
        result.shutdown(wait=True)

    def test_gc_is_noop_in_non_reuse_mode(self):
        """
        In reuse_mode=False, _collect_idle_executors is a no-op and no GC
        thread is started.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=False, idle_timeout_seconds=10.0)
        mock_executor = MagicMock()
        self.pool.pool_available = [mock_executor]
        self.pool._returned_at[id(mock_executor)] = 100.0

        self.pool._collect_idle_executors(now=10_000.0)

        self.assertEqual(
            [mock_executor], self.pool.pool_available,
            "Expected non-reuse mode to skip GC entirely; pool_available untouched."
        )
        mock_executor.shutdown.assert_not_called()
        self.assertIsNone(
            self.pool._gc_thread,
            "Expected no GC thread to be started in non-reuse mode."
        )

    def test_default_idle_timeout_is_set(self):
        """
        A pool constructed without idle_timeout_seconds picks up the
        documented class default.
        """
        # pylint: disable=attribute-defined-outside-init
        self.pool = AsyncioExecutorPool(reuse_mode=True)
        self.assertEqual(
            AsyncioExecutorPool.DEFAULT_IDLE_TIMEOUT_SECONDS,
            self.pool.idle_timeout_seconds,
            "Expected the default idle timeout to be DEFAULT_IDLE_TIMEOUT_SECONDS."
        )

    def test_sweep_returns_quickly_even_when_shutdowns_are_slow(self):
        """
        The hybrid design moves the expensive shutdown(wait=True) off
        the caller's path. Even when each per-executor shutdown is
        deliberately slow, _collect_idle_executors must return in time
        bounded by the list/dict mutation only -- well under the slow
        per-shutdown time.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=True, idle_timeout_seconds=10.0)

        # Each mock's shutdown will block for 50 ms. With sequential
        # synchronous shutdown of 5 stale executors, a passive sweep
        # would take >=250 ms. With the hybrid design, the sweep should
        # return in single-digit ms.
        def slow_shutdown(*_args, **_kwargs):
            time.sleep(0.05)

        stale_executors = [MagicMock(name=f"stale_{i}") for i in range(5)]
        for executor in stale_executors:
            executor.shutdown.side_effect = slow_shutdown

        self.pool.pool_available = list(stale_executors)
        self.pool._returned_at = {id(executor): 0.0 for executor in stale_executors}

        start = time.perf_counter()
        self.pool._collect_idle_executors(now=1_000.0)
        sweep_elapsed = time.perf_counter() - start

        # Caller-visible sweep should be much faster than the synchronous
        # alternative (5 * 50ms = 250ms). 50 ms is a generous bound that
        # still proves the shutdowns aren't on the caller's thread.
        self.assertLess(
            sweep_elapsed, 0.05,
            f"Sweep should return without waiting on slow shutdowns; "
            f"actually took {sweep_elapsed*1000:.1f} ms."
        )

        # Verify the GC thread actually does shut them all down.
        self.pool._gc_queue.join()
        for executor in stale_executors:
            executor.shutdown.assert_called_once_with(wait=True)

    def test_shutdown_stops_gc_thread(self):
        """
        pool.shutdown() drains the GC queue and stops the GC thread.
        After shutdown(), the thread is no longer running.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=True, idle_timeout_seconds=10.0)
        gc_thread = self.pool._gc_thread
        self.assertIsNotNone(gc_thread, "Expected GC thread to be started in reuse mode.")
        self.assertTrue(gc_thread.is_alive(), "Expected GC thread to be alive after construction.")

        self.pool.shutdown()

        self.assertFalse(gc_thread.is_alive(), "Expected GC thread to exit after shutdown().")
        self.assertIsNone(self.pool._gc_thread, "Expected _gc_thread to be cleared after shutdown().")
        # Second shutdown() call is idempotent.
        self.pool.shutdown()

    def test_gc_thread_survives_shutdown_exception(self):
        """
        If one executor's shutdown raises, the GC thread logs and moves on
        to the next item rather than dying.
        """
        # pylint: disable=attribute-defined-outside-init,protected-access
        self.pool = AsyncioExecutorPool(reuse_mode=True, idle_timeout_seconds=10.0)

        bad_executor = MagicMock(name="bad")
        bad_executor.shutdown.side_effect = RuntimeError("simulated shutdown failure")
        good_executor = MagicMock(name="good")

        self.pool.pool_available = [bad_executor, good_executor]
        self.pool._returned_at = {
            id(bad_executor): 0.0,
            id(good_executor): 0.0,
        }

        self.pool._collect_idle_executors(now=1_000.0)
        self.pool._gc_queue.join()

        bad_executor.shutdown.assert_called_once_with(wait=True)
        good_executor.shutdown.assert_called_once_with(wait=True)
        # GC thread must still be alive after handling the exception.
        self.assertTrue(
            self.pool._gc_thread.is_alive(),
            "Expected GC thread to survive a per-executor shutdown exception."
        )

    def test_no_extra_gc_threads_leak_across_pools(self):
        """
        Each pool starts exactly one GC thread; shutdown() reliably stops
        it. Constructing and shutting down many pools must not leak
        threads.
        """
        # pylint: disable=attribute-defined-outside-init
        pools = [AsyncioExecutorPool(reuse_mode=True) for _ in range(5)]
        for pool in pools:
            pool.shutdown()
        # The current TestCase's pool is None; tearDown is a no-op.
        live_gc_threads = [
            t for t in threading.enumerate()
            if t.name.startswith("AsyncioExecutorPool-GC-") and t.is_alive()
        ]
        self.assertEqual(
            [], live_gc_threads,
            f"Expected no GC threads to remain after shutdown(); found {live_gc_threads}."
        )
