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
