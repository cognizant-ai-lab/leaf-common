
# Copyright © 2019-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
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
See class comment for details.
"""


from leaf_common.fitness.metrics_provider import MetricsProvider


class CandidateMetricsProvider(MetricsProvider):
    """
    MetricsProvider implementation that gets metrics from a Candidate dictionary
    """

    def __init__(self, candidate):
        """
        Constructor.
        :param candidate: The candidate whose metrics dictionary we want
        """
        self._candidate = candidate

    def get_metrics(self):
        """
        Returns the metrics of this entity.
        :return: a dictionary of metrics
        """

        if self._candidate is None:
            return None

        metrics = self._candidate.get('metrics', None)

        # Allow for old-school candidates
        # or Worker results dicts
        if metrics is None:
            metrics = self._candidate

        return metrics
