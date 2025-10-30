
# Copyright 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# END COPYRIGHT
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
        raise NotImplementedError
