
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
