
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
See class comment for details.
"""


class FitnessObjective():
    """
    A Data-only class which describes a single fitness objective.
    """

    def __init__(self, metric_name, maximize_fitness=True):
        """
        Constructor.

        :param metric_name: the String name of the field in a Metrics Record
                    whose value directly corresponds to this fitness
                    objective
        :param maximize_fitness: True when maximizing fitness.
                    False when minimizing. Default value is True.
        """
        self._metric_name = metric_name
        self._maximize_fitness = maximize_fitness

    def get_metric_name(self):
        """
        :return: the String name of the fitness metric
        """
        return self._metric_name

    def is_maximize_fitness(self):
        """
        :return: true if we are maximizing fitness.
                False otherwise.
        """
        return self._maximize_fitness
