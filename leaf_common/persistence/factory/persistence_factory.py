
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

from typing import Tuple

from logging import getLogger
from logging import Logger
import os

from leaf_common.persistence.factory.json_gzip_persistence import JsonGzipPersistence
from leaf_common.persistence.factory.hocon_persistence import HoconPersistence
from leaf_common.persistence.factory.json_persistence import JsonPersistence
from leaf_common.persistence.factory.raw_bytes_persistence import RawBytesPersistence
from leaf_common.persistence.factory.reference_helper import ReferenceHelper
from leaf_common.persistence.factory.text_persistence import TextPersistence
from leaf_common.persistence.factory.null_persistence import NullPersistence
from leaf_common.persistence.interface.persistence import Persistence
from leaf_common.persistence.interface.persistence_mechanism import PersistenceMechanism
from leaf_common.serialization.interface.dictionary_converter import DictionaryConverter
from leaf_common.serialization.interface.reference_pruner import ReferencePruner
from leaf_common.persistence.factory.yaml_persistence import YamlPersistence
from leaf_common.persistence.mechanism.persistence_mechanism_factory import PersistenceMechanismFactory
from leaf_common.serialization.format.serialization_formats import SerializationFormats


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
    def __init__(self, bucket_base: str = "", key_base: str = "", object_type: str = "object",
                 reference_pruner: ReferencePruner = None,
                 dictionary_converter: DictionaryConverter = None) -> None:
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

        self.persistence_factory: PersistenceMechanismFactory = PersistenceMechanismFactory(
            bucket_base=bucket_base,
            key_base=key_base,
            object_type=object_type)
        self.object_type: str = object_type
        self.reference_pruner: ReferencePruner = reference_pruner
        self.dictionary_converter: DictionaryConverter = dictionary_converter
        self.fallback: str = SerializationFormats.JSON

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def create_persistence(self, persist_dir: str, persist_file: str,
                           serialization_format: str = None,
                           persistence_mechanism: str = None,
                           must_exist: bool = True,
                           use_file_extension: str = None,
                           full_ref: str = None) -> Persistence:
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

        use_serialization_format: str = self._resolve_serialization_format(
            serialization_format)

        use_persist_dir, use_persist_file, use_file_extension = \
            self._rearrange_components(persist_dir, persist_file,
                                       use_file_extension, full_ref)

        persistence_mechanism_instance: PersistenceMechanism = \
            self.persistence_factory.create_persistence_mechanism(
                use_persist_dir,
                use_persist_file,
                persistence_mechanism=persistence_mechanism,
                must_exist=must_exist)

        persistence: Persistence = None
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
            message: str = "Don't know serialization format '%s' for type '%s'." +\
                        " Using fallback %s."
            logger: Logger = getLogger(__name__)
            logger.warning(message, str(use_serialization_format),
                           str(self.object_type), str(self.fallback))
            persistence = self.create_persistence(use_persist_dir,
                                                  use_persist_file,
                                                  serialization_format=self.fallback,
                                                  persistence_mechanism=persistence_mechanism,
                                                  must_exist=must_exist,
                                                  use_file_extension=use_file_extension)

        return persistence

    def _resolve_serialization_format(self, serialization_format: str) -> str:
        """
        :param serialization_format: a string description of the
                    serialization format desired.
                    If None, use the serialization format in the fallback
                    Otherwise, use the override in this argument
        :return: a string of the accepted serialization format
        """

        # Find the SerializationFormat type to use
        use_serialization_format: str = self._find_serialization_format(serialization_format)
        if use_serialization_format is None:
            # None found for argument, use fallback
            message: str = "Don't know serialization format '%s' for type '%s'." + \
                        " Using fallback %s."
            logger: Logger = getLogger(__name__)
            logger.warning(message, str(serialization_format),
                           str(self.object_type), str(self.fallback))
            use_serialization_format = self.fallback

        return use_serialization_format

    def _find_serialization_format(self, serialization_format: str) -> str:
        """
        :param serialization_format: The string name of the
                serialization_format mechanism to use.
        :return: The matching cannonical string for the serialization format
                if it is found in the list of SERIALIZATION_FORMATS.
                None otherwise.
        """

        # Figure out the SerializationFormat specified in the fallback
        found_serialization_format: str = None
        if serialization_format is not None:
            # Match the argument against each known format, ignoring case.
            for serialization in SerializationFormats.SERIALIZATION_FORMATS:
                use_serialization: str = serialization
                if serialization_format.lower() == use_serialization.lower():
                    found_serialization_format = use_serialization

        return found_serialization_format

    def _rearrange_components(self, persist_dir: str, persist_file: str,
                              file_extension: str, full_ref: str) -> Tuple[str, str, str]:
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
        use_persist_dir: str = persist_dir
        use_persist_file: str = persist_file

        # See if there are any directory components in persist_file
        if persist_file is not None:
            split_tuple: Tuple[str, str] = os.path.split(persist_file)
            head: str = split_tuple[0]
            if head is not None:
                use_persist_dir = os.path.join(persist_dir, head)

        use_folder, use_base_name, use_file_extension = \
            ReferenceHelper.get_components(full_ref, use_persist_dir,
                                           use_persist_file, file_extension)

        return use_folder, use_base_name, use_file_extension
