
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


class ReversedComparator(Comparator):
    """
    Wrapper class for a Comparator that reverses the comparison
    """

    def __init__(self, basis_comparator):
        """
        Constructor.

        :param basis_comparator: The comparator to wrap whose comparison
            results will be reversed.
        """
        self._basis_comparator = basis_comparator

    def compare(self, obj1, obj2):
        """
        :param obj1: The first object offered for comparison
        :param obj2: The second object offered for comparison
        :return:  A negative integer, zero, or a positive integer as the first
                argument is less than, equal to, or greater than the second.
        """
        unflipped = self._basis_comparator.compare(obj1, obj2)
        flipped = -unflipped
        return flipped

    def get_basis_value(self, obj):
        """
        This default implementation returns the object itself, which is a
        reasonable basis for numeric comparator implementations.

        :param obj: the basis object
        :return: The value from the object which is the basis of comparison
        """
        return self._basis_comparator.get_basis_value(obj)

    def get_basis_comparator(self):
        """
        :return: the basis comparator
        """
        return self._basis_comparator

    @staticmethod
    def reverse(basis_comparator):
        """
        Motivation behind this method is that it is possible to layer
        ReversedComparators on top of each other, when what you really
        want is the main comparator back.  This method exists to get
        you that efficient reversal.

        :param basis_comparator: The comparator to efficiently reverse
        :return: A Comparator that is an efficient reversal of
                the basis_comparator
        """

        if basis_comparator is None:
            return None

        if isinstance(basis_comparator, ReversedComparator):
            # Reversal of a ReversedComparator is the original
            return basis_comparator.get_basis_comparator()

        return ReversedComparator(basis_comparator)
