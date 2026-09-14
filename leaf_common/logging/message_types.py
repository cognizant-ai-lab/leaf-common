
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

from enum import Enum
from logging import INFO
from logging import addLevelName


# We need to use specific logging levels for our own message types to
# have our LogRecord derivitives be compatible with stock python loggers.
# To be sure the API and METRICS log levels show up when log-level INFO is on,
# we make their log level intefer value a few clicks up from INFO.
# Seeing API is more important than seeing METRICS
# pylint: disable=invalid-name
API: int = INFO + 7
METRICS: int = INFO + 5

# Give the new log levels names for standard reporting
addLevelName(API, "API")
addLevelName(METRICS, "METRICS")


class MessageType(str, Enum):
    """
    Represents the various types of log messages an application may generate.
    """

    # For messages that do not fit into any of the other categories
    # Used for DEBUG and INFO
    OTHER: str = "Other"

    # Error messages intended for technical personnel, such as internal errors, stack traces
    # Used for CRITICAL, ERROR, and exception()
    ERROR: str = "Error"

    # Warning only
    WARNING: str = "Warning"

    # Metrics messages, for example, API call counts
    METRICS: str = "Metrics"

    # Tracking API calls
    API: str = "API"
