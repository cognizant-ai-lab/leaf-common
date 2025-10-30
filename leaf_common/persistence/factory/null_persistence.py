
# Copyright 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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
