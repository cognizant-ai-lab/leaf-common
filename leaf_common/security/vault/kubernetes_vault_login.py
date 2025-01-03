
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

from os import access
from os import R_OK
from os.path import isfile

import logging

from hvac import Client as VaultClient

from leaf_common.security.vault.vault_login import VaultLogin


# pylint: disable=too-few-public-methods
class KubernetesVaultLogin(VaultLogin):
    """
    VaultLogin implementation that uses a Kubernetes role
    and optional kuberentes service token path to authenticate
    with the specified Vault server.

    Note that the Vault server admin must have already specified that kubernetes
    logins are acceptable using commands like:
        vault auth enable kubernetes
        vault write auth/kubernetes/config \
            kubernetes_host=https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT}
        vault write auth/kubernetes/role/<role-name> \
            bound_service_account_names=vault-auth \
            bound_service_account_namespaces=default \
            policies=<named-policies> \
            ttl=1h
    See: https://www.vaultproject.io/docs/auth/kubernetes for more details.

    An example named policy .hcl file (vault configuration file) might look like this:
        path "oauth2/self/my-machine-auth" {
            capabilities = ["read"]
        }
    ... for access to the vault_secret "oauth2/self/my-machine-auth"

    Vault server operators can install this policy like this:
        vault policy write <named-policy> <named-policy>.hcl

    For more info on Vault policies, see:
        https://www.vaultproject.io/docs/concepts/policies
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
        logger.info("Using vault login method 'kubernetes'")

        # Get the role that defines what permissions the vault client
        # will have after authenticating via kubernetes.
        # See https://www.vaultproject.io/docs/auth/kubernetes#configuration
        role = config.get("role", None)
        if role is None:
            logger.warning("Kubernetes role missing from security_config spec")
            return None

        # From https://www.vaultproject.io/docs/auth/kubernetes#code-example
        # Kubernetes will store its service account JWT token in this
        # mounted location. This can be configured differently, so this
        # is merely a default which can be overridden in the specified
        # config.
        jwt_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
        jwt_path = config.get("jwt_path", jwt_path)

        # If an actual JWT was specified in the config, use that.
        jwt = config.get("jwt", None)
        if jwt is None:
            if isfile(jwt_path) and access(jwt_path, R_OK):
                with open(jwt_path, "r", encoding="utf-8") as jwt_file:
                    jwt = jwt_file.read()
            else:
                logger.warning("Kubernetes jwt_path %s cannot be read",
                               jwt_path)
                return None

        # If the full auth path is specified, use that as an override.
        mount_point = config.get("path", "kubernetes")

        vault_client = VaultClient(url=vault_url, verify=vault_cacert)
        _ = vault_client.auth.kubernetes.login(role=role,
                                               jwt=jwt,
                                               mount_point=mount_point)

        return vault_client
