
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

from leaf_common.session.extension_packaging import ExtensionPackaging
from leaf_common.session.response_candidate_dictionary_converter \
    import ResponseCandidateDictionaryConverter
from leaf_common.serialization.interface.dictionary_converter \
    import DictionaryConverter


class PopulationResponseDictionaryConverter(DictionaryConverter):
    """
    A DictionaryConverter implementation to assist in packaging up
    PopulationResponses suitable for protocol
    buffers transmission to/from an idiomatic python dictionary form.
    """

    def __init__(self, population_response_class: ClassVar,
                 candidate_class: ClassVar = None,
                 candidate_converter: DictionaryConverter = None,
                 string_encoding: str = 'UTF-8'):
        """
        Constructor

        :param population_response_class: The grpc class for the
            PopulationResponse
        :param candidate_class: The grpc class for the Candidate
                    Can be None if a candidate_converter is passed in.
        :param candidate_converter: A DictionaryConverter that knows how
                    to convert between
        :param string_encoding: The string encoding to use when encoding/
            decoding strings.
        """
        self.population_response_class = population_response_class
        self.candidate_converter = candidate_converter
        if candidate_converter is None:
            self.candidate_converter = ResponseCandidateDictionaryConverter(
                                                        candidate_class)
        self.extension_packaging = ExtensionPackaging(string_encoding)

    def from_dict(self, obj_dict: Dict[str, object]) -> object:
        """
        Convert a Population Response in python idiomatic dictionary form
        into a gRPC PopulationRequest structure suitable for transmission
        over the wire.
        :param obj_dict: a dictionary set up to look like a
            PopulationResponse structure
        :return: a PopulationResponse structure populated according to the
            fields of the response_dictionary
        """
        return self.from_dict_with_checkpoint(obj_dict, default_checkpoint=None)

    def from_dict_with_checkpoint(self, obj_dict, default_checkpoint=None):
        """
        Convert a Population Response in python idiomatic dictionary form
        into a gRPC PopulationRequest structure suitable for transmission
        over the wire.
        :param obj_dict: a dictionary set up to look like a
            PopulationResponse structure
        :param default_checkpoint: when None, returning of None is allowed
            as an entire response is allowed from from_dict().
        :return: a PopulationResponse structure populated according to the
            fields of the response_dictionary
        """
        use_response_dict = obj_dict
        if obj_dict is None or \
                not isinstance(obj_dict, dict) or \
                len(obj_dict.keys()) == 0:

            if default_checkpoint is None:
                return None

            use_response_dict = {}

        # Always return some struct, but *not* None.
        # GRPC server infrastructure can't deal with None.
        population_response = self.population_response_class()
        population_response.generation_count = \
            use_response_dict.get('generation_count', -1)
        population_response.checkpoint_id = \
            use_response_dict.get('checkpoint_id', default_checkpoint)

        evaluation_stats = \
            use_response_dict.get('evaluation_stats', None)
        evaluation_stats_bytes = \
            self.extension_packaging.to_extension_bytes(evaluation_stats)
        population_response.evaluation_stats = evaluation_stats_bytes

        population = None
        dict_population = use_response_dict.get('population', None)
        if dict_population is not None and isinstance(dict_population, list):
            population = []
            for candidate_dict in dict_population:
                candidate = self.candidate_converter.from_dict(candidate_dict)
                population.append(candidate)

        if population is not None and len(population) > 0:
            # pylint-protobuf somehow doesn't pick up the extend() method of a
            # repeated field.
            # See: https://developers.google.com/protocol-buffers/docs/
            #               reference/python-generated?csw=1#fields
            population_response.population.extend(population)

        return population_response

    def to_dict(self, obj: object) -> Dict[str, object]:
        """
        Convert a Population Response to its python idiomatic dictionary form

        :param obj: a PopulationResponse structure handed
            over the wire
        :return: a dictionary set up to look like a PopulationResponse structure
            but all in dictionary form for internal pythonic consumption
            without regard to grpc as a communication mechanism
        """
        population_response = obj

        if population_response is None or \
            not isinstance(population_response,
                           self.population_response_class):
            return None

        population = []
        for candidate in population_response.population:
            candidate_dict = self.candidate_converter.to_dict(candidate)
            population.append(candidate_dict)

        evaluation_stats = \
            self.extension_packaging.from_extension_bytes(
                population_response.evaluation_stats)

        # Check for an empty PopulationResponse message
        if evaluation_stats is None and \
                len(population) == 0 and \
                population_response.generation_count == 0 and \
                len(population_response.checkpoint_id) == 0:
            return None

        if len(population) == 0:
            population = None

        obj = {
            "population": population,
            "generation_count": population_response.generation_count,
            "checkpoint_id": population_response.checkpoint_id,
            "evaluation_stats": evaluation_stats
        }

        return obj
