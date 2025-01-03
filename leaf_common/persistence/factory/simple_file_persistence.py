
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

import io
import os
import shutil

from leaf_common.persistence.interface.persistence import Persistence
from leaf_common.serialization.interface.serialization_format import SerializationFormat


class SimpleFilePersistence(Persistence):
    """
    Implementation of the leaf-common Persistence interface which
    saves/restores an object to a file using a SerializationFormat object.
    """

    def __init__(self, serialization_format: SerializationFormat):
        """
        Constructor.

        :param serialization_format: A means of serializing an object by way of a
                          SerializationFormat implementation
        """
        self.serialization_format = serialization_format

    def persist(self, obj: object, file_reference: str = None) -> str:
        """
        Persists the object passed in.

        :param obj: an object to persist
        :param file_reference: The file reference to use when persisting.
        """
        file_name = self.affix_file_extension(file_reference)

        with self.serialization_format.from_object(obj) as buffer_fileobj:
            writestyle = 'wb'
            if isinstance(buffer_fileobj, io.StringIO):
                writestyle = 'w'
            with open(file_name, writestyle) as dest_fileobj:
                shutil.copyfileobj(buffer_fileobj, dest_fileobj)

        return file_name

    def restore(self, file_reference: str = None) -> object:
        """
        :param file_reference: The file reference to use when restoring.
        :return: an object from some persisted store
        """
        file_name = self.affix_file_extension(file_reference)

        obj = None
        with io.BytesIO() as buffer_fileobj:

            with open(file_name, 'rb') as source_fileobj:
                shutil.copyfileobj(source_fileobj, buffer_fileobj)

            # Move pointer to beginning of buffer
            buffer_fileobj.seek(0, os.SEEK_SET)

            # Deserialize from stream
            obj = self.serialization_format.to_object(buffer_fileobj)

        return obj

    def get_file_extension(self) -> object:
        """
        :return: A string representing a file extension for the
                serialization method, including the ".",
                *or* a list of these strings that are considered valid
                file extensions.
        """
        return self.serialization_format.get_file_extension()

    def affix_file_extension(self, file_reference: str) -> str:
        """
        Affixes the SerializationFormat's file extension if it is not
        already on the file_reference

        :param file_reference: The file reference to use
        """
        if file_reference is None:
            raise ValueError("file_reference cannot be None")

        # Figure out the FileExtensionProvider to use
        extension = self.serialization_format.get_file_extension()

        # Add the file extension if necessary
        use_ref = file_reference
        if not file_reference.endswith(extension):
            use_ref = file_reference + extension

        return use_ref
