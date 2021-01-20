
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
import logging
import os

import boto3
import botocore

from leaf_common.persistence.mechanism.abstract_persistence_mechanism \
    import AbstractPersistenceMechanism


class S3FilePersistenceMechanism(AbstractPersistenceMechanism):
    """
    Implementation of the AbstractPersistenceMechanism which
    saves objects to a file on S3.
    """

    def __init__(self, folder, base_name, must_exist=True,
                 bucket_base="", key_base=""):

        super().__init__(folder, base_name, must_exist)

        # Quiet some rather chatty logging from dependencies
        logging.getLogger('boto').setLevel(logging.INFO)
        logging.getLogger('s3transfer').setLevel(logging.INFO)
        logging.getLogger('botocore').setLevel(logging.INFO)
        logging.getLogger('urllib3').setLevel(logging.INFO)

        self.s3_client = boto3.client('s3')
        self.bucket_base = bucket_base
        self.key_base = key_base

    def open_source_for_read(self, read_to_fileobj,
                             file_extension_provider=None):
        """
        :param read_to_fileobj: A fileobj into which we will put all data
                            read in from the persisted instance.
        :param file_extension_provider:
                An implementation of the FileExtensionProvider interface
                which is often related to the Serialization implementation.
        :return: Either:
            1. None, indicating that the file desired does not exist.
            2. Some fileobj opened and ready to receive data which this class
                will fill and close in the restore() method.  Callers must
                use some form of copy() to get the all the data into any
                buffers backing the read_to_fileobj.
            3. The value 1, indicating to the parent class that the file exists,
               and the read_to_fileobj has been already filled with data by
               this call.
        """

        key = self.get_key_name(file_extension_provider)

        return_fileobj = None
        try:
            self.s3_client.download_fileobj(Fileobj=read_to_fileobj,
                                            Bucket=self.bucket_base, Key=key)
            logger = logging.getLogger(__name__)
            logger.info("S3 file read %s %s succeeded",
                        str(self.bucket_base), str(key))
            return_fileobj = 1

            # Set the seek pointer to the beginning of the data
            read_to_fileobj.seek(0, os.SEEK_SET)

        except botocore.exceptions.ClientError as exception:
            logger = logging.getLogger(__name__)
            if exception.response['Error']['Code'] == "404" \
                    and not self.must_exist():

                # If the file doesn't exist, that's OK,
                # we will check again later.
                logger.info("S3 file read %s %s does not exist",
                            str(self.bucket_base), str(key))
                return_fileobj = None
            else:
                # Something else has gone wrong
                logger.error("S3 file read %s %s some other error happened %s",
                             str(self.bucket_base),
                             str(key),
                             str(exception.response['Error']['Code']))
                raise

        return return_fileobj

    def open_dest_for_write(self, send_from_fileobj,
                            file_extension_provider=None):
        """
        :param send_from_fileobj: A fileobj from which we will get all data
                            written out to the persisted instance.
        :param file_extension_provider:
                An implementation of the FileExtensionProvider interface
                which is often related to the Serialization implementation.
        :return: None, indicating to the parent class that the send_from_fileobj
                has been filled with data by this call.
        """

        retval = None

        key = self.get_key_name(file_extension_provider)

        self.s3_client.upload_fileobj(Fileobj=send_from_fileobj,
                                      Bucket=self.bucket_base, Key=key)

        # upload_fileobj() actually flushes the buffer to S3,
        # so no need to do anything further.

        return retval

    def get_key_name(self, file_extension_provider):
        """
        :param file_extension_provider:
                An implementation of the FileExtensionProvider interface
                which is often related to the Serialization implementation.
        :return: the key name to use for the persisted entity
            This is a combination of:
                1. a constant "key base" folder component
                2. the last path component of the folder,
                    which corresponds to the experiment name
                3. the base_name passed in at construct time
                4. any file extension provided by the file_extension_provider
        """

        key_file = self.base_name
        if file_extension_provider is not None:
            file_extension = file_extension_provider.get_file_extension()
            key_file = key_file + file_extension

        # Use only the last piece of the path passed in at construct time
        key_experiment = os.path.basename(self.folder)
        if len(key_experiment) == 0:

            # Got an empty experiment name. It just means folder
            # ended with /. Go up one for the directory. If we do not,
            # there can be collisions.
            dirname = os.path.dirname(self.folder)
            key_experiment = os.path.basename(dirname)

        key_name = os.path.join(self.key_base, key_experiment, key_file)

        return key_name
