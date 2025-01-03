
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

import os


class EnvironmentDefaults():
    """
    Utility class with methods to manipulate the environment variables
    initially read in from the shell which calls the python app using
    this code.
    """

    @classmethod
    def set_environment_defaults(cls, default_dict):
        """
        :param default_dict:  For each key in this dictionary, if there is
            not a corresponding key in the os.environ dictionary, then the
            value in default_dict is added to the os.environ dictionary.
            Keys that are already in the os.environ dictionary are not
            added.
        :return: a dictionary of values that were added. This dictionary
                could be empty if nothing was added, or None if default_dict
                was not a valid dictioanry.
        """

        if default_dict is None or \
                not isinstance(default_dict, dict):
            return None

        added = {}
        for key in default_dict.keys():

            # See if the key exists
            existing_value = os.environ.get(key, None)
            if existing_value is None:

                # Key does not exist, add from defaults
                # os.environ values must be strings
                new_value = str(default_dict.get(key))
                os.environ[key] = new_value
                added[key] = new_value

        return added
