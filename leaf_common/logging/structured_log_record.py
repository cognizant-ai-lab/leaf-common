
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

import logging
from datetime import datetime

from leaf_common.logging.message_types import MessageType
from leaf_common.logging.message_types import API
from leaf_common.logging.message_types import METRICS


# Set up a global variable to allow cascading of LogRecord factories
_STRUCTURED_OLD_FACTORY = None


def _structured_log_record_factory(*args, **kwargs):
    """
    Expected entry point for standard Python logging system to be
    used with the StructuredLogRecord class below.
    This needs to be a regular method, dissociated from any class.

    :param args: The positional arguments to the invocation of the
                 LogRecord constructor
    :param kwargs: The keyword arguments to the invocation of the
                 LogRecord constructor
    :return: A LogRecord instance from the Python logging package
            with added thread-specific fields added.
    """

    # Use the class variable to get a handle on the old LogRecord factory
    log_record = _STRUCTURED_OLD_FACTORY(*args, **kwargs)

    # Determine the MessageType we wish to store with each LogRecord
    if log_record.exc_info is not None:
        message_type = MessageType.ERROR
    elif log_record.levelno == logging.CRITICAL:
        message_type = MessageType.ERROR
    elif log_record.levelno == logging.ERROR:
        message_type = MessageType.ERROR
    elif log_record.levelno == logging.WARNING:
        message_type = MessageType.WARNING
    elif log_record.levelno == API:
        message_type = MessageType.API
    elif log_record.levelno == METRICS:
        message_type = MessageType.METRICS
    elif log_record.levelno == logging.INFO:
        message_type = MessageType.OTHER
    elif log_record.levelno == logging.DEBUG:
        message_type = MessageType.OTHER
    else:
        message_type = MessageType.OTHER

    # Add the message_type as a string field to the log_record
    log_record.message_type = message_type.value

    # Add a log_record field for the structured timestamp
    log_timestamp_since_epoch = log_record.created
    log_datetime = datetime.fromtimestamp(log_timestamp_since_epoch)
    iso_timestamp = log_datetime.isoformat()
    log_record.iso_timestamp = iso_timestamp

    # Return the new LogRecord with the new logging fields set
    return log_record


# pylint: disable=too-few-public-methods
class StructuredLogRecord():
    """
    Helper class which adds extra fields pertinent to service logging
    messages via the standard Python LogRecord class.

    Extra logging fields that contribute to structured logging are stored
    on the python logging system's LogRecord class that is created for
    each log message.  In particular, a 'message_type' field is created
    from the log level of each message coming in and a new iso formatted
    time field is added for each message as well.
    """

    @classmethod
    def set_up_record_factory(cls):
        """
        Called early on in the lifetime of a service to redirect the standard
        Python LogRecord creation to our _record_factory() call at the top
        of the file.

        This needs to be called once by a service before any constructor of
        this class is called or message is logged.
        """
        # Need to access global variable. No other way.
        # Hacktastic python logging infrastructure is riddled with global needs
        # pylint: disable=global-statement
        global _STRUCTURED_OLD_FACTORY
        if _STRUCTURED_OLD_FACTORY is None:
            _STRUCTURED_OLD_FACTORY = logging.getLogRecordFactory()
        logging.setLogRecordFactory(_structured_log_record_factory)
