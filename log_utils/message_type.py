"""
Represents the various types of log messages an application may generate.
"""
from enum import Enum


class MessageType(str, Enum):
    """
    Represents the various types of log messages an application may generate.
    """

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
