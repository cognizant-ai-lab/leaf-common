
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


class GrpcMetadataUtil():
    """
    Utility class that converts various structures like dictionaries and lists
    to/from the tuple format that grpc expects.
    """

    @classmethod
    def to_tuples(cls, metadata):
        """
        Converts the metadata into the tuple-of-tuples form GRPC can digest.
        :param metadata: Can be None, a single tuple, a tuple of tuples
                a list of tuples, a list of lists, a dictionary.
        :return: the same metadata in tuple-of-tuple form
        """

        # No means no
        if metadata is None:
            return None

        # Don't know how to convert anything that's not a dict, list or tuple
        if not isinstance(metadata, dict) and \
           not isinstance(metadata, list) and \
           not isinstance(metadata, tuple):
            return None

        # Empty structures we support means we don't send metadata
        if not any(metadata):
            return None

        # Start out by assuming the metadata is in the form we want
        use_metadata = metadata

        # In the dictionary case, convert the key/value pairs to
        # the list-of-lists form.
        if isinstance(metadata, dict):
            use_metadata = list(metadata.items())

        # If the first element of the list/tuple is a scalar,
        # make a list out of it to be in a canonical form
        first = use_metadata[0]
        if not isinstance(first, list) and \
           not isinstance(first, tuple):
            use_metadata = [use_metadata]

        # Convert individual elements to tuples
        elements_to_convert = list(use_metadata)
        converted_elements = []
        for element in elements_to_convert:
            converted_element = tuple(element)
            converted_elements.append(converted_element)

        # Convert list to tuples
        converted = tuple(converted_elements)

        return converted

    @classmethod
    def to_dict(cls, metadata):
        """
        Converts the metadata tuples into a dictionary more palettable to
        python manipulation.

        :param metadata: the tuple-d metadata
        :return: A dictionary of key/value pairs corresponding to the metadata
        """

        metadata_dict = {}
        if metadata is None:
            return metadata_dict

        if isinstance(metadata, dict):
            return metadata

        metadata_list = metadata
        if isinstance(metadata, tuple):
            metadata_list = list(metadata)

        for element in metadata_list:
            key = element[0]
            value = element[1]
            metadata_dict[key] = value

        return metadata_dict
