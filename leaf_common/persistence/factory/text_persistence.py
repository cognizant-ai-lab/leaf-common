
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

from leaf_common.persistence.factory.abstract_persistence \
    import AbstractPersistence
from leaf_common.serialization.format.text_serialization_format \
    import TextSerializationFormat


class TextPersistence(AbstractPersistence):
    """
    Implementation of the AbstractPersistence class which
    saves text data of an object via some persistence mechanism.
    """

    def __init__(self, persistence_mechanism, use_file_extension=None):
        """
        Constructor

        :param persistence_mechanism: the PersistenceMechanism to use
                for storage
        :param use_file_extension: Use the provided string instead of the
                standard file extension for the format. Default is None,
                indicating the standard file extension for the format should
                be used.
        """

        super().__init__(persistence_mechanism,
                         use_file_extension=use_file_extension)
        self._serialization = TextSerializationFormat(
            must_exist=persistence_mechanism.must_exist())

    def get_serialization_format(self):
        return self._serialization

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".",
                *or* a list of these strings that are considered valid
                file extensions.
        """
        return self._serialization.get_file_extension()
