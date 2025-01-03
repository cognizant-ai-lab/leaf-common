
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

import io
import json
import os

from leaf_common.serialization.interface.serialization_format \
    import SerializationFormat

from leaf_common.serialization.format.conversion_policy \
    import ConversionPolicy


class JsonSerializationFormat(SerializationFormat):
    """
    An implementation of the Serialization interface which provides
    JSON Serializer and a Deserializer implementations under one roof.
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
        self.conversion_policy = ConversionPolicy(
            reference_pruner=reference_pruner,
            dictionary_converter=dictionary_converter,
            pretty=pretty)

    def from_object(self, obj):
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """

        pruned_dict = self.conversion_policy.convert_from_object(obj)

        # See if JSON should be pretty or not
        indent = None
        sort_keys = False
        if self.conversion_policy.is_pretty():
            indent = 4
            sort_keys = True

        # Now convert the pruned dictionary to JSON
        json_str = json.dumps(pruned_dict, indent=indent, sort_keys=sort_keys)

        # Make a file-like object out of the JSON string
        byte_array = bytearray(json_str, 'utf-8')
        fileobj = io.BytesIO(byte_array)
        fileobj.seek(0, os.SEEK_SET)

        return fileobj

    def to_object(self, fileobj):
        """
        :param fileobj: The file-like object to deserialize.
                It is expected that the file-like object be open and be
                pointing at the beginning of the data (ala seek to the
                beginning).

                After calling this method, the seek pointer will be at the end
                of the data. Closing of the fileobj is left to the caller.
        :return: the deserialized object
        """

        pruned_dict = None
        if fileobj is not None:
            # Load the JSON into a dictionary
            pruned_dict = json.load(fileobj)

        obj = self.conversion_policy.convert_to_object(pruned_dict)
        return obj

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".json"
