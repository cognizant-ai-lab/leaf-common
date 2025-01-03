
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


from leaf_common.fitness.metrics_provider import MetricsProvider


class CandidateMetricsProvider(MetricsProvider):
    """
    MetricsProvider implementation that gets metrics from a Candidate dictionary
    """

    def __init__(self, candidate):
        """
        Constructor.
        :param candidate: The candidate whose metrics dictionary we want
        """
        self._candidate = candidate

    def get_metrics(self):
        """
        Returns the metrics of this entity.
        :return: a dictionary of metrics
        """

        if self._candidate is None:
            return None

        metrics = self._candidate.get('metrics', None)

        # Allow for old-school candidates
        # or Worker results dicts
        if metrics is None:
            metrics = self._candidate

        return metrics
