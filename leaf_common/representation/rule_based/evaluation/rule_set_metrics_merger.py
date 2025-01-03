
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
from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.evaluation.rule_metrics_merger import RuleMetricsMerger


class RuleSetMetricsMerger(MetricsMerger):
    """
    An incremental MetricsMerger for RuleSets.
    """

    def __init__(self, copy_over_original: bool = False):
        """
        Constructor

        :param copy_over_original: When True, this class does the apply()
            in-place on the original without making a copy beforehand.
        """
        self.copy_over_original = copy_over_original
        self.rule_merger = RuleMetricsMerger()

    def apply(self, original: RuleSet, incremental: RuleSet) -> RuleSet:
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

        result = original
        if not self.copy_over_original:
            result = deepcopy(original)

        if incremental is not None:

            # Incrementally update the RuleSet times_applied
            result.times_applied = original.times_applied + incremental.times_applied

            # Incrementally update each Rule's times_applied
            for idx, original_rule in enumerate(original.rules):
                incremental_rule = incremental.rules[idx]
                result_rule = self.rule_merger.apply(original_rule, incremental_rule)
                result.rules[idx] = result_rule

        return result

    def reset(self, incremental: RuleSet):
        """
        :param incremental: The incremental structure whose metrics are to be reset
                in-place.
        """
        incremental.times_applied = 0

        for rule in incremental.rules:
            self.rule_merger.reset(rule)
