
# Copyright (C) 2020 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
#
# This software is a trade secret, and contains proprietary and confidential
# materials of Cognizant Digital Business Evolutionary AI.
# Cognizant Digital Business prohibits the use, transmission, copying,
# distribution, or modification of this software outside of the
# Cognizant Digital Business EAI organization.
#
# END COPYRIGHT


class ComponentEvaluator():
    '''
    An interface that evaluates a component against an optional reference
    to data.  Components themselves can be as narrow or broad in scope
    as needed -- from an entire population of candidates to a single
    sub-component of genetic material.

    An Evaluator has as its most meaningful class method, a Pure Function
    which evaluates a given component against a given data reference.
    The results of the evaluation are given in the returned EvaluationResults
    object of the evaluate() method.

    Both the input component and the input data reference are expected to be
    read-only, data-only objects with no explicit policy attached to them.
    Evaluation policy (including data reference interpretation) emanates from
    derivations from this interface.

    Any given ComponentEvalautor will be tightly coupled (at least) to
    the class of the component it is evaluating, as well as the base type
    of the results yielded by the evaluation.

    For any given component, there might be more than one way
    to interpret the data described by it. In such a case, there would be a
    single implementation of this class for each interpretation
    of the component data.

    Also, for any given component interpretation, there might be more
    than one way to perform the evaluation to obtain the same evaluation results,
    (e.g. optimized vs. brute force, or GPU vs. CPU). Each of these cases
    might have their own ComponentEvaluator implementation as well.
    '''

    def evaluate(self, component: object, evaluation_data: object = None) -> object:
        '''
        Evaluate the given component on the given evaluation_data reference.
        This method is a Pure Function.

        :param component:
                an unspecified type which can provide access to the
                data-only components of just what is to be evaluated.

                A component implementation provides no policy methods
                as to specifically how an evaluation of its data will take
                place in and of itself. Such policy methods are specifically
                reserved for one or more ComponentEvaluator classes for
                a specific component type, which allows for multiple ways to interpret
                the same component data.

       :param evaluation_data:
                a data reference of some kind which can completely describe
                the data against which a component is evaluated.

                It is expected that a single instance of a component could
                be tested against multiple instances of evaluation_data
                for the purposes of training of real-life/inference use.

                All interpretations of the evaluation_data references are also
                left to implementations, such as data layout and semantics of the
                evaluation_data itself, as specific classes/groupings of the
                component might require specific schema for accessing data.

                Items which might need to appear somewhere as a field (or
                dictionary sub-field) in an evaluation_data dictionary could include:
                    a) Data Sample information
                    b) Data View information as to which part of a Data Sample
                        is under scrutiny at the time of evaluation.
                    c) Feedback data for a specific Individual's transient,
                        state which is carried forward for evaluation.

                The default value of evaluation_data is be None, indicating
                that access to any evaluation data is up to the implementation.

       :return: The results are an unspecified type. Typical implementation contain
                the transient results of the evaluation, coupled with a separate
                Metrics dictionary measurements describing *how* the evaluate() call
                went, regardless of results.
        '''
        raise NotImplementedError
