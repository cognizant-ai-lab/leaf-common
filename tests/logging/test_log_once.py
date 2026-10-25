
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

from logging import INFO
from logging import Logger
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from leaf_common.logging.log_once import LogOnce


class TestLogOnce(TestCase):
    """
    Tests for LogOnce.
    """

    def setUp(self) -> None:
        """
        Gives each test an empty global record of seen msg signatures.
        """
        patcher = patch.dict(LogOnce.SEEN_LOGGING_SIGNATURES, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_first_message_is_logged(self) -> None:
        """
        The first call with a msg signature goes to the wrapped logger.
        """
        logger: Logger = MagicMock()
        LogOnce(logger).info("Loaded %s", "abc", exc_info=True)
        logger.info.assert_called_once_with("Loaded %s", "abc", exc_info=True)

    def test_repeated_message_is_not_logged(self) -> None:
        """
        A later call with the same msg signature but different args is dropped.
        """
        logger: Logger = MagicMock()
        once = LogOnce(logger)
        once.info("Loaded %s", "abc")
        once.info("Loaded %s", "xyz")
        logger.info.assert_called_once_with("Loaded %s", "abc")

    def test_different_messages_are_logged(self) -> None:
        """
        Calls with different msg signatures are all logged.
        """
        logger: Logger = MagicMock()
        once = LogOnce(logger)
        once.warning("first")
        once.warning("second")
        self.assertEqual(logger.warning.call_count, 2)

    def test_signatures_are_shared_across_instances_and_levels(self) -> None:
        """
        The record is global, so a different instance and level still drop a seen signature.
        """
        logger_one: Logger = MagicMock()
        logger_two: Logger = MagicMock()
        LogOnce(logger_one).error("Same %s", 1)
        LogOnce(logger_two).debug("Same %s", 2)
        LogOnce(logger_two).log(INFO, "Same %s", 3)
        logger_one.error.assert_called_once_with("Same %s", 1)
        logger_two.debug.assert_not_called()
        logger_two.log.assert_not_called()

    def test_exception_passes_exc_info(self) -> None:
        """
        exception() forwards exc_info to the wrapped logger.
        """
        logger: Logger = MagicMock()
        LogOnce(logger).exception("Failed %s", "op")
        logger.exception.assert_called_once_with("Failed %s", "op", exc_info=True)
