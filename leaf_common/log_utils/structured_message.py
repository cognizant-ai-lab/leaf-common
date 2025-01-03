
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
For structured logging.
"""

import datetime
import json
import logging

from leaf_common.log_utils.message_type import MessageType


class StructuredMessage:
    """
    Encapsulates the data required for a single structured log message, which will result in a single line in the
    output (usually stdout).
    This is in line with NDJSON. See: https://github.com/ndjson/ndjson-spec
    """

    def __init__(self, source, message, extra_properties, message_type):
        self._source = source
        self._message_type = message_type
        self._message = message
        self._extra_properties = extra_properties

    def __str__(self):
        json_to_log = {
            'timestamp': datetime.datetime.now().isoformat(),
            'source': self._source,
            'message_type': self._message_type,
            'message': self._message,
        }
        if self._extra_properties:
            json_to_log['extra_properties'] = self._extra_properties
        return json.dumps(json_to_log)


def log_structured(source: str, message: StructuredMessage, logger: logging.Logger,
                   message_type: MessageType = MessageType.Other, extra_properties: dict = None):
    """
    Logs a message in structured format using the supplied logger. All messages logged via this function will
    be logged at `INFO` level.
    :param source: Application or component that was the source of this message, for example "my_app"
    :param message: Human-readable message, for example "Connected to database"
    :param logger: A `logger` from the standard Python `logging` package. Will be used to log the message. In general
    the formatter associated with this logger should be "bare", just the message, with no header, so that the resulting
    message will be pure, parseable JSON. For example, the formatter should NOT include the log level or timestamp.
    :param message_type:
    :param extra_properties: A dictionary containing arbitrary properties that should be logged along with the message.
    For example: `{'time_taken': 3}`
    """
    logger.info(str(StructuredMessage(source, message, extra_properties, message_type)))
