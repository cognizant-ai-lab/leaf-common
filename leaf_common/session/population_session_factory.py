
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

from leaf_common.session.population_session import PopulationSession


class PopulationSessionFactory():
    """
    Abstract factory class for creating PopulationSession objects for
    communicating with a Population Service and/or underlying algorithm.
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def create_session(self, population_service_host: str,
                       population_service_port: str,
                       timeout_in_seconds: int = None,
                       service: str = None,
                       service_routing: str = None,
                       metadata: dict = None,
                       security_cfg: dict = None,
                       umbrella_timeout: object = None,
                       connection_options: dict = None) -> PopulationSession:
        """
        :param population_service_host: The host name of for the
                    Population Service hosting the algorithm
        :param population_service_port: The port number for the
                    Population Service hosting the algorithm
        :param timeout_in_seconds: the timeout for each remote method call
                    If None, the timeout length is left to the implementation
        :param service: the name of the service to connect to
        :param service_routing: string enumerating the style of service routing
                    to do. None implies the coded default.
        :param metadata: A grpc metadata of key/value pairs to be inserted into
                         the header. Default is None. Preferred format is a
                         dictionary of string keys to string values.
        :param security_cfg: An optional dictionary of parameters used to
                        secure the TLS and the authentication of the gRPC
                        connection.  Supplying this implies use of a secure
                        GRPC Channel.  Default is None, uses insecure channel.
        :param umbrella_timeout: A Timeout object under which the length of all
                        looping and retries should be considered
        :param connection_options: A dictionary of key/value pairs to be used
                        when constructing/configuring the communications channel
                        to the service.

        :return: an appropriate PopulationSession instance based on the
                    arguments
        """
        raise NotImplementedError
