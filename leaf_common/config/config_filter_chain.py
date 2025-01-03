
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
from typing import Dict

from leaf_common.config.config_filter import ConfigFilter


class ConfigFilterChain(ConfigFilter):
    """
    A generic filter chain for use with LEAF ConfigFilter implementations.
    of a common GeneticMaterial type.

    When this class's filter_config() method is called, each ConfigFilter
    that was registered with register() is called in order.  In general,
    the output of one filter is fed to the next as input.
    """

    def __init__(self):
        """
        Constructor.
        """
        self._filters = []

    def register(self, one_filter: ConfigFilter):
        """
        Registers a single filter with this filter chain instance.
        The order that these calls are made matters.

        :param one_filter: a ConfigFilter to add to the filter chain.
        """
        self._filters.append(one_filter)

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
        filtered = basis_config

        # Go through the filter chain
        for one_filter in self._filters:
            filtered = one_filter.filter_config(filtered)

        return filtered
