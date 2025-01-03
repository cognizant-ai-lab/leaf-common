
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
See class comments.
"""


class PopulationSession():
    """
    An interface describing the methods used to invoke the API
    from the standpoint of the service-calling code.

    Implementations might make calls directly to the underlying
    library in a dev/test situation, or might call an RPC service
    underneath.

    In the comments for these method calls, there are references to
    a "PopulationResponse".  A PopulationResponse is more or less a
    dictionary with the following keys:

        * "population" - this is a list of Candidate dictionaries,
                        semantics of which are defined by the method

            Candidates themselves have the following structure:

                "id" - a string id that uniquely identifies the candidate
                       within the context of the experiment (at least)

                "interpretation" - an opaque structure representing
                       some interpretation of what has been evolved
                       which is to be evaluated.

                "metrics" - a structure which is optional, depending on
                        the context, containing evaluation metrics for
                        the candidate.

                "identity" - an optional structure containing information
                        about the circumstances of the candidates origins.


        * "generation_count" - this is an integer representing the
                             current known generation count

        * "checkpoint_id" - this is a string identifier for resuming
                            work from a particular checkpoint

        * "evaluation_stats" - this is another dictionary with various
                            evaluation stats collected by whatever is doing
                            the evaluating
    """

    def next_population(self, experiment_id, config,
                        evaluated_population_response):
        """
        :param experiment_id: A relatively unique human-readable String
                used for isolating artifacts of separate experiments

        :param config: Config instance

        :param evaluated_population_response: A population response containing
            the population for which the nextion will be based.
            If this is None, it is assumed that a new population will be started
            from scratch.

        :return: A PopulationResponse containing unevaluated candidates
            for the next generation.
        """
        raise NotImplementedError

    def get_population(self, experiment_id, checkpoint_id):
        """
        :param experiment_id: A String unique to the experiment
                used for isolating artifacts of separate experiments

        :param checkpoint_id: String specified of the checkpoint desired.

        :return: A PopulationResponse where ...

                "population" is a list of candidate data comprising the entire
                population *that has yet to be evaluated* (not what you
                might have just evaluated). This means no previous fitness
                information can be expected from any component of the list,
                although it is possible that elites might come down with
                previous metrics attached to them.

                "generation_count" will be what was last handed out when
                the population was created

                "checkpoint_id" an actual not-None checkpoint_id
                            from which the returned unevaluated population
                            can be recovered via the get_current_population()
                            call.

                "evaluation_stats" will contain the same contents as were
                passed in when the population was created
        """
        raise NotImplementedError

    def get_service_info(self):
        """
        :return: A ServiceInfoResponse dictionary with various keys
                filled in with information about the service.
                This is intended to be a very quick call round-trip,
                equivalent to a ping of the service, with very little
                work performed.
        """
        raise NotImplementedError
