
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


class MetricsMerger():
    """
    A class to assist with incrementally merge metrics records.
    """

    def apply(self, original, incremental):
        """
        :param original: The original metrics Record/dictionary
                Can be None.
        :param incremental: The metrics Record/dictionary with the same
                keys/structure, but whose data is an incremental update
                to be (somehow) applied to the original.
                Can be None.
        :return: A new Record/dictionary with the incremental update performed.
        """
        raise NotImplementedError

    def reset(self, incremental):
        """
        :param incremental: The incremental structure whose metrics are to be reset
                in-place.
        """
        raise NotImplementedError
