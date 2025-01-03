
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
from typing import List

from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.serialization.interface.file_extension_provider \
    import FileExtensionProvider


class RepresentationFileExtensionProviderRegistry():
    """
    Registry class which returns a leaf-common FileExtensionProvider class
    for given RepresentationType(s).

    This is not to be used directly, but instead is an abstract basis
    For RepresentationPersistenceRegistry and
    RepresentationSerializationFormatRegistry.
    """

    def __init__(self):
        """
        Constructor.
        """

        # Initialize the maps

        # _type_map is a straightforward mapping of RepresentationType (string) to
        # FileExtensionProvider implementation for that guy.
        self._type_map = {}

        # _extention_map is less straightforward, as multiple RepresentationTypes
        # can conceivably use the same file type (like JSON), so its keys are
        # extension strings and its values are lists of FileExtensionProvider implementations
        self._extension_map = {}

    def get_for_representation_type(self, rep_type: RepresentationType) -> FileExtensionProvider:
        """
        Given a RepresentationType, return its register()-ed FileExtensionProvider
        implementation.

        :param rep_type: A RepresentationType to look up
        :return: A FileExtensionProvider implementation corresponding to the rep_type
        """

        file_extension_provider = self._type_map.get(rep_type, None)

        if file_extension_provider is None:
            raise ValueError(f"Unknown representation_type: {rep_type}")

        return file_extension_provider

    def representation_types_from_filename(self, filename: str) -> List[RepresentationType]:
        """
        Given a filename, return a list of potential register()-ed RepresentationTypes

        Note that this implementation does not actually open the file
        to examine any self-identifying aspects of the contents, and as
        a single file type (like JSON) has the potential to contain a
        number of different possibilities, this method returns a list
        if it finds anything.

        :param filename: A string filename whose file extension is used as a key for look up
        :return: A list of potential RepresentationTypes corresponding to the filename
                 or None if no representation types are found for the filename
        """

        provider_list = self.lookup_from_filename(filename)
        if provider_list is None:
            return None

        representation_types = []
        for representation_type, value in self._type_map.items():

            if value in provider_list:
                representation_types.append(representation_type)

        # Be sure Structure is the last thing for clients to try,
        # as it has no self-identification in its contents.
        if RepresentationType.Structure in representation_types:
            representation_types.remove(RepresentationType.Structure)
            representation_types.append(RepresentationType.Structure)

        return representation_types

    def lookup_from_filename(self, filename: str) -> List[FileExtensionProvider]:
        """
        Given a filename, return a list of potential register()-ed FileExtensionProvider
        implementations.

        Note that this implementation does not actually open the file
        to examine any self-identifying aspects of the contents, and as
        a single file type (like JSON) has the potential to contain a
        number of different possibilities, this method returns a list
        if it finds anything.

        :param filename: A string filename whose file extension is used as a key for look up
        :return: A list of potential FileExtensionProvider implementations corresponding to the filename
                 or None if no FileExtensionProvider implementations are found for the filename
        """

        provider_list = None
        found_key = None

        for key, value in self._extension_map.items():

            use_key: bool = filename is not None and filename.endswith(key)
            if use_key:
                # Use the longest match of the file extension keys
                # Assume this means more specific
                if found_key is not None and len(key) < len(found_key):
                    use_key = False

            if use_key:
                found_key = key
                provider_list = value

        return provider_list

    def register(self, rep_type: RepresentationType,
                 file_extension_provider: FileExtensionProvider):
        """
        Register a FileExtensionProvider implementation for a RepresentationType

        :param rep_type: A RepresentationType to use as a key
        :param file_extension_provider: A FileExtensionProvider implementation to use as a value
        """
        self._type_map[rep_type] = file_extension_provider

        # Allow for the return of potentially multiple file extensions.
        # This handles the cases of Persistence implementations that
        # can do JSON, YAML, etc out of the same dictionary.
        provider_extensions = file_extension_provider.get_file_extension()
        if isinstance(provider_extensions, str):
            provider_extensions = [provider_extensions]

        for provider_extension in provider_extensions:
            extension_list = self._extension_map.get(provider_extension, None)
            if extension_list is None:
                extension_list = []
                self._extension_map[provider_extension] = extension_list

            extension_list.append(file_extension_provider)
