
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

import errno
import logging
import sys

from io import StringIO


class StreamToLogger(StringIO):
    """
    File-like stream object that redirects writes to a logger instance.
    Riffed on from original suggestion at:
    https://stackoverflow.com/questions/11124093/redirect-python-print-output-to-logger/11124247
    """

    def __init__(self, logger, log_level=logging.INFO):
        """
        Constructor.

        :param logger: The logger to redirect write() calls to.
        :param log_level: The logging level at which the writes() will be
                    written.  Default is logging.INFO.
        """
        super().__init__()

        self.logger = logger
        self.log_level = log_level

        # These two compose the stacks that help us avoid infinite recursion
        # in cases where loggers are set up to go to stdout
        self.last_logged = []
        self.last_num_lines_logged = []

    def write(self, s):
        """
        Write the string s to the stream and return the number of characters
        written.  The "stream" in this case is really any set of logging
        handlers set up by LoggingSetup.  Any one of these can be stdout,
        which this method is meant to subvert.

        :param s: the string to write to the log
        :return: the number of characters written
        """

        # Monitor what is coming in.
        stripped = s.rstrip()
        lines = stripped.splitlines()
        num_lines = len(lines)

        # Look to break infinite loops in logging exceptions
        # _ is Pythonic for unused variable
        exception_type, exception_value, _ = sys.exc_info()

        # If we have logged something before in this call stack
        dont_log = len(self.last_num_lines_logged) > 0
        # ... and we are logging the same number of lines as before
        dont_log = dont_log and self.last_num_lines_logged[-1] == num_lines
        # ... and the string we last logged is in the what we are trying to log
        dont_log = dont_log and self.last_logged[-1] in stripped

        # Prevent some infinite loops when exceptions happen in loggers when
        # lower-level python logging code encounters a BrokenPipe error.
        dont_log = dont_log or \
            (exception_type == BrokenPipeError) or \
            (exception_type == RecursionError) or \
            ((exception_type == OSError) and
             (str(exception_value) == str(errno.EPIPE)))
        dont_log = dont_log or \
            (num_lines > 0 and lines[0].startswith("--- Logging error ---"))

        if dont_log:
            # ... then bail to avoid infinite recursion
            # because the loggers can be set up to send output
            # back out to stdout.
            return 0

        # Push our current information on the stack(s)
        self.last_logged.append(stripped)
        self.last_num_lines_logged.append(num_lines)

        # If multiline, write each line separately with its own log message
        for line in lines:
            line_to_write = line.rstrip()
            self.logger.log(self.log_level, line_to_write)

        # Pop our current information off the stack(s)
        self.last_logged.pop()
        self.last_num_lines_logged.pop()

        # Return what write() interface wants, more or less.
        num_chars = len(s)
        return num_chars

    @classmethod
    def subvert(cls, logger=None, reroute_stdout=True, reroute_stderr=True):
        """
        Subverts stdout and stderr to separate instances of the python logger
        for this class.
        :param logger: The logger to use for subverting stdout and stderr
                    By default this is None, indicating a new logger
                    will be based off this class.
        :param reroute_stdout: True if stdout should be rerouted to the
                            StreamToLogger.  False otherwise
        :param reroute_stderr: True if stderr should be rerouted to the
                            StreamToLogger.  False otherwise

        """

        # Get the logger
        use_logger = logger
        if use_logger is None:
            use_logger = logging.getLogger(cls.__name__)

        # Deal with stdout
        info_stream_logger = StreamToLogger(use_logger, logging.INFO)
        if reroute_stdout:
            sys.stdout = info_stream_logger

        # Deal with stderr
        error_stream_logger = StreamToLogger(use_logger, logging.ERROR)
        if reroute_stderr:
            sys.stderr = error_stream_logger
