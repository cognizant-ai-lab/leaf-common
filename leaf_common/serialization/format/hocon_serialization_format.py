
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
"""
See class comment for details.
"""

from json import dumps
from json import loads

from pyhocon import ConfigFactory
from pyhocon import ConfigTree

from leaf_common.serialization.format.json_serialization_format import JsonSerializationFormat
from leaf_common.serialization.interface.dictionary_converter import DictionaryConverter
from leaf_common.serialization.interface.reference_pruner import ReferencePruner
from leaf_common.serialization.util.bytes_decoder import BytesDecoder


class HoconSerializationFormat(JsonSerializationFormat):
    """
    An implementation of the Serialization interface which provides
    Hocon Serializer and a Deserializer implementations under one roof.
    With this class, hocon serialization (from_object) is just JSON.
    """

    def __init__(self, reference_pruner: ReferencePruner = None, dictionary_converter: DictionaryConverter = None,
                 pretty: bool = True, sanitize_keys: bool = False):
        """
        Constructor.

        :param reference_pruner: A ReferencePruner implementation
                that knows how to prune/graft repeated references
                throughout the object hierarchy
        :param dictionary_converter: A DictionaryConverter implementation
                that knows how to convert from a dictionary to the object type
                in question.
        :param pretty: a boolean which says whether the output is to be
                nicely formatted or not.  Try for: indent=4, sort_keys=True
        :param sanitize_keys: When True, to_object() removes the quotation
                marks that pyhocon embeds in keys that had to be quoted in
                the HOCON source because they contain characters that are
                special in HOCON keys -- "$", "}", "[", "]", ":", "=",
                "+", "#", "`", "^", "?", "!", "@", "*", "&", and "." --
                e.g. "llama3.1" or "llama3:8b".
                Default is False, preserving the existing (quote-retaining)
                behavior for current callers.
        """
        super().__init__(reference_pruner=reference_pruner,
                         dictionary_converter=dictionary_converter,
                         pretty=pretty)
        self.sanitize_keys: bool = sanitize_keys

    def to_object(self, fileobj, basedir=None):
        """
        :param fileobj: The file-like object to deserialize.
                It is expected that the file-like object be open and be
                pointing at the beginning of the data (ala seek to the
                beginning).

                After calling this method, the seek pointer will be at the end
                of the data. Closing of the fileobj is left to the caller.
        :param basedir: Optional base directory for resolving include directives.
                When provided, HOCON include paths are resolved relative to this
                directory rather than the process working directory. Pass the
                directory of the file being parsed so that sibling includes work
                correctly regardless of where the server is started from.
        :return: the deserialized object
        """

        pruned_dict = None
        if fileobj is not None:
            hocon_bytes = fileobj.getvalue()
            hocon_string, _ = BytesDecoder.decode_bytes(hocon_bytes)

            # Load the HOCON into a dictionary
            pruned_dict = ConfigFactory.parse_string(hocon_string, basedir=basedir)

            if pruned_dict is not None and self.sanitize_keys:
                # as_plain_ordered_dict() removes the quotation marks that
                # pyhocon embeds in keys containing forbidden characters
                # such as "." and ":".  Only ConfigTree has that method and
                # a root-level HOCON array parses to a ConfigList, so wrap
                # the parse result in a ConfigTree first to sanitize any
                # ConfigTrees nested within it.
                wrapper = ConfigTree()
                wrapper.put("root", pruned_dict)
                pruned_dict = wrapper.as_plain_ordered_dict()["root"]

            # Hocon tends to produce regular dictionaries that have
            # ConfigTree structures for nested dictionaries.
            # No one ever wants that, so have the result go through a json
            # encode/decode step before handing the dictionary back to save
            # the world the trouble of having to do it everywhere.
            if pruned_dict is not None:
                pruned_dict = loads(dumps(pruned_dict))

        obj = self.conversion_policy.convert_to_object(pruned_dict)
        return obj

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".hocon"
