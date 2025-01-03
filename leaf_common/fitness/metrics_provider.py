
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


class MetricsProvider:
    """
    An interface for dealing with an entity (like an Individual) which has
    a way of giving Metrics Records.
    """

    def get_metrics(self):
        """
        Returns the metrics of this entity.
        :return: a dictionary of metrics
        """
        raise NotImplementedError
