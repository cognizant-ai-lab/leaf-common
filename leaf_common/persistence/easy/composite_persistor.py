
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

from typing import List

from leaf_common.persistence.interface.persistor import Persistor


class CompositePersistor(Persistor):
    """
    This implementation of the Persistor interface allows multiple
    ways for the same data to be persist()-ed in an abstract manner.
    """

    def __init__(self, persistors: List[Persistor] = None):
        """
        Constructor.

        :param persistor: an initial list of Persistors to start with.
                    Default is None.
        """
        self._persistors: List[Persistor] = persistors
        if persistors is None:
            self._persistors = []

    def persist(self, obj: object, file_reference: str = None):
        """
        Persists the object passed in.

        :param file_reference: If None (the default), this arg is ignored,
            and the file(s) to save are determined by each individual Persistor.
            If not None, the arg is passed to each individual Persistor.
        """

        for persistor in self._persistors:
            # DEF: Should we do anything automatically here with file suffixes?
            persistor.persist(obj, file_reference)

    def add_persistor(self, persistor: Persistor):
        """
        :param persistor: The Persistor implementation to be added to the list
        """
        if persistor is not None:
            self._persistors.append(persistor)
