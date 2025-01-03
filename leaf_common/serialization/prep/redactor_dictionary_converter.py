
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
from typing import Dict
from typing import List

from leaf_common.serialization.interface.dictionary_converter \
    import DictionaryConverter


class RedactorDictionaryConverter(DictionaryConverter):
    """
    DictionaryConverter implementation that converts dictionaries themselves
    redacting values of keys with sensitive keywords in them.
    """

    def __init__(self,
                 redacted_value="<redacted>",
                 unsafe_key_fragments: List[str] = None):
        """
        Constructor

        :param redacted_value: The filtered value for any key having a fragment
                    in the unsafe_key_fragments list. Default is "<redacted>".
        :param unsafe_key_fragments: A List of lowercase strings indicating a
                    key fragments for redaction. Default is None
                    implying a default list.
        """
        self.redacted_value = redacted_value

        self.unsafe_key_fragments = unsafe_key_fragments
        if self.unsafe_key_fragments is None:
            self.unsafe_key_fragments = [
                'account',
                'auth',
                'credentials',
                'key',
                'pass',
                'secret',
                'token',
                'user'
            ]

    def to_dict(self, obj: object) -> Dict[str, object]:
        """
        :param obj: The object to be converted into a dictionary
                This is expected to be a dictionary itself
        :return: A data-only dictionary that represents all the data for
                the given object, either in primitives
                (booleans, ints, floats, strings), arrays, or dictionaries.
                If obj is None, then the returned dictionary should also be
                None.  If obj is not the correct type, it is also reasonable
                to return None.
        """
        if obj is None or \
                not isinstance(obj, dict):
            return None

        obj_dict = self.redact_dict(obj)
        return obj_dict

    def from_dict(self, obj_dict: Dict[str, object]) -> object:
        """
        :param obj_dict: The data-only dictionary to be converted into an object
        :return: An object instance created from the given dictionary.
                If obj_dict is None, the returned object should also be None.
                If obj_dict is not the correct type, it is also reasonable
                to return None.
        """
        return obj_dict

    def redact_dict(self, unsafe_dict: Dict[str, object]) -> Dict[str, object]:
        """
        Does the secret filtering operation for a single layer of
        dictionary keys.  Will recurse if dictionary or list values found.

        :param unsafe_dict: The dictionary to filter secrets on
        :return: The redacted dictionary
        """

        safe_dict = {}

        # Loop through all the keys
        for key, value in unsafe_dict.items():
            safe_value = self.redact_value(key, value)
            safe_dict[key] = safe_value

        return safe_dict

    def redact_list(self, unsafe_list: List[object]) -> List[object]:
        """
        Does the secret filtering operation for a list.
        No immediate components are redacted, but this method recurses
        for safety of component lists and/or dictionaries.

        :param unsafe_list: The list to filter secrets on
        :return: The redacted list
        """

        key = None
        safe_list = []
        for component in unsafe_list:

            redacted_component = self.redact_value(key, component)
            safe_list.append(redacted_component)

        return safe_list

    def redact_scalar(self, key: str, unsafe_value: object) -> object:
        """
        Might redact a value to the "redacted_value" passed in the constructor
        based on contents of the given key.

        :param key: The string key which cues for redaction.
                    If None, then no redaction happens (used in list components).
                    Otherwise, the key is inspected for unsafe key fragments
        :param value: The original unsafe value for potential redaction
        :return: The safe value, redacted or not, depending on the key
        """

        safe_value = unsafe_value

        # Only redact keys that are not None
        if key is not None:
            lower_key = key.lower()

            # If the key name contains something sensitive,
            # redact it for output.
            for unsafe_key_fragment in self.unsafe_key_fragments:
                if lower_key.find(unsafe_key_fragment) >= 0:
                    safe_value = self.redacted_value
                    break

        return safe_value

    def redact_value(self, key: str, unsafe_value: object) -> object:
        """
        Might redact a value to the "redacted_value" passed in the constructor
        based on contents of the given key.

        :param key: The string key which cues for redaction.
                    If None, then no redaction happens (used in list components).
                    Otherwise, the key is inspected for unsafe key fragments
        :param value: The original unsafe value for potential redaction
        :return: The safe value, redacted or not, depending on the key
        """

        safe_value = None

        if isinstance(unsafe_value, dict):
            safe_value = self.redact_dict(unsafe_value)
        elif isinstance(unsafe_value, list):
            safe_value = self.redact_list(unsafe_value)
        else:
            safe_value = self.redact_scalar(key, unsafe_value)

        return safe_value
