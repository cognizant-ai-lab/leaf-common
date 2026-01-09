
# Copyright © 2019-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
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
