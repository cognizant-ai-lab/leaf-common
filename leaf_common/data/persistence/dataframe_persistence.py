
from typing import Any
from typing import Dict
from typing import List

import logging
import os

from pandas import DataFrame
from pandas import read_csv


from leaf_common.persistence.interface.persistence import Persistence
from leaf_common.serialization.prep.redactor_dictionary_converter \
    import RedactorDictionaryConverter

from leaf_common.data.persistence.versioned_url_util import VersionedUrlUtil

# Note that the default Pandas encoding is "ISO-8859-1"
# We deviate from that simply from our own experience in what users want
DEFAULT_ENCODING = "UTF-8"

# By default we do not suddenly want row indexes appearing as a new column
# when they were not explicitly invited.
DEFAULT_INDEX = False


class DataFramePersistence(Persistence):
    """
    Implementation of the Persistence interface which allows persisting and
    restoring Pandas DataFrames to/from csv files using pandas native APIs
    which can handle local or s3 file_references.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Constructor.

        :param config: Optional config dict with the following keys:
            aws_access_key_id       If not present, will use the AWS_ACCESS_KEY_ID
                                    env var for s3:// file references
            aws_secret_access_key   If not present, will use the AWS_SECRET_ACCESS_KEY
                                    env var for s3:// file references
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        if self.config is None:
            # At least start with an empty dictionary to avoid
            # all kinds of other None checks in code
            self.config = {}
        else:
            # Translate for ephemeral creds that come from Vault
            # if no creds are already present.
            # This translation could still yield no creds
            if self.config.get("aws_secret_access_key") is None and \
                    self.config.get("secret_key") is not None:
                self.config["aws_secret_access_key"] = self.config.get("secret_key")

            if self.config.get("aws_access_key_id") is None and \
                    self.config.get("access_key") is not None:
                self.config["aws_access_key_id"] = self.config.get("access_key")

    def persist(self, obj: DataFrame, file_reference: object = None) -> object:
        """
        Persists the object passed in.

        :param obj: an object to persist
        :param file_reference: The file reference to use when persisting.
                Default is None, implying the file reference is up to the
                implementation.
                This implementation of persist() allows file_references which are:
                    * strings containing a local path
                    * strings containing a url specification (to allow for S3 storage)
                    * A file-like object containing the output
        :return: an object describing the location to which the object was persisted
                 This is most often the passed-in file_reference itself.
        """
        if obj is None:
            # Nothing ventured, nothing gained
            return None

        if file_reference is None:
            raise ValueError("Cannot persist() to None file_reference")

        dataframe = obj
        storage_options = self.get_storage_options(file_reference)

        file_ref_name = file_reference
        if not isinstance(file_reference, str):
            file_ref_name = "file-obj"
        # Redact sensitive keys before logging out configuration data:
        redacted: Dict[str, Any] = RedactorDictionaryConverter().to_dict(self.config)
        self.logger.info("Writing csv to %s with config %s",
                         file_ref_name, str(redacted))

        # All defaults are per
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
        # ... except for 'encoding', which is here for backwards compatibility with existing code.
        # Note that these args are not handled, most on purpose:
        #   float_format
        #   columns
        #   index
        #   index_label
        #   mode
        #   quoting
        #   chunksize
        dataframe.to_csv(file_reference,
                         sep=self.config.get("delimiter", ","),
                         na_rep=self.config.get("na_rep", ""),
                         header=self.config.get("header", True),
                         index=self.config.get("index", DEFAULT_INDEX),
                         encoding=self.config.get("encoding", DEFAULT_ENCODING),
                         compression=self.config.get("compression", "infer"),
                         quotechar=self.config.get("quotechar", '"'),
                         lineterminator=self.config.get("lineterminator", None),
                         date_format=self.config.get("date_format", None),
                         doublequote=self.config.get("doublequote", True),
                         escapechar=self.config.get("escapechar", None),
                         decimal=self.config.get("decimal", "."),
                         errors=self.config.get("errors", "strict"),
                         storage_options=storage_options)

        # DEF: Should probably return something with S3 version
        return file_reference

    def restore(self, file_reference: object = None) -> DataFrame:
        """
        :param file_reference: The file reference to use when restoring.
                Default is None, implying the file reference is up to the
                implementation.
                This implementation of persist() allows file_references which are:
                    * strings containing a local path
                    * strings containing a url specification (to allow for S3 storage)
                    * A file-like object containing the input
        :return: an object from some persisted store
        """
        if file_reference is None:
            raise ValueError("Cannot restore() from None file_reference")

        storage_options = self.get_storage_options(file_reference)

        file_ref_name = file_reference
        if not isinstance(file_reference, str):
            file_ref_name = "file-obj"
        # Redact sensitive keys before logging out configuration data:
        redacted: Dict[str, Any] = RedactorDictionaryConverter().to_dict(self.config)
        self.logger.info("Reading csv from %s with config %s",
                         file_ref_name, str(redacted))

        found_file_reference = self.find_file_reference(file_reference)

        # Since we can't close() a string, we might have to
        # do our own close() in the finally below.
        try:
            # All defaults are per
            # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
            # unless there is a DEFAULT_* used from above.
            data_source_df = read_csv(found_file_reference,
                                      sep=self.config.get("sep", ","),
                                      engine=self.config.get("engine", None),
                                      index_col=self.config.get("index_col", None),
                                      na_values=self.config.get("na_rep", None),
                                      header=self.config.get("header", "infer"),
                                      encoding=self.config.get("encoding", DEFAULT_ENCODING),
                                      compression=self.config.get("compression", "infer"),
                                      quotechar=self.config.get("quotechar", '"'),
                                      lineterminator=self.config.get("lineterminator", None),
                                      doublequote=self.config.get("doublequote", True),
                                      escapechar=self.config.get("escapechar", None),
                                      decimal=self.config.get("decimal", "."),
                                      skipinitialspace=self.config.get("skipinitialspace", False),
                                      encoding_errors=self.config.get("errors", "strict"),
                                      storage_options=storage_options)
        finally:
            # Maybe close the found_file_reference
            if not isinstance(found_file_reference, str):
                # The file reference we found is not a string, so we assume it's a
                # file-like object and we consider closing it here.
                if isinstance(file_reference, str):
                    # The original file_reference was a string, which means we have
                    # the responsibility for closing the file-like object we made.
                    found_file_reference.close()

        return data_source_df

    def get_file_extension(self) -> List[str]:
        """
        :return: A string representing a file extension for the
                serialization method, including the ".",
                *or* a list of these strings that are considered valid
                file extensions.
        """
        return [".csv"]

    def get_storage_options(self, file_reference: object) -> Dict[str, Any]:
        """
        If the file name starts with s3://, pandas will use S3 thanks to s3fs.
        If that's the case, make sure the AWS credentials are passed to Pandas,
        either from the config of this object, or if not present, from the env vars.

        For alternative AWS credentials management,
        see https://github.com/s3fs-fuse/s3fs-fuse/blob/master/README.md#examples

        :param file_reference: Can either be a url string or a Python file-like object
        :return: A dictionary with credentials suitable for digestion by Pandas.
        """
        storage_options = None

        if not isinstance(file_reference, str):
            # Can't parse a buffer. Besides, it's definitely not an S3 url.
            return storage_options

        if file_reference.startswith("s3://"):
            # If nothing is defined, default is None
            aws_access_key_id = self.config.get('aws_access_key_id',
                                                os.getenv("AWS_ACCESS_KEY_ID"))
            aws_secret_access_key = self.config.get('aws_secret_access_key',
                                                    os.getenv("AWS_SECRET_ACCESS_KEY"))
            storage_options = {
                "key": aws_access_key_id,
                "secret": aws_secret_access_key
            }
        return storage_options

    def find_file_reference(self, file_reference: object) -> object:
        """
        Do some work looking at the file_reference to see if there
        is any S3 versioning going on in the reference.

        :param file_reference: The file reference to inspect
        :return: The file_reference to use in the Pandas call
        """
        if not isinstance(file_reference, str):
            # Can't parse a buffer. Besides, it's definitely not an S3 url.
            return file_reference

        # Find the versionId, if any.
        version_id = VersionedUrlUtil.get_version_id_from_url(file_reference)
        if version_id is None:
            # Not a versioned url, so just use the file_reference as-is.
            return file_reference

        s3_url = VersionedUrlUtil.get_file_reference_from_url(file_reference)
        storage_options = self.get_storage_options(file_reference)

        # See https://s3fs.readthedocs.io/en/latest/#bucket-version-awareness
        # lazy import: moving the import here for only when it is required
        from s3fs import S3FileSystem  # pylint: disable=import-outside-toplevel,import-error
        s3fs = S3FileSystem(anon=False, version_aware=True,
                            key=storage_options.get("key"),
                            secret=storage_options.get("secret"))
        found_file_reference = s3fs.open(s3_url, version_id=version_id)

        return found_file_reference
