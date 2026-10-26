
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

from typing import Dict

from logging import NOTSET
from threading import Lock
from typing_extensions import override

from leaf_common.logging.abstract_conditional_logger import AbstractConditionalLogger


class LogOnce(AbstractConditionalLogger):
    """
    Wraps a logger so that each message signature is logged one time only.
    Uses the same general Logger interface as the whole world already uses.

    The message signature is the first string argument (the format string) given to a logging call,
    before any % args are applied. The first call with a given signature goes to the wrapped logger.
    All later calls with the same signature are dropped, for all LogOnce instances in the process.
    """

    # Global class-variable record of the message signatures that a LogOnce instance has logged
    # and at what log level (the integer).
    # All LogOnce instances share this dictionary.
    SEEN_LOGGING_SIGNATURES: Dict[str, int] = {}

    # Makes the check-and-set on SEEN_LOGGING_SIGNATURES atomic across threads.
    SEEN_LOGGING_SIGNATURES_LOCK: Lock = Lock()

    @override
    def should_log(self, message: str, log_level: int) -> bool:
        """
        Records the message signature as seen.

        :param message: The message signature to check
        :param log_level: The log level of the message
        :return: True if this is the first time the message signature is seen.
                False if the message signature was seen before.
        """
        should_log: bool = True

        # Don't hold the lock if we don't need to.
        last_log_level: int = LogOnce.SEEN_LOGGING_SIGNATURES.get(message, NOTSET)
        if last_log_level >= log_level:
            should_log = False
        else:
            with LogOnce.SEEN_LOGGING_SIGNATURES_LOCK:
                # Check again, now that we have the lock to avoid a race in a non-trivial decision
                last_log_level = LogOnce.SEEN_LOGGING_SIGNATURES.get(message, NOTSET)
                if last_log_level >= log_level:
                    should_log = False
                else:
                    LogOnce.SEEN_LOGGING_SIGNATURES[message] = log_level

        return should_log
