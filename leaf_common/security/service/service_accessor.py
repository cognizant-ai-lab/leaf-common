
# Copyright 2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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


class ServiceAccessor:
    """
    Interface whose implementations get a service access token
    for secure communication between client and service.
    """

    def get_auth_token(self) -> str:
        """
        :return: A string that is the ephemeral service access token,
                used to set up a secure gRPC connection.
        """
        raise NotImplementedError

    @staticmethod
    def is_appropriate_for(security_config: Dict[str, Any]) -> bool:
        """
        :param security_config: A standardized LEAF security config dictionary
        :return: True if this class is appropriate given the contents of
                 the security_config dictionary
        """
        raise NotImplementedError
