
# Copyright (C) 2019-2020 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# ENN-release SDK Software in commercial settings.
#
# END COPYRIGHT


class SerializationFormats():
    """
    Class containing string constants for serialization formats.
    """

    # SerializationFormats
    GZIP = "gzip"
    HOCON = "hocon"
    JSON = "json"
    JSON_GZIP = JSON + "_"+ GZIP
    LEGACY_PICKLE = "legacy_pickle"
    RAW_BYTES = "raw_bytes"
    TEXT = "text"
    YAML = "yaml"

    SERIALIZATION_FORMATS = [LEGACY_PICKLE, HOCON, JSON, JSON_GZIP, RAW_BYTES, TEXT, YAML]
