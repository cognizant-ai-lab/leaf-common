
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
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

from typing import Any
from typing import Dict
from typing import List

import json
import logging

import grpc

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import Parse

from leaf_common.session.grpc_client_retry import GrpcClientRetry
from leaf_common.session.grpc_channel_security import GrpcChannelSecurity
from leaf_common.session.grpc_metadata_util import GrpcMetadataUtil
from leaf_common.time.timeout import Timeout


# pylint: disable=too-few-public-methods
class AbstractServiceSession:
    """
    An abstract class which handles the invocation of one or more gRPC
    method calls on a gRPC service.

    Requests can be sent either as a specific gRPC protobufs request structure
    or a dictionary that is to be turned into such a request structure.

    The gRPC response received will match the typing of the request
    (dict for dict, grpc for grpc).

    Concrete subclasses should multiply inherit from some strongly typed
    interface that supports the call structure particular to the service.

    For dictionary-oriented client sessions, each gRPC method should have
    a dictionary-based doppelganger method defined in that interface, the
    idea being that testing is done with the dictionaries and gRPC-ness is
    an implementation detail.

    For gRPC-oriented forwarding sessions, the multiple inheritance should
    come directly from a code-generated gRPC Servicer class for the stub.
    """

    # pylint: disable=too-many-arguments
    def __init__(self,
                 service_name: str,
                 service_stub: Any,
                 host: str,
                 port: str,
                 timeout_in_seconds: int = 30,
                 metadata: Dict[str, str] = None,
                 security_cfg: Dict[str, Any] = None,
                 umbrella_timeout: Timeout = None):
        """
        Creates an AbstractServiceSession that can connect to the specified
        service_stub and do retires when those calls fail.

        :param service_name: The string name of the service to be forwarded.
        :param service_stub: The gRPC service_stub for the service.
                    Looks like: <my_service_name>_pb2_grpc.<MyServiceName>ServiceStub
        :param host: the service host to connect to
        :param port: the service port
        :param timeout_in_seconds: timeout to use when communicating
                with the service
        :param metadata: A grpc metadata of key/value pairs to be inserted into
                         the header. Default is None. Preferred format is a
                         dictionary of string keys to string values.
        :param security_cfg: An optional dictionary of parameters used to
                        secure the TLS and the authentication of the gRPC
                        connection.  Supplying this implies use of a secure
                        GRPC Channel.  Default is None, uses insecure channel.
        :param umbrella_timeout: A Timeout object under which the length of all
                        looping and retries should be considered
        """
        # This version corresponds to a vague notion of cluster version
        # that we want to talk to.  This doesn't necessarily correspond to
        # any version related to the internal implementation of that cluster.
        # It is populated as a field with each request so that some other entity
        # can potentially route or even provide some backwards compatibility
        # given this client's expectations.
        self.request_version = "1"
        self.name = service_name

        self.session_metadata = self._build_request_metadata(metadata)

        self.poll_interval_seconds = 15

        self.channel_security = GrpcChannelSecurity(
                            security_cfg=security_cfg,
                            service_name=self.name,
                            poll_interval_seconds=self.poll_interval_seconds,
                            umbrella_timeout=umbrella_timeout)

        # Set up a GRPC retry context that assumes that the initial submission
        # has gone through on the service end when the UNAVAILABLE message
        # is first returned from sending the message *after* the connection
        # is first established.
        limited_retry_set = set()
        limited_retry_set.add(grpc.StatusCode.UNAVAILABLE)

        self.initial_submission_retry = GrpcClientRetry(
            service_name=self.name,
            service_stub=service_stub,
            host=host,
            port=port,
            timeout_in_seconds=timeout_in_seconds,
            poll_interval_seconds=self.poll_interval_seconds,
            limited_retry_set=limited_retry_set,
            limited_retry_attempts=1,
            metadata=self.session_metadata,
            channel_security=self.channel_security,
            umbrella_timeout=umbrella_timeout)

        self.umbrella_timeout = umbrella_timeout

    def call_grpc_method(self, method_name: str,
                         stub_method_callable: Any,
                         request: Any,
                         request_instance: Any = None) -> Any:
        """
        :param method_name: The name of the gRPC method call for logging purposes
        :param stub_method_callable: a global-scope method whose signature looks
                    like this:

            @staticmethod
            def _my_stub_method_callable(service_stub_instance, timeout_in_seconds,
                                       metadata, credentials, *args):
                response = service_stub_instance.MyRpcCall(*args,
                                                           timeout=timeout_in_seconds,
                                                           metadata=metadata,
                                                           credentials=credentials)
                return response
        :param request: Can be one of either:
                    * A gRPC Request structure to forward as the gRPC method argument
                    * A request dictionary whose data will fill in the request_instance
                        if present.
        :param request_instance: If present serves as the storage point for converting
                    a request dictionary to the request structure.
        :return: If this method received a dictionary request, then it will return
                a response in dictionary form if the method call was successful.
                If this method received a gRPC Request structure, then it will return a
                gRPC response structure if the method call was successful.
                In either case if the call was unsuccessful, the return value will be None.
        """
        logger = logging.getLogger(__name__)
        # Checkmarx flags this as a source for Filtering Sensitive Logs path 5
        # This is a False Positive, as we are merely abstractly logging a
        # service method name and no secrets themselves.
        logger.debug("Calling %s() on the %s", method_name, str(self.name))

        grpc_request = request
        is_dictionary_request = isinstance(request, Dict)
        if is_dictionary_request:
            if request_instance is not None:
                grpc_request = Parse(json.dumps(request), request_instance)
            else:
                # We really only expect this to be raised during development,
                # should someone not match the calling semantics.
                raise ValueError(f"Request to {method_name} on {self.name} was dictionary, " +
                                 "but no request_instance passed")

        # Submit the request
        rpc_method_args = [grpc_request]

        response = self._poll_for_response(method_name,
                                           stub_method_callable,
                                           rpc_method_args,
                                           want_dictionary_response=is_dictionary_request)

        # Checkmarx flags this as a dest for Filtering Sensitive Logs path 6
        # This is a False Positive, as we are merely abstractly logging a
        # service method name and no secrets themselves.
        logger.debug("Successfully called %s().", method_name)
        return response

    def _build_request_metadata(self, metadata):
        """
        Build metadata to be sent over with every gRPC call
        we make during this service session.
        We take metadata provided as a parameter
        and add service routing information,
        which uses service request version.

        :param metadata: external metadata provided for this session

        :return: metadata extended with service routing information.
        """

        request_routing_key = "service_version"
        external_metadata = GrpcMetadataUtil.to_tuples(metadata)
        if external_metadata is None:
            external_metadata_list = []
        else:
            external_metadata_list = list(external_metadata)

        external_metadata_list.append((request_routing_key, self.request_version))
        return GrpcMetadataUtil.to_tuples(external_metadata_list)

    def _poll_for_response(self, method_name: str,
                           stub_method_callable: Any,
                           rpc_method_args: List[Any],
                           want_dictionary_response: bool = True):
        """
        Will call the given stub_method_callable with the rpc_method_args and
        wait for a result with a valid response dictionary to come back.

        If the initial call fails for some reason (usually linux socket
        timeout inside the service), it assumes that it's going to take
        a while for the service to return with the response.

        If after a long time these requests fail,
        it assumes there has been a problem with the service and attempts
        to retry the initial call, and the process starts all over again
        until a real answer comes back.

        :param method_name: GRPC protocol method to call
        :param stub_method_callable: a global-scope method whose signature looks
                    like this:

            @staticmethod
            def _my_stub_method_callable(service_stub_instance, timeout_in_seconds,
                                       metadata, credentials, *args):
                response = service_stub_instance.MyRpcCall(*args,
                                                           timeout=timeout_in_seconds,
                                                           metadata=metadata,
                                                           credentials=credentials)
                return response
        :param rpc_method_args: a list (always) of arguments to pass to the
                   GRPC method
        :param want_dictionary_response: When True (the default) a dictionary
                    version of the gRPC response is returned.  When False,
                    the raw gRPC response is returned.
        :return: a dictionary or gRPC response structure corresponding to the
                response message from the GPC method call.
        """

        response_dict = None
        response = None

        keep_trying = True
        while keep_trying and \
            Timeout.has_time(self.poll_interval_seconds,
                             timeout=self.umbrella_timeout):

            response = None
            response_dict = None

            try:
                # Get the initial response from the service method.
                response = self.initial_submission_retry.must_have_response(
                    method_name, stub_method_callable, *rpc_method_args)

            except KeyboardInterrupt as exception:
                # Allow for command-line quitting
                raise exception

            except Exception:       # pylint: disable=broad-except
                logger = logging.getLogger(__name__)
                # Checkmarx flags this as a dest for Filtering Sensitive Logs path 4
                # This is a False Positive, as we are merely abstractly logging a
                # service method name and no secrets themselves.
                logger.info("Assuming %s request submitted.", str(method_name))
                # Otherwise pass

            # Read the initial response
            if response is not None and want_dictionary_response:
                if not isinstance(response, grpc.Future):
                    response_dict = MessageToDict(response)
                else:
                    # Assume the response is a '_MultiThreadedRendezvous' from a stream.
                    # Results are then actually a list
                    response_list = []
                    responses = list(response)
                    self.initial_submission_retry.close_channel()
                    for one_response in responses:
                        response_dict = MessageToDict(one_response)
                        response_list.append(response_dict)

                    response_dict = response_list

            if (want_dictionary_response and response_dict is None) or \
                    response is None:
                logger = logging.getLogger(__name__)
                # Checkmarx flags this as a dest for Filtering Sensitive Logs path 3
                # This is a False Positive, as we are merely abstractly logging a
                # service method name and no secrets themselves.
                logger.info("No %s response yet. Retrying %s request.",
                            str(method_name), str(method_name))
                keep_trying = True
            else:
                # We got what we wanted
                keep_trying = False

        if want_dictionary_response:
            # Return the dictionary, cuz that is what was desired
            return response_dict

        return response
