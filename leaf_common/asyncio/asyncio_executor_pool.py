
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
See class comments
"""
from typing import Any
from typing import Dict

import copy
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
        # List of available (not currently used) AsyncioExecutor instances in the pool.
        self.pool_available = []

        # List of currently used AsyncioExecutor instances in the pool.
        self.pool_used = []

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
                if len(self.pool_available) > 0:
                    result = self.pool_available.pop(0)
                    self.logger.debug("Reusing AsyncioExecutor %s", id(result))
                    self.pool_used.append(result)
                    return result
        # Create AsyncioExecutor outside of lock
        # to avoid potentially longer locked periods
        result = AsyncioExecutor()
        result.start()
        self.logger.debug("Creating AsyncioExecutor %s", id(result))
        self.pool_used.append(result)
        return result

    def return_executor(self, executor: AsyncioExecutor):
        """
        Return AsyncioExecutor instance back to the pool of available instances.
        :param executor: AsyncioExecutor to return.
        """
        if executor not in self.pool_used:
            raise ValueError(f"Returned executor {id(executor)} is not in the pool of used executors")

        if self.reuse_mode:
            executor.cancel_current_tasks()
            with self.lock:
                self.pool_used.remove(executor)
                self.pool_available.append(executor)
                self.logger.debug("Returned to pool: AsyncioExecutor %s pool size: %d", id(executor), len(self.pool_available))
        else:
            # Shutdown AsyncioExecutor outside of lock
            # to avoid potentially longer locked periods
            self.logger.debug("Shutting down: AsyncioExecutor %s", id(executor))
            with self.lock:
                self.pool_used.remove(executor)
            # Note: shutdown is called outside of lock to avoid potentially long shutdown execution.
            executor.shutdown()

    def get_threads_metrics(self) -> Dict[str, Any]:
        """
        Get metrics related to threads in the pool of executors, including:
        - total_threads: Total number of threads across all executors in the pool (including both used and available executors).
        - used_threads: Total number of threads across all currently used executors in the pool.
        - used_running: Total number of currently running threads across all currently used executors in the pool.
        - available_threads: Total number of threads across all currently available executors in the pool.
        - available_running: Total number of currently running threads across all currently available executors in the pool.
        """
        with self.lock:
            available_copy = copy.copy(self.pool_available)
            used_copy = copy.copy(self.pool_used)
        used_threads: int = 0
        used_running: int = 0
        available_threads: int = 0
        available_running: int = 0
        total_threads: int = 0
        for executor in used_copy:
            threads, running = executor.get_threads_metrics()
            used_threads += threads
            used_running += running
        for executor in available_copy:
            threads, running = executor.get_threads_metrics()
            available_threads += threads
            available_running += running
        total_threads = used_threads + len(used_copy) + available_threads + len(available_copy)
        result_dict = {
            "total_threads": total_threads,
            "used_threads": used_threads,
            "used_running": used_running,
            "available_threads": available_threads,
            "available_running": available_running
        }
        return result_dict
