
# Copyright © 2019-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
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

import copy
import logging
import threading


# Set up some global variables to allow cascading of LogRecord factories
_SERVICE_OLD_FACTORY = None
_DEFAULT_EXTRA_LOGGING_FIELDS_DICT = {}

_SERVICE_LOGGING_FIELDS_KEY = "service_logging_fields_dict"


def _service_log_record_factory(*args, **kwargs):
    """
    Expected entry point for standard Python logging system to be
    used with the ServiceLogRecord class below.
    This needs to be a regular method, dissociated from any class.

    :param args: The positional arguments to the invocation of the
                 LogRecord constructor
    :param kwargs: The keyword arguments to the invocation of the
                 LogRecord constructor
    :return: A LogRecord instance from the Python logging package
            with added thread-specific fields added.
    """

    # Use the class variable to get a handle on the old LogRecord factory
    log_record = _SERVICE_OLD_FACTORY(*args, **kwargs)

    # Get the current threads attributes as a dictionary
    current_thread = threading.current_thread()
    thread_dict = current_thread.__dict__

    # Find the logging fields dictionary from the current thread
    logging_fields_dict = _DEFAULT_EXTRA_LOGGING_FIELDS_DICT
    if _SERVICE_LOGGING_FIELDS_KEY in thread_dict:
        logging_fields_dict = thread_dict[_SERVICE_LOGGING_FIELDS_KEY]

    # Get the current LogRecord as a dictionary
    log_record_dict = log_record.__dict__

    # Update the record dict with the key/value pairs set up
    # in the logging fields dict
    log_record_dict.update(logging_fields_dict)

    # Return the new LogRecord with the new logging fields set
    return log_record


class ServiceLogRecord():
    """
    Helper class which adds extra fields pertinent to service logging
    messages via the standard Python LogRecord class.

    Extra logging fields are stored in a dictionary on thread-local storage,
    so the lifetime of a single one of these objects should be the length
    of the context of the thread-specific information, which is typically
    the time it takes to service a single service request.

    The extra logging fields themselves do not have to be defined at this
    level.  They can be anything the client code wants.
    """

    @classmethod
    def set_up_record_factory(cls, default_extra_logging_fields=None):
        """
        Called early on in the lifetime of a service to redirect the standard
        Python LogRecord creation to our _record_factory() call at the top
        of the file.

        This needs to be called once by a service before any constructor of
        this class is called or message is logged.
        """

        # Need to access global variable. No other way.
        # Hacktastic python logging infrastructure is riddled with global needs
        # pylint: disable=global-statement
        global _SERVICE_OLD_FACTORY
        if _SERVICE_OLD_FACTORY is None:
            _SERVICE_OLD_FACTORY = logging.getLogRecordFactory()

        if default_extra_logging_fields is not None:
            # pylint: disable=global-statement
            global _DEFAULT_EXTRA_LOGGING_FIELDS_DICT
            _DEFAULT_EXTRA_LOGGING_FIELDS_DICT = copy.copy(default_extra_logging_fields)

        logging.setLogRecordFactory(_service_log_record_factory)

    @classmethod
    def get_default_extra_logging_fields(cls):
        """
        :return: The dictionary previously passed into set_up_record_factory()
        """
        # pylint: disable=global-statement,global-variable-not-assigned
        global _DEFAULT_EXTRA_LOGGING_FIELDS_DICT       # noqa: F824
        default_extra_logging_fields = copy.copy(_DEFAULT_EXTRA_LOGGING_FIELDS_DICT)
        return default_extra_logging_fields

    def __init__(self, logging_fields_dict=None):
        """
        Constructor.

        :param logging_fields_dict: Dictionary with thread-specific information
                for logging, whose keys will become attributes on a LogRecord.
                By default this is None, implying that an empty dictionary
                will be initially created as a placeholder for the thread's
                additional log messaging fields.
        """
        # Get the current thread
        current_thread = threading.current_thread()

        # Get the dictionary for the current thread structure
        thread_dict = current_thread.__dict__

        use_dict = logging_fields_dict
        if use_dict is None:
            use_dict = {}

        # Create our own dictionary as an instance variable
        self.thread_local_dict = use_dict

        # Save the new instance dict on the thread dictionary as an attribute
        thread_dict[_SERVICE_LOGGING_FIELDS_KEY] = self.thread_local_dict

    def set_logging_fields_dict(self, logging_fields_dict):
        """
        Called once when a service request is initiated.

        :param logging_fields_dict:  The thread-specific dictionary containing
            logging fields that will be added to each LogRecord produced.
        """
        self.thread_local_dict.update(logging_fields_dict)
