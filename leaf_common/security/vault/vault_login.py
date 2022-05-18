"""
See class comment for details.
"""
from typing import Any
from typing import Dict

from hvac import Client as VaultClient


# pylint: disable=too-few-public-methods
class VaultLogin:
    """
    Interface whose implementations return a Hashicorp Vault
    client whose authentication/login is up to the implementation.
    """

    def login(self, vault_url: str, config: Dict[str, Any]) -> VaultClient:
        """
        This method can raise an exception if authentication with the
        Vault server fails in any way.

        :param vault_url: A url to the vault server we are trying to connect to
        :param config: A config dictionary with vault login parameters
        :return: A VaultClient that may or may not have authenticated to the
                Vault server at the specified vault_url.
                Can also be None if the config Dict was not specific enough
                to even attempt a login.

                Clients of this code are encouraged to call is_authenticated()
                on the return value to be sure all is good with the connection.
        """
        raise NotImplementedError
