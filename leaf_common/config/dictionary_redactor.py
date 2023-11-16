
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
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

from typing import Any
from typing import Dict
from typing import Sequence
from typing import Union
from copy import deepcopy


class DictionaryRedactor:
    """
    Class assisting with redacting sensitive properties
    in a dictionary or sequence data structure.
    """

    def __init__(self):
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

    def _is_sensitive(self, key: str) -> bool:
        """
        Detect if dictionary key is sensitive and should be redacted
        :param key: dictionary key
        :return: True if value for this key should be redacted;
                 False otherwise
        """
        lower_key: str = key.lower()
        for unsafe_key_fragment in self.unsafe_key_fragments:
            if lower_key.find(unsafe_key_fragment) >= 0:
                return True
        return False

    def redact(self,
               unsafe_tree: Union[Dict[str, Any], Sequence[Any]]) \
            -> Union[Dict[str, Any], Sequence[Any]]:
        """
        Redacts values of keys of a given dictionary or sequence

        :param unsafe_tree: The data structure to redact
        :return: A redacted deep copy of the unsafe structure where
                redacted keys have their values set to '<redacted>'.
        """
        safe_tree = deepcopy(unsafe_tree)
        self._redact_internal(safe_tree)
        return safe_tree

    def _redact_internal(
            self,
            safe_tree: Union[Dict[str, Any], Sequence[Any]]):
        """
        Redacts values of keys of a given dictionary or sequence

        :param safe_tree: The data structure to redact in-place
        :return: Nothing
        """
        if safe_tree is None:
            return
        if isinstance(safe_tree, list):
            for elem in safe_tree:
                self._redact_internal(elem)
            return
        if isinstance(safe_tree, dict):
            # Loop through all the keys
            keys = safe_tree.keys()
            for key in keys:
                if self._is_sensitive(key):
                    safe_tree[key] = "<redacted>"
                else:
                    self._redact_internal(safe_tree[key])
        return
