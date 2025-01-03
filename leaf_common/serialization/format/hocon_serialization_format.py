
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

import json

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

        pruned_dict = None
        if fileobj is not None:
            hocon_bytes = fileobj.getvalue()
            hocon_string = hocon_bytes.decode("utf-8")

            # Load the HOCON into a dictionary
            pruned_dict = ConfigFactory.parse_string(hocon_string)

            # Hocon tends to produce regular dictionaries that have
            # ConfigTree structures for nested dictionaries.
            # No one ever wants that, so have the result go through a json
            # encode/decode step before handing the dictionary back to save
            # the world the trouble of having to do it everywhere.
            if pruned_dict is not None:
                pruned_dict = json.loads(json.dumps(pruned_dict))

        obj = self.conversion_policy.convert_to_object(pruned_dict)
        return obj

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".hocon"
