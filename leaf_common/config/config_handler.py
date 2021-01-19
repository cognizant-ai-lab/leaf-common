
# Copyright (C) 2019-2020 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# ENN-release SDK Software in commercial settings.
#
# END COPYRIGHT

import copy
from collections.abc import Mapping

from leaf_common.persistence.easy.easy_hocon_persistence \
    import EasyHoconPersistence
from leaf_common.persistence.easy.easy_yaml_persistence \
    import EasyYamlPersistence


class ConfigHandler():
    """
    An abstract class which handles configuration dictionaries
    """

    def import_config(self, config_source, default_config=None):

        # Set up a very basic config dictionary
        config = {}
        if default_config is not None and isinstance(default_config, dict):
            config = copy.deepcopy(default_config)

        # Potentially read config from a file, if config arg is a string filename
        update_source = {}
        if isinstance(config_source, str):
            update_source = self.read_config_from_file(config_source)

        # Override entries from the defaults in setupConfig with the
        #     contents of the config arg that was passed in.
        elif isinstance(config_source, dict):
            update_source = config_source

        config = self.deep_update(config, update_source)
        return config


    def deep_update(self, dest, source):
        for key, value in source.items():
            if isinstance(value, Mapping):
                recurse = self.deep_update(dest.get(key, {}), value)
                dest[key] = recurse
            else:
                dest[key] = source[key]
        return dest


    def read_config_from_file(self, filepath):

        # Create a map of our parser methods
        file_extension_to_parser_map = {
            '.conf': 'parse_hocon',
            '.hocon': 'parse_hocon',
            '.json': 'parse_hocon',
            '.properties': 'parse_hocon',
            '.yaml': 'parse_yaml'
        }

        # See what the filepath extension says to use
        parser = None
        for file_extension in list(file_extension_to_parser_map.keys()):
            if filepath.endswith(file_extension):
                parser = file_extension_to_parser_map.get(file_extension)

        if parser is not None:
            config = self.parse_with_method(parser, filepath)
        else:
            # Specifically use print here because this can happen
            # as part of setting up logging.
            print("Could not read {0} as config".format(filepath))
            config = {}

        return config

    def parse_with_method(self, parser, filepath):
        # Python magic to get a handle to the method
        parser_method = getattr(self, parser)

        # Call the parser method with the filepath, get dictionary back
        config = parser_method(filepath)
        return config

    def parse_hocon(self, filepath):
        persistence = EasyHoconPersistence(full_ref=filepath)
        config = persistence.restore()
        return config

    def parse_yaml(self, filepath):
        persistence = EasyYamlPersistence(full_ref=filepath)
        config = persistence.restore()
        return config
