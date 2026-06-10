
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
See class comments
"""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import copy
import logging
import threading
import time

from leaf_common.asyncio.asyncio_executor import AsyncioExecutor


class AsyncioExecutorPool:
    # pylint: disable=too-many-instance-attributes
    """
    Class maintaining a dynamic set of reusable AsyncioExecutor instances.

    Garbage collection policy
    -------------------------
    When reuse_mode is True, executors are returned to pool_available rather
    than shut down. Each time an executor is returned, its return timestamp
    is recorded.

    Garbage collection is performed by a dedicated daemon GC thread that
    runs on its own schedule, independent of any get_executor() /
    return_executor() activity. Every gc_sweep_interval_seconds the thread
    wakes, identifies any executor whose idle period exceeds
    idle_timeout_seconds, removes it from pool_available, and shuts it
    down. This keeps the caller of get_executor / return_executor off both
    the sweep and the shutdown latency paths entirely.

    Both the idle threshold and the sweep interval are internally
    configurable via constructor parameters, with defaults given by
    DEFAULT_IDLE_TIMEOUT_SECONDS and DEFAULT_GC_SWEEP_INTERVAL_SECONDS.

    Lifecycle: callers should invoke shutdown() to stop the GC thread when
    the pool is no longer needed. The GC thread is a daemon so it will not
    block process exit if shutdown() is not called, but explicit shutdown
    is cleaner for tests and managed long-running services.
    """

    # Internal configuration: default idle time (seconds) after which an
    # executor sitting in pool_available is shut down and removed.
    DEFAULT_IDLE_TIMEOUT_SECONDS: float = 3 * 60.0

    # Internal configuration: default interval (seconds) at which the GC
    # thread wakes to look for stale executors.
    DEFAULT_GC_SWEEP_INTERVAL_SECONDS: float = 30.0

    def __init__(self, reuse_mode: bool = True, *,
                 idle_timeout_seconds: float = DEFAULT_IDLE_TIMEOUT_SECONDS,
                 gc_sweep_interval_seconds: float = DEFAULT_GC_SWEEP_INTERVAL_SECONDS):
        """
        Constructor.
        :param reuse_mode: True, if requested executor instances
                                 are taken from pool of available ones (pool mode);
                           False, if requested executor instances are created new
                                 and shutdown on return (backward compatible mode)
        :param idle_timeout_seconds: Idle time threshold in seconds. An
                                 AsyncioExecutor sitting in pool_available
                                 longer than this is shut down and removed
                                 by the background GC thread. Only applies
                                 when reuse_mode is True.
        :param gc_sweep_interval_seconds: Interval at which the GC thread
                                 checks pool_available for stale executors.
                                 Stale executors linger at most one sweep
                                 interval beyond the idle timeout before
                                 being collected. Only applies when
                                 reuse_mode is True.
        """
        self.reuse_mode: bool = reuse_mode
        self.idle_timeout_seconds: float = idle_timeout_seconds
        self.gc_sweep_interval_seconds: float = gc_sweep_interval_seconds

        # List of available (not currently used) AsyncioExecutor instances in the pool.
        self.pool_available: List[AsyncioExecutor] = []

        # List of currently used AsyncioExecutor instances in the pool.
        self.pool_used: List[AsyncioExecutor] = []

        # Maps id(executor) -> monotonic timestamp when the executor was
        # returned to pool_available. Only contains entries for executors
        # currently in pool_available; pruned on get_executor() and on sweep.
        self._returned_at: Dict[int, float] = {}

        self.lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Active GC: a daemon thread runs _gc_loop, sweeping on its own
        # schedule. The stop event lets shutdown() interrupt the sweep
        # interval wait promptly.
        self._gc_stop_event: threading.Event = threading.Event()
        self._gc_thread: Optional[threading.Thread] = None
        if self.reuse_mode:
            self._gc_thread = threading.Thread(
                target=self._gc_loop,
                name=f"AsyncioExecutorPool-GC-{id(self)}",
                daemon=True,
            )
            self._gc_thread.start()

        self.logger.debug(
            "AsyncioExecutorPool created: %s reuse: %s idle_timeout: %.1fs sweep_interval: %.1fs",
            id(self), str(self.reuse_mode), self.idle_timeout_seconds, self.gc_sweep_interval_seconds)

    def get_executor(self) -> AsyncioExecutor:
        """
        Get active (running) executor from the pool. Does not sweep;
        sweeping is the GC thread's responsibility. If a stale executor
        happens to sit at the head of pool_available before the next
        sweep, get_executor() will reuse it -- which is fine, since
        "stale" only means "would otherwise be collected as idle".
        :return: AsyncioExecutor instance
        """
        if self.reuse_mode:
            with self.lock:
                if len(self.pool_available) > 0:
                    result = self.pool_available.pop(0)
                    self._returned_at.pop(id(result), None)
                    self.logger.debug("Reusing AsyncioExecutor %s", id(result))
                    self.pool_used.append(result)
                    return result
        # Create AsyncioExecutor outside of lock
        # to avoid potentially longer locked periods
        result = AsyncioExecutor()
        result.start()
        self.logger.debug("Creating AsyncioExecutor %s", id(result))
        with self.lock:
            self.pool_used.append(result)
        return result

    def return_executor(self, executor: AsyncioExecutor):
        """
        Return AsyncioExecutor instance back to the pool of available instances.
        Does not sweep; the GC thread handles stale collection on its own
        schedule.
        :param executor: AsyncioExecutor to return.
        """
        with self.lock:
            if executor not in self.pool_used:
                raise ValueError(f"Returned executor {id(executor)} is not in the pool of used executors")
            self.pool_used.remove(executor)

        # Executor clean up: cancel current tasks and shutdown if not in reuse mode.
        if self.reuse_mode:
            executor.cancel_current_tasks()
        else:
            self.logger.debug("Shutting down: AsyncioExecutor %s", id(executor))
            executor.shutdown()

        if self.reuse_mode:
            with self.lock:
                self.pool_available.append(executor)
                self._returned_at[id(executor)] = time.monotonic()
                self.logger.debug("Returned to pool: AsyncioExecutor %s pool size: %d",
                                  id(executor), len(self.pool_available))

    def shutdown(self) -> None:
        """
        Stop the background GC thread. After this returns, the pool no
        longer reaps idle executors. Idempotent. Executors still held in
        pool_used or pool_available are NOT shut down here; callers that
        want those gone should handle them explicitly.
        """
        if self._gc_thread is None:
            return
        self._gc_stop_event.set()
        self._gc_thread.join()
        self._gc_thread = None

    def _gc_loop(self) -> None:
        """
        Active GC loop: sweep, then wait for either the configured
        interval or the stop event, whichever comes first. Exits cleanly
        when shutdown() sets the stop event.

        Exceptions from _sweep_once are logged but do not stop the loop,
        so a single bad executor cannot leak the rest of the pool.
        """
        while not self._gc_stop_event.is_set():
            try:
                self._sweep_once()
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self.logger.warning("GC: sweep raised %s; continuing", exc)
            # Sleep until the next sweep tick or until shutdown is signaled.
            self._gc_stop_event.wait(timeout=self.gc_sweep_interval_seconds)

    def _sweep_once(self, now: Optional[float] = None) -> None:
        """
        Identify any executors in pool_available whose idle time exceeds
        idle_timeout_seconds, remove them from the pool, and shut them
        down. No-op when not in reuse mode.

        pool_available is FIFO-ordered by return time (oldest at the head),
        so the scan stops at the first non-stale entry.

        Run by the GC thread on its periodic schedule; tests may call it
        directly with a synthetic `now` for deterministic verification.

        :param now: Optional override for the current time, in the same
                    units as time.monotonic(). Intended for tests; production
                    callers should omit this and let it default to
                    time.monotonic().
        """
        if not self.reuse_mode:
            return
        if now is None:
            now = time.monotonic()
        to_collect: List[AsyncioExecutor] = []
        with self.lock:
            keep_from: int = 0
            for executor in self.pool_available:
                returned_at: float = self._returned_at.get(id(executor), now)
                if now - returned_at > self.idle_timeout_seconds:
                    to_collect.append(executor)
                    keep_from += 1
                else:
                    break
            if keep_from > 0:
                for executor in self.pool_available[:keep_from]:
                    self._returned_at.pop(id(executor), None)
                del self.pool_available[:keep_from]
        # Shutdown outside the lock to keep the critical section short.
        for executor in to_collect:
            try:
                self.logger.debug("GC: shutting down idle AsyncioExecutor %s", id(executor))
                executor.shutdown(wait=True)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self.logger.warning(
                    "GC: shutdown failed for AsyncioExecutor %s: %s", id(executor), exc)

    def get_threads_metrics(self) -> Dict[str, Any]:
        """
        Get metrics related to threads in the pool of executors:
        for both collections of used and available executors,
        get the total number of executors in this collection "executors",
        the total number of work threads across all executors in this collection "work_threads",
        and the total number of currently running work threads
        across all executors in this collection "threads_running".
        """
        with self.lock:
            available_copy = copy.copy(self.pool_available)
            used_copy = copy.copy(self.pool_used)
        used_threads: int = 0
        used_running: int = 0
        available_threads: int = 0
        available_running: int = 0
        for executor in used_copy:
            threads, running = executor.get_threads_metrics()
            used_threads += threads
            used_running += running
        for executor in available_copy:
            threads, running = executor.get_threads_metrics()
            available_threads += threads
            available_running += running
        result_dict = {
            "used": {
                "executors": len(used_copy),
                "work_threads": used_threads,
                "threads_running": used_running
            },
            "available": {
                "executors": len(available_copy),
                "work_threads": available_threads,
                "threads_running": available_running
            }
        }
        return result_dict
