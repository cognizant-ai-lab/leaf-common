
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

from os import getenv


class EnvironmentUtil():
    """
    Utility class with methods to consolidate access to the environment variables
    """

    @staticmethod
    def getenv(env_key: str, default_value: str = None) -> str:
        """
        :param env_key: The os.environ key whose value should be gotten
        :param default_value: default value when the key is not present
        :return: The value of the environment variable which is always a string
        """
        value: str = None
        if env_key is None:
            return value
        value = getenv(env_key, default_value) or default_value
        return value
