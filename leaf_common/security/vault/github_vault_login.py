
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
        logger.info("Using vault login method 'github'")
        use_token = config.get("token", None)

        # If not specified, assume the vault server only has one organization
        # registered for authentication under the vault-standard "github" path.
        org_path = "github"

        # If the config tells us the github organization, formulate an auth
        # path that is leaf-standard, as we might want to have users coming
        # in from multiple github organizations for authorization.
        # See discussion about vault GitHub auth and orgs here:
        # https://discuss.hashicorp.com/t/github-auth-with-a-personal-github-account/6407
        org = config.get("organization", None)
        if org is not None:
            org_path = f"github-orgs/{org}"

        # If the full auth path is specified, use that as an override.
        use_path = config.get("path", org_path)

        if use_token is None:
            logger.warning("GitHub token missing from security_config spec")
            return None

        vault_client = VaultClient(url=vault_url, verify=vault_cacert)
        _ = vault_client.auth.github.login(token=use_token, mount_point=use_path)

        return vault_client
