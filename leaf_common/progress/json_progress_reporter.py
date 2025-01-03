
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

import json

from leaf_common.persistence.interface.persistor import Persistor
from leaf_common.persistence.easy.easy_json_persistence \
    import EasyJsonPersistence

from leaf_common.progress.progress_reporter import ProgressReporter


class JsonProgressReporter(ProgressReporter, Persistor):
    """
    An ProgressReporter implementation that spits out JSON descriptions
    of progress dictionaries.
    """

    def __init__(self, status_dict: Dict[str, Any],
                 identifier: str = "default",
                 pretty: bool = True):
        """
        Constructor

        :param status_dict: A status dictionary common to a
                StatusDictProgressReporter
        :param identifier: String identifier used to find the root progress
                structures in the status_dict.
        :param pretty: Boolean saying whether output should be human readable
                or not
        """
        self._status_dict = status_dict
        self._identifier = identifier
        self._pretty = pretty
        self._persistence = EasyJsonPersistence(base_name="progress",
                                                folder="../progress")

    def report(self, progress: Dict[str, Any]):
        """
        :param progress: A progress dictionary
        :return: Nothing
        """
        # Report the whole shebang
        root_progress = self._status_dict[self._identifier]

        self.persist(root_progress)

    def subcontext(self, progress: Dict[str, Any]) -> ProgressReporter:
        """
        :param progress: A progress dictionary
        :return: A ProgressReporter governing the progress of a new
                progress subcontext
        """
        return self

    def persist(self, obj: object, file_reference: str = None):
        """
        :param obj: The progress dictionary to persist
        :param file_reference: The file_reference to use when persisting
                    to a file.
        """

        root_progress = obj
        if self._pretty:
            json_string = json.dumps(root_progress, sort_keys=True, indent=4)
        else:
            json_string = json.dumps(root_progress)

        print(f"Progress: {json_string}")

        if self._persistence is not None:
            self._persistence.persist(root_progress,
                                      file_reference=file_reference)
