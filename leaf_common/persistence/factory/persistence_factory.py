
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

import logging
import os

from leaf_common.persistence.factory.json_gzip_persistence \
    import JsonGzipPersistence
from leaf_common.persistence.factory.hocon_persistence \
    import HoconPersistence
from leaf_common.persistence.factory.json_persistence \
    import JsonPersistence
from leaf_common.persistence.factory.raw_bytes_persistence \
    import RawBytesPersistence
from leaf_common.persistence.factory.reference_helper \
    import ReferenceHelper
from leaf_common.persistence.factory.text_persistence \
    import TextPersistence
from leaf_common.persistence.factory.null_persistence \
    import NullPersistence
from leaf_common.persistence.factory.yaml_persistence \
    import YamlPersistence

from leaf_common.persistence.mechanism.persistence_mechanism_factory \
    import PersistenceMechanismFactory


from leaf_common.serialization.format.serialization_formats \
    import SerializationFormats


class PersistenceFactory():
    """
    Factory class for Persistence implementations.
    Given:
    1. a string specifying PersistenceMechanism type
    2. a "persist_dir" passed from the caller (which often is experiment name)
    3. a "persist_file" passed from the caller (i.e. file name)

    ... the create_persistence() method will dish out the correct persistence
        implementation.
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, bucket_base="", key_base="", object_type="object",
                 reference_pruner=None, dictionary_converter=None):
        """
        Constructor.

        :param bucket_base:  The bucket base for S3 storage
        :param key_base:  The key (folder) base for S3 storage
        :param object_type: A string describing what kind of object
                is to be persisted.
        :param reference_pruner: A ReferencePruner implementation
                to prevent persisting reference data twice.
        :param dictionary_converter: A DictionaryConverter implementation
                that knows how to convert an object to/from a data-only
                dictionary.
        """

        self.persistence_factory = PersistenceMechanismFactory(
            bucket_base=bucket_base,
            key_base=key_base,
            object_type=object_type)
        self.object_type = object_type
        self.reference_pruner = reference_pruner
        self.dictionary_converter = dictionary_converter
        self.fallback = SerializationFormats.JSON

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def create_persistence(self, persist_dir, persist_file,
                           serialization_format=None,
                           persistence_mechanism=None,
                           must_exist=True,
                           use_file_extension=None,
                           full_ref=None):
        """
        :param persist_dir: Directory/Folder of where the persisted
                    file should reside.
        :param persist_file: File name for the persisted file.
        :param serialization_format: a string description of the
                SerializationFormat format desired.
        :param persistence_mechanism: a string description of the persistence
                mechanism desired.
        :param must_exist: When False, if the file does
                not exist upon restore() no exception is raised.
                When True (the default), an exception is raised.
        :param use_file_extension: Use the provided string instead of the
                standard file extension for the format. Default is None,
                indicating the standard file extension for the format should
                be used.
        :param full_ref: A full file reference to be broken apart into
                consituent pieces for purposes of persistence.
        :return: a new Persistence implementation given all the specifications
        """

        use_serialization_format = self._resolve_serialization_format(
            serialization_format)

        use_persist_dir, use_persist_file, use_file_extension = \
            self._rearrange_components(persist_dir, persist_file,
                                       use_file_extension, full_ref)

        persistence_mechanism_instance = \
            self.persistence_factory.create_persistence_mechanism(
                use_persist_dir,
                use_persist_file,
                persistence_mechanism=persistence_mechanism,
                must_exist=must_exist)

        persistence = None
        if persistence_mechanism_instance is None:
            persistence = NullPersistence()
        elif use_serialization_format == SerializationFormats.HOCON:
            persistence = HoconPersistence(persistence_mechanism_instance,
                                           reference_pruner=self.reference_pruner,
                                           dictionary_converter=self.dictionary_converter,
                                           use_file_extension=use_file_extension)
        elif use_serialization_format == SerializationFormats.JSON:
            persistence = JsonPersistence(persistence_mechanism_instance,
                                          reference_pruner=self.reference_pruner,
                                          dictionary_converter=self.dictionary_converter,
                                          use_file_extension=use_file_extension)
        elif use_serialization_format == SerializationFormats.JSON_GZIP:
            persistence = JsonGzipPersistence(persistence_mechanism_instance,
                                              reference_pruner=self.reference_pruner,
                                              dictionary_converter=self.dictionary_converter,
                                              use_file_extension=use_file_extension)
        elif use_serialization_format == SerializationFormats.RAW_BYTES:
            persistence = RawBytesPersistence(persistence_mechanism_instance,
                                              use_file_extension=use_file_extension)
        elif use_serialization_format == SerializationFormats.TEXT:
            persistence = TextPersistence(persistence_mechanism_instance,
                                          use_file_extension=use_file_extension)
        elif use_serialization_format == SerializationFormats.YAML:
            persistence = YamlPersistence(persistence_mechanism_instance,
                                          reference_pruner=self.reference_pruner,
                                          dictionary_converter=self.dictionary_converter,
                                          use_file_extension=use_file_extension)
        else:
            # Default
            message = "Don't know serialization format '%s' for type '%s'." +\
                        " Using fallback %s."
            logger = logging.getLogger(__name__)
            logger.warning(message, str(use_serialization_format),
                           str(self.object_type), str(self.fallback))
            persistence = self.create_persistence(use_persist_dir,
                                                  use_persist_file,
                                                  serialization_format=self.fallback,
                                                  persistence_mechanism=persistence_mechanism,
                                                  must_exist=must_exist,
                                                  use_file_extension=use_file_extension)

        return persistence

    def _resolve_serialization_format(self, serialization_format):
        """
        :param serialization_format: a string description of the
                    serialization format desired.
                    If None, use the serialization format in the fallback
                    Otherwise, use the override in this argument
        :return: a string of the accepted serialization format
        """

        # Find the SerializationFormat type to use
        use_serialization_format = self._find_serialization_format(serialization_format)
        if use_serialization_format is None:
            # None found for argument, use fallback
            message = "Don't know serialization format '%s' for type '%s'." + \
                        " Using fallback %s."
            logger = logging.getLogger(__name__)
            logger.warning(message, str(serialization_format),
                           str(self.object_type), str(self.fallback))
            use_serialization_format = self.fallback

        return use_serialization_format

    def _find_serialization_format(self, serialization_format):
        """
        :param serialization_format: The string name of the
                serialization_format mechanism to use.
        :return: The matching cannonical string for the serialization format
                if it is found in the list of SERIALIZATION_FORMATS.
                None otherwise.
        """

        # Figure out the SerializationFormat specified in the fallback
        found_serialization_format = None
        if serialization_format is not None:
            for serialization in SerializationFormats.SERIALIZATION_FORMATS:
                if serialization_format.lower() == serialization.lower():
                    found_serialization_format = serialization

        return found_serialization_format

    def _rearrange_components(self, persist_dir, persist_file,
                              file_extension, full_ref):
        """
        Potentially rearrange the components of the persistence path
        in case one has pieces of the other.

        :param persist_dir: Directory/Folder of where the persisted
                    file should reside.
        :param persist_file: File name for the persisted file.
        :param file_extension: Use the provided string instead of the
                standard file extension for the format. Default is None,
                indicating the standard file extension for the format should
        :param full_ref: A full file reference to be broken apart into
                consituent pieces for purposes of persistence.
        """
        use_persist_dir = persist_dir
        use_persist_file = persist_file

        # See if there are any directory components in persist_file
        if persist_file is not None:
            split_tuple = os.path.split(persist_file)
            head = split_tuple[0]
            if head is not None:
                use_persist_dir = os.path.join(persist_dir, head)

        use_folder, use_base_name, use_file_extension = \
            ReferenceHelper.get_components(full_ref, use_persist_dir,
                                           use_persist_file, file_extension)

        return use_folder, use_base_name, use_file_extension
