# Copyright (C) 2019-2021 Cognizant Digital Business, Evolutionary AI.
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
from typing import Union

import logging

from hvac import Client as VaultClient

from leaf_common.security.vault.github_vault_login import GithubVaultLogin
from leaf_common.security.vault.kubernetes_vault_login import KubernetesVaultLogin
from leaf_common.security.vault.token_vault_login import TokenVaultLogin
from leaf_common.security.vault.vault_login import VaultLogin


class VaultLoginFactory(VaultLogin):
    """
    Factory-ish class which returns a VaultClient based on
    a vault_login configuration dictionary.
    Interface whose implementations return a Hashicorp Vault
    client whose authentication/login is up to the implementation.
    """

    def login(self, vault_url: str,
              config: Union[Dict[str, Any], List[Dict[str, Any]]],
              vault_cacert: str = None) -> VaultClient:
        """
        This method can raise an exception if authentication with the
        Vault server fails in any way.

        :param vault_url: A url to the vault server we are trying to connect to
        :param config: Either:
                * A config dictionary with vault login parameters
                * An ordered list of config dictionaries to try.
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
        config_list = config
        if isinstance(config, dict):
            config_list = [config]

        vault_client = None
        throw_me = None
        for try_config in config_list:

            try:
                # Try each vault config in the list via _login_one()
                vault_client = self._login_one(vault_url, try_config, vault_cacert)

            except Exception caught:
                # If there was a problem, catch the exception and save it for
                # later. The next config in the list might break through.
                throw_me = caught

            # If we have a valid connection, no need to loop through any more
            # in the list.
            if self.is_connection_valid(vault_client):
                break

        # If we still don't have a client but we had some exception along the
        # way, throw that exception.
        if vault_client is None and throw_me is not None:
            raise throw_me

        return vault_client

    def _login_one(self, vault_url: str,
                   config: Dict[str, Any],
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

        # Some defaults
        use_config = {}
        vault_login = TokenVaultLogin()

        # No vault login specified.
        if config is None:
            logger.warning("No vault_login specified in security config.")

        # Vault login specified, but it's an unknown data type.
        elif not isinstance(config, str) and \
                not isinstance(config, dict):
            logger.warning("vault_login in security config is unknown type.")

        # Single string specified, consider it a token
        elif isinstance(config, str):
            use_config = {
                "method": "token",
                "token": config
            }

        else:
            # config is a dictionary. Parse it.
            use_config = config
            method = config.get("method", None)

            # Check for token token dictionary specification
            if method is None:
                logger.warning("vault_login dictionary method missing.")

            elif not isinstance(method, str):
                logger.warning("vault_login dictionary method is of unknown type.")

            else:
                normalized_method = method.lower()
                if normalized_method == "token":
                    vault_login = TokenVaultLogin()

                elif normalized_method == "github":
                    vault_login = GithubVaultLogin()

                elif normalized_method == "kubernetes":
                    vault_login = KubernetesVaultLogin()

                else:
                    logger.warning("vault_login dictionary method is unknown.")

        vault_client = vault_login.login(vault_url, config=use_config)
        return vault_client

    def is_connection_valid(self, vault_client: VaultClient,
                            verbose: bool = True) -> bool:
        """
        :param vault_client: The VaultClient to test against
        :param verbose: Default of True will spit out informational
                log messages as to why this method is returning False
                (when that happens).
        :return: True if the given client exists and the authentication
                succeeded.  False otherwise.
        """
        logger = logging.getLogger(self.__class__.__name__)

        if vault_client is None:
            if verbose:
                logger.error("Could not create vault client")
            return False

        # Be sure we are authenticated correctly
        if not vault_client.is_authenticated():
            if verbose:
                logger.error("Could not authenticate to vault server")
            return False

        return True
