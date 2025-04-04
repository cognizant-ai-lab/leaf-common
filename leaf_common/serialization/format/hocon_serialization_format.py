
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

from collections import OrderedDict
from typing import Dict

from pyhocon import ConfigFactory

from leaf_common.serialization.format.json_serialization_format \
    import JsonSerializationFormat


class HoconSerializationFormat(JsonSerializationFormat):
    """
    An implementation of the Serialization interface which provides
    Hocon Serializer and a Deserializer implementations under one roof.
    With this class, hocon serialization (from_object) is just JSON.
    """

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

        def ordered_dict_to_dict(obj: OrderedDict) -> Dict:
            """Recursively converts an OrderedDict (or dict) to a regular dict."""
            if isinstance(obj, OrderedDict):  # Handle both dict and OrderedDict
                return {k: ordered_dict_to_dict(v) for k, v in obj.items()}
            if isinstance(obj, list):  # Handle lists of OrderedDicts/dicts
                return [ordered_dict_to_dict(item) for item in obj]

            return obj

        pruned_dict = None
        if fileobj is not None:
            hocon_bytes = fileobj.getvalue()
            hocon_string = hocon_bytes.decode("utf-8")

            # Load the HOCON into a dictionary
            pruned_dict = ConfigFactory.parse_string(hocon_string)

            # Hocon tends to produce regular dictionaries that have
            # ConfigTree structures for nested dictionaries.
            # Use as_plain_ordered_dict to convert ConfigTree to OrderedDict.
            # This method also sanitize keys with forbidden characters,
            # such as ".", ":", "$", "@", "#", "!", "?", "=", "+", and white spaces,
            # then recursively convert to dictionary.
            if pruned_dict is not None:
                pruned_dict = ordered_dict_to_dict(pruned_dict.as_plain_ordered_dict())

        obj = self.conversion_policy.convert_to_object(pruned_dict)
        return obj

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".hocon"
