
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


from leaf_common.fitness.none_comparator import NoneComparator


class NumberComparator(NoneComparator):
    """
    An implementation of the Comparator interface for
    comparing two numbers.
    """

    def compare(self, obj1, obj2):
        """
        :param obj1: The first object offered for comparison
        :param obj2: The second object offered for comparison
        :return:  A negative integer, zero, or a positive integer as the first
                argument is less than, equal to, or greater than the second.
        """

        comparison = super().compare(obj1, obj2)
        if comparison is not None:
            return comparison

        if obj1 < obj2:
            return -1
        if obj1 > obj2:
            return 1

        return 0
