
# Copyright (C) 2019-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# leaf-server-common SDK Software in commercial settings.
#
# END COPYRIGHT
"""
See class comments for description.
"""
import threading


class AtomicCounter:
    """
    A class for thread-safe increment/decrement of a counter shared among threads.
    """

    def __init__(self, value: int = 0):
        """
        Constructor

        :param value: The initial value of the counter. Default is 0.
        """
        self._value = int(value)
        self._lock = threading.Lock()

    def increment(self, step: int = 1) -> int:
        """
        Increment the counter and return the new value
        as an atomic operation.

        :param step: The amount by which the counter should be incremented.
                     Default is 1.
        """
        with self._lock:
            self._value += int(step)
            return self._value

    def decrement(self, step: int = 1) -> int:
        """
        Decrement the counter and return the new value
        as an atomic operation.

        :param step: The amount by which the counter should be decremented.
                     Default is 1.
        """
        self.increment(-step)

    def get_count(self) -> int:
        """
        :return: The value of the counter.
        """
        return self._value
