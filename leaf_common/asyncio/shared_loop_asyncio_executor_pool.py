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

All operations on active executors must run on their host event loop.
return_executor() requests cancellation without blocking; await
executor.ashutdown() if completion of cleanup must be guaranteed.
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

    def get_executor(self) -> SharedLoopAsyncioExecutor:
        """Return a fresh, started executor bound to the currently running loop."""
        executor = SharedLoopAsyncioExecutor(max_workers=self.max_workers)
        executor.start()
        self.pool_used.append(executor)
        return executor

    def return_executor(self, executor: SharedLoopAsyncioExecutor) -> None:
        """Retire an executor and request cancellation; do not block the loop.

        Cancellation finalizers run when the loop next gets control. This method
        does not guarantee they have completed on return. A foreign or already
        returned executor is an error, matching the native pool contract.
        """
        if executor not in self.pool_used:
            raise ValueError(f"Returned executor {id(executor)} is not in the pool of used executors")
        executor.shutdown(wait=False, cancel_futures=True)
        self.pool_used.remove(executor)

    def shutdown(self, wait: bool = True) -> None:
        """No-op: there is no GC thread to stop.

        Like leaf-common's pool.shutdown(), this does not close checked-out
        executors. Return those individually. The wait argument is ignored.
        """

    def get_threads_metrics(self) -> Dict[str, Dict[str, int]]:
        """Preserve the native metrics shape, with zero worker threads."""
        return {
            "used": {"executors": len(self.pool_used), "work_threads": 0, "threads_running": 0},
            "available": {"executors": 0, "work_threads": 0, "threads_running": 0},
        }

    # per_loop_timeout_s is accepted for signature parity; there is no
    # cross-thread probe here that could time out.
    # pylint: disable=unused-argument
    def dump_tasks_in_used_executors(self, per_loop_timeout_s: float = 2.0) -> Dict[str, Any]:
        """Snapshot owned tasks directly; no cross-thread probe or timeout needed."""
        result: Dict[str, Any] = {}
        for executor in self.pool_used:
            tasks: List[Dict[str, Any]] = []
            # These executors share one loop: all_tasks() would incorrectly
            # attribute other requests' tasks to every executor.
            for task in executor._tasks:  # pylint: disable=protected-access
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
            result[str(id(executor))] = {"loop_state": state, "tasks": tasks}
        return result

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
