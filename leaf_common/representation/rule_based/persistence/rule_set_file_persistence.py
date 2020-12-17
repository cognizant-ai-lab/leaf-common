
# Copyright (C) 2019-2020 Cognizant Digital Business, Evolutionary AI.
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

from leaf_common.persistence.factory.simple_file_persistence import SimpleFilePersistence
from leaf_common.serialization.interface.serialization_format import SerializationFormat

from leaf_common.representation.rule_based.serialization.rule_set_serialization_format \
    import RuleSetSerializationFormat


class RuleSetFilePersistence(SimpleFilePersistence):
    """
    Implementation of the leaf-common Persistence interface which
    saves/restores a RuleSet to a file.
    """

    def __init__(self, serialization_format: SerializationFormat = None):
        """
        Constructor.

        :param serialization_format: A means of serializing a RuleSet
                by default this is None and a RuleSetSerializationFormat is used
        """
        use_format = serialization_format
        if use_format is None:
            use_format = RuleSetSerializationFormat()
        super().__init__(use_format)
