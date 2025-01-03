
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

# Allows for method to return same class without error
from __future__ import annotations

from typing import Any
from typing import Dict

import copy

from leaf_common.progress.progress_reporter import ProgressReporter


class IteratingProgressReporter(ProgressReporter):
    """
    A convenience ProgressReporter that reports formatted subcontexts when
    iterating over a loop.
    """

    def __init__(self, wrapped_reporter: ProgressReporter,
                 iterate_over: object,
                 subcontext_report: Dict[str, Any]):
        """
        Constructor

        :param wrapped_reporter: The progress reporter this guy
                will call to do the heavy lifting
        :param iterate_over: Object to iterate over. Can be List, Dict or int
        :param subcontext_report: What to report for parent progress
                when we create the subcontext
        """
        self._wrapped_subcontext = wrapped_reporter.subcontext(subcontext_report)
        self._iterations_done = 0

        self._num_iterations = iterate_over
        if isinstance(iterate_over, list):
            self._num_iterations = len(iterate_over)
        elif isinstance(iterate_over, dict):
            self._num_iterations = len(iterate_over.items())

    def report(self, progress: Dict[str, Any]):
        """
        Can only be called once per iteration to report properly,
        as the internal notion of iteration tracking is incremented
        in here.

        :param progress: A template progress dictionary concentrating
                    only on the lowest-level scope of the iteration
                    at hand.  A human-readable (starting with 1 not 0)
                    iteration index is appended to the string "phase" key
                    of this template.
        :return: Nothing
        """
        # Progress is intended for anxious humans waiting for something
        # to finish.  Increase the counter before hand so we don't have
        # item's numbered 0 in the output at all.
        self._iterations_done = self._iterations_done + 1
        iteration_progress = self._create_iteration_progress(progress)
        self._wrapped_subcontext.report(iteration_progress)

    def subcontext(self, progress: Dict[str, Any]) -> ProgressReporter:
        """
        :param progress: A progress dictionary
        :return: A ProgressReporter governing the progress of a new
                progress subcontext
        """
        subcontext = self._wrapped_subcontext.subcontext(progress)
        return subcontext

    def _create_iteration_progress(self, progress: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a progress dictionary for the current iteration
        """
        iteration_progress = copy.deepcopy(progress)
        iteration_progress["phase"] = f"{iteration_progress['phase']} {self._iterations_done}"
        iteration_progress["progress"] = self._iterations_done / self._num_iterations

        return iteration_progress
