
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
from leaf_common.persistence.easy.easy_json_persistence import EasyJsonPersistence
from leaf_common.representation.rule_based.serialization.rule_set_dictionary_converter \
    import RuleSetDictionaryConverter


class RuleSetFilePersistence(EasyJsonPersistence):
    """
    Implementation of the leaf-common Persistence interface which
    saves/restores a RuleSet to a file.
    """

    def __init__(self):
        """
        Constructor.
        """
        converter = RuleSetDictionaryConverter()
        super().__init__(object_type=RepresentationType.RuleBased.value,
                         use_file_extension=".rules",
                         dictionary_converter=converter)
