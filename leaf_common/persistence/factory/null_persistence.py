
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

from leaf_common.persistence.interface.persistence \
    import Persistence


class NullPersistence(Persistence):
    """
    Null implementation of the Persistence interface.
    """

    def persist(self, obj, file_reference: str = None):
        """
        Persists object passed in.

        :param obj: an object to be persisted
        :param file_reference: Ignored
        """

    def restore(self, file_reference: str = None):
        """
        :param file_reference: Ignored
        :return: a restored instance of a previously persisted object
        """
        return None

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".",
                *or* a list of these strings that are considered valid
                file extensions.
        """
        return ""
