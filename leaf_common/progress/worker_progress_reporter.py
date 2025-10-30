
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

from leaf_common.progress.composite_progress_reporter \
    import CompositeProgressReporter
from leaf_common.progress.json_progress_reporter \
    import JsonProgressReporter
from leaf_common.progress.status_dict_progress_reporter \
    import StatusDictProgressReporter


class WorkerProgressReporter(CompositeProgressReporter):
    """
    A ProgressReporter implementation to be used on the CompletionService
    Worker during distributed evaluation.
    """

    def __init__(self, identifier: str = "default",
                 status_dict: Dict[str, Any] = None,
                 pretty: bool = True):
        """
        Constructor
        """
        super().__init__()

        use_status_dict = status_dict
        if use_status_dict is None:
            use_status_dict = {}

        component = StatusDictProgressReporter(identifier, use_status_dict)
        self.add_progress_reporter(component)

        component = JsonProgressReporter(use_status_dict, identifier,
                                         pretty=pretty)
        self.add_progress_reporter(component)
