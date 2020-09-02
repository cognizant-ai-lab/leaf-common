
# Copyright (C) 2019-2020 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# ENN-release SDK Software in commercial settings.
#
# END COPYRIGHT

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

    def __init__(self, file_name: str, serialization_format: SerializationFormat):
        """
        Constructor.

        :param file_name: The file name to save to/restore from
        :param serialization_format: A means of serializing an object by way of a
                          SerializationFormat implementation
        """
        self.file_name = file_name
        self.serialization_format = serialization_format

    def persist(self, obj: object) -> None:
        """
        Persists the object passed in.

        :param obj: an object to persist
        """
        with self.serialization_format.from_object(obj) as buffer_fileobj:
            with open(self.file_name, 'w') as dest_fileobj:
                shutil.copyfileobj(buffer_fileobj, dest_fileobj)

    def restore(self) -> object:
        """
        :return: an object from some persisted store
        """
        obj = None
        with io.BytesIO() as buffer_fileobj:

            with open(self.file_name, 'r') as source_fileobj:
                shutil.copyfileobj(source_fileobj, buffer_fileobj)

            # Move pointer to beginning of buffer
            buffer_fileobj.seek(0, os.SEEK_SET)

            # Deserialize from stream
            obj = self.serialization_format.to_object(buffer_fileobj)

        return obj
