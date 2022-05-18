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
