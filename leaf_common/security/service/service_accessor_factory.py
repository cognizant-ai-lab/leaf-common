
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

import logging

from leaf_common.security.service.auth0_direct_service_accessor \
    import Auth0DirectServiceAccessor
from leaf_common.security.service.service_accessor \
    import ServiceAccessor
from leaf_common.security.service.static_token_service_accessor \
    import StaticTokenServiceAccessor
from leaf_common.security.service.vault_dynamic_token_service_accessor \
    import VaultDynamicTokenServiceAccessor
from leaf_common.time.timeout import Timeout

ACCESSOR_PRECEDENCE = [
    VaultDynamicTokenServiceAccessor,       # Prefer dynamic tokens
    StaticTokenServiceAccessor,             # Specified static token
    Auth0DirectServiceAccessor,             # No specific token
]


# pylint: disable=too-few-public-methods
class ServiceAccessorFactory:
    """
    Factory which returns an appropriate ServiceAccessor implementation,
    given a security_config dictionary
    """

    @staticmethod
    def get_service_accessor(security_config: Dict[str, Any] = None,
                             auth0_defaults: Dict[str, Any] = None,
                             service_name: str = None,
                             poll_interval_seconds: int = 15,
                             umbrella_timeout: Timeout = None) -> ServiceAccessor:
        """
        :param security_config: A LEAF-standard security config dictionary.
                        Default is None, uses insecure channel.
        :param auth0_defaults: An optional dictionary containing defaults for
                auth0 access. Primarily for ESP compatibility.
        :param service_name: An optional string to be used for error messages
                when connecting to a service. If not given, we attempt to
                get this from the security_cfg/auth0_defaults.
        :param poll_interval_seconds: length of time in seconds methods
                            on this class will wait before retrying connections
                            or specific gRPC calls. Default to 15 seconds.
        :param umbrella_timeout: A Timeout object under which the length of all
                        looping and retries should be considered
        :return: A ServiceAccessor implementation befitting the config
        """

        logger = logging.getLogger("ServiceAccessorFactory")

        # No dict to read from
        if security_config is None or \
                not isinstance(security_config, dict) or \
                not any(security_config):
            # No config, no ServiceAccessor.
            logger.info("No security config, using None for ServiceAccessor")
            return None

        for accessor_class in ACCESSOR_PRECEDENCE:
            if accessor_class.is_appropriate_for(security_config):

                accessor = None
                if accessor_class == Auth0DirectServiceAccessor:
                    # Special args
                    accessor = Auth0DirectServiceAccessor(
                                            security_config=security_config,
                                            auth0_defaults=auth0_defaults,
                                            service_name=service_name,
                                            poll_interval_seconds=poll_interval_seconds,
                                            umbrella_timeout=umbrella_timeout)
                elif accessor_class == VaultDynamicTokenServiceAccessor:
                    # Special args
                    accessor = VaultDynamicTokenServiceAccessor(security_config,
                                                                auth0_defaults)
                else:
                    accessor = accessor_class(security_config)

                logger.info("Using %s", accessor.__class__.__name__)
                return accessor

        # Default returns a constant value from the security config
        # if it exists
        logger.info("Using default StaticTokenServiceAccessor")
        return StaticTokenServiceAccessor(security_config)

    @staticmethod
    def is_useful_config(security_config: Dict[str, Any]) -> bool:
        """
        :param security_config: A LEAF-standard security config dictionary
        :return: True if the security_config has enough information to be useful
        """

        for accessor_class in ACCESSOR_PRECEDENCE:
            if accessor_class.is_appropriate_for(security_config):
                return True

        return False
