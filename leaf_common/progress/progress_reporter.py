
# Copyright 2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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
"""
See class comments.
"""

# Allows for method to return same class without error
from __future__ import annotations

from typing import Any
from typing import Dict


class ProgressReporter:
    """
    An interface for reporting progress
    """

    def report(self, progress: Dict[str, Any]):
        """
        Report the given progress dictionary as the
        lowest level of progress context/scope that
        has no notion of context/scope that it happens
        to be nested within (if at all).

        You can think of this as a kind of print statement
        that you would sprinkle throughout a single method
        with many phases, reporting on the progress of that
        method.

        Client code should only be concerned with its own
        limited progress context/scope for its own procedures.

        Implementations are expected to have references to
        parent ProgressReporter contexts/scopes so that placement
        within a broader, nested progress context/scope can be done
        without specifically worrying about the data details
        of those broader contexts/scopes.

        :param progress: A single, un-nested progress dictionary,
                limited in scope to the progressing procedure at hand.
        :return: Nothing
        """
        raise NotImplementedError

    def subcontext(self, progress: Dict[str, Any]) -> ProgressReporter:
        """
        Create a new ProgressReporter that is starting a new progress scope
        at the lowest level.

        :param progress: A progress dictionary which acts as a "title"
                for the new progress context/scope
        :return: A ProgressReporter governing the progress of a new
                progress subcontext
        """
        raise NotImplementedError
