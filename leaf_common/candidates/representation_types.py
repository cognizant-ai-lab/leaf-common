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

    @staticmethod
    def get_file_type_for_representation(representation: 'RepresentationType') -> str:
        """
        Determines which file type (extension) to use for a given representation
        :param representation: Representation of candidates, chosen from this enum itself
        :return: A string indicating which file extension to use
        """
        if representation == RepresentationType.KerasNN:
            file_type = 'hd5'
        elif representation == RepresentationType.NNWeights:
            file_type = 'pickle'
        elif representation == RepresentationType.RuleBased:
            file_type = 'json_txt'
        else:
            file_type = None

        return file_type

    @staticmethod
    def is_valid_file_type(file_name: str, representation: 'RepresentationType'):
        """
        Determines whether the supplied filename is valid, that is, whether it is consistent with the supplied
        candidate representation type.
        :param file_name:
        :param representation:
        :return:
        """
        is_valid_keras_nn_file = representation == RepresentationType.KerasNN and file_name.endswith('.hd5')
        is_valid_weights_nn_file = representation == RepresentationType.NNWeights and file_name.endswith('.pickle')
        is_valid_rule_set_file = representation == RepresentationType.RuleBased and file_name.endswith('.json_txt')
        return is_valid_keras_nn_file or is_valid_weights_nn_file or is_valid_rule_set_file
