
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
