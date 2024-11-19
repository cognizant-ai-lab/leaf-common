
from urllib.parse import parse_qsl
from urllib.parse import urlparse
from urllib.parse import urlunparse

VERSION_ID_PARAM = "versionId"


class VersionedUrlUtil:
    """
    Utility class to deal with all the different aspects of a url that refers
    to a versioned file.  This is only for use with S3 versioned files,
    but it's conceivable other file systems could have a notion of versioning.

    Note that this is solely a problem with reading files, as there is no such
    thing as a version specification for writing files in S3 land.

    A typical boto-supported S3 url looks like this:

        s3://<endpoint>/<bucket>/<filename>

    ... with nothing extra tacked on the end.

    Trouble is, we want to be able to work with versioned files, and currently
    there is no url format for doing that. Consequently, we create our own
    extension to this url with parameters for versioned files:

        s3://<endpoint>/<bucket>/<filename>?versionId=<version>
    """

    @staticmethod
    def create_versioned_url(base_url: str, version_id: str = None) -> str:
        """
        :param base_url: The basis url to attach a version to
        :param version_id: The version to attach
        :return: A new url string which has the appropriate versionId parameter
                tacked on that further invocations of this class can understand.
        """
        if version_id is None:
            return base_url

        # Assumes versionId is not already in there
        new_url = f"{base_url}?{VERSION_ID_PARAM}={version_id}"
        return new_url

    @staticmethod
    def get_version_id_from_url(url: str) -> str:
        """
        :param url: The url to parse
        :return: The string version id in the url.  Can return None if
                there is no "?versionId" parameter specified in the url.
        """
        # Split the url into parts, then parse the params (if any) into a dictionary.
        # This is really:
        #   scheme, netloc, path, params, query, fragment
        # See https://docs.python.org/3/library/urllib.parse.html#url-parsing
        split_url = urlparse(url)
        scheme, _, _, _, query, _ = split_url

        # If we are not doing S3, we don't need to get any fancier than
        # our existing file reference
        if scheme != "s3":
            return None

        # We really only want to get fancy if there is a versionId specified
        # as part of the s3 url.  This notion of a ?versionId=<version>
        # is our own making.
        # FWIW: I'm very surprised version addition to s3 url hasn't been a thing
        param_dict = dict(parse_qsl(query))
        version_id = param_dict.get(VERSION_ID_PARAM, None)

        return version_id

    @staticmethod
    def get_file_reference_from_url(url: str) -> str:
        """
        :param url: The url to parse
        :return: The basis file reference in the url.
        """
        # Split the url into parts, then parse the params (if any) into a dictionary.
        # This is really:
        #   scheme, netloc, path, params, query, fragment
        # See https://docs.python.org/3/library/urllib.parse.html#url-parsing
        split_url = urlparse(url)
        scheme, netloc, path, _, _, _ = split_url

        # If we are not doing S3, we don't need to get any fancier than
        # our existing file reference
        if scheme != "s3":
            return url

        # We are doing versions with S3. We have no choice but to open a stream.
        # To do that we need to reassemble the url without the query, params or fragment.
        url_tuple = (scheme, netloc, path, "", "", "")
        s3_url = urlunparse(url_tuple)

        return s3_url
