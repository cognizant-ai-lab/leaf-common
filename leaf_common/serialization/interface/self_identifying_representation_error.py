
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
