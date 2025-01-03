
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


def cmp_to_key(comparator):
    """
    Helper method to convert a comparison function into
    a key function for python's list sort() method.
    This is useful to keep things on the up-and-up for Python 3
    where we still want to use the Comparator interface.
    """

    class CmpToKey():
        'Convert a cmp= function into a key= function'

        def __init__(self, obj):
            self.obj = obj

        def __lt__(self, other):
            return comparator.compare(self.obj, other.obj) < 0

        def __gt__(self, other):
            return comparator.compare(self.obj, other.obj) > 0

        def __eq__(self, other):
            return comparator.compare(self.obj, other.obj) == 0

        def __le__(self, other):
            return comparator.compare(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return comparator.compare(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return comparator.compare(self.obj, other.obj) != 0

    return CmpToKey
