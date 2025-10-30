
# Copyright 2019-2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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
See class comments
"""

import logging
import threading
from leaf_common.asyncio.asyncio_executor import AsyncioExecutor


class AsyncioExecutorPool:
    """
    Class maintaining a dynamic set of reusable AsyncioExecutor instances.
    """

    def __init__(self, reuse_mode: bool = True):
        """
        Constructor.
        :param reuse_mode: True, if requested executor instances
                                 are taken from pool of available ones (pool mode);
                           False, if requested executor instances are created new
                                 and shutdown on return (backward compatible mode)
        """
        self.reuse_mode: bool = reuse_mode
        self.pool = []
        self.lock: threading.Lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("AsyncioExecutorPool created: %s reuse: %s",
                          id(self), str(self.reuse_mode))

    def get_executor(self) -> AsyncioExecutor:
        """
        Get active (running) executor from the pool
        :return: AsyncioExecutor instance
        """
        if self.reuse_mode:
            with self.lock:
                if len(self.pool) > 0:
                    result = self.pool.pop(0)
                    self.logger.debug("Reusing AsyncioExecutor %s", id(result))
                    return result
        # Create AsyncioExecutor outside of lock
        # to avoid potentially longer locked periods
        result = AsyncioExecutor()
        result.start()
        self.logger.debug("Creating AsyncioExecutor %s", id(result))
        return result

    def return_executor(self, executor: AsyncioExecutor):
        """
        Return AsyncioExecutor instance back to the pool of available instances.
        :param executor: AsyncioExecutor to return.
        """
        if self.reuse_mode:
            with self.lock:
                executor.cancel_current_tasks()
                self.pool.append(executor)
                self.logger.debug("Returned to pool: AsyncioExecutor %s pool size: %d", id(executor), len(self.pool))
        else:
            # Shutdown AsyncioExecutor outside of lock
            # to avoid potentially longer locked periods
            self.logger.debug("Shutting down: AsyncioExecutor %s", id(executor))
            executor.shutdown()
