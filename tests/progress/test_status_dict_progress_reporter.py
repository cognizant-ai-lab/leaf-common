
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

import unittest

from leaf_common.progress.status_dict_progress_reporter \
    import StatusDictProgressReporter


class TestStatsDictProgressReporter(unittest.TestCase):
    """
    Validates the creation of nested progress reports.
    """

    def setUp(self):
        self.status_dict = {}

    def test_simple(self):
        """
        Tests simple progress one-deep
        :return: nothing
        """

        reporter = StatusDictProgressReporter("test_simple", self.status_dict)
        reporter.report({
            "phase": "one",
            "progress": 0.5
        })

        self.assertDictEqual(self.status_dict, {
            "test_simple": {
                "phase": "one",
                "progress": 0.5
            }
        })

        reporter.report({
            "phase": "two",
            "progress": 1.0
        })

        self.assertDictEqual(self.status_dict, {
            "test_simple": {
                "phase": "two",
                "progress": 1.0
            }
        })

    def test_simple_nested(self):
        """
        Tests simple progress two-deep
        :return: nothing
        """

        reporter = StatusDictProgressReporter("test_simple_nested", self.status_dict)
        reporter.report({
            "phase": "one",
            "progress": 0.0
        })

        self.assertDictEqual(self.status_dict, {
            "test_simple_nested": {
                "phase": "one",
                "progress": 0.0
            }
        })

        reporter = reporter.subcontext({
            "phase": "two",
            "progress": 0.5
        })

        reporter.report({
            "phase": "nested 1",
            "progress": 0.1
        })

        self.assertDictEqual(self.status_dict, {
            "test_simple_nested": {
                "phase": "two",
                "progress": 0.5,
                "subcontexts": [
                    {
                        "phase": "nested 1",
                        "progress": 0.1
                    }
                ]
            }
        })

        reporter.report({
            "phase": "nested 2",
            "progress": 0.2
        })

        self.assertDictEqual(self.status_dict, {
            "test_simple_nested": {
                "phase": "two",
                "progress": 0.5,
                "subcontexts": [
                    {
                        "phase": "nested 2",
                        "progress": 0.2
                    }
                ]
            }
        })

        reporter = reporter.subcontext({
            "phase": "nested 3",
            "progress": 0.75
        })

        reporter.report({
            "phase": "nested A",
            "progress": 0.3
        })

        self.assertDictEqual(self.status_dict, {
            "test_simple_nested": {
                "phase": "two",
                "progress": 0.5,
                "subcontexts": [
                    {
                        "phase": "nested 3",
                        "progress": 0.75,
                        "subcontexts": [
                            {
                                "phase": "nested A",
                                "progress": 0.3
                            }
                        ]
                    }
                ]
            }
        })
