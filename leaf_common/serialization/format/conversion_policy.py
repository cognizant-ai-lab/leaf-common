
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


class ConversionPolicy():
    """
    Common code for passing an object through a ReferencePruner and
    DictionaryConverter.
    """

    def __init__(self, reference_pruner=None, dictionary_converter=None,
                 pretty=True):
        """
        Constructor.

        :param reference_pruner: A ReferencePruner implementation
                that knows how to prune/graft repeated references
                throughout the object hierarchy
        :param dictionary_converter: A DictionaryConverter implementation
                that knows how to convert from a dictionary to the object type
                in question.
        :param pretty: a boolean which says whether the output is to be
                nicely formatted or not.  Try for: indent=4, sort_keys=True
        """
        self._reference_pruner = reference_pruner
        self._dictionary_converter = dictionary_converter
        self._pretty = pretty

    def is_pretty(self):
        """
        :return: Whether or not the output should be pretty
        """
        return self._pretty

    def convert_from_object(self, obj):
        """
        :param obj: The object to convert into a pruned dictionary
        :return: a pruned dictionary representation of the object
        """

        # Prune the object of duplicate references
        pruned_obj = obj
        if self._reference_pruner is not None:
            pruned_obj = self._reference_pruner.prune(obj)

        pruned_dict = None
        if self._dictionary_converter is not None:
            pruned_dict = self._dictionary_converter.to_dict(pruned_obj)
        elif isinstance(pruned_obj, dict):
            pruned_dict = pruned_obj
        else:
            pruned_dict = pruned_obj.__dict__

        return pruned_dict

    def convert_to_object(self, pruned_dict):
        """
        :param pruned_dict: The pruned dictionary that is to
                be converted back into the object.
                Can be None.
        :return: the deserialized object
        """

        # Assume the input is a pruned dictionary. Convert it back to an object
        pruned_obj = None
        if self._dictionary_converter is not None:
            pruned_obj = self._dictionary_converter.from_dict(pruned_dict)
        else:
            # No DictionaryConverter
            pruned_obj = pruned_dict

        # Graft duplicate references back onto the object
        obj = pruned_obj
        if self._reference_pruner is not None:
            obj = self._reference_pruner.graft(pruned_obj)

        return obj
