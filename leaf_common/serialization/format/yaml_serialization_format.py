
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

from typing import Any
from typing import Dict
from typing import IO

import os

from ruamel.yaml import YAML
from ruamel.yaml.compat import BytesIO

from leaf_common.serialization.interface.serialization_format \
    import SerializationFormat

from leaf_common.serialization.format.conversion_policy \
    import ConversionPolicy
from leaf_common.serialization.interface.dictionary_converter \
    import DictionaryConverter
from leaf_common.serialization.interface.reference_pruner \
    import ReferencePruner


class YamlSerializationFormat(SerializationFormat):
    """
    An implementation of the SerializationFormat interface which provides
    Yaml Serializer and a Deserializer implementations under one roof.
    """

    def __init__(self, reference_pruner: ReferencePruner = None,
                 dictionary_converter: DictionaryConverter = None,
                 pretty: bool = True) -> None:
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
        """
        self.conversion_policy: ConversionPolicy = ConversionPolicy(reference_pruner,
                                                                    dictionary_converter,
                                                                    pretty)

    def from_object(self, obj: Any) -> IO:
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """
        pruned_dict: Dict[str, Any] = self.conversion_policy.convert_from_object(obj)

        # See if YAML should be pretty or not
        yaml: YAML = YAML(typ='safe', pure=True)
        if self.conversion_policy.is_pretty():
            yaml.default_flow_style = False
            yaml.indent(mapping=4, sequence=6, offset=3)

        # Now convert the pruned dictionary to YAML
        fileobj: BytesIO = BytesIO()
        yaml.dump(pruned_dict, fileobj)
        fileobj.seek(0, os.SEEK_SET)

        return fileobj

    def to_object(self, fileobj: IO) -> Any:
        """
        :param fileobj: The file-like object to deserialize.
                It is expected that the file-like object be open
                and be pointing at the beginning of the data
                (ala seek to the beginning).

                After calling this method, the seek pointer
                will be at the end of the data. Closing of the
                fileobj is left to the caller.
        :return: the deserialized object
        """

        pruned_dict: Dict[str, Any] = None
        if fileobj is not None:
            # Load the YAML into a dictionary
            yaml: YAML = YAML(typ='safe', pure=True)
            pruned_dict = yaml.load(fileobj)

        obj: Any = self.conversion_policy.convert_to_object(pruned_dict)
        return obj

    def get_file_extension(self) -> str:
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".yaml"
