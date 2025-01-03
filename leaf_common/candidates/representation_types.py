
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
This module is responsible for handling model representation types and associated services and transformations.
"""

from enum import Enum


# Inherit from 'str' so JSON serialization happens for free. See: https://stackoverflow.com/a/51976841
class RepresentationType(str, Enum):
    """
    Encapsulates the various model representation types supported by ESP.
    """

    # pylint: disable=invalid-name
    # The bytes of a Keras neural network hd5 file.
    KerasNN = 'KerasNN'

    # The weights for a neural network as a Numpy array.
    NNWeights = 'NNWeights'

    # The rule set representation.
    RuleBased = 'RuleBased'

    # Evolved dictionary representation.
    Structure = 'Structure'
