
# Copyright (C) 2019-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# leaf-common SDK Software in commercial settings.
#
# END COPYRIGHT
"""
See class comment for details
"""

# Needed for Timeout self-typing in has_time() below
from __future__ import annotations      # noqa: F407

import time

from leaf_common.time.timeout_reached_exception import TimeoutReachedException


class Timeout:
    """
    Class providing basic timeout functionality.
    """

    def __init__(self, name: str = "", limit_in_seconds: float = -1):
        """
        Constructor.

        :param name: name (possibly empty) used to identify this timeout object
        :param limit_in_seconds: timeout limit in seconds
                                 if this value is negative (< 0),
                                 timeout limit will never be reached (infinite timeout)
        """
        self.name: str = name
        self.limit_in_seconds: float = limit_in_seconds
        # start time in seconds since epoch - time when timeout was started
        #                                     (this value < 0 if timeout is not set)
        self.start_time: float = -1

    def is_reached(self) -> bool:
        """
        Check if the timeout is reached.

        :return: True if timeout is reached at current time,
                 False otherwise
        """

        return self.get_remaining_time_in_seconds() == 0

    def set_name(self, name: str):
        """
        Sets the name for timeout object.

        :param name: name to set.
        :return: None
        """

        self.name = name

    def get_name(self) -> str:
        """
        Returns the name of timeout object.

        :return: current name of timeout
        """

        return self.name

    def set_limit_in_seconds(self, timeout_limit_in_seconds: float):
        """
        Sets timeout active with given limit in seconds
        Start time will be set to current time.

        :param timeout_limit_in_seconds: timeout limit in seconds
        :return: None
        """

        self.limit_in_seconds = timeout_limit_in_seconds
        self.start_time = time.time()

    def get_limit_in_seconds(self) -> float:
        """
        Get currently set timeout limit in seconds.

        :return: timeout limit in seconds.
        """

        return self.limit_in_seconds

    def get_remaining_time_in_seconds(self) -> float:
        """
        Get time in seconds remaining until current timeout is reached.

        Returned value will be negative if:
        timeout is not set, or
        timeout limit is set to be infinite ("limit_in_seconds" < 0)

        :return: remaining time in seconds
        """

        if self.start_time < 0 or \
                self.limit_in_seconds < 0:  # timeout is not set
            return -1

        remain = self.start_time + self.limit_in_seconds - time.time()
        remain = max(remain, 0)
        return remain

    @classmethod
    def has_time(cls, interval_seconds: float, timeout: Timeout = None) -> bool:
        """
        Helper method that allows loops to asks whether they have enough
        time, given then information in the timeout.
        :param interval_seconds: The invertval of time to be queried,
                    in seconds.
        :param timeout: The Timeout class to test against.
                    This can be None, in which case there is always enough time.
        :return: True if there is enough time in the given interval and a loop
                should continue, False otherwise.
        """
        if timeout is None:
            return True

        secs_remaining = timeout.get_remaining_time_in_seconds()
        if secs_remaining < 0:
            # Special case where timeout is not set
            return True

        if secs_remaining > interval_seconds:
            return True

        return False

    def check_timeout(self):
        """
        Check if the task timeout is reached.
        If so, raise TimeoutReachedException exception
        and pass timeout information along with it.

        :return: None
        """

        if self.is_reached():
            raise TimeoutReachedException(self)

    @classmethod
    def check_if_not_none(cls, timeout: Timeout):
        """
        Helper that calls check_timeout() as long as the given timeout is not None.
        :param timeout:
        """
        if timeout is not None:
            timeout.check_timeout()
