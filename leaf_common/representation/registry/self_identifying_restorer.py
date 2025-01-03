
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
from leaf_common.persistence.interface.restorer import Restorer
from leaf_common.representation.registry.representation_persistence_registry \
    import RepresentationPersistenceRegistry
from leaf_common.serialization.interface.self_identifying_representation_error \
    import SelfIdentifyingRepresentationError


class SelfIdentifyingRestorer(Restorer):
    """
    A Restorer that, given a RepresentationPersistenceRegistry, knows how
    to look inside the contents of a file to see which Persistence
    implementation should be used to restore() an object from a file reference.
    """

    def __init__(self, persistence_registry: RepresentationPersistenceRegistry):
        """
        Constructor.
        """

        self._persistence_registry = persistence_registry
        self._last_restored_representation_type = None

    def restore(self, file_reference: str = None) -> object:
        """
        :param file_reference: The file reference to use when restoring.
                Default is None, implying the file reference is up to the
                implementation.
        :return: an object from some persisted store
        """
        if file_reference is None:
            return None

        rep_type_list = self._persistence_registry.representation_types_from_filename(file_reference)
        if rep_type_list is None:
            raise ValueError(f"Could not find representation type for {file_reference}")

        # For any given file extension (like JSON), there could be multiple
        # representation types that could live in there.  Here we need to attempt
        # to read the contents of the files to see which one works.
        # We assume that anything invalid will throw an error or return None
        # on restore().
        rep_type = None
        restored_object = None
        for test_rep_type in rep_type_list:
            persistence = self._persistence_registry.get_for_representation_type(test_rep_type)
            try:
                restored_object = persistence.restore(file_reference)
                if restored_object is not None:
                    # We found the RepresentationType that worked
                    rep_type = test_rep_type
                    break

            except SelfIdentifyingRepresentationError:
                # Swallow in case the next representation type works.
                # Specifically do not swallow IOErrors so that
                # FileNotFoundError and the likes can be propagated to caller.
                pass

        if restored_object is None:
            self._last_restored_representation_type = None
            raise ValueError(f"Could not open file {file_reference} using any RepresentationType in {rep_type_list}")

        self._last_restored_representation_type = rep_type
        return restored_object

    def get_last_restored_representation_type(self) -> RepresentationType:
        """
        :return: The last RepresentationType restored by this instance.
                Can return None if no successful restore() has yet happened.
        """
        return self._last_restored_representation_type
