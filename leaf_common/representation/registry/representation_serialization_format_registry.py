
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
See class comment for details.
"""
from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.serialization.interface.serialization_format import SerializationFormat
from leaf_common.serialization.format.json_serialization_format import JsonSerializationFormat

from leaf_common.representation.registry.representation_file_extension_provider_registry \
    import RepresentationFileExtensionProviderRegistry
from leaf_common.representation.rule_based.serialization.rule_set_serialization_format \
    import RuleSetSerializationFormat


class RepresentationSerializationFormatRegistry(RepresentationFileExtensionProviderRegistry):
    """
    Registry class which returns a leaf-common SerializationFormat class
    for the RepresentationType
    """

    def __init__(self):
        """
        Constructor.
        """

        super().__init__()

        # Do some simple registrations
        self.register(RepresentationType.Structure, JsonSerializationFormat())
        self.register(RepresentationType.RuleBased, RuleSetSerializationFormat())

    def register(self, rep_type: RepresentationType, file_extension_provider: SerializationFormat):
        """
        Register a SerializationFormat implementation for a RepresentationType

        :param rep_type: A RepresentationType to use as a key
        :param file_extension_provider: A SerializationFormat implementation to use as a value
        """
        super().register(rep_type, file_extension_provider)
