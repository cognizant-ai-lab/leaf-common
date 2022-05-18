"""
See class comment for details.
"""
from typing import Any
from typing import Dict

import logging

from hvac import Client as VaultClient

from leaf_common.security.vault.vault_login import VaultLogin


# pylint: disable=too-few-public-methods
class GithubVaultLogin(VaultLogin):
    """
    VaultLogin implementation that uses a GitHub token to authenticate
    with the specified Vault server.

    Note that the Vault server admin must have already specified that github
    logins are acceptable using commands like:
        vault auth enable github
        vault write auth/github/config organization=<github-org>
        vault write auth/github/map/users/<github-user-id> value=<named-policies>

    An example named policy .hcl file (vault configuration file) might look like this:
        path "oauth2/self/my-machine-auth" {
            capabilities = ["read"]
        }
    ... for access to the vault_secret "oauth2/self/my-machine-auth"

    Vault server operators can install this policy like this:
        vault policy write <named-policy> <named-policy>.hcl

    ... and enable a particular GitHub user to use this policy by doing this:
        vault write auth/github/map/users/<github-username> value=default,<named-policy>

    For more info on Vault policies, see:
        https://www.vaultproject.io/docs/concepts/policies

    Also note that it is possible to get GitHub user information given a
    Personal Access Token via the GitHub API:
        curl -i -u x-access-token:${ENN_SOURCE_CREDENTIALS} https://api.github.com/user
    See also:
        https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api#get-your-own-user-profile
    This can be useful in subsequent requests that might like a username as part
    of the http headers.
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
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("Using vault login method 'github'")
        use_token = config.get("token", None)

        if use_token is None:
            logger.warning("GitHub token missing from security_config spec")
            return None

        vault_client = VaultClient(url=vault_url)
        _ = vault_client.auth.github.login(token=use_token)

        return vault_client
