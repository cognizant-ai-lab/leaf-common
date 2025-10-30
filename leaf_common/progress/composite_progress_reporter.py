
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

from typing import Any
from typing import Dict

from leaf_common.progress.progress_reporter import ProgressReporter


class CompositeProgressReporter(ProgressReporter):
    """
    A ProgressReporter implementation that reports progress to more than
    one ProgressReporter
    """

    def __init__(self):
        """
        Constructor
        """
        self._components = []

    def add_progress_reporter(self, progress_reporter: ProgressReporter):
        """
        Adds a component progress reporter
        """
        self._components.append(progress_reporter)

    def report(self, progress: Dict[str, Any]):
        """
        :param progress: A progress dictionary
        """
        for component in self._components:
            component.report(progress)

    def subcontext(self, progress: Dict[str, Any]) -> ProgressReporter:
        """
        Creates a subcontext ProgressReporter that will be a
        CompositeProgressReporter composed of subcontexts from
        all this guy's components, in order.

        :param progress: A progress dictionary
        :return: A ProgressReporter governing the progress of a new
                progress subcontext
        """
        subcontext = CompositeProgressReporter()

        for component in self._components:
            component_sub = component.subcontext(progress)
            subcontext.add_progress_reporter(component_sub)

        return subcontext
