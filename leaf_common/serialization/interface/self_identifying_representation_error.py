
# Copyright 2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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
See class comment for details
"""

from leaf_common.candidates.representation_types import RepresentationType


class SelfIdentifyingRepresentationError(ValueError):
    """
    Specific exception to raise when attempting to deserialize a stream
    via a Deserializer's to_object() call and the logic realizes that
    what is being deserialized is not of the correct RepresentationType.
    """

    def __init__(self, expected_representation_type: RepresentationType = None,
                 found_representation_type: RepresentationType = None,
                 message: str = None):
        """
        Constructor

        :param expected_representation_type: The RepresentationType that had
                been expected
        :param found_representation_type: The RepresentationType that had
                been found
        :param message: A string message which overrides the standard messaging
                provided by this class and its arguments
        """
        use_message = message
        if use_message is None:
            use_message = "Unexpected RepresentationType"
            if expected_representation_type is not None:
                use_message = "Expected RepresentationType {expected_representation_type.value}"
            if found_representation_type is not None:
                use_message = f"{use_message} found {found_representation_type.value}"
        super().__init__(use_message)
