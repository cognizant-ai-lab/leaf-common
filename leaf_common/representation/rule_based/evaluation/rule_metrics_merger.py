
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

from copy import deepcopy

from leaf_common.evaluation.metrics_merger import MetricsMerger
from leaf_common.representation.rule_based.data.rule import Rule


class RuleMetricsMerger(MetricsMerger):
    """
    An incremental MetricsMerger for Rules.
    """

    def apply(self, original: Rule, incremental: Rule) -> Rule:
        """
        :param original: The original metrics Record/dictionary
                Can be None.
        :param incremental: The metrics Record/dictionary with the same
                keys/structure, but whose data is an incremental update
                to be (somehow) applied to the original.
                Can be None.
        :return: A new Record/dictionary with the incremental update performed.
        """
        if original is None:
            return None

        result = deepcopy(original)

        if incremental is not None:
            result.times_applied = original.times_applied + incremental.times_applied

        return result

    def reset(self, incremental: Rule):
        """
        :param incremental: The incremental structure whose metrics are to be reset
                in-place.
        """
        incremental.times_applied = 0
