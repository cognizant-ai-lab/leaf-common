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

import json
import logging
import requests

from leaf_common.security.service.service_accessor import ServiceAccessor


class Auth0DirectServiceAccessor(ServiceAccessor):
    """
    ServiceAccessor implmentation that obtains a security token
    directly from Auth0 for secure communication between client and service.
    """

    def __init__(self, security_config: Dict[str, Any],
                 auth0_defaults: Dict[str, Any] = None):
        """
        Constructor

        :param security_config: A security config dictionary for access to a
                particular server
        :param auth0_defaults: An optional dictionary containing defaults for
                auth0 access. Primarily for ESP compatibility.
        """
        # Secure channel, so make sure we have data we need to obtain Auth0 tokens
        self.auth0_username = security_config.get("username", None)
        self.auth0_password = security_config.get("password", None)
        if not self.auth0_username or not self.auth0_password:
            raise ValueError("Auth0 username and password must be supplied when using secure channel")

        use_auth0_defaults = auth0_defaults
        if auth0_defaults is None:
            use_auth0_defaults = {}

        # Our settings generally come from the security_config first
        # but if they are not there, then try to get them from
        # the passed in auth0_defaults.
        self.auth0_scope = security_config.get("scope",
                                               use_auth0_defaults.get("DEFAULT_AUTH0_PERMISSION"))
        self.auth0_client_secret = security_config.get("auth_secret",
                                                       use_auth0_defaults.get("DEFAULT_AUTH0_CLIENT_SECRET"))
        self.auth0_client_id = security_config.get("auth_client_id",
                                                   use_auth0_defaults.get("DEFAULT_AUTH0_CLIENT_ID"))
        self.auth0_audience = security_config.get("auth_audience",
                                                  use_auth0_defaults.get("DEFAULT_AUTH0_AUDIENCE"))

        # Use auth_domain first for compatibility with ENN's security config...
        self.auth0_url = use_auth0_defaults.get("DEFAULT_AUTH0_URL")
        auth_domain = security_config.get("auth_domain", None)
        if auth_domain is not None:
            self.auth0_url = f"https://{auth_domain}/oauth/token"

        # But let a full auth_url override, if present
        self.auth0_url = security_config.get("auth_url", self.auth0_url)

    def get_auth_token(self) -> str:
        """
        :return: A string that is the ephemeral service access token,
                used to set up a secure gRPC connection.
        """

        logger = logging.getLogger(self.__class__.__name__)

        logger.info('Requesting new auth token...')
        post_params = {
            'client_id': self.auth0_client_id,
            'client_secret': self.auth0_client_secret,
            'audience': self.auth0_audience,
            'grant_type': 'password',
            'username': self.auth0_username,
            'password':  self.auth0_password,
            'scope': self.auth0_scope,
            'realm': 'Username-Password-Authentication'
        }

        result = requests.post(url=self.auth0_url, json=post_params,
                               headers={'content-type': 'application/json'})
        result_as_dict = json.loads(result.text)

        access_token = result_as_dict.get('access_token', None)
        if access_token is not None:
            logger.info('Auth token received.')
        else:
            logger.error("Auth0 token request failed. Please check your Auth0 username and password:")
            logger.error("  result: %s", str(result))
            logger.error("  reason: %s", str(result.reason))
            logger.error("  json: %s", str(result.json()))

        return access_token

    @staticmethod
    def is_appropriate_for(security_config: Dict[str, Any]) -> bool:
        """
        :param security_config: A standardized LEAF security config dictionary
        :return: True if this class is appropriate given the contents of
                 the security_config dictionary
        """
        username = security_config.get("username", None)
        password = security_config.get("password", None)
        return bool(username) and bool(password)
