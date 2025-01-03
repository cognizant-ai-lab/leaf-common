
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

from leaf_common.persistence.interface.persistor import Persistor
from leaf_common.persistence.interface.restorer import Restorer
from leaf_common.serialization.interface.file_extension_provider import FileExtensionProvider


class Persistence(Persistor, Restorer, FileExtensionProvider):
    """
    Interface which allows multiple mechanisms of persistence for an object.
    How and where entities are persisted are left as implementation details.
    """

    def persist(self, obj: object, file_reference: str = None) -> object:
        """
        Persists the object passed in.

        :param obj: an object to persist
        :param file_reference: The file reference to use when persisting.
                Default is None, implying the file reference is up to the
                implementation.
        :return an object describing the location to which the object was persisted
        """
        raise NotImplementedError

    def restore(self, file_reference: str = None):
        """
        :param file_reference: The file reference to use when restoring.
                Default is None, implying the file reference is up to the
                implementation.
        :return: an object from some persisted store
        """
        raise NotImplementedError

    def get_file_extension(self) -> object:
        """
        :return: A string representing a file extension for the
                serialization method, including the ".",
                *or* a list of these strings that are considered valid
                file extensions.
        """
        raise NotImplementedError
