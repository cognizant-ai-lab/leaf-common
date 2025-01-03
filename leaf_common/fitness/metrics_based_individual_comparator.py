
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

from leaf_common.fitness.comparator import Comparator
from leaf_common.fitness.metrics_provider import MetricsProvider
from leaf_common.fitness.number_comparator import NumberComparator

from leaf_common.parsers.field_extractor import FieldExtractor


class MetricsBasedIndividualComparator(Comparator):
    """
    A comparator that compares metrics_providers based on a given metric.
    """

    def __init__(self, metric_name: str, raise_on_problems: bool = True):
        """
        Creates a comparator that compares MetricsProviders based on the the
        value of the passed metric.

        :param metric_name: the name of the metric to use to compare 2
            MetricsProviders.
        :param raise_on_problems: True (default) if comparison problems
            are allowed to raise exceptions.
            False will always return -1 when there are comparison issues.
            While this behavior isn't necessarily desirable, it avoids
            problems where this comparator is used in services.
        """
        self._metric_name = metric_name
        self._raise_on_problems = raise_on_problems
        self._field_extractor = FieldExtractor()
        self._number_comparator = NumberComparator()

    def compare(self, obj1, obj2):
        """
        :param obj1: The first MetricsProvider offered for comparison
        :param obj2: The second MetricsProvider offered for comparison
        :return:  A negative integer, zero, or a positive integer as the first
                argument is less than, equal to, or greater than the second.
        """

        metrics_provider_1 = obj1
        metrics_provider_2 = obj2

        metric_1 = self.get_basis_value(metrics_provider_1)
        metric_2 = self.get_basis_value(metrics_provider_2)

        if metric_1 is None or metric_2 is None or \
           isinstance(metric_1, (int, float)):

            # Int and Float and None are supported in here
            return self._number_comparator.compare(metric_1, metric_2)

        # String and Boolean are supported here.
        # Unfortunately, Record.getField() returns an Object so we have to cast
        retval = -1
        if isinstance(metric_1, str):
            str2 = str(metric_2)
            if metric_1 < str2:
                retval = -1
            elif metric_1 > str2:
                retval = 1
            else:
                retval = 0

        elif isinstance(metric_1, bool):
            if metric_1 == bool(metric_2):
                retval = 0
            elif metric_1:
                retval = 1
            else:
                retval = -1

        elif not self._raise_on_problems:
            retval = -1
        else:
            metric_type_name = type(metric_1).__name__
            raise ValueError(f"Cannot compare metric type {metric_type_name}")
        return retval

    def get_basis_value(self, obj):
        """
        Returns the value of this selector's metric for the passed
        metrics_provider.

        :param obj: the metrics_provider for which to
            retrieve the metric value. Can be a metrics dictionary
            in and of itself as well.
        :return: the value of the of the metric field
        """
        metrics_provider = obj

        if metrics_provider is None:
            return None

        # Allow a MetricsProvider, or a metrics dict itself
        metrics = metrics_provider
        if isinstance(metrics_provider, MetricsProvider):
            # Use the interface on instances that implement it
            metrics = metrics_provider.get_metrics()
        elif isinstance(metrics_provider, dict):
            # Check for the case of the metrics provider being a dictionary.
            # Use the provided dict as its own default, as this allows
            # for both something containing the metrics dictionary
            # and a metrics dictionary itself to be passed in as an arg.
            metrics = metrics_provider.get("metrics", metrics_provider)
        else:
            # Don't know how to get metrics from this object
            return None

        metric = None
        if metrics is not None:
            metric = self._field_extractor.get_field(metrics, self._metric_name)

        return metric
