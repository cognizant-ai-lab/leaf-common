
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

from leaf_common.serialization.interface.dictionary_converter \
    import DictionaryConverter


class EmptyDictionaryConverter(DictionaryConverter):
    """
    DictionaryConverter implementation which always converts to
    an empty dictionary for to_dict() and returns None for from_dict().
    """

    def to_dict(self, obj):
        """
        :param obj: The object to be converted into a dictionary
        :return: A data-only dictionary that represents all the data for
                the given object, either in primitives
                (booleans, ints, floats, strings), arrays, or dictionaries.
                If obj is None, then the returned dictionary should also be
                None.  If obj is not the correct type, it is also reasonable
                to return None.
        """
        empty_dict = {}
        return empty_dict

    def from_dict(self, obj_dict):
        """
        :param obj_dict: The data-only dictionary to be converted into an object
        :return: An object instance created from the given dictionary.
                If obj_dict is None, then the returned object should also be
                None.  If obj_dict is not the correct type, it is also reasonable
                to return None.
        """
        if obj_dict is None or \
                not isinstance(obj_dict, dict):
            return None

        return None
