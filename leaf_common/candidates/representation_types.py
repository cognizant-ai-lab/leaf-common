
# Copyright © 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
