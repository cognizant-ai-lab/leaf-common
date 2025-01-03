
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
