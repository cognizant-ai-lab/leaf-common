
# Copyright 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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

from typing import Any
from typing import Dict

from leaf_common.security.service.service_accessor import ServiceAccessor


class StaticTokenServiceAccessor(ServiceAccessor):
    """
    ServiceAccessor implmentation that obtains a single security token
    directly from a provided security config dictionary.
    """

    def __init__(self, security_config: Dict[str, Any]):
        """
        Constructor

        :param security_config: A standardized LEAF security config dictionary
        """
        self.auth_token = security_config.get("auth_token", None)

        # Take care of some cases that are as good as not actually
        # having a token
        if self.auth_token is not None:
            if not isinstance(self.auth_token, str):
                self.auth_token = None
            elif len(self.auth_token) == 0:
                self.auth_token = None

    def get_auth_token(self) -> str:
        """
        :return: A string that is the ephemeral service access token,
                used to set up a secure gRPC connection.
        """
        return self.auth_token

    @staticmethod
    def is_appropriate_for(security_config: Dict[str, Any]) -> bool:
        """
        :param security_config: A standardized LEAF security config dictionary
        :return: True if this class is appropriate given the contents of
                 the security_config dictionary
        """
        auth_token = security_config.get("auth_token", None)
        return auth_token is not None
