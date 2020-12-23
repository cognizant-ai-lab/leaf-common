
# Copyright (C) 2019-2020 Cognizant Digital Business, Evolutionary AI.
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

from io import StringIO
from typing import TextIO

from leaf_common.serialization.interface.serialization_format import SerializationFormat
from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.serialization.rule_set_dictionary_converter \
    import RuleSetDictionaryConverter


class RuleSetSerializationFormat(SerializationFormat):
    """
    Class for serialization policy for RuleSets.
    """

    # Use a class variable to tell us whether or not we need to
    # do the registration of the numpy handlers
    registered = False

    def __init__(self, indent: int = 4, sort_keys: bool = True):
        """
        Constructor

        :param indent: indentation of serialization. Default is 4
        :param sort_keys: should dict keys be sorted for serialization. Default is True
        """
        self.indent = indent
        self.sort_keys = sort_keys

    def get_file_extension(self) -> str:
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".rules"

    def from_object(self, obj: RuleSet) -> TextIO:
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """
        converter = RuleSetDictionaryConverter()
        obj_dict = converter.to_dict(obj)

        json_string = json.dumps(obj_dict, indent=self.indent, sort_keys=self.sort_keys)
        fileobj = StringIO(json_string)
        return fileobj

    def to_object(self, fileobj: TextIO) -> RuleSet:
        """
        :param fileobj: The file-like object to deserialize.
                It is expected that the file-like object be open
                and be pointing at the beginning of the data
                (ala seek to the beginning).

                After calling this method, the seek pointer
                will be at the end of the data. Closing of the
                fileobj is left to the caller.
        :return: the deserialized object
        """
        json_string = fileobj.getvalue()
        obj_dict = json.loads(json_string)

        converter = RuleSetDictionaryConverter()
        obj = converter.from_dict(obj_dict)
        return obj
