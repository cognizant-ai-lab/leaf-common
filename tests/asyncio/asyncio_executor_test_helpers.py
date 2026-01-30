
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
Helper functions for AsyncioExecutor unit tests.
"""

import asyncio


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
