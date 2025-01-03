
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

from leaf_common.security.service.service_accessor import ServiceAccessor
from leaf_common.security.vault.vault_login_factory import VaultLoginFactory


class VaultDynamicTokenServiceAccessor(ServiceAccessor):
    """
    ServiceAccessor implmentation that obtains a dynamic security token
    from a Hashicorp Vault.

    Expects the vault server to have this plugin for OAuth:
        https://github.com/puppetlabs/vault-plugin-secrets-oauthapp
    ... and be set up for its "Client Credentials Flow"

    Remember that *both* of these need to be set up for memory locking:
        1) the vault binary         AND
        2) the oathapp plugin

    ... before the server starts via this command:
        sudo /sbin/setcap cap_ipc_lock=+ep <executable>

    ... or "Unrecognized remote plugin" messages can occur.

    The vault server must also be set up for the plugin along these lines
    (after logging into Vault server as operator with root token):
        # Plugin setup
        vault plugin register -sha256=`sha256sum /etc/vault.d/plugins/oauthapp | awk '{ print $1 }'` secret oauthapp
        vault secrets enable -path=oauth2 oauthapp

        # Specific server setup
        vault write oauth2/servers/auth0-<service-name> \
                    provider=oidc \
                    provider_options=issuer_url=https://cognizant-ai.auth0.com/ \
                    client_id=<auth0-app-client-id-for-service> \
                    client_secret=<auth0-app-client-secret-for-service>
        vault write oauth2/self/<service-name> \
                    server=auth0-<service_name> \
                    token_url_params=audience=http://api.cognizant-ai.dev/<service> \
                    scopes=all:<service>

    Server setup verification can be done with this command:
        vault read oauth2/self/<service-name>

        "oauth2/self/<service-name>" ends up becoming the value for "vault_secret"
        in the security_configs.
    """

    def __init__(self, security_config: Dict[str, Any],
                 auth0_defaults: Dict[str, Any] = None):
        """
        Constructor

        :param security_config: A standardized LEAF security config dictionary
        :param auth0_defaults: An optional dictionary containing defaults for
                auth0 access. Primarily for gleaning service information for
                default vault_secret.
        """
        self.vault_url = security_config.get("vault_url", None)
        self.vault_login = security_config.get("vault_login", None)
        self.vault_cacert = security_config.get("vault_cacert", None)

        # Get a default for the vault secret path together based on
        # the audience in the auth0 defaults.
        default_vault_secret = None

        auth_audience = ""
        if auth0_defaults is not None:
            auth_audience = auth0_defaults.get("auth_audience", auth_audience)
        auth_audience = security_config.get("auth_audience", auth_audience)

        service_name = auth_audience.split("/")[-1]
        if not service_name.endswith("-service"):
            service_name = f"{service_name}-service"

        default_vault_secret = f"oauth2/self/{service_name}"

        self.vault_secret = security_config.get("vault_secret", default_vault_secret)
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_auth_token(self) -> str:
        """
        :return: A string that is the ephemeral service access token,
                used to set up a secure gRPC connection.
        """
        login_factory = VaultLoginFactory()
        vault_client: VaultClient = login_factory.login(self.vault_url,
                                                        config=self.vault_login,
                                                        vault_cacert=self.vault_cacert)
        if not login_factory.is_connection_valid(vault_client, verbose=True):
            return None

        read_response = vault_client.read(self.vault_secret)
        empty = {}
        data = read_response.get("data", empty)
        token = data.get("access_token", None)
        return token

    @staticmethod
    def is_appropriate_for(security_config: Dict[str, Any]) -> bool:
        """
        :param security_config: A standardized LEAF security config dictionary
        :return: True if this class is appropriate given the contents of
                 the security_config dictionary
        """
        vault_url = security_config.get("vault_url", None)
        return bool(vault_url)
