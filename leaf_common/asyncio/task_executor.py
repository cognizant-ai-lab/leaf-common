
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
from typing import Awaitable
from typing import Callable

from asyncio import AbstractEventLoop
from asyncio import Task
from asyncio import Future


class TaskExecutor:
    """
    Interface contract for a class managing execution
    of dynamic collection of asynchronous tasks in an event loop.
    """

    def get_event_loop(self) -> AbstractEventLoop:
        """
        :return: The AbstractEventLoop associated with this executor instance
        """
        return None

    def start(self):
        """
        Starts the executor.
        Do this separately from constructor for more control.
        """
        raise NotImplementedError

    def initialize(self, init_function: Callable):
        """
        Call initializing function on executor event loop
        and wait for it to finish.
        Used for setting up executor tasks run-time state before any tasks are submitted.
        :param init_function: function to call.
        """
        raise NotImplementedError

    def submit(self, submitter_id: str, function, /, *args, **kwargs) -> Task:
        """
        Submit a function to be run in the executor.
        Note that the function is run in "fire and forget" mode,
        so no result, successful or otherwise, is returned to the caller.

        :param submitter_id: A string id denoting who is doing the submitting.
        :param function: The function handle to run
        :param /: Positional or keyword arguments.
            See https://realpython.com/python-asterisk-and-slash-special-parameters/
        :param args: args for the function
        :param kwargs: keyword args for the function
        :return: An asyncio.Task that corresponds to the submitted task
        """
        raise NotImplementedError

    def create_task(self, awaitable: Awaitable, submitter_id: str, raise_exception: bool = False) -> Future:
        """
        Creates a task for the event loop given an Awaitable
        :param awaitable: The Awaitable to create and schedule a task for
        :param submitter_id: A string id denoting who is doing the submitting.
        :param raise_exception: True if exceptions are to be raised in the executor.
                    Default is False.
        :return: The Task object bound to our event loop
        """
        raise NotImplementedError

    def shutdown(self, wait: bool = True, *, cancel_futures: bool = False):
        """
        Shuts down the executor.
        :param wait: True if we should wait for the background thread to join up.
                     False otherwise.  Default is True.
        :param cancel_futures: Ignored? Default is False.
        """
        raise NotImplementedError
