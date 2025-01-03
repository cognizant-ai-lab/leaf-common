
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


class Comparator():
    """
    An interface for comparing two objects.
    """

    def compare(self, obj1, obj2):
        """
        :param obj1: The first object offered for comparison
        :param obj2: The second object offered for comparison
        :return:  A negative integer, zero, or a positive integer as the first
                argument is less than, equal to, or greater than the second.
        """
        raise NotImplementedError

    def get_basis_value(self, obj):
        """
        This default implementation returns the object itself, which is a
        reasonable basis for numeric comparator implementations.

        :param obj: the basis object
        :return: The value from the object which is the basis of comparison
        """
        return obj
