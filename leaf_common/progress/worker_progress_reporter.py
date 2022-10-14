
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
