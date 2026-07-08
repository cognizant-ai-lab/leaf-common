
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
See class comment for details.
"""

from logging import Logger

from leaf_common.logging.conditional_logger import ConditionalLogger


class SensitiveLogger(ConditionalLogger):
    """
    Wraps a logger to mask sensitive information.
    Uses the same general Logger interface as the whole world already uses.

    We assume that any information coming in to this logger is considered sensitive information.
    Turning off senstive logging information can be done by setting the LEAF_LOG_SENSTIVE to "false".
    By default this is turned on, allowing developers to see sensitive information.
    Strongly consider turning this off for production deployments.
    """

    def __init__(self, logger: Logger):
        """
        Constructor.

        :param logger: The wrapped logger to redirect write() calls to.
        """
        super().__init__(logger, "LEAF_LOG_SENSITIVE")
