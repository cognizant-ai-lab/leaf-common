
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

from leaf_common.persistence.easy.abstract_easy_persistence \
    import AbstractEasyPersistence
from leaf_common.serialization.format.serialization_formats \
    import SerializationFormats


class EasyYamlPersistence(AbstractEasyPersistence):
    """
    A superclass for concrete Persistence implementation needs
    where a dictionary is to be persisted in YAML format.
    A bunch of common defaults are set up and some common
    extra behaviors on persist() and restore() are implemented.
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, base_name=None, folder=".", must_exist=False,
                 object_type="dict", dictionary_converter=None,
                 use_file_extension=None, full_ref=None):
        """
        Constructor.

        :param base_name: The base name of the file.
                This does *not* include the ".yaml" extension.
        :param folder: The folder in which the file is to be persisted.
        :param must_exist: Default False.  When True, an error is
                raised when the file does not exist upon restore()
                When False, the lack of a file to restore from is
                ignored and a dictionary value of None is returned
        :param object_type: A string indicating the type of object to be
                persisted. "dict" by default.
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
        """

        super().__init__(SerializationFormats.YAML,
                         base_name=base_name,
                         folder=folder,
                         must_exist=must_exist,
                         object_type=object_type,
                         dictionary_converter=dictionary_converter,
                         use_file_extension=use_file_extension,
                         full_ref=full_ref)
