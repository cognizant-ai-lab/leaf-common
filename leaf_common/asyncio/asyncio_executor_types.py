
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

from typing import List


class AsyncioExecutorTypes():
    """
    Class containing string constants for the kinds of TaskExecutor
    that AsyncioExecutorFactory knows how to build.

    These are plain strings rather than an enum.Enum so that they survive
    transpilation to TypeScript as ordinary string constants, and so they can
    come straight out of a config file without a lookup step.
    """

    # An executor that owns a background thread and the event loop running on
    # it. The default, and the only one that supports blocking callers such as
    # AsyncToSyncGenerator.
    THREADED: str = "threaded"

    # An executor that borrows the caller's already-running event loop and
    # creates no threads. The variant for runtimes that have no threads to
    # give -- Pyodide in the browser, and transpiled JavaScript.
    SHARED_LOOP: str = "shared_loop"

    ASYNCIO_EXECUTOR_TYPES: List[str] = [THREADED, SHARED_LOOP]
