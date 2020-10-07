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
    RuleBased = 'RuleBased'

    # Evolved dictionary representation.
    Structure = 'Structure'
