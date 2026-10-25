
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

from typing import Any
from typing import Dict

from logging import Logger
from threading import Lock

# Global record of the message signatures that a LogOnce instance has logged.
# All LogOnce instances share this dictionary.
SEEN_LOGGING_SIGNATURES: Dict[str, bool] = {}

# Makes the check-and-set on SEEN_LOGGING_SIGNATURES atomic across threads.
SEEN_LOGGING_SIGNATURES_LOCK: Lock = Lock()


class LogOnce:
    """
    Wraps a logger so that each message signature is logged one time only.
    Uses the same general Logger interface as the whole world already uses.

    The message signature is the first string argument (the format string) given to a logging call,
    before any % args are applied. The first call with a given signature goes to the wrapped logger.
    All later calls with the same signature are dropped, for all LogOnce instances in the process.
    """

    def __init__(self, logger: Logger) -> None:
        """
        Constructor.

        :param logger: The wrapped logger to redirect logging calls to.
        """
        self.logger: Logger = logger

    def should_log(self, message: str) -> bool:
        """
        Records the message signature as seen.

        :param message: The message signature to check
        :return: True if this is the first time the message signature is seen.
                False if the message signature was seen before.
        """
        with SEEN_LOGGING_SIGNATURES_LOCK:
            if SEEN_LOGGING_SIGNATURES.get(message, False):
                return False
            SEEN_LOGGING_SIGNATURES[message] = True
            return True

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=True)
        """
        if not self.should_log(msg):
            return
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "notable problem", exc_info=True)
        """
        if not self.should_log(msg):
            return
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=True)
        """
        if not self.should_log(msg):
            return
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=True)
        """
        if not self.should_log(msg):
            return
        self.logger.error(msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, exc_info: bool = True, **kwargs: Any) -> None:
        """
        Convenience method for logging an ERROR with exception information.
        """
        if not self.should_log(msg):
            return
        self.logger.exception(msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=True)
        """
        if not self.should_log(msg):
            return
        self.logger.critical(msg, *args, **kwargs)

    def fatal(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Don't use this method, use critical() instead.
        """
        if not self.should_log(msg):
            return
        self.logger.fatal(msg, *args, **kwargs)

    def log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log 'msg % args' with the integer severity 'level'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.log(level, "We have a %s", "mysterious problem", exc_info=True)
        """
        if not self.should_log(msg):
            return
        self.logger.log(level, msg, *args, **kwargs)
