# Copyright © 2023-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
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
from asyncio import AbstractEventLoop
from asyncio import get_running_loop
from asyncio import run
from asyncio import to_thread
from typing import AsyncIterator
from typing import List

from leaf_common.asyncio.task_executor import TaskExecutor


class TaskExecutorCallStacks:
    """
    Test helper that builds synchronous and asynchronous call stacks of varying depth.
    Each call stack ends in a call to TaskExecutor.is_running_in_owned_loop().
    """

    # Synchronous call stacks

    @staticmethod
    def sync_level_1(executor: TaskExecutor) -> bool:
        """
        Calls is_running_in_owned_loop() directly from a synchronous method.

        :param executor: The TaskExecutor to ask
        :return: The result of is_running_in_owned_loop()
        """
        return executor.is_running_in_owned_loop()

    @staticmethod
    def sync_level_2(executor: TaskExecutor) -> bool:
        """
        Calls is_running_in_owned_loop() through one intermediate synchronous method.

        :param executor: The TaskExecutor to ask
        :return: The result of is_running_in_owned_loop()
        """
        return TaskExecutorCallStacks.sync_level_1(executor)

    @staticmethod
    def sync_level_3(executor: TaskExecutor) -> bool:
        """
        Calls is_running_in_owned_loop() through two intermediate synchronous methods.

        :param executor: The TaskExecutor to ask
        :return: The result of is_running_in_owned_loop()
        """
        return TaskExecutorCallStacks.sync_level_2(executor)

    # Asynchronous call stacks

    @staticmethod
    async def async_level_1(executor: TaskExecutor) -> bool:
        """
        Calls is_running_in_owned_loop() directly from an async method.

        :param executor: The TaskExecutor to ask
        :return: The result of is_running_in_owned_loop()
        """
        return executor.is_running_in_owned_loop()

    @staticmethod
    async def async_level_2(executor: TaskExecutor) -> bool:
        """
        Calls is_running_in_owned_loop() through one intermediate async method.

        :param executor: The TaskExecutor to ask
        :return: The result of is_running_in_owned_loop()
        """
        return await TaskExecutorCallStacks.async_level_1(executor)

    @staticmethod
    async def async_level_3(executor: TaskExecutor) -> bool:
        """
        Calls is_running_in_owned_loop() through two intermediate async methods.

        :param executor: The TaskExecutor to ask
        :return: The result of is_running_in_owned_loop()
        """
        return await TaskExecutorCallStacks.async_level_2(executor)

    @staticmethod
    async def async_then_sync_level_3(executor: TaskExecutor) -> bool:
        """
        Calls is_running_in_owned_loop() 3 synchronous levels below an async method.

        :param executor: The TaskExecutor to ask
        :return: The result of is_running_in_owned_loop()
        """
        return TaskExecutorCallStacks.sync_level_3(executor)

    @staticmethod
    async def async_generator_level_1(executor: TaskExecutor) -> AsyncIterator[bool]:
        """
        Yields the result of is_running_in_owned_loop() called directly from an async generator.

        :param executor: The TaskExecutor to ask
        :return: An async iterator that yields the result of is_running_in_owned_loop()
        """
        yield executor.is_running_in_owned_loop()

    @staticmethod
    async def async_collect_generator(executor: TaskExecutor) -> List[bool]:
        """
        Collects each value that async_generator_level_1() yields.

        :param executor: The TaskExecutor to ask
        :return: The list of values that async_generator_level_1() yields
        """
        results: List[bool] = []
        # Collect each value that the async generator yields
        result: bool
        async for result in TaskExecutorCallStacks.async_generator_level_1(executor):
            results.append(result)
        return results

    # Thread boundaries

    @staticmethod
    async def async_run_in_thread_pool(executor: TaskExecutor) -> bool:
        """
        Runs sync_level_3() in the default thread pool of the running event loop.
        The worker thread runs no event loop of its own.

        :param executor: The TaskExecutor to ask
        :return: The result of is_running_in_owned_loop() on the worker thread
        """
        loop: AbstractEventLoop = get_running_loop()
        return await loop.run_in_executor(None, TaskExecutorCallStacks.sync_level_3, executor)

    @staticmethod
    async def async_run_in_other_loop(executor: TaskExecutor) -> bool:
        """
        Runs async_level_3() on a new event loop in a worker thread.
        The new event loop is not the executor's event loop.

        :param executor: The TaskExecutor to ask
        :return: The result of is_running_in_owned_loop() on the new event loop
        """
        return await to_thread(run, TaskExecutorCallStacks.async_level_3(executor))
