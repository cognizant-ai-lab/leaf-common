"""
This module is responsible for handling model representation types and associated services and transformations.
"""

from enum import Enum


# Inherit from 'str' so JSON serialization happens for free. See: https://stackoverflow.com/a/51976841
class RepresentationType(str, Enum):
    """
    Encapsulates the various model representation types supported by ESP.
    """

    # The bytes of a Keras neural network hd5 file.
    KerasNN = 'KerasNN'

    # The weights for a neural network as a Numpy array.
    NNWeights = 'NNWeights'

    # The rule set representation.
    RuleBased = 'Rules'

    @staticmethod
    def get_representation(experiment_params):
        """
        Given a set of experiment_params, inspects those params to determine the model representation fornmat
        :param experiment_params: A set of experiment parameters in JSON format.
        :return: The element of this enum corresponding to the inferred representation type.
        """
        leaf_representation = RepresentationType.KerasNN
        leaf_params = experiment_params.get("LEAF", None) if experiment_params else None
        if leaf_params:
            # Default to KerasNN representation if not otherwise specified.
            representation_type_as_string = leaf_params.get("representation", RepresentationType.KerasNN.value)
            try:
                leaf_representation = RepresentationType[representation_type_as_string]
            except KeyError:
                raise ValueError('Invalid representation type: "{}"'.format(representation_type_as_string))
        return leaf_representation
