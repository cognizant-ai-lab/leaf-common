
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
