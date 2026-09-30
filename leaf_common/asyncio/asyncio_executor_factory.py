
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

from typing import Any
from typing import Dict
from typing import List
from typing import Type

from leaf_common.asyncio.asyncio_executor_pool import AsyncioExecutorPool
from leaf_common.asyncio.asyncio_executor_types import AsyncioExecutorTypes
from leaf_common.asyncio.shared_loop_asyncio_executor_pool import SharedLoopAsyncioExecutorPool


class AsyncioExecutorFactory():
    """
    Factory class for executor pools.

    Given a string from AsyncioExecutorTypes, create_pool() dishes out the pool
    that hands out that kind of executor.

    Note what this factory deliberately does NOT do: build a bare executor.
    Executors are constructed only by their pool, so that every executor in the
    system has an owner that knows how to start it, hand it out, and tear it
    down. A caller that wants one asks a pool for it:

        pool = AsyncioExecutorFactory.create_pool(reuse_mode=False)
        executor = pool.get_executor()      # already started
        ...
        pool.return_executor(executor)      # shuts it down when reuse_mode=False
        pool.shutdown()

    A caller needing exactly one long-lived executor -- a background service,
    say -- makes a pool-of-one with reuse_mode=False. That costs nothing: the
    pool's GC thread only exists when reuse_mode is True.

    Why a factory at all: the two pool implementations are not interchangeable
    at run time, they are interchangeable per *deployment*. A server process
    wants the threaded executor; a browser has no threads to run it on, so it
    wants the shared-loop one. The choice belongs to whoever configures the
    process, not to the code doing the submitting.

    Two deliberate constraints, both so this survives transpilation to JavaScript:

    1. The registry below is a static dict of already-imported classes.
       Resolving an implementation by module name through importlib would not
       work in a browser bundle, where the importlib stub is built on Node's
       createRequire.
    2. The type is an explicit argument. This class deliberately does not sniff
       sys.platform or probe for a running loop to pick for itself, because
       platform branching is exactly what does not survive the trip.
    """

    # Maps an AsyncioExecutorTypes string to the pool class that hands out
    # -- and solely constructs -- that kind of executor.
    POOL_CLASSES: Dict[str, Type[Any]] = {
        AsyncioExecutorTypes.THREADED: AsyncioExecutorPool,
        AsyncioExecutorTypes.SHARED_LOOP: SharedLoopAsyncioExecutorPool,
    }

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    @staticmethod
    def create_pool(executor_type: str = AsyncioExecutorTypes.THREADED,
                    reuse_mode: bool = True,
                    *,
                    idle_timeout_seconds: float = AsyncioExecutorPool.DEFAULT_IDLE_TIMEOUT_SECONDS,
                    gc_sweep_interval_seconds: float = AsyncioExecutorPool.DEFAULT_GC_SWEEP_INTERVAL_SECONDS,
                    max_workers: int = None) -> Any:
        """
        Create a pool that hands out executors of the requested type.

        The arguments after executor_type are those of AsyncioExecutorPool, and
        are passed through unchanged. The SHARED_LOOP pool accepts all of them
        for compatibility but honors none of them: it has no reuse, no idle
        expiry, no worker threads, and no GC thread to sweep with.

        :param executor_type: One of AsyncioExecutorTypes. Defaults to THREADED,
                    which is what every caller predating this factory got.
        :param reuse_mode: True if requested executor instances are taken from a
                    pool of available ones; False if they are created new and
                    shut down on return. Pass False for a pool-of-one holding a
                    single long-lived executor.
        :param idle_timeout_seconds: Idle time in seconds after which a pooled
                    executor is collected. Only applies when reuse_mode is True.
        :param gc_sweep_interval_seconds: Interval in seconds at which the GC
                    thread looks for stale executors. Only applies when
                    reuse_mode is True.
        :param max_workers: Maximum number of threads per executor.
        :return: A new executor pool of the requested type
        """
        pool_class: Type[Any] = AsyncioExecutorFactory.POOL_CLASSES.get(executor_type)
        if pool_class is None:
            known: List[str] = sorted(AsyncioExecutorFactory.POOL_CLASSES.keys())
            raise ValueError(f"Unknown executor pool type '{executor_type}'. "
                             f"Known types are: {known}")
        return pool_class(reuse_mode,
                          idle_timeout_seconds=idle_timeout_seconds,
                          gc_sweep_interval_seconds=gc_sweep_interval_seconds,
                          max_workers=max_workers)
