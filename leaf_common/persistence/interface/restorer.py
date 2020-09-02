
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

class Restorer():
    """
    This interface provides a way to retrieve an object
    from some storage like a file, a database or S3.
    """

    def restore(self):
        """
        :return: an object from some persisted store
        """
        raise NotImplementedError
