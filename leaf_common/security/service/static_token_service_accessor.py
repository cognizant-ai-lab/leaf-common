
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
