
# Copyright 2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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


class SerializationFormats():
    """
    Class containing string constants for serialization formats.
    """

    # SerializationFormats
    GZIP = "gzip"
    HOCON = "hocon"
    JSON = "json"
    JSON_GZIP = JSON + "_" + GZIP
    RAW_BYTES = "raw_bytes"
    TEXT = "text"
    YAML = "yaml"

    # Note: We are specifically *not* including pickle as a SerializationFormat
    #   in leaf-common because of all the security and maintenence problems
    #   it prompts.  While there is nothing about the system that prevents
    #   such a SerializationFormat coming into being (we had it in the past),
    #   we would much rather encourage the "clean living" that is possible
    #   without pickle.  Why not try JSON instead? ;)
    SERIALIZATION_FORMATS = [HOCON, JSON, JSON_GZIP, RAW_BYTES, TEXT, YAML]
