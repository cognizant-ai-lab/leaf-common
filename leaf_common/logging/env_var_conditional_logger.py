
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

from logging import Logger
from typing_extensions import override

from leaf_common.logging.abstract_conditional_logger import AbstractConditionalLogger
from leaf_common.utils.environment_util import EnvironmentUtil


class EnvVarConditionalLogger(AbstractConditionalLogger):
    """
    Wraps a logger to mask logged information conditionally based on an environment variable setting.
    Uses the same general Logger interface as the whole world already uses.
    """

    def __init__(self, logger: Logger, env_var: str) -> None:
        """
        Constructor.

        :param logger: The wrapped logger to redirect write() calls to.
        """
        super().__init__(logger)
        self._should_log: bool = EnvironmentUtil.getenv(env_var, "true").lower() == "true"

    @override
    def should_log(self, message: str = None, log_level: int = None) -> bool:
        """
        :param message: The message to log
        :param log_level: The log level of the message
        :return: True if this logger should log
        """
        return self._should_log
