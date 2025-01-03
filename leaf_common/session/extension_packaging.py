
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
import json
import sys


class ExtensionPackaging():
    """
    Class to assist in packaging up byte extensions suitable for protocol
    buffers transmission in a bytes field.  In such transmissions we use
    no python-specific data (like pickle or direct bytes of classes) to keep
    in the spirit of protobuf's language agnosticism going over the wire.
    """

    def __init__(self, string_encoding='UTF-8'):
        """
        Constructor
        :param string_encoding: The string encoding to use when encoding/
            decoding strings.
        """
        self.string_encoding = string_encoding

        # Protobuf 3 has no concept of None. Instead we set to
        # the default value of a bytes field which is the value below.
        _b = sys.version_info[0] < 3 and (lambda x: x) or (lambda x: x.encode('latin1'))
        self.none_bytes = _b("")

    def to_extension_bytes(self, obj):
        """
        Converts an object to extension bytes suitable for protocol buffers
        bytes field.  Just how this is converted depends on the type of the
        object. Supports:

        * None values
        * dictionaries - converted to JSON strings first. Uses string_encoding
        * strings - converted to their bytes. Uses string_encoding
        * bytes - passed through as raw data

        :param obj: the object to convert
        :return: a bytes object suitable for assignment in a
                    protobuf bytes filed
        """

        extension_bytes = self.none_bytes
        if obj is None:
            return extension_bytes

        use_obj = obj
        if isinstance(use_obj, dict):
            # For now just do JSON for the sake of language compatibility
            # XXX Might allow other format conversion in future
            use_obj = json.dumps(use_obj)

        if isinstance(use_obj, str):
            use_obj = bytearray(use_obj, self.string_encoding)

        if isinstance(use_obj, bytearray):
            use_obj = bytes(use_obj)

        if isinstance(use_obj, bytes):
            extension_bytes = use_obj

        return extension_bytes

    def from_extension_bytes(self, extension_bytes, out_type=dict):
        """
        Converts extension bytes from a protocol buffers bytes field to
        the desired out_type. Supports

        * None values
        * bytes - passed through as raw data
        * strings - converted from their bytes. Uses string_encoding
        * dictionaries - converted from JSON strings first. Uses string_encoding

        :param extension_bytes: the bytes to convert
        :param out_type: the type to convert the bytes to.
                By default this is a python dictionary
        :return: the object type desired, or None if the extension_bytes was empty
        """

        if extension_bytes is None or \
           extension_bytes == self.none_bytes:
            return None

        obj = extension_bytes
        if out_type == bytes:
            # Just return the raw bytes
            return obj

        if out_type == str or out_type == dict:
            # We want some string encoded data
            obj = extension_bytes.decode(self.string_encoding)
            if obj is None:
                # Could not decode
                return obj

            if out_type == str:
                # Wanted a string
                return obj

            # Try to detect the object encoding
            stripped = obj.strip()
            if stripped.startswith("{"):
                # JSON
                obj = json.loads(stripped)
            else:
                # XXX Might allow other format conversion in future
                # We don't know how to decode, just return the raw bytes
                obj = extension_bytes

        return obj
