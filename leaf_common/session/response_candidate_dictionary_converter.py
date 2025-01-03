
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
from typing import ClassVar
from typing import Dict

from leaf_common.serialization.interface.dictionary_converter \
    import DictionaryConverter
from leaf_common.session.extension_packaging import ExtensionPackaging


class ResponseCandidateDictionaryConverter(DictionaryConverter):
    """
    Interface for converting Candidate objects from a PopulationResponse
    back and forth to dictionaries.
    """

    def __init__(self, candidate_class: ClassVar,
                 string_encoding: str = 'UTF-8'):
        """
        Constructor
        :param string_encoding: The string encoding to use when encoding/
            decoding strings.
        """
        self.extension_packaging = ExtensionPackaging(string_encoding)
        self.candidate_class = candidate_class

    def to_dict(self, obj: object) -> Dict[str, object]:
        """
        :param obj: The object to be converted into a dictionary
        :return: A data-only dictionary that represents all the data for
                the given object, either in primitives
                (booleans, ints, floats, strings), arrays, or dictionaries.
                If obj is None, then the returned dictionary should also be
                None.  If obj is not the correct type, it is also reasonable
                to return None.
        """
        candidate = obj

        try:
            interpretation = self.extension_packaging.from_extension_bytes(
                                candidate.interpretation)
        except UnicodeDecodeError:
            # Allow pass through of bytes on failure here.
            # Some client code has to do more to decode interpretation bytes
            interpretation = candidate.interpretation

        metrics = self.extension_packaging.from_extension_bytes(
                                candidate.metrics)
        identity = self.extension_packaging.from_extension_bytes(
                                candidate.identity)
        candidate_dict = {
            "id": candidate.id,
            "interpretation": interpretation,
            "metrics": metrics,
            "identity": identity
        }
        return candidate_dict

    def from_dict(self, obj_dict: Dict[str, object]) -> object:
        """
        :param obj_dict: The data-only dictionary to be converted into an object
        :return: An object instance created from the given dictionary.
                If obj_dict is None, the returned object should also be None.
                If obj_dict is not the correct type, it is also reasonable
                to return None.
        """
        candidate_dict = obj_dict

        candidate = self.new_candidate()
        candidate.id = candidate_dict.get('id', None)
        candidate.interpretation = \
            self.extension_packaging.to_extension_bytes(
                        candidate_dict.get('interpretation', None))
        candidate.metrics = \
            self.extension_packaging.to_extension_bytes(
                        candidate_dict.get('metrics', None))
        candidate.identity = \
            self.extension_packaging.to_extension_bytes(
                        candidate_dict.get('identity', None))
        return candidate

    def new_candidate(self):
        """
        Creates a new candidate structure per the candidate class
        pass in via the constructor
        :return: A new Candidate instance
        """
        candidate = self.candidate_class()
        return candidate
