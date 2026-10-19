
# Copyright © 2023-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
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

from abc import abstractmethod
from leaf_common.utils.interface import interface


@interface
class Startable:
    """
    Interface for objects which have a specific starting phase.
    """

    @abstractmethod
    def start(self) -> None:
        """
        Perform start up.
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """
        Perform steps to stop/shut-down
        By default this does nothing
        """
