
# Copyright © 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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

import logging

from leaf_common.parsers.parser import Parser


class CanonicalMultiConfigParser(Parser):
    """
    Class to aid in parsing config fields that could be any one of:

        1. A single string, naming a class for some Factory to instantiate
        2. An array of strings, naming multiple classes for some Factory
        3. A dictionary whose keys are class names for some factory
            and whose values are configuration dictionaries for each
            class name key.
        4. An array of dictionaries, each a distinct configuration with the
            name of the class under the key specified by the constructor
            name_key argument.

    This class is able to parse all of the above formats for specifying
    potentially multiple classes and their configs to a canonical format of
    they array of dictionaries (#4) for digestion by higher-level code.
    We settle on this list as our canonical form as it allows for the case
    where the ordering of what is parsed matters.
    """

    def __init__(self, name_key="name"):
        """
        Constructor.

        :param name_key: The key to use in each canonical dictionary
                as the name to be later invoked by some Factory class
                for instantiation.
        """
        self.name_key = name_key

    def parse(self, input_obj):
        """
        :param input_obj: the string (or other object) to parse

        :return: A list in format #4 above -- an array of configuration
                dictionaries with a name_key in each indicating the
                class to pass to a factory.  This will return an
                empty list if the value to parse is None.
        """

        # Parse the value to be in a cannonical form of an array of
        # configuration dictionaries
        config_list = []
        config_list = self.parse_one_value(None, input_obj, config_list)

        return config_list

    def parse_one_value(self, key, value, config_list):
        """
        Parses a single config value and adds the entry
        to the config_list.

        :param key: the key that was obtained
        :param value: the value for the key
        :param config_list: The working copy of the list of configurations
                            and their individual config
        :return: An updated config_list
        """

        if value is None:
            return config_list

        if isinstance(value, str):
            # The value is a string.
            # Assume this is the name of a config
            # to be used with its default configuration.
            # Add a key for the string with a None value to indicate this.
            config_dict = {
                self.name_key: value
            }
            config_list.append(config_dict)

        elif isinstance(value, list):
            # The value is a list
            # Parse each component of the list as if it were
            # its own value to recurse on.
            for sub_value in value:
                config_list = self.parse_one_value(key, sub_value, config_list)

        elif isinstance(value, dict):

            # The value is a dictionary.
            use_key = key
            if use_key is None:
                # Look to see if the name of the config is embedded
                # within the config dictionary for it
                use_key = value.get(self.name_key, None)

            if use_key is None:
                # Assume the dictionary is a key-value pair
                # of config name -> config for that config
                for sub_key in value.keys():
                    sub_value = value.get(sub_key)
                    # Recurse.
                    config_list = self.parse_one_value(sub_key, sub_value,
                                                       config_list)
            else:
                # The dictionary is the config for the given key.
                # Add an entry to the config_list for this pair.
                config_dict = {
                    self.name_key: use_key
                }
                config_dict.update(value)
                config_list.append(config_dict)

        else:
            logger = logging.getLogger(__name__)
            logger.warning("Can't parse multi-config value %s.", str(value))

        return config_list
