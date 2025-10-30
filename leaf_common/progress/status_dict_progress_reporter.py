
# Copyright © 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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


class StatusDictProgressReporter(ProgressReporter):
    """
    ProgressReporter implementation that updates the global status
    dictionary for a particular identifier
    """

    def __init__(self, identifier: str = "default",
                 status_dict: Dict[str, Any] = None,
                 root_status: Dict[str, Any] = None,
                 parent_progress: Dict[str, Any] = None):
        """
        Constructor

        :param identifier: The string identifier of the progress stream
        :param status_dict: A dictionary containing multiple progress streams
        :param root_status: The anchor of the nested progress reports
        :param parent_progress: A middle node in the nested progress reports
                                onto which new progress gets hung
        """
        self._identifier = str(identifier)

        self._status_dict = status_dict
        if self._status_dict is None:
            self._status_dict = {}

        self._root_status = root_status
        self._parent_progress = parent_progress

        if self._parent_progress is not None and \
                self._root_status is None:
            raise ValueError("Parent progress without root status")

    def report(self, progress: Dict[str, Any]):
        """
        :param progress: A progress dictionary
        """
        use_root = self._root_status
        if use_root is None:
            use_root = progress

        use_parent = self._parent_progress
        if use_parent is not None:
            # Update status at the specified parent in the nested structure
            self._parent_progress["subcontexts"] = [progress]

        # Always update the main status dictionary with the root
        self._status_dict[self._identifier] = use_root

    def subcontext(self, progress: Dict[str, Any]) -> ProgressReporter:
        """
        :param progress: A progress dictionary
        :return: A ProgressReporter governing the progress of a new
                progress subcontext
        """
        # Report the given status like normal
        # This will insert the progress into the nested hierarchy
        # before splitting off a new ProgressReporter
        self.report(progress)

        # The root is what anchors the nested progress report to the
        # status dictionary
        use_root = self._root_status
        if use_root is None:
            use_root = progress

        # Use the current dictionary to report as the new parent
        use_parent = progress

        subcontext = StatusDictProgressReporter(self._identifier,
                                                self._status_dict,
                                                use_root,
                                                use_parent)
        return subcontext
