
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
Unit tests for AsyncioExecutorPool.dump_tasks_in_used_executors() and
its companion formatter format_task_dump().

The dump probes every executor in pool_used by scheduling a one-shot
coroutine on that executor's event loop via run_coroutine_threadsafe.
The returned dict is keyed by str(id(executor)) with per-loop status and
(when responsive) the list of tasks with their suspended stacks.

These tests exercise the main paths with REAL AsyncioExecutor instances
(so scheduling on the executor loops actually goes through
run_coroutine_threadsafe end to end), and verify:
  - empty pool -> empty dict;
  - a live executor with a sleeping task -> loop_state="responded" plus
    the task in the result with correct name and coroutine identity;
  - multiple used executors -> one entry per executor;
  - a wedged loop -> loop_state="unresponsive_timeout" instead of
    blocking the caller indefinitely;
  - format_task_dump() covers the empty, responded, and unresponsive
    branches without needing a live probe.
"""
import asyncio
import time
from typing import List

from unittest import TestCase

from leaf_common.asyncio.asyncio_executor import AsyncioExecutor
from leaf_common.asyncio.asyncio_executor_pool import AsyncioExecutorPool


class AsyncioExecutorPoolDumpTasksTest(TestCase):
    """
    Verifies the on-demand asyncio-task dump: shape of the result dict,
    handling of unresponsive loops, and the formatter's output.
    """

    def setUp(self):
        """
        Each test gets its own pool with a very short GC sweep interval
        so GC noise doesn't leak into results, but non-zero so reuse_mode
        stays enabled.
        """
        # pylint: disable=attribute-defined-outside-init
        self.pool: AsyncioExecutorPool = AsyncioExecutorPool(
            reuse_mode=True,
            idle_timeout_seconds=60.0,
            gc_sweep_interval_seconds=60.0,
        )
        self._acquired: List[AsyncioExecutor] = []

    def tearDown(self):
        """
        Return every executor we acquired and shut down the pool + its
        GC thread so tests don't leak threads into each other.
        """
        for executor in self._acquired:
            try:
                self.pool.return_executor(executor)
            except ValueError:
                # Already returned by the test itself; ignore.
                pass
        self.pool.shutdown()
        # Also shut down any executors sitting in pool_available so we
        # don't leak their loop threads across tests.
        for executor in list(self.pool.pool_available):
            executor.shutdown(wait=True)

    def _acquire(self) -> AsyncioExecutor:
        """
        Get a running executor from the pool and remember it so
        tearDown() can hand it back reliably.
        """
        executor: AsyncioExecutor = self.pool.get_executor()
        self._acquired.append(executor)
        return executor

    def _schedule_sleeping_task(self, executor: AsyncioExecutor,
                                name: str, sleep_seconds: float = 30.0) -> None:
        """
        Schedule a long-sleeping coroutine on the executor's loop via the
        executor's own create_task() -- so the task is registered in
        executor._background_tasks and cancel_current_tasks() (called by
        pool.return_executor() at teardown) can cancel it promptly.

        The sleep duration is intentionally long so the task stays parked
        for the duration of the probe; teardown cancellation is what
        keeps the tests fast.
        """
        async def _sleeper():
            await asyncio.sleep(sleep_seconds)

        # create_task() is thread-safe: it uses call_soon_threadsafe under
        # the hood and blocks the caller until the task is actually created.
        task = executor.create_task(_sleeper(), submitter_id="dump-tasks-test")
        # AsyncioExecutor tasks are named "<submitter_id>:<qualname>"; rename
        # explicitly so the assertion side of the test can look up by our label.
        task.set_name(name)

    def test_empty_pool_returns_empty_dict(self):
        """
        No executors ever handed out -> dump_tasks_in_used_executors()
        returns an empty dict (not None, not an error).
        """
        result = self.pool.dump_tasks_in_used_executors()
        self.assertEqual({}, result,
                         f"Expected empty dict for empty pool; got {result}.")

    def test_single_used_executor_reports_running_task(self):
        """
        A live executor with a suspended task must appear in the dump
        with loop_state='responded' and the task in its tasks list.
        """
        executor: AsyncioExecutor = self._acquire()
        self._schedule_sleeping_task(executor, name="probe_alpha")
        # A brief settle so the task is definitely on the loop before we probe.
        time.sleep(0.1)

        result = self.pool.dump_tasks_in_used_executors(per_loop_timeout_s=2.0)

        key: str = str(id(executor))
        self.assertIn(key, result)
        entry = result[key]
        self.assertEqual("responded", entry["loop_state"],
                         f"Expected 'responded' loop_state; got {entry}.")
        task_names = [t["name"] for t in entry["tasks"]]
        self.assertIn("probe_alpha", task_names,
                      f"Expected probe_alpha in dump; got tasks={entry['tasks']}.")
        # Ensure the coroutine identity is captured, not just repr(coro).
        matching = [t for t in entry["tasks"] if t["name"] == "probe_alpha"][0]
        self.assertIn("_sleeper", matching["coro"])
        # And the suspended stack is non-empty (task is parked in asyncio.sleep).
        self.assertGreater(len(matching["stack"]), 0)

    def test_multiple_used_executors_all_reported(self):
        """
        Each executor in pool_used shows up in the result dict as its own
        top-level entry keyed by str(id(executor)).
        """
        executor_a: AsyncioExecutor = self._acquire()
        executor_b: AsyncioExecutor = self._acquire()
        executor_c: AsyncioExecutor = self._acquire()

        # Put a distinct task on each so tests catch cross-loop mixups.
        self._schedule_sleeping_task(executor_a, name="task_a")
        self._schedule_sleeping_task(executor_b, name="task_b")
        self._schedule_sleeping_task(executor_c, name="task_c")
        time.sleep(0.1)

        result = self.pool.dump_tasks_in_used_executors(per_loop_timeout_s=2.0)

        expected_keys = {str(id(executor_a)), str(id(executor_b)), str(id(executor_c))}
        self.assertEqual(expected_keys, set(result.keys()))

        # Each executor sees only its own task, not the others'.
        self.assertEqual(["task_a"],
                         [t["name"] for t in result[str(id(executor_a))]["tasks"]])
        self.assertEqual(["task_b"],
                         [t["name"] for t in result[str(id(executor_b))]["tasks"]])
        self.assertEqual(["task_c"],
                         [t["name"] for t in result[str(id(executor_c))]["tasks"]])

    def test_wedged_loop_is_reported_as_unresponsive(self):
        """
        If a loop is CPU-bound on a synchronous hog and cannot service
        our probe coroutine within per_loop_timeout_s, its entry is
        marked 'unresponsive_timeout' instead of blocking the caller.
        The probe caller must still return promptly.
        """
        executor: AsyncioExecutor = self._acquire()

        # Wedge the executor's loop by scheduling a sync busy-wait that
        # runs on the loop thread itself. call_soon_threadsafe queues a
        # callback that, once picked up, will monopolize the loop for
        # far longer than the probe timeout.
        wedge_seconds: float = 1.5
        import threading  # pylint: disable=import-outside-toplevel
        wedge_started = threading.Event()

        def _wedge():
            wedge_started.set()
            time.sleep(wedge_seconds)

        executor.get_event_loop().call_soon_threadsafe(_wedge)
        self.assertTrue(wedge_started.wait(timeout=0.5), "Wedge callback did not start in time")
        start = time.monotonic()
        result = self.pool.dump_tasks_in_used_executors(per_loop_timeout_s=0.2)
        elapsed = time.monotonic() - start

        # Reasonable upper bound: the timeout plus a bit of scheduling slack.
        self.assertLess(elapsed, 1.0,
                        f"dump_tasks should not block past per_loop_timeout; took {elapsed:.2f}s")

        entry = result[str(id(executor))]
        self.assertEqual("unresponsive_timeout", entry["loop_state"],
                         f"Expected 'unresponsive_timeout' when loop is wedged; got {entry}")
        self.assertEqual([], entry["tasks"])

        # Wait for the wedge to finish so tearDown can shut the loop cleanly.
        time.sleep(wedge_seconds)


class AsyncioExecutorPoolFormatTaskDumpTest(TestCase):
    """
    Direct tests for format_task_dump. It's a pure function of the dict
    returned by dump_tasks_in_used_executors, so we test it with
    hand-crafted inputs -- no live executors needed.
    """

    def test_empty_dump_reports_no_executors(self):
        """format_task_dump({}) returns a single-line placeholder message."""
        self.assertEqual("(no used executors)",
                         AsyncioExecutorPool.format_task_dump({}))

    def test_responded_dump_includes_task_and_stack(self):
        """
        A responded entry's task list, coroutine name, and stack frames
        are visible in the formatted output.
        """
        dump = {
            "42": {
                "loop_state": "responded",
                "tasks": [
                    {
                        "name": "worker-1",
                        "coro": "my.module.do_work",
                        "done": False,
                        "cancelled": False,
                        "stack": [
                            {"file": "/tmp/x.py", "line": 17, "func": "do_work"},
                        ],
                    }
                ],
            }
        }
        text = AsyncioExecutorPool.format_task_dump(dump)
        self.assertIn("executor 42", text)
        self.assertIn("loop_state=responded", text)
        self.assertIn("worker-1", text)
        self.assertIn("my.module.do_work", text)
        self.assertIn("/tmp/x.py", text)
        self.assertIn("line 17", text)

    def test_unresponsive_dump_still_renders_cleanly(self):
        """
        An unresponsive_timeout entry has no tasks; format_task_dump
        still labels the executor and its loop_state without erroring.
        """
        dump = {"99": {"loop_state": "unresponsive_timeout", "tasks": []}}
        text = AsyncioExecutorPool.format_task_dump(dump)
        self.assertIn("executor 99", text)
        self.assertIn("loop_state=unresponsive_timeout", text)
        self.assertIn("tasks=0", text)

    def test_probe_error_dump_includes_error_message(self):
        """
        A probe_error entry surfaces the error field in the formatted
        output so operators can see why the probe failed.
        """
        dump = {
            "7": {
                "loop_state": "probe_error",
                "error": "RuntimeError: kaboom",
                "tasks": [],
            }
        }
        text = AsyncioExecutorPool.format_task_dump(dump)
        self.assertIn("executor 7", text)
        self.assertIn("loop_state=probe_error", text)
        self.assertIn("probe_error: RuntimeError: kaboom", text)
