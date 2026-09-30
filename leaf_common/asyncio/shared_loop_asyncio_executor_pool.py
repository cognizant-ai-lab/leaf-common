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
"""Uncached shared-loop executor pool with the leaf-common pool interface.

Mirrors the surface of AsyncioExecutorPool so callers can hold either, but there
is deliberately no reuse, idle expiry, worker pool, or GC thread: every
acquisition builds a fresh SharedLoopAsyncioExecutor on the running loop.

Returning an executor differs from the native pool, and the difference is not
cosmetic. AsyncioExecutorPool.return_executor() shuts the executor down with
wait=True, joining its thread, so when that call returns the work really is
finished. Here there is no thread to join and the executor runs on the caller's
own loop, so a synchronous method cannot drain it -- blocking would mean the
loop waiting on itself. Hence two paths:

  - await areturn_executor(executor) is the complete one. It awaits
    ashutdown() and only then gives up ownership.
  - return_executor(executor) requests cancellation and returns at once. The
    pool KEEPS ownership of the executor until its tasks actually end, so a
    task that catches CancelledError and keeps running stays visible in
    get_threads_metrics() and dump_tasks_in_used_executors() instead of
    vanishing. Such an executor is "retiring"; await ashutdown() drains any
    that remain.

All operations on active executors must run on their host event loop.
"""
from typing import Any
from typing import Dict
from typing import List


from leaf_common.asyncio.shared_loop_asyncio_executor import SharedLoopAsyncioExecutor


class SharedLoopAsyncioExecutorPool:
    """Create a new shared-loop executor for every acquisition; never reuse it."""

    DEFAULT_IDLE_TIMEOUT_SECONDS: float = 180.0
    DEFAULT_GC_SWEEP_INTERVAL_SECONDS: float = 30.0

    # reuse_mode is accepted for signature parity with AsyncioExecutorPool;
    # this pool never reuses an executor. See the class comment.
    # pylint: disable=unused-argument
    def __init__(self, reuse_mode: bool = True, *,
                 idle_timeout_seconds: float = DEFAULT_IDLE_TIMEOUT_SECONDS,
                 gc_sweep_interval_seconds: float = DEFAULT_GC_SWEEP_INTERVAL_SECONDS,
                 max_workers: int = None):
        # Accept native pool options for import-level compatibility. There is
        # deliberately no reuse, idle expiry, worker pool, or cleanup thread.
        self.reuse_mode: bool = False
        self.idle_timeout_seconds: float = idle_timeout_seconds
        self.gc_sweep_interval_seconds: float = gc_sweep_interval_seconds
        self.max_workers: int = max_workers
        self.pool_used: List[SharedLoopAsyncioExecutor] = []
        self.pool_available: List[SharedLoopAsyncioExecutor] = []

        # Executors that have been returned but whose tasks have not finished.
        # Still owned by the pool: reported by metrics and task dumps, and
        # drained by ashutdown(). See the module comment.
        self.pool_retiring: List[SharedLoopAsyncioExecutor] = []

    def get_executor(self) -> SharedLoopAsyncioExecutor:
        """Return a fresh, started executor bound to the currently running loop.

        :return: A new SharedLoopAsyncioExecutor, already started
        """
        self._prune_retired()
        executor: SharedLoopAsyncioExecutor = SharedLoopAsyncioExecutor(max_workers=self.max_workers)
        executor.start()
        self.pool_used.append(executor)
        return executor

    def return_executor(self, executor: SharedLoopAsyncioExecutor) -> None:
        """Request cancellation and retire an executor without blocking.

        Ownership is KEPT until the executor's tasks actually end, so a task
        that catches CancelledError stays visible in metrics and task dumps.
        This method does NOT guarantee cleanup has completed on return; use
        await areturn_executor() when that guarantee is needed.

        A foreign or already returned executor is an error, matching the
        native pool contract.

        :param executor: The executor to retire
        """
        self._check_owned(executor)
        executor.shutdown(wait=False, cancel_futures=True)
        self.pool_used.remove(executor)
        if executor.has_pending_tasks():
            self.pool_retiring.append(executor)

    async def areturn_executor(self, executor: SharedLoopAsyncioExecutor,
                               timeout: float = None) -> None:
        """Retire an executor and await its cleanup. The complete path.

        On success the pool gives up ownership. If a timeout is given and it
        expires, ashutdown() raises TimeoutError and the executor stays
        retiring -- deliberately, so the pool does not lose track of an
        executor precisely when it has misbehaved. Await ashutdown() or call
        this again to retry.

        :param executor: The executor to retire
        :param timeout: Seconds to wait for owned tasks, or None to wait
                    indefinitely
        """
        if executor in self.pool_used:
            self.pool_used.remove(executor)
            self.pool_retiring.append(executor)
        elif executor not in self.pool_retiring:
            raise ValueError(f"Returned executor {id(executor)} is not in the pool of used executors")

        # A TimeoutError here leaves the executor in pool_retiring on purpose.
        await executor.ashutdown(cancel_futures=True, timeout=timeout)
        self._release(executor)

    def shutdown(self, wait: bool = True) -> None:
        """Shut the pool down. There is no GC thread to stop.

        Like leaf-common's pool.shutdown(), this does not close executors that
        are still checked out; return those individually.

        :param wait: True to insist that no retiring executor is still
                    working. Since this pool cannot block the shared loop, that
                    insistence is expressed as a raise rather than a wait --
                    the same way SharedLoopAsyncioExecutor.shutdown(wait=True)
                    does. Pass False to shut down without that check.
        """
        self._prune_retired()
        if wait and self.pool_retiring:
            raise RuntimeError(f"Cannot block the shared loop to drain "
                               f"{len(self.pool_retiring)} retiring executor(s); "
                               f"use await pool.ashutdown()")

    async def ashutdown(self, timeout: float = None) -> None:
        """Drain every retiring executor, then give up ownership of them.

        Executors still checked out are left alone, as in shutdown(). An
        executor whose tasks outlast the timeout stays retiring.

        :param timeout: Seconds to wait for each retiring executor's tasks, or
                    None to wait indefinitely
        """
        for executor in list(self.pool_retiring):
            await executor.ashutdown(cancel_futures=True, timeout=timeout)
            self._release(executor)

    def get_threads_metrics(self) -> Dict[str, Dict[str, int]]:
        """Report pool occupancy, with zero worker threads throughout.

        The native "used" and "available" buckets are joined by "retiring", so
        an executor that was returned while still running is counted rather
        than silently dropped.

        :return: A dict of bucket name to counts
        """
        self._prune_retired()
        return {
            "used": {"executors": len(self.pool_used), "work_threads": 0, "threads_running": 0},
            "available": {"executors": 0, "work_threads": 0, "threads_running": 0},
            "retiring": {"executors": len(self.pool_retiring), "work_threads": 0, "threads_running": 0},
        }

    # per_loop_timeout_s is accepted for signature parity; there is no
    # cross-thread probe here that could time out.
    # pylint: disable=unused-argument
    def dump_tasks_in_used_executors(self, per_loop_timeout_s: float = 2.0) -> Dict[str, Any]:
        """Snapshot owned tasks directly; no cross-thread probe or timeout needed.

        Covers retiring executors as well as used ones, each marked with
        "retiring", since a returned-but-still-running executor is exactly what
        a caller reaches for this method to find.

        :param per_loop_timeout_s: Ignored. See the comment above.
        :return: A dict keyed by str(id(executor)) describing each executor
        """
        self._prune_retired()
        result: Dict[str, Any] = {}
        for executor in self.pool_used + self.pool_retiring:
            tasks: List[Dict[str, Any]] = []
            # These executors share one loop: all_tasks() would incorrectly
            # attribute other requests' tasks to every executor.
            for task in executor.get_tracked_tasks():
                coro = task.get_coro()
                tasks.append({
                    "name": task.get_name(),
                    "coro": getattr(coro, "__qualname__", repr(coro)),
                    "done": task.done(),
                    "cancelled": task.cancelled(),
                    "stack": [{"file": frame.f_code.co_filename,
                               "line": frame.f_lineno,
                               "func": frame.f_code.co_name} for frame in task.get_stack()],
                })
            state: str = "responded" if executor.get_event_loop().is_running() else "not_running"
            result[str(id(executor))] = {
                "loop_state": state,
                "retiring": executor in self.pool_retiring,
                "tasks": tasks,
            }
        return result

    def _check_owned(self, executor: SharedLoopAsyncioExecutor) -> None:
        """Verify this pool handed the executor out and has not taken it back.

        :param executor: The executor to check
        """
        if executor not in self.pool_used:
            raise ValueError(f"Returned executor {id(executor)} is not in the pool of used executors")

    def _release(self, executor: SharedLoopAsyncioExecutor) -> None:
        """Give up ownership of a retiring executor that is finished.

        :param executor: The executor to forget
        """
        if executor in self.pool_retiring:
            self.pool_retiring.remove(executor)

    def _prune_retired(self) -> None:
        """Forget every retiring executor whose tasks have all finished.

        Called from the public methods rather than on a timer, since this pool
        has no GC thread and the shared loop gives us no other tick.
        """
        for executor in list(self.pool_retiring):
            if not executor.has_pending_tasks():
                self.pool_retiring.remove(executor)

    @staticmethod
    def format_task_dump(dump: Dict[str, Any]) -> str:
        """Render a task snapshot without importing the threaded implementation."""
        if not dump:
            return "(no used executors)"
        lines: List[str] = []
        for key, entry in dump.items():
            tasks: List[Dict[str, Any]] = entry.get("tasks", [])
            lines.append(f"== executor {key}  loop_state={entry.get('loop_state', 'unknown')}  "
                         f"tasks={len(tasks)} ==")
            if entry.get("loop_state") == "probe_error":
                lines.append(f"   probe_error: {entry.get('error')}")
            for task in tasks:
                lines.append(f"  - name={task['name']!r}  coro={task['coro']}  "
                             f"done={task['done']}  cancelled={task['cancelled']}")
                for frame in task.get("stack", []):
                    lines.append(f"      File \"{frame['file']}\", "
                                 f"line {frame['line']}, in {frame['func']}")
        return "\n".join(lines)
