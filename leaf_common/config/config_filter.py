
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
See class comment for details
"""

from typing import Dict


class ConfigFilter():
    """
    Interface for modifying a config dictionary.

    This interface is meant to be generic enough to that multiple
    implementations could be chained together.

    Ideally, implementations would take no arguments in their constructor,
    thus allowing config modification at an early stage in an app's lifecyle.
    """

    def filter_config(self, basis_config: Dict[str, object]) \
            -> Dict[str, object]:
        """
        Filters the given basis config.

        Ideally this would be a Pure Function in that it would not
        modify the caller's arguments so that the caller has a chance
        to decide whether to take any changes returned.

        :param basis_config: The config dictionary to act as the basis
                for filtering
        :return: A config dictionary, potentially modified as per the
                policy encapsulated by the implementation
        """
        raise NotImplementedError
