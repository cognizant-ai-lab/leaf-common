
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
