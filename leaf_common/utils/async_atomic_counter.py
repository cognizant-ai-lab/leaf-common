
# Copyright 2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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
See class comments for description.
"""
import asyncio


class AsyncAtomicCounter:
    """
    Class implements atomic incrementing counter for async execution environment.
    """
    def __init__(self, start: int = 0):
        """
        Constructor

        :param value: The initial value of the counter. Default is 0.
        """
        self._value = start
        self._lock = asyncio.Lock()

    async def increment(self, step: int = 1) -> int:
        """
        Increment the counter and return the new value
        as an atomic operation.

        :param step: The amount by which the counter should be incremented.
                     Default is 1.
        """
        async with self._lock:
            self._value += int(step)
            return self._value

    async def decrement(self, step: int = 1) -> int:
        """
        Decrement the counter and return the new value
        as an atomic operation.

        :param step: The amount by which the counter should be decremented.
                     Default is 1.
        """
        return await self.increment(-step)

    async def get_count(self) -> int:
        """
        :return: The value of the counter.
        """
        return self._value
