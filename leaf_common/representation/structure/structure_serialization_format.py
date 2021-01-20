
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
See class comment.
"""
import json

from io import StringIO
from typing import Dict
from typing import TextIO

from leaf_common.serialization.interface.serialization_format import SerializationFormat


class StructureSerializationFormat(SerializationFormat):
    """
    Class for serialization policy for Structures (dictionaries).
    """
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
        return ".json"

    def from_object(self, obj: Dict[str, object]) -> TextIO:
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """
        json_string = json.dumps(obj, indent=self.indent, sort_keys=self.sort_keys)
        fileobj = StringIO(json_string)
        return fileobj

    def to_object(self, fileobj: TextIO) -> Dict[str, object]:
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
        obj = json.loads(json_string)
        return obj
