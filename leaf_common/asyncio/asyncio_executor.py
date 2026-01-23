
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
See class comment for details.
"""
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import List

import asyncio
import copy
import functools
import inspect
import threading
import traceback

from asyncio import AbstractEventLoop
from asyncio import Future
from asyncio import Task
from concurrent import futures

EXECUTOR_START_TIMEOUT_SECONDS: int = 5


class AsyncioExecutor(futures.Executor):
    """
    Class for managing asynchronous background tasks in a single thread
    Riffed from:
    https://stackoverflow.com/questions/38387443/how-to-implement-a-async-grpc-python-server/63020796#63020796
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self._shutdown: bool = False
        self._thread: threading.Thread = None
        # We are going to start new thread for this Executor,
        # so we need a new event loop bound to this particular thread:
        self._loop: AbstractEventLoop = asyncio.new_event_loop()
        self._loop.set_exception_handler(AsyncioExecutor.loop_exception_handler)
        self._loop_ready = threading.Event()
        self._init_done = threading.Event()
        self._background_tasks: Dict[int, Dict[str, Any]] = {}
        # background tasks table will be accessed from different threads,
        # so protect it:
        self._background_tasks_lock = threading.Lock()

    def get_event_loop(self) -> AbstractEventLoop:
        """
        :return: The AbstractEventLoop associated with this instance
        """
        return self._loop

    def start(self):
        """
        Starts the background thread.
        Do this separately from constructor for more control.
        """
        # Don't start twice
        if self._thread is not None:
            return

        self._thread = threading.Thread(target=self.loop_manager,
                                        args=(self._loop, self._loop_ready),
                                        daemon=True)
        self._thread.start()
        timeout: int = EXECUTOR_START_TIMEOUT_SECONDS
        was_set: bool = self._loop_ready.wait(timeout=timeout)
        if not was_set:
            raise ValueError(f"FAILED to start executor event loop in {timeout} sec")

    def initialize(self, init_function: Callable):
        """
        Call initializing function on executor event loop
        and wait for it to finish.
        :param init_function: function to call.
        """
        if self._shutdown:
            raise RuntimeError('Cannot schedule new calls after shutdown')
        if not self._loop.is_running():
            raise RuntimeError("Loop must be started before any function can "
                               "be submitted")
        self._init_done.clear()
        self._loop.call_soon_threadsafe(self.run_initialization, init_function, self._init_done)
        timeout: int = EXECUTOR_START_TIMEOUT_SECONDS
        was_set: bool = self._init_done.wait(timeout=timeout)
        if not was_set:
            raise ValueError(f"FAILED to run executor initializer in {timeout} sec")

    @staticmethod
    def run_initialization(init_function: Callable, init_done: threading.Event):
        """
        Run in-loop initialization
        """
        try:
            init_function()
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Initializing function raised exception: {exc}")
        finally:
            init_done.set()

    @staticmethod
    def notify_loop_ready(loop_ready: threading.Event):
        """
        Function will be called once the event loop starts
        """
        loop_ready.set()

    @staticmethod
    def loop_manager(loop: AbstractEventLoop, loop_ready: threading.Event):
        """
        Entry point static method for the background thread.

        :param loop: The AbstractEventLoop to use to run the event loop.
        :param loop_ready: event notifying that loop is ready for execution.
        """
        asyncio.set_event_loop(loop)
        loop.call_soon(AsyncioExecutor.notify_loop_ready, loop_ready)
        loop.run_forever()

        # If we reach here, the loop was stopped.
        # We should gather any remaining tasks and finish them.
        pending = asyncio.all_tasks(loop=loop)
        if pending:
            # We want all possibly pending tasks to execute -
            # don't need them to raise exceptions.
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        # Close the event loop to free its related resources
        loop.close()

    @staticmethod
    def loop_exception_handler(loop: AbstractEventLoop, context: Dict[str, Any]):
        """
        Handles exceptions for the asyncio event loop

        DEF - I believe this exception handler is for exceptions that happen in
              the event loop itself, *not* the submit()-ed coroutines.
              Exceptions from the coroutines are handled by submission_done() below.

        :param loop: The asyncio event loop
        :param context: A context dictionary described here:
                https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.call_exception_handler
        """
        # Call the default exception handler first
        loop.default_exception_handler(context)

        message = context.get("message", None)
        print(f"Got exception message {message}")

        exception = context.get("exception", None)
        formatted_exception = traceback.format_exception(exception)
        print(f"Event loop traceback:\n{formatted_exception}")

    def get_function_name(self, function, submitter_id: str) -> str:
        """
        :param function: The function handle
        :param submitter_id: A string id denoting who is doing the submitting
        :return: The fully qualified name of the function, suitable for logging/tracking
        """
        function_name: str = None
        try:
            function_name = function.__qualname__  # Fully qualified name of function
        except AttributeError:
            # Just get the class name
            function_name = function.__class__.__name__
        if submitter_id:
            function_name = f"{submitter_id}:{function_name}"
        return function_name

    def _submit_as_task(self, submitter_id: str, function, /, *args, **kwargs) -> futures.Future:
        """
        Submit a function to be run in the asyncio event loop as a Task.

        :param submitter_id: A string id denoting who is doing the submitting.
        :param function: The function handle to run
        :param /: Positional or keyword arguments.
            See https://realpython.com/python-asterisk-and-slash-special-parameters/
        :param args: args for the function
        :param kwargs: keyword args for the function
        :return: A Future object which will return a created Task in our event loop.
        """

        if self._shutdown:
            raise RuntimeError('Cannot schedule new tasks after shutdown')

        if not self._loop.is_running():
            raise RuntimeError("Loop must be started before any function can "
                               "be submitted")

        task_creation_future: futures.Future = futures.Future()
        task_name: str = self.get_function_name(function, submitter_id)

        def create_in_loop_thread():
            if inspect.isawaitable(function):
                task = self._loop.create_task(function, name=task_name)
                print(f"Created awaitable task {task.get_name()}")
                task_creation_future.set_result(task)
                return task_creation_future

            try:
                if inspect.iscoroutinefunction(function):
                    # function is async def -> create task for its coroutine
                    coro = function(*args, **kwargs)
                    task = self._loop.create_task(coro, name=task_name)
                    print(f"Created coroutine task {task.get_name()}")
                else:
                    # function is sync -> run it in a worker thread, but task lives in event loop
                    func = functools.partial(function, *args, **kwargs)
                    task = self._loop.create_task(asyncio.to_thread(func), name=task_name)
                    print(f"Created threaded task {task.get_name()}")
                task_creation_future.set_result(task)
            except BaseException as exc:
                task_creation_future.set_exception(exc)

        # Ensure task is created in the event loop thread
        self._loop.call_soon_threadsafe(create_in_loop_thread)
        print(f"Submitted creation for task {task_name}")
        return task_creation_future

    def submit(self, submitter_id: str, function, /, *args, **kwargs) -> Task:
        """
        Submit a function to be run in the asyncio event loop.

        :param submitter_id: A string id denoting who is doing the submitting.
        :param function: The function handle to run
        :param /: Positional or keyword arguments.
            See https://realpython.com/python-asterisk-and-slash-special-parameters/
        :param args: args for the function
        :param kwargs: keyword args for the function
        :return: An asyncio.Task that corresponds to the submitted task
        """

        task_creation_future: futures.Future = self._submit_as_task(submitter_id, function, *args, **kwargs)
        # Wait for task to be created in event loop thread (blocking calling thread)

        print("Waiting for task creation to complete...")
        task: Task = task_creation_future.result()
        print(f"Task created: {task.get_name()}")
        self.track_task(task)
        return task

    def create_task(self, awaitable: Awaitable, submitter_id: str, raise_exception: bool = False) -> Future:
        """
        Creates a task for the event loop given an Awaitable
        :param awaitable: The Awaitable to create and schedule a task for
        :param submitter_id: A string id denoting who is doing the submitting.
        :param raise_exception: True if exceptions are to be raised in the executor.
                    Default is False.
        :return: The Future corresponding to the results of the scheduled task
        """
        task_creation_future: futures.Future = self._submit_as_task(submitter_id, awaitable)
        # Wait for task to be created in event loop thread (blocking calling thread)
        task: Task = task_creation_future.result()
        self.track_task(task, raise_exception=raise_exception)
        return task

    def track_task(self, task: Future, raise_exception: bool = False):
        """
        :param task: The task to track
        :param raise_exception: True if exceptions are to be raised in the executor.
                    Default is False.
        """

        # Weak references in the asyncio system can cause tasks to disappear
        # before they execute.  Hold a reference in a global as per
        # https://docs.python.org/3/library/asyncio-task.html#creating-tasks

        task_info_dict: Dict[str, Any] = {
            "future": task,
            "raise_exception": raise_exception
        }
        task_id = id(task)
        self._background_tasks[task_id] = task_info_dict
        task.add_done_callback(self.submission_done)

        print(f"!!!!!! >>>>>>>>>>>> Tracking future id {task_id} for {task.get_name()} table: {self._background_tasks.keys()}")

        return task

    def ensure_awaitable(self, x: Any) -> Awaitable:
        """
        Return an awaitable for x.
        - Coroutine object / Task / asyncio.Future / objects with __await__ -> returned as is;
        - concurrent.futures.Future -> wrapped for asyncio event loop;
        - Otherwise -> raise TypeError
        """
        if inspect.isawaitable(x):
            return x
        if isinstance(x, futures.Future):
            # Wrap a thread/process-pool future so it becomes awaitable
            return asyncio.wrap_future(x, loop=self._loop)
        raise TypeError(f"Object {x!r} of type {type(x).__name__} is not awaitable.")

    @staticmethod
    async def _cancel_and_drain(tasks: List[Future]):
        # Request cancellation for tasks that are not already done:
        pending = []
        for task in tasks:
            if not task.done():
                task.cancel("cancel-and-drain")
                pending.append(task)
        # Don't raise exceptions in the tasks being cancelled -
        # we don't really need to react to them.
        _ = await asyncio.gather(*pending, return_exceptions=True)

    def cancel_current_tasks(self, timeout: float = 5.0):
        """
        Method to cancel the currently submitted tasks for this executor.
        :param timeout: The maximum time in seconds to cancel the current tasks
        """
        if not self._loop.is_running():
            raise RuntimeError("Loop must be running to cancel remaining tasks")
        tasks_to_cancel: List[Future] = []

        with self._background_tasks_lock:
            # Clear the background tasks map
            # and allow next tasks (if any) to be added.
            # Currently present tasks will be cancelled below.
            background_tasks_save: Dict[int, Dict[str, Any]] = copy.copy(self._background_tasks)
            #self._background_tasks = {}

        for task_dict in background_tasks_save.values():
            task: Future = task_dict.get("future", None)
            if task:
                print(f"!!!!!! SCHEDULING to Cancel: future id {id(task)}")
                tasks_to_cancel.append(self.ensure_awaitable(task))
        cancel_task = asyncio.run_coroutine_threadsafe(AsyncioExecutor._cancel_and_drain(tasks_to_cancel), self._loop)
        try:
            cancel_task.result(timeout)
        except futures.TimeoutError:
            print(f"Timeout {timeout} sec exceeded while cleaning up AsyncioExecutor {id(self)}")
            raise

    def submission_done(self, future: Future):
        """
        Intended as a "done_callback" method on futures created by submit() above.
        Does some processing on a future that has been marked as done
        (for whatever reason).

        :param future: The Future which has completed
        """

        # Get a dictionary entry describing some metadata about the future itself.
        future_id: int = id(future)
        future_info: Dict[str, Any] = {}
        future_info = self._background_tasks.get(future_id, future_info)

        if not future.done():
            # Something is very wrong if we get here:
            # submission_done() must only be called when task is done in some way.
            raise RuntimeError(f"Task {future_id} is not done, but submission_done is called.")
        if not isinstance(future, Task):
            # We only register this callback on Tasks, so this is unexpected.
            raise RuntimeError(f"Future {future_id} is expected to be Task.")

        origination: str = future.get_name()
        if future_id not in self._background_tasks:
            # Another wrong situation: but this one we can just log and move on.
            print(f"Task {future_id} is not present in the tasks table.")

        try:
            # First see if there was any exception
            try:
                exception = future.exception()
            except (asyncio.CancelledError, futures.CancelledError) as exc:
                # Cancelled task is OK - it may happen for different reasons.
                print(f">>>>>>>>>>>>>>>>>TASK was CANCELLED! reason: {exc.args}")
                traceback.print_exception(exc)
                exception = None

            #print(f"GOT EXCEPTION: {exception} from {origination}")


            if exception is not None:
                print(">>>>>>>>>>>>>>>>>>>EVENT LOOP: Exception traceback:")
                traceback.print_exception(exception)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


                print(f"==============Coroutine from {origination} raised an exception:")
            if exception is not None and future_info.get("raise_exception"):
                raise exception

            print(f"Getting result from coroutine from {origination}")
            result = future.result()
            _ = result
            print(f"GOT result from coroutine from {origination}")

        except StopAsyncIteration:
            # StopAsyncIteration is OK
            pass

        except futures.TimeoutError:
            print(f"Task from {origination} took too long()")

        except asyncio.exceptions.CancelledError:
            # Cancelled task is OK - it may happen for different reasons.
            print(f"Task from {origination} was cancelled")
            traceback.print_exc()


        # pylint: disable=broad-exception-caught
        except Exception as exc:
            print(f"^^^^^^^^^^^^^^^^^^^^=======type: {type(exc)}")
            print(f"^^^^^^^^^^^^^^^^^^^^=======name: {type(exc).__mro__}")
            print(f">>>>>>>Coroutine from {origination} raised an exception:")
            traceback.print_exception(exc)
            print("end trace >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


            formatted_exception: List[str] = traceback.format_exception(exc)
            for line in formatted_exception:
                if line.endswith("\n"):
                    line = line[:-1]
                print(line)

        # As a last gesture, remove the background task from the map
        # we use to keep its reference around. Do it safely:
        with self._background_tasks_lock:
            self._background_tasks.pop(future_id, None)

    def shutdown(self, wait: bool = True, *, cancel_futures: bool = False):
        """
        Shuts down the event loop.

        :param wait: True if we should wait for the background thread to join up.
                     False otherwise.  Default is True.
        :param cancel_futures: Ignored? Default is False.
        """
        # Here is an outline of how this call works:
        # 1. shutdown() tells event loop to stop
        # (telling loop to execute loop.stop(), and doing this from caller thread by call_soon_threadsafe())
        #  then it starts to wait to join executor thread;
        # 2. executor thread returns from loop.run_forever(), because event loop has stopped,
        # does some finishing with outstanding loop tasks, and closes the loop. Then executor thread finishes.
        # Note that closing event loop frees loop-bound resources which otherwise
        # are not necessarily released.
        # 3. shutdown() joins the finished executor thread and peacefully finishes itself.
        # 4. shutdown() call returns to caller.
        self._shutdown = True
        self._loop.call_soon_threadsafe(self._loop.stop)
        if wait:
            self._thread.join()
        self._thread = None
