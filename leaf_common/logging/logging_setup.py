
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

import inspect
import logging
import logging.config
import os

from leaf_common.config.config_handler import ConfigHandler
from leaf_common.logging.stream_to_logger import StreamToLogger


# pylint: disable=too-many-instance-attributes
class LoggingSetup():
    """
    Class to aid in setting up python logging from a JSON file
    that configures the logging.
    """

    # Tied for Public Enemy #2 for too-many-arguments
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, default_log_config_dir=".",
                 default_log_config_file='logging.json',
                 default_log_level='DEBUG',
                 log_config_env=None,
                 log_level_env=None,
                 log_file=None,
                 logging_config=None,
                 source_anchor=None,
                 default_logger_name=None):
        """
        Constructor.

        :param default_log_config_dir: Directory on filesystem where the logging
                        configuration file lives.  Default is current directory.
        :param default_log_config_file: The default name of the logging
                        configuration file.  Default is 'logging.json'
        :param default_log_level: The default log level if no config file found.
                        Default is 'DEBUG'
        :param log_config_env: Environment variable name from which
                            to get a potential override of the
                            previously mentioned coded defaults config file.
                            Default is None, indicating no override is
                            possible.
        :param log_level_env: Environment variable name from which
                            to get a potential override of the
                            previously mentioned coded default log level.
                            Default is None, indicating no override is
                            possible.
        :param log_file: The actual file to log to.
                        This overrides anything in the config.
                        Default is None - no override.
        :param logging_config: Config reference. Can be file or dictionary
                        Default is None, implying use everything else above.
        :param source_anchor: object whose source file is the anchor
                        for relative paths. Default is None, implying
                        this the current working directory.
        :param default_logger_name:  The name of the logger to use
                        for default print diversion.
        """
        self.default_log_config_dir = default_log_config_dir
        self.default_log_config_file = default_log_config_file
        self.default_log_level = default_log_level
        self.log_config_env = log_config_env
        self.log_level_env = log_level_env
        self.log_file = log_file
        self.logging_config = logging_config
        self.source_anchor = source_anchor
        self.default_logger_name = default_logger_name

    def setup_with_diversion(self):
        """
        Sets up logging while diverting stdout/err to the
        logger for the source anchor.

        :return: the logger used for diversion
        """

        self.setup()

        # Determine the default logger name
        logger_name = self.default_logger_name
        if logger_name is None:
            logger_name = "default"
            if self.source_anchor is not None:
                logger_name = self.source_anchor.__class__.__name__

        logger = logging.getLogger(logger_name)
        log_level = self.determine_log_level()
        logger.setLevel(log_level)
        StreamToLogger.subvert(logger=logger,
                               reroute_stdout=True,
                               reroute_stderr=True)

        # Specifically use print here to be sure that print
        # statements are going to the logger.
        print("Print statements diverted to logger")

        return logger

    def setup(self):
        """
        Actually set up the logging per the parameters in the constructor.
        """

        # First, assume the config was what we got from constructor
        config = self.logging_config

        # We need to go through the motions of constructing the path
        # and tearing it down again because we might be getting it
        # from an env variable.
        log_config_file_path = self.determine_log_config_file_path()
        if log_config_file_path is not None:

            # Read the logging config file
            config_handler = ConfigHandler()
            config = config_handler.import_config(log_config_file_path)

        # Use the configuration we got.
        if config is not None \
                and isinstance(config, dict):
            config = self.replace_log_file(config)
            logging.config.dictConfig(config)
        else:
            log_level = self.determine_log_level()
            logging.basicConfig(filename=self.log_file,
                                level=log_level)

    def determine_log_config_file_path(self):
        """
        Determine the path of the log config file based on constructor args.
        :return: a single string path to the log file
        """

        # By default, use defaults passed into constructor
        default_logging_config_file = os.path.join(self.default_log_config_dir,
                                                   self.default_log_config_file)

        # See if explicit config was given in constructor
        if self.logging_config is not None:

            # If the explicit config was an actual dictionary,
            # then we do not need to go reading a file
            if isinstance(self.logging_config, dict):
                return None

            # If it was a string, use that as the full path
            if isinstance(self.logging_config, str):
                default_logging_config_file = self.logging_config

        # See if we need to get an override from environment
        log_config_file_path = default_logging_config_file
        if self.log_config_env is not None:
            log_config_file_path = os.environ.get(self.log_config_env,
                                                  default_logging_config_file)

        # Whatever we got, make sure it is an absolute path
        if log_config_file_path.startswith("."):
            log_config_file_path = LoggingSetup.get_absolute_source_file_path(
                                            log_config_file_path,
                                            source_anchor=self.source_anchor)

        log_config_file_path = os.path.abspath(log_config_file_path)

        return log_config_file_path

    def determine_log_level(self):
        """
        This is only used when no config file is found.
        :return: The log level for a basicConfig
        """
        # Determine the default log level
        log_level = self.default_log_level
        if self.log_level_env is not None:
            log_level = os.environ.get(self.log_level_env,
                                       self.default_log_level)
        return log_level

    def replace_log_file(self, config):
        """
        Replace the log file in the given config with the one passed into the
        constructor.
        :param config: The dictionary containing the logging config.
        :return: A potentially modified dictionary containing the logging config
        """

        # If there is nothing to change, return early
        if self.log_file is None:
            return config

        # Loop through each handler to find the first one with the filename set.
        handlers = config.get("handlers", {})
        for handler_key in handlers.keys():

            handler = handlers.get(handler_key, {})

            filename = handler.get("filename", None)
            if filename is not None:
                handler["filename"] = self.log_file
                break

        return config

    @classmethod
    def get_absolute_source_file_path(cls, relative_filepath, source_anchor=None):
        """
        :param relative_filepath: The filepath relative to the source file
                for this class
        :param source_anchor: An instance whose source file is to be the anchor
                for any relative source paths.  Default value of None implies
                use of the current working directory.
        :return: the full absolute path to the provided relative_filepath
        """

        relative_dir = os.getcwd()
        if source_anchor is not None:
            if isinstance(source_anchor, str):
                relative_dir = source_anchor
            else:
                module_file = inspect.getfile(source_anchor.__class__)
                module_path = os.path.abspath(module_file)
                relative_dir = os.path.dirname(module_path)

        partial_relative_path = os.path.join(relative_dir, relative_filepath)
        absolute_file_path = os.path.abspath(partial_relative_path)
        return absolute_file_path
