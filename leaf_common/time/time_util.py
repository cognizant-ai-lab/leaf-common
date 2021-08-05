
# Copyright (C) 2019-2021 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# leaf-common SDK Software in commercial settings.
#
# END COPYRIGHT

import datetime
from pytz import timezone


class TimeUtil:
    """
    Utilities dealing with time.
    """

    @staticmethod
    def get_time(space: bool = True):
        """
        Creates a nicely formated timestamp
        """
        if space:
            return datetime.datetime.now(timezone('US/Pacific')) \
                .strftime("%Y-%m-%d %H:%M:%S %Z%z")

        return datetime.datetime.now(timezone('US/Pacific')) \
            .strftime("%Y-%m-%d_%H-%M-%S_%Z%z")
