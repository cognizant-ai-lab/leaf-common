
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

import copy
from collections.abc import Mapping

from leaf_common.persistence.easy.easy_hocon_persistence \
    import EasyHoconPersistence
from leaf_common.persistence.easy.easy_json_persistence \
    import EasyJsonPersistence
from leaf_common.persistence.easy.easy_yaml_persistence \
    import EasyYamlPersistence


class ConfigHandler():
    """
    An abstract class which handles configuration dictionaries
    """

    def import_config(self, config_source, default_config=None,
                      must_exist=True):
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
        config = {}
        if default_config is not None and isinstance(default_config, dict):
            config = copy.deepcopy(default_config)

        # Potentially read config from a file, if config arg is a string filename
        update_source = {}
        if isinstance(config_source, str):
            update_source = self.read_config_from_file(config_source, must_exist)

        # Override entries from the defaults in setupConfig with the
        #     contents of the config arg that was passed in.
        elif isinstance(config_source, dict):
            update_source = config_source

        config = self.deep_update(config, update_source)
        return config

    def deep_update(self, dest, source):
        """
        Performs overlay functionality
        DEF: Use DictionaryOverlay class instead.
        """
        for key, value in source.items():
            if isinstance(value, Mapping):
                recurse = self.deep_update(dest.get(key, {}), value)
                dest[key] = recurse
            else:
                dest[key] = source[key]
        return dest

    def read_config_from_file(self, filepath, must_exist):
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
        file_extension_to_parser_map = {
            '.conf': 'parse_hocon',
            '.hocon': 'parse_hocon',
            # Treat json separately as it's been shown that large json files
            # are really slow for the hocon parser to load.
            '.json': 'parse_json',
            '.properties': 'parse_hocon',
            '.yaml': 'parse_yaml'
        }

        # See what the filepath extension says to use
        parser = None
        for file_extension in list(file_extension_to_parser_map.keys()):
            if filepath.endswith(file_extension):
                parser = file_extension_to_parser_map.get(file_extension)

        message = f"Could not read {filepath} as config. Unknown file extension."
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

    def parse_with_method(self, parser, filepath, must_exist):
        """
        :param parser: The parser method on this class to use
        :param filepath: The file to parse
        :param must_exist: When True, an error is
                raised when the file does not exist upon restore()
                When False, the lack of a file to restore from is
                ignored and a dictionary value of None is returned
        :return: The dictionary parsed from the config file
        """
        # Python magic to get a handle to the method
        parser_method = getattr(self, parser)

        # Call the parser method with the filepath, get dictionary back
        config = parser_method(filepath, must_exist)
        return config

    def parse_json(self, filepath, must_exist):
        """
        :param filepath: The json file to parse
        :param must_exist: When True, an error is
                raised when the file does not exist upon restore()
                When False, the lack of a file to restore from is
                ignored and a dictionary value of None is returned
        :return: The dictionary parsed from the hocon config file
        """
        persistence = EasyJsonPersistence(full_ref=filepath,
                                          must_exist=must_exist)
        config = persistence.restore()
        return config

    def parse_hocon(self, filepath, must_exist):
        """
        :param filepath: The hocon file to parse
        :param must_exist: When True, an error is
                raised when the file does not exist upon restore()
                When False, the lack of a file to restore from is
                ignored and a dictionary value of None is returned
        :return: The dictionary parsed from the hocon config file
        """
        persistence = EasyHoconPersistence(full_ref=filepath,
                                           must_exist=must_exist)
        config = persistence.restore()
        return config

    def parse_yaml(self, filepath, must_exist):
        """
        :param filepath: The yaml file to parse
        :param must_exist: When True, an error is
                raised when the file does not exist upon restore()
                When False, the lack of a file to restore from is
                ignored and a dictionary value of None is returned
        :return: The dictionary parsed from the yaml config file
        """
        persistence = EasyYamlPersistence(full_ref=filepath,
                                          must_exist=must_exist)
        config = persistence.restore()
        return config
