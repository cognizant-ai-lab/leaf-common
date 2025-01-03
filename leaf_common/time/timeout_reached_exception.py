
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


class TimeoutReachedException(Exception):
    """
    Exception raised by the Timeout.check_timeout() method.
    """

    def __init__(self, timeout: object):
        """
        Constructor.
        Store timeout information to pass it
        to anyone who will handle this exception.

        :param timeout: The Timeout object which reached the timeout.
                Note we do not type this to prevent circular dependencies
        """

        Exception.__init__(self)
        self.timeout = timeout
