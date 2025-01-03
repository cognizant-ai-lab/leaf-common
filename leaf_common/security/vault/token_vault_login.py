
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
import os

from hvac import Client as VaultClient

from leaf_common.security.vault.vault_login import VaultLogin


# pylint: disable=too-few-public-methods
class TokenVaultLogin(VaultLogin):
    """
    VaultLogin implementation that uses a specific token to access
    the given vault server.
    """

    def login(self, vault_url: str, config: Dict[str, Any],
              vault_cacert: str = None) -> VaultClient:
        """
        This method can raise an exception if authentication with the
        Vault server fails in any way.

        :param vault_url: A url to the vault server we are trying to connect to
        :param config: A config dictionary with vault login parameters
        :param vault_cacert: A string containing either a local file path to
                the cert or the actual cert itself.  Default value is None,
                indicating that the vault of the VAULT_CACERT environment
                variable should be used (vault default).
        :return: A VaultClient that may or may not have authenticated to the
                Vault server at the specified vault_url.
                Can also be None if the config Dict was not specific enough
                to even attempt a login.

                Clients of this code are encouraged to call is_authenticated()
                on the return value to be sure all is good with the connection.
        """
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("Using vault login method 'token'")

        use_config = {}
        if config is not None:
            use_config = config

        use_token = use_config.get("token", None)
        if use_token is None:
            logger.info("vault_login token missing. Using VAULT_TOKEN.")
            use_token = os.environ.get("VAULT_TOKEN", None)

        vault_client = VaultClient(url=vault_url, token=use_token, verify=vault_cacert)
        return vault_client
