"""
See class comment for details.
"""

import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy

from io import StringIO
from typing import TextIO

from leaf_common.serialization.interface.serialization_format import SerializationFormat
from leaf_common.representation.rule_based.rules_agent import RulesAgent


class RulesAgentSerializationFormat(SerializationFormat):
    """
    Class for serialization policy for RulesAgents.
    """

    # Use a class variable to tell us whether or not we need to
    # do the registration of the numpy handlers
    registered = False

    def __init__(self):
        """
        Constructor.

        Doesn't do much except do the registration of the jsonpickle business.
        """
        if not self.registered:
            self.registered = True
            jsonpickle_numpy.register_handlers()

    def get_file_extension(self) -> str:
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".rules"

    def from_object(self, obj: RulesAgent) -> TextIO:
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """
        json_string = jsonpickle.encode(obj, keys=True)
        fileobj = StringIO(json_string)
        return fileobj

    def to_object(self, fileobj: TextIO) -> RulesAgent:
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
        obj = jsonpickle.decode(json_string, keys=True)
        return obj
