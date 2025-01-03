
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

import datetime

from pytz import timezone


class TimeUtil:
    """
    Utilities dealing with time.
    """

    @staticmethod
    def get_time():
        """
        Creates a nicely formated timestamp
        """
        now = datetime.datetime.now()

        local_now = now.astimezone()
        use_tz = local_now.tzinfo

        # If the user's machine doesn't care about the time zone,
        # make it nice for the debugging developers.
        local_tzname = use_tz.tzname(local_now)
        if local_tzname == "UTC":
            use_tz = timezone('US/Pacific')

        now = datetime.datetime.now(use_tz)
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S %Z%z")

        return formatted_time
