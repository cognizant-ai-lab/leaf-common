
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
from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.persistence.interface.persistence import Persistence
from leaf_common.persistence.easy.easy_json_persistence import EasyJsonPersistence

from leaf_common.representation.registry.representation_file_extension_provider_registry \
    import RepresentationFileExtensionProviderRegistry
from leaf_common.representation.rule_based.persistence.rule_set_file_persistence \
    import RuleSetFilePersistence


class RepresentationPersistenceRegistry(RepresentationFileExtensionProviderRegistry):
    """
    Registry class which returns a leaf-common Persistence class
    for the RepresentationType
    """

    def __init__(self):
        """
        Constructor.
        """

        super().__init__()

        # Do some simple registrations
        self.register(RepresentationType.Structure, EasyJsonPersistence())
        self.register(RepresentationType.RuleBased, RuleSetFilePersistence())

    def register(self, rep_type: RepresentationType, file_extension_provider: Persistence):
        """
        Register a Persistence implementation for a RepresentationType

        :param rep_type: A RepresentationType to use as a key
        :param file_extension_provider: A Persistence implementation to use as a value
        """
        super().register(rep_type, file_extension_provider)
