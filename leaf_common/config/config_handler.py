
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
from typing import Union

from copy import deepcopy
from collections.abc import Mapping

from leaf_common.persistence.easy.easy_hocon_persistence import EasyHoconPersistence
from leaf_common.persistence.easy.easy_json_persistence import EasyJsonPersistence
from leaf_common.persistence.easy.easy_yaml_persistence import EasyYamlPersistence


class ConfigHandler():
    """
    An abstract class which handles configuration dictionaries
    """

    def import_config(self, config_source: Union[str, Dict[str, Any]],
                      default_config: Dict[str, Any] = None,
                      must_exist: bool = True) -> Dict[str, Any]:
        """
        Main entry point for reading config files
        :param config_source: Either a string filename reference to a
                config dictionary to be read from the file, or
                a config dictionary in and of itself
        :param default_config: A config dictionary to be used as a default.
                Default is None, indicating that no defaults are to be
                applied when reading from the config_source.
                When a dictionary is supplied, the default_config is used
                as a basis for which any new config parameters read
                from the config_source are overlayed on top of.
        :param must_exist: Default True.  When True, an error is
                raised when the file does not exist upon config
                reading via a Persistor restore() method.
                When False, the lack of a file to restore from is
                ignored and a dictionary value of None is returned
        """

        # Set up a very basic config dictionary
        config: Dict[str, Any] = {}
        if default_config is not None and isinstance(default_config, dict):
            config = deepcopy(default_config)

        # Potentially read config from a file, if config arg is a string filename
        update_source: Dict[str, Any] = {}
        if isinstance(config_source, str):
            update_source = self.read_config_from_file(config_source, must_exist)

        # Override entries from the defaults in setupConfig with the
        #     contents of the config arg that was passed in.
        elif isinstance(config_source, dict):
            update_source = config_source

        new_config: Dict[str, Any] = self.deep_update(config, update_source)
        return new_config

    def deep_update(self, dest: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs overlay functionality
        DEF: Use DictionaryOverlay class instead.
        """
        key: str = None
        value: Any = None
        for key, value in source.items():
            if isinstance(value, Mapping):
                recurse: Dict[str, Any] = self.deep_update(dest.get(key, {}), value)
                dest[key] = recurse
            else:
                dest[key] = source[key]
        return dest

    def read_config_from_file(self, filepath: str, must_exist: bool) -> Dict[str, Any]:
        """
        :param filepath: The file to parse
        :param must_exist: When True, an error is
                raised when the file does not exist upon config
                reading via a Persistor restore() method.
                When False, the lack of a file to restore from is
                ignored and a dictionary value of None is returned
        :return: The dictionary parsed from the config file
        """

        # Create a map of our parser methods
        file_extension_to_parser_map: Dict[str, str] = {
            ".conf": "parse_hocon",
            ".hocon": "parse_hocon",
            # Treat json separately as it's been shown that large json files
            # are really slow for the hocon parser to load.
            ".json": "parse_json",
            ".properties": "parse_hocon",
            ".yaml": "parse_yaml"
        }

        # See what the filepath extension says to use
        parser: str = None
        file_extension: str = None
        for file_extension in list(file_extension_to_parser_map.keys()):
            if filepath.endswith(file_extension):
                parser = file_extension_to_parser_map.get(file_extension)

        message: str = f"Could not read {filepath} as config. Unknown file extension."

        config: Dict[str, Any] = {}
        if parser is not None:
            config = self.parse_with_method(parser, filepath, must_exist)
        elif must_exist:
            raise ValueError(message)
        else:
            # Specifically use print here because this can happen
            # as part of setting up logging.
            print(message)
            config = {}

        return config

    def parse_with_method(self, parser: str, filepath: str, must_exist: bool) -> Dict[str, Any]:
        """
        :param parser: The parser method on this class to use
        :param filepath: The file to parse
        :param must_exist: When True, an error is
                raised when the file does not exist upon restore()
                When False, the lack of a file to restore from is
                ignored and a dictionary value of None is returned
        :return: The dictionary parsed from the config file
        """
        config: Dict[str, Any] = None

        if parser == "parse_hocon":
            config = self.parse_hocon(filepath, must_exist)
        elif parser == "parse_json":
            config = self.parse_json(filepath, must_exist)
        elif parser == "parse_yaml":
            config = self.parse_yaml(filepath, must_exist)
        return config

    def parse_json(self, filepath: str, must_exist: bool) -> Dict[str, Any]:
        """
        :param filepath: The json file to parse
        :param must_exist: When True, an error is
                raised when the file does not exist upon restore()
                When False, the lack of a file to restore from is
                ignored and a dictionary value of None is returned
        :return: The dictionary parsed from the hocon config file
        """
        persistence = EasyJsonPersistence(full_ref=filepath, must_exist=must_exist)
        config: Dict[str, Any] = persistence.restore(None)
        return config

    def parse_hocon(self, filepath: str, must_exist: bool) -> Dict[str, Any]:
        """
        :param filepath: The hocon file to parse
        :param must_exist: When True, an error is
                raised when the file does not exist upon restore()
                When False, the lack of a file to restore from is
                ignored and a dictionary value of None is returned
        :return: The dictionary parsed from the hocon config file
        """
        persistence = EasyHoconPersistence(full_ref=filepath, must_exist=must_exist)
        config: Dict[str, Any] = persistence.restore(None)
        return config

    def parse_yaml(self, filepath: str, must_exist: bool) -> Dict[str, Any]:
        """
        :param filepath: The yaml file to parse
        :param must_exist: When True, an error is
                raised when the file does not exist upon restore()
                When False, the lack of a file to restore from is
                ignored and a dictionary value of None is returned
        :return: The dictionary parsed from the yaml config file
        """
        persistence = EasyYamlPersistence(full_ref=filepath, must_exist=must_exist)
        config: Dict[str, Any] = persistence.restore(None)
        return config
