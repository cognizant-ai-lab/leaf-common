from enum import IntEnum


class RejectionReason(IntEnum):
    """
    Rejection reasons
    Must match: proto/common_structs.proto
    Replicated here to avoid pulling in gRPC stuff
    """
    OTHER_REASON = 0
    TOO_MANY_CATEGORIES = 1
    SINGLE_VALUED = 2
    HAS_NAN = 3
    INVALID_COLUMN_NAME = 4
