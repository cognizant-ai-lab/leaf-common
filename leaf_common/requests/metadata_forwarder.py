
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

from leaf_common.requests.metadata_util import MetadataUtil


# pylint: disable=too-few-public-methods
class MetadataForwarder():
    """
    Base class for setting up extra grpc metadata/header information
    to be forwarded from a grpc context.
    """

    def __init__(self, key_list):
        """
        Constructor.

        :param key_list: The list of string keys whose grpc metadata
                is to be forwarded.
        """
        self.key_list = key_list
        if self.key_list is None:
            self.key_list = []

    def forward(self, context):
        """
        Gets metadata key/value pairs from the grpc context
        and forwards them into a new metadata dictionary.

        :param context: The grpc context for the request
        :return: a dictionary of metadata that was able to be forwarded
                from the given context
        """
        forwarded_dict = {}

        # Get the request context metadata in dictionary form
        metadata = context.invocation_metadata()

        meta_dict = MetadataUtil.to_dict(metadata)
        if meta_dict is None:
            meta_dict = {}

        # Find the keys we want to forward (if they exist)
        # and put them in the returned dictionary
        for key in self.key_list:
            if key in meta_dict:
                forwarded_dict[key] = meta_dict.get(key)

        return forwarded_dict
