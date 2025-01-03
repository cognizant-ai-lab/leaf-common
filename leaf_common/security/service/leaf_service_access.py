
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

from typing import Dict

import copy
import logging
import os

from pathlib import Path

from leaf_common.config.config_handler import ConfigHandler
from leaf_common.security.service.service_accessor_factory import ServiceAccessorFactory


# pylint: disable=too-few-public-methods
class LeafServiceAccess:
    """
    Class that gets credentials for LEAF service(s).
    """

    def __init__(self, service_prefix: str = "LEAF",
                 server: str = None):
        """
        Constructor

        :param service_prefix: The service prefix to use when looking
                for security configs. Default is "LEAF".
                Other common values are "ESP" and "ENN".
                This value ends up being used as a convenience for
                a whole bunch of other aspects of this class
                like which env vars, file names, security-config
                and server names to use.
        :param server: A string specifying which server to look for
                in the security_config. These servers are portions of
                urls, and this class uses substring match on the
                security config file contents for it.
                Default of None implies that the lowercase version
                of the service_prefix is used.
        """
        # Basis for the rest
        self.service_prefix = service_prefix

        self.service_name = f"{self.service_prefix}_SERVICE"
        self.service_user_key = f"{self.service_name}_USER"
        self.service_password_key = f"{self.service_name}_PASSWORD"
        self.service_config = self.service_prefix.lower() + "_service_config"
        self.default_server = server
        if server is None:
            self.default_server = self.service_prefix.lower()

    def get_service_creds(self, server: str = None) -> Dict[str, str]:
        """
        :return: A dictionary containing the SERVICE_USER and SERVICE_PASSWORD
                keys filled in with the following precedence:
                    1.  <service_prefix>_SERVICE_USER / <service_prefix>_SERVICE_PASSWORD env vars
                    2.  Look through a list of service_config.hocon files
                        (like the one ENN uses) for a buried key that is
                        suitable.  If we find one, we return the entire security config
                        corresponding to the service prefix including the SERVICE_USER
                        and SERVICE_PASSWORD keys set.
        """
        # Initialize return dictionary
        service_creds = {}

        service_user = os.getenv(self.service_user_key, None)
        service_password = os.getenv(self.service_password_key, None)

        source = f"{self.service_name} environment variables"

        if service_user is None or \
                service_password is None:

            service_creds, source = self._read_security_config_files(source, server)
            service_user = service_creds.get("username", None)
            service_password = service_creds.get("password", None)

        # Last resort. Tell people they need to do something when shit fails.
        if service_user is None:
            service_user = f"Need-to-set-{self.service_user_key}"
            source += f". Need to set {self.service_user_key}"
        if service_password is None:
            service_password = f"Need-to-set-{self.service_password_key}"
            source += f". Need to set {self.service_password_key}"

        service_creds["SERVICE_USER"] = service_user
        service_creds["SERVICE_PASSWORD"] = service_password
        if service_creds.get("username", None) is None:
            service_creds["username"] = service_user
        if service_creds.get("password", None) is None:
            service_creds["password"] = service_password

        logger = logging.getLogger(self.__class__.__name__)
        logger.info("%s creds source is %s", self.service_name, source)

        return service_creds

    def _read_security_config_files(self, source: str, server: str = None):     # noqa: C901
        """
        :param source: A default source string to return if nothing was found
        :return: A security config from the appropriate security_config.hocon
                file, as long as it has a username and password specified.
                Otherwise return an empty dictionery
        """
        # Initialize values
        service_creds = {}
        use_server = server
        if server is None:
            use_server = self.default_server

        # Per https://stackoverflow.com/questions/4028904/what-is-a-cross-platform-way-to-get-the-home-directory
        # This is a cross-platform way of getting a HOME directory - Linux or Windows.
        home = str(Path.home())

        # Try a security_config.hocon
        # Search the hidden directory for the specified service_prefix first,
        # followed by a precedence order of other known services.
        security_config_files = [
            os.path.join(home, "." + self.service_prefix.lower(), "security_config.hocon"),
            os.path.join(home, ".esp", "security_config.hocon"),
            os.path.join(home, ".enn", "security_config.hocon")
        ]
        config_reader = ConfigHandler()
        for security_config_file in security_config_files:

            # Try to open the security_config file
            try:
                security_config = config_reader.import_config(
                    security_config_file)
            except FileNotFoundError:
                security_config = {}

            # Find the right top-level service config
            # Try the one corresponding to the actual service prefix first
            try_service_config = security_config.get(self.service_config, None)

            if try_service_config is None:
                # No use going any further
                continue

            source = f"security config file {security_config_file}"

            server_config = {}
            for try_server, server_config in try_service_config.items():

                if not isinstance(server_config, dict):
                    # Not a dict, no use going any further
                    continue

                if try_server.find(use_server) < 0:
                    # The server name needs to match something in the url
                    # Note: This is a substring match, not an exact match.
                    continue

                if ServiceAccessorFactory.is_useful_config(server_config):
                    service_creds = copy.copy(server_config)
                    service_creds["source_file_reference"] = source
                    break

            # End of loop for one security config file
            if ServiceAccessorFactory.is_useful_config(server_config):
                # Found something useful
                break

        return service_creds, source
