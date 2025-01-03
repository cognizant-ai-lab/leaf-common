
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
