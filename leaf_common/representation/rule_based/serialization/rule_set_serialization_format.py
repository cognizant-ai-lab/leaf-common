
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

from leaf_common.serialization.format.json_serialization_format import JsonSerializationFormat
from leaf_common.representation.rule_based.serialization.rule_set_dictionary_converter \
    import RuleSetDictionaryConverter


class RuleSetSerializationFormat(JsonSerializationFormat):
    """
    Class for serialization policy for RuleSets.
    """

    def __init__(self, pretty: bool = True,
                 verify_representation_type: bool = True):
        """
        Constructor

        :param pretty: a boolean which says whether the output is to be
                nicely formatted or not.  Pretty is: indent=4, sort_keys=True
        :param verify_representation_type: When True, from_dict() will raise
                 an error if the representation_type key does not match what we
                 are expecting.  When False, no such error is raised.
                 Default is True.
        """
        converter = RuleSetDictionaryConverter(
            verify_representation_type=verify_representation_type)
        super().__init__(dictionary_converter=converter, pretty=pretty)
