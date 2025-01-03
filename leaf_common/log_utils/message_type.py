
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
Represents the various types of log messages an application may generate.
"""
from enum import Enum


class MessageType(str, Enum):
    """
    Represents the various types of log messages an application may generate.
    """

    # pylint: disable=invalid-name
    # For messages that do not fit into any of the other categories
    Other = 'Other'

    # Error messages intended for technical personnel, such as internal errors, stack traces
    Error = 'Error'

    # Warning only
    Warning = 'Warning'

    # Metrics messages, for example, API call counts
    Metrics = 'Metrics'

    # Tracking API calls
    API = 'API'
