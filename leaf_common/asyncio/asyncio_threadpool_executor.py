
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
from typing import Tuple
from concurrent.futures import ThreadPoolExecutor
import logging
import functools
import threading

class AsyncioThreadPoolExecutor(ThreadPoolExecutor):
    """
    Class instrumenting a ThreadPoolExecutor with some additional run-time metrics
    such as number of created and active threads.
    """
    def __init__(self, *args, **kwargs):
        """Constructor."""
        super().__init__(*args, **kwargs)
        self.running: int = 0
        self.lock: threading.Lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _format_callable(self, fn):
        if isinstance(fn, functools.partial):
            return (
                f"partial("
                f"{self._format_callable(fn.func)}, "
                f"args={fn.args!r}, "
                f"kwargs={fn.keywords!r})"
            )

        return f"{fn.__module__}.{fn.__qualname__}"

    def submit(self, fn, /, *args, **kwargs):
        """
        Override of submit method to wrap the submitted function with additional logic
        for counting the number of active (running) threads.
        """
        def wrapped(*a, **kw):
            with self.lock:
                self.running += 1
            try:
                return fn(*a, **kw)
            finally:
                with self.lock:
                    self.running -= 1

        name = self._format_callable(fn)
        print(f"======================Submitting task {name} [{self.running}] to {self.__class__.__name__}")
        return super().submit(wrapped, *args, **kwargs)

    def get_threads_metrics(self) -> Tuple[int, int]:
        """
        Get number of threads in the pool and number of currently running threads.
         :return: Tuple of (number of threads in the pool, number of currently running threads)
         Note: number of threads in the pool is an approximation, as ThreadPoolExecutor does not provide
               a direct way to get this information. The method tries to access the protected member _threads,
               which may not be available in all implementations of ThreadPoolExecutor.
        """
        num_threads: int = 0
        try:
            num_threads = len(self._threads)
        except AttributeError:
            self.logger.info("FAILED to get number of threads from %s", self.__class__.__name__)
        with self.lock:
            return num_threads, self.running
