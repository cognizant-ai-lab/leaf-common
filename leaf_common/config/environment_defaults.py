
# Copyright © 2019-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
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

from typing import Any
from typing import Dict

from os import environ


class EnvironmentDefaults():
    """
    Utility class with methods to manipulate the environment variables
    initially read in from the shell which calls the python app using
    this code.
    """

    @staticmethod
    def set_environment_defaults(default_dict: Dict[str, Any]) -> Dict[str, str]:
        """
        :param default_dict:  For each key in this dictionary, if there is
            not a corresponding key in the environ dictionary, then the
            value in default_dict is added to the environ dictionary.
            Keys that are already in the environ dictionary are not
            added.
        :return: a dictionary of values that were added. This dictionary
                could be empty if nothing was added, or None if default_dict
                was not a valid dictioanry.
        """

        if default_dict is None or \
                not isinstance(default_dict, dict):
            return None

        added: Dict[str, str] = {}
        # Copy over only those defaults the environment does not already define.
        for key in default_dict.keys():
            use_key: str = key

            # See if the key exists
            existing_value: str = environ.get(use_key, None)
            if existing_value is None:

                # Key does not exist, add from defaults
                # environ values must be strings
                new_value: str = str(default_dict.get(use_key))
                environ[use_key] = new_value
                added[use_key] = new_value

        return added
