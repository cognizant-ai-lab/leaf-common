
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

from inspect import currentframe
from inspect import getframeinfo

import OpenSSL

from grpc import access_token_call_credentials
from grpc import composite_call_credentials
from grpc import composite_channel_credentials
from grpc import ssl_channel_credentials

from leaf_common.time.timeout import Timeout
from leaf_common.security.service.service_accessor_factory \
    import ServiceAccessorFactory


class GrpcChannelSecurity():
    """
    A class aiding in the creation of GRPC channel security credentials by
    reading key/value pairs from a security configuration dictionary to
    figure out just how we will be getting a token to access a LEAF service.
    This class also handles caching of a token as well.
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, security_cfg: Dict[str, Any] = None,
                 auth0_defaults: Dict[str, Any] = None,
                 service_name: str = None,
                 poll_interval_seconds: int = 15,
                 umbrella_timeout: Timeout = None):
        """
        :param security_cfg: An optional dictionary of parameters used to
                        secure the TLS and the authentication of the gRPC
                        connection.  Supplying this implies use of a secure
                        GRPC Channel.  Default is None, uses insecure channel.
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
        """

        self.security_cfg = security_cfg

        # This class being a client of security_cfg, translate None or non-dict
        # values to be an empty dictionary
        if self.security_cfg is None or \
                not isinstance(self.security_cfg, dict):

            # If we had no security config, assume there are to be
            # no secure connections.
            self.security_cfg = {
                "connection_type": "insecure"
            }

        self.jwt_token = None
        self.service_accessor = ServiceAccessorFactory.get_service_accessor(
                                    security_config=self.security_cfg,
                                    auth0_defaults=auth0_defaults,
                                    service_name=service_name,
                                    poll_interval_seconds=poll_interval_seconds,
                                    umbrella_timeout=umbrella_timeout)

    def has_token(self) -> bool:
        """
        :return: True when we alrady have a JWT token
        """
        has = self.jwt_token is not None
        return has

    def reset_token(self) -> None:
        """
        Resets the JWT Token
        """
        self.jwt_token = None

    def needs_credentials(self) -> bool:
        """
        Credentials are needed not needed if the connection_type key
        in the security_config is set to "insecure".  When this key is
        not set (the default setup of the user's security_config),
        this returns True.  Implementation here leaves outs for specifying
        other kinds of secure connections, should they arise.

        :return: True if the contents of the security_cfg for this object
                dictates that obtaining credentials from an auth_domain
                is required. False otherwise.
        """

        needed = True

        connection_type = self.security_cfg.get("connection_type", None)
        if connection_type is None:
            needed = True
        elif not isinstance(connection_type, str):
            needed = True
        elif connection_type.lower() == "insecure":
            needed = False

        if self.service_accessor is None:
            needed = False

        return needed

    def get_auth_host_override(self) -> str:
        """
        :return: The auth_host_override from the security config dictionary,
                or None if this does not exist.
        """
        auth_host_override = self.security_cfg.get("auth_host_override", None)
        return auth_host_override

    def get_composite_channel_credentials(self):
        """
        :return: The GRPC composite channel credentials, given the information
                in the instance's security_cfg dictionary.
        """

        credentials = None
        if self.needs_credentials():
            # We have no previous credentials passed into the security config dict.
            # Try to get the credentials given other information in the dict.
            chan_creds = self._get_channel_credentials()
            call_creds = self._get_call_credentials()
            if chan_creds is not None:
                if call_creds is not None:
                    credentials = composite_channel_credentials(chan_creds,
                                                                call_creds)
                else:
                    credentials = chan_creds
            elif call_creds is not None:
                credentials = call_creds

        return credentials

    def _get_channel_credentials(self):
        """
        Extract certificates based on the values specified by the
        user on the command line.  Certs and keys are then returned
        along with any token information supplied by the user in a
        format that works for the gRPC packages

        :return: A tuple of grpc ChannelCredentials and CallCredentials
                Both of these can be None if there is not enough information
                in the security config dictionary to determine how security
                should be done.
        """

        trusted_certs = None
        client_key = None
        client_cert = None
        try:
            ca_pem_file = self.security_cfg.get("ca_pem", None)
            if ca_pem_file is not None:
                with open(ca_pem_file, 'rb') as pem_file:
                    trusted_certs = pem_file.read()
                    OpenSSL.crypto.load_certificate(
                        OpenSSL.crypto.FILETYPE_PEM,
                        trusted_certs)

            client_key_file = self.security_cfg.get("client_key", None)
            if client_key_file is not None:
                with open(client_key_file, 'rb') as key_file:
                    client_key = key_file.read()
                    OpenSSL.crypto.load_privatekey(
                        OpenSSL.crypto.FILETYPE_PEM,
                        client_key)

            client_cert_file = self.security_cfg.get("client_cert", None)
            if client_cert_file is not None:
                with open(client_cert_file, 'rb') as crt_file:
                    client_cert = crt_file.read()
                    OpenSSL.crypto.load_certificate(
                        OpenSSL.crypto.FILETYPE_PEM,
                        client_cert)

        except Exception as err:
            frameinfo = getframeinfo(currentframe())
            logger = logging.getLogger(__name__)
            logger.warning("%s %s %s", str(err),
                           str(frameinfo.filename),
                           str(frameinfo.lineno))
            raise err

        # Any one of the certs provided can be None.
        # If all are None, then we are assuming auto-certs on the service side.
        chan_creds = ssl_channel_credentials(root_certificates=trusted_certs,
                                             private_key=client_key,
                                             certificate_chain=client_cert)

        return chan_creds

    def _get_call_credentials(self):
        """
        :return: The composite CallCredentials, given the jwt_token already
                stored on the instance.  Can fetch a new jwt token,
                if no jwt_token yet exists.
        """
        if not self.has_token():
            if self.service_accessor is not None:
                self.jwt_token = self.service_accessor.get_auth_token()

        # Allow for no service accessor which means we have no way
        # to get a token.
        composite_call_creds = None
        if self.has_token():
            call_creds = access_token_call_credentials(self.jwt_token)
            composite_call_creds = composite_call_credentials(call_creds)

        return composite_call_creds
