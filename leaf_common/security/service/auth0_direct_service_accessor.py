
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

import base64
import http.client
import json
import logging
import struct
import threading

import jwt

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

from leaf_common.security.service.service_accessor import ServiceAccessor
from leaf_common.time.timeout import Timeout


class Auth0DirectServiceAccessor(ServiceAccessor):
    """
    ServiceAccessor implmentation that obtains a security token
    directly from Auth0 for secure communication between client and service.
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, security_config: Dict[str, Any] = None,
                 auth0_defaults: Dict[str, Any] = None,
                 service_name: str = None,
                 poll_interval_seconds: int = 15,
                 umbrella_timeout: Timeout = None):
        """
        Constructor

        :param security_config: A security config dictionary for access to a
                particular server
        :param auth0_defaults: An optional dictionary containing defaults for
                auth0 access. Primarily for ESP compatibility.
        :param service_name: An optional string to be used for error messages
                when connecting to a service. If not given, we attempt to
                get this from the security_config/auth0_defaults.
        :param poll_interval_seconds: length of time in seconds methods
                on this class will wait before retrying connections
                or specific gRPC calls. Default to 15 seconds.
        :param umbrella_timeout: A Timeout object under which the length of all
                looping and retries should be considered
        """

        self.security_config = security_config
        self.auth0_defaults = auth0_defaults
        if self.auth0_defaults is None:
            self.auth0_defaults = {}
        self.poll_interval_seconds = poll_interval_seconds
        self.gave_help = False
        self.umbrella_timeout = umbrella_timeout

        # Determine the service name from the auth_audience for error messages
        self.service_name = service_name
        if self.service_name is None:
            auth_audience = self.auth0_defaults.get("auth_audience", "")
            if security_config is not None:
                auth_audience = security_config.get("auth_audience", auth_audience)
            self.service_name = auth_audience.split("/")[-1]
            if not self.service_name.endswith("-service"):
                self.service_name = f"{self.service_name}-service"

    def get_auth_token(self) -> str:
        """
        Queries the token issuing host to retrieve a new JWT based token for use with
        the gRPC interface in use.
        :return: The token.
        """
        # See https://auth0.com/blog/how-to-handle-jwt-in-python/#How-to-Verify-a-JWT
        unverified_header, token = self._get_unverified_header_and_token()

        # This comes back as a string with the key in PEM format
        rsa_key: str = self._get_rsa_key(unverified_header)

        # Will raise an exception on any validation failures
        alg = unverified_header.get("alg", None)
        if not alg:
            token = None
        else:
            alg = [alg]

        # Need proper audience otherwise we get errors
        auth_audience = self.security_config.get("auth_audience",
                                                 self.auth0_defaults.get("auth_audience"))

        # If we can do this without an exception, then it's verified
        # Hence, we don't really care about the output.
        _ = jwt.decode(token, key=rsa_key, algorithms=alg, audience=auth_audience)

        return token

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

    def _create_auth_domain_payload(self) -> str:
        """
        :return: A payload string to be used in verifying with the
                 auth_domain.
        """

        # Create the payload to send to the auth_domain
        auth_client_id = self.security_config.get("auth_client_id",
                                                  self.auth0_defaults.get("auth_client_id"))
        auth_secret = self.security_config.get("auth_secret",
                                               self.auth0_defaults.get("auth_secret"))
        auth_audience = self.security_config.get("auth_audience",
                                                 self.auth0_defaults.get("auth_audience"))
        username = self.security_config.get("username")
        password = self.security_config.get("password")
        scope = self.security_config.get("scope", self.auth0_defaults.get("scope"))

        payload = "client_id={0}&" \
                  "client_secret={1}&" \
                  "audience={2}&" \
                  "username={3}&" \
                  "password={4}&" \
                  "scope={5}&" \
                  "realm=Username-Password-Authentication&" \
                  "grant_type=password"
        payload = payload.format(auth_client_id, auth_secret,
                                 auth_audience, username, password,
                                 scope)

        return payload

    def _get_unverified_header_and_token(self):
        """
        Open an HTTP connection to the 'auth_domain' to obtain an unverified
        header to be used later.

        :return: An unverified header from the security_config dictionary's
                'auth_domain'.
        """
        unverified_header = None
        token = None

        payload = self._create_auth_domain_payload()

        # Create the headers to send to the auth_domain
        headers = {'content-type': "application/x-www-form-urlencoded"}

        # Connect to the auth_domain
        auth_domain = self.security_config.get("auth_domain",
                                               "cognizant-ai.auth0.com")
        self.gave_help = False

        while not unverified_header and \
            Timeout.has_time(self.poll_interval_seconds,
                             timeout=self.umbrella_timeout):
            try:
                conn = http.client.HTTPSConnection(auth_domain)
                if conn is not None:
                    conn.request("POST", "/oauth/token", payload, headers)

                    res = conn.getresponse()
                    data = res.read()

                    utf8_data = data.decode("utf-8")
                    resp_dict = json.loads(utf8_data)
                    token = resp_dict.get('access_token', None)
                    if token is not None:
                        unverified_header = jwt.get_unverified_header(token)
            finally:
                conn.close()

            if not unverified_header:
                message = f"Could not get access_token to {self.service_name}. "
                self._log_retry_help(message)

        return unverified_header, token

    @staticmethod
    def intarr2long(arr):
        """
        Riffed from: https://github.com/jpf/okta-jwks-to-pem/blob/master/jwks_to_pem.py
        """
        # Honestly have no idea what's happening here, but per the riff source, it works.
        # pylint: disable=consider-using-f-string
        return int(''.join(["%02x" % byte for byte in arr]), 16)

    def base64_to_long(self, data):
        """
        Riffed from: https://github.com/jpf/okta-jwks-to-pem/blob/master/jwks_to_pem.py
        """
        # Honestly have no idea what's happening here, but per the riff source, it works.
        mybytes = bytearray(data, "utf-8")
        mybytes += b'=='
        _d = base64.urlsafe_b64decode(mybytes)
        # pylint: disable=consider-using-f-string
        mylong = self.intarr2long(struct.unpack('%sB' % len(_d), _d))
        return mylong

    def _get_rsa_key(self, unverified_header: str) -> str:
        """
        Opens an HTTP connection to the auth_domain to get the rsa_key
        and returns it as a PEM formatted string.

        :param unverified_header:  The unverified_header from a previous call
                    to _get_unverified_header() above.
        :returns: A pem-formatted version of the rsa key
        """
        rsa_key_dict: Dict[str, Any] = self._get_rsa_key_dict(unverified_header)

        # Riffed from: https://github.com/jpf/okta-jwks-to-pem/blob/master/jwks_to_pem.py
        raw_exp = rsa_key_dict['e']
        exponent = self.base64_to_long(raw_exp)

        raw_mod = rsa_key_dict['n']
        modulus = self.base64_to_long(raw_mod)

        numbers = RSAPublicNumbers(exponent, modulus)
        public_key = numbers.public_key(backend=default_backend())
        pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                      format=serialization.PublicFormat.SubjectPublicKeyInfo)
        return pem

    def _get_rsa_key_dict(self, unverified_header: str) -> Dict[str, Any]:
        """
        Opens an HTTP connection to the auth_domain to get the rsa_key
        :param unverified_header:  The unverified_header from a previous call
                    to _get_unverified_header() above.
        :returns: A dictionary of rsa_key information
        """

        # Validate the key we have retrieved if we can to double check its
        # authenticity
        rsa_key = {}

        auth_domain = self.security_config.get("auth_domain",
                                               "cognizant-ai.auth0.com")
        self.gave_help = False

        # Empty dictionaries return False here
        while not bool(rsa_key) and \
            Timeout.has_time(self.poll_interval_seconds,
                             timeout=self.umbrella_timeout):
            try:
                conn = http.client.HTTPSConnection(auth_domain)
                if conn is not None:
                    conn.request("GET", "/.well-known/jwks.json")
                    res = conn.getresponse()
                    decoded_response = res.read().decode("utf-8")
                    hmac_key = json.loads(decoded_response)

                    for key in hmac_key["keys"]:
                        if key["kid"] == unverified_header["kid"]:
                            rsa_key = {
                                "alg": key["alg"],
                                "kty": key["kty"],
                                "kid": key["kid"],
                                "use": key["use"],
                                "n": key["n"],
                                "e": key["e"]
                            }
            finally:
                conn.close()

            # Empty dictionaries return False here
            if not bool(rsa_key):
                message = f"Could not get rsa_key for {self.service_name}. "
                self._log_retry_help(message)

        return rsa_key

    def _log_retry_help(self, message: str):
        """
        Logs the given message.
        Adds a help message if the help has not yet been given.
        Also adds a retry message.
        :param message: The message to log
        """

        logger = logging.getLogger(__name__)
        logger.warning(message)

        if not self.gave_help:
            file_ref = self.security_config.get("source_file_reference",
                                                "the command line arguments")
            help_message = \
                """
The most likely cause(s) of this are:
    1.  Your security credentials in %s are
        not entirely correct.  Please review the contents of that file
        to be sure the credentials in there are correct.
    2.  You are not able to reach outside the perimeter of your firewall.
        This is most likely the case if this is your first time (ever) in
        attempting to connect to the %s.
    3.  There is some kind of network outage between your machine and the %s.
        Ensuing automatic retries will assist in simply waiting to get past
        this problem if it is temporary.  If it persists, reconsider your
        connections to the internet.
                """
            logger.warning(help_message, file_ref, self.service_name,
                           self.service_name)
            self.gave_help = True

        logger.info("Retrying in %s seconds.", self.poll_interval_seconds)

        threading.Event().wait(timeout=self.poll_interval_seconds)
