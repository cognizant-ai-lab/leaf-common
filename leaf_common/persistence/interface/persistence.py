
# Copyright © 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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
