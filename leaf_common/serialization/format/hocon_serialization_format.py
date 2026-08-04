
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

import json

from pyhocon import ConfigFactory

from leaf_common.serialization.format.json_serialization_format \
    import JsonSerializationFormat
from leaf_common.serialization.util.bytes_decoder import BytesDecoder


class HoconSerializationFormat(JsonSerializationFormat):
    """
    An implementation of the Serialization interface which provides
    Hocon Serializer and a Deserializer implementations under one roof.
    With this class, hocon serialization (from_object) is just JSON.
    """

    def to_object(self, fileobj, basedir=None, sanitize_keys=False):
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
        :param sanitize_keys: When True, keys that had to be quoted in the
                HOCON source because they contain forbidden characters,
                such as ".", ":", "$", "@", "#", "!", "?", "=", "+", and
                white spaces (e.g. "llama3.1", "llama3:8b"), come back
                without the quotation marks that pyhocon embeds in the
                key strings.
                Default is False, preserving the existing (quote-retaining)
                behavior for current callers.
        :return: the deserialized object
        """

        pruned_dict = None
        if fileobj is not None:
            hocon_bytes = fileobj.getvalue()
            hocon_string, _ = BytesDecoder.decode_bytes(hocon_bytes)

            # Load the HOCON into a dictionary
            pruned_dict = ConfigFactory.parse_string(hocon_string, basedir=basedir)

            # Hocon tends to produce regular dictionaries that have
            # ConfigTree structures for nested dictionaries.
            # No one ever wants that, so convert to regular dictionaries
            # before handing the result back to save the world the trouble
            # of having to do it everywhere.
            if pruned_dict is not None:
                if sanitize_keys:
                    # as_plain_ordered_dict() removes the quotation marks that
                    # pyhocon embeds in keys containing forbidden characters
                    # such as "." and ":".  It returns nested OrderedDicts,
                    # so recursively convert those to regular dicts.
                    pruned_dict = self.to_plain_dict(
                        pruned_dict.as_plain_ordered_dict())
                else:
                    pruned_dict = json.loads(json.dumps(pruned_dict))

        obj = self.conversion_policy.convert_to_object(pruned_dict)
        return obj

    @staticmethod
    def to_plain_dict(obj):
        """
        :param obj: An object potentially containing nested OrderedDicts,
                as returned by pyhocon's as_plain_ordered_dict().
        :return: the same structure with all dict-like values converted
                to regular dicts
        """
        if isinstance(obj, dict):
            return {key: HoconSerializationFormat.to_plain_dict(value)
                    for key, value in obj.items()}
        if isinstance(obj, list):
            return [HoconSerializationFormat.to_plain_dict(item)
                    for item in obj]
        return obj

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".hocon"
