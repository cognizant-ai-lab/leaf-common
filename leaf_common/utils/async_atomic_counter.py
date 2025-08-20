
# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san SDK Software in commercial settings.
#
# END COPYRIGHT

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
