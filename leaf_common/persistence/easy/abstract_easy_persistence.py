
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
See class comment for details
"""

from leaf_common.persistence.factory.persistence_factory \
    import PersistenceFactory
from leaf_common.persistence.interface.persistence \
    import Persistence
from leaf_common.persistence.mechanism.persistence_mechanisms \
    import PersistenceMechanisms
from leaf_common.serialization.prep.pass_through_dictionary_converter \
    import PassThroughDictionaryConverter


class AbstractEasyPersistence(Persistence):
    """
    A superclass for concrete Persistence implementation needs
    where an object is to be persisted in some SerializationFormat
    to be specified by a concrete subclass.
    A bunch of common defaults are set up and some common
    extra behaviors on persist() and restore() are implemented.
    """

    # Tied for Public Enemy #2 for too-many-arguments
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, serialization_format,
                 base_name=None, folder=".", must_exist=False,
                 object_type="dict", dictionary_converter=None,
                 use_file_extension=None, full_ref=None,
                 persistence_mechanism=PersistenceMechanisms.LOCAL):
        """
        Constructor.

        :param serialization_format: The format name from
                SerializationFormats to use
        :param base_name: The base name of the file.
                This does *not* include the ".txt" extension.
        :param folder: The folder in which the file is to be persisted.
        :param must_exist: Default False.  When True, an error is
                raised when the file does not exist upon restore()
                When False, the lack of a file to restore from is
                ignored and a dictionary value of None is returned
        :param object_type: A string indicating the type of object to be
                persisted. "string" by default.
        :param dictionary_converter: An implementation of a DictionaryConverter
                to use when converting the yaml to/from a dictionary.
                Default value of None implies that a
                PassThroughDictionaryConverter will be used, which does not
                modify the dictionary at all.
        :param use_file_extension: Use the provided string instead of the
                standard file extension for the format. Default is None,
                indicating the standard file extension for the format should
                be used.
        :param full_ref: A full file reference to be broken apart into
                consituent pieces for purposes of persistence.
        :param persistence_mechanism: By default, use
                PersistenceMechanisms.LOCAL
        """

        # Set up the DictionaryConverter
        use_dictionary_converter = dictionary_converter
        if dictionary_converter is None and \
                object_type == "dict":
            use_dictionary_converter = PassThroughDictionaryConverter()

        # default initialization
        factory = PersistenceFactory(object_type=object_type,
                                     dictionary_converter=use_dictionary_converter)

        # To be initialized further by concrete subclasses
        self.persistence = factory.create_persistence(folder, base_name,
                                                      persistence_mechanism=persistence_mechanism,
                                                      serialization_format=serialization_format,
                                                      must_exist=must_exist,
                                                      use_file_extension=use_file_extension,
                                                      full_ref=full_ref)

    def persist(self, obj, file_reference: str = None):
        """
        Persists the object passed in.

        :param obj: an object to persist
        :param file_reference: An optional file reference string to override
                any file settings fixed at construct time. Default of None
                indicates to resort to implementation's fixed file reference
                settings.
        """
        return self.persistence.persist(obj, file_reference)

    def restore(self, file_reference: str = None):
        """
        :param file_reference: An optional file reference string to override
                any file settings fixed at construct time. Default of None
                indicates to resort to implementation's fixed file reference
                settings.
        :return: an object from some persisted store as specified
                by the constructor.  If must_exist is False,
                this method can return None.
        """
        obj = self.persistence.restore(file_reference)
        return obj

    def get_file_reference(self, file_reference: str = None):
        """
        :param file_reference: An optional file reference string to override
                any file settings fixed at construct time. Default of None
                indicates to resort to implementation's fixed file reference
                settings.
        :return: The full file reference of what is to be persisted
        """
        filename = self.persistence.get_file_reference(file_reference)
        return filename

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".",
                *or* a list of these strings that are considered valid
                file extensions.
        """
        return self.persistence.get_file_extension()
