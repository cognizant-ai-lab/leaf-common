
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

from leaf_common.persistence.interface.persistence \
    import Persistence


class NullPersistence(Persistence):
    """
    Null implementation of the Persistence interface.
    """

    def persist(self, obj):
        """
        Persists object passed in.

        :param obj: an object to be persisted
        """

    def restore(self):
        """
        :return: a restored instance of a previously persisted object
        """
        return None
