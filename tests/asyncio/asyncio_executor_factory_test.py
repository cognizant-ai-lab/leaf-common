
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
Unit tests for AsyncioExecutorFactory's type selection.

The factory builds pools only, never a bare executor, so these tests check the
pool surface and the pool-of-one shape that long-lived callers use. The
SHARED_LOOP cases assert the property the browser depends on: nothing the
factory builds for that type starts a thread. threading.Thread.start is patched
to fail rather than merely counted, so a regression shows up as a test failure
at the point of the call rather than as a count mismatch later.
"""

from unittest import IsolatedAsyncioTestCase
from unittest import TestCase
from unittest.mock import patch

from leaf_common.asyncio.asyncio_executor import AsyncioExecutor
from leaf_common.asyncio.asyncio_executor_factory import AsyncioExecutorFactory
from leaf_common.asyncio.asyncio_executor_pool import AsyncioExecutorPool
from leaf_common.asyncio.asyncio_executor_types import AsyncioExecutorTypes
from leaf_common.asyncio.shared_loop_asyncio_executor import SharedLoopAsyncioExecutor
from leaf_common.asyncio.shared_loop_asyncio_executor_pool import SharedLoopAsyncioExecutorPool


class AsyncioExecutorFactoryTest(TestCase):
    """
    Tests the synchronous surface of AsyncioExecutorFactory.
    """

    def test_builds_pools_only(self) -> None:
        """
        The factory has no way to construct a bare executor. Executors come
        from a pool, so that every one of them has an owner.
        """
        self.assertFalse(hasattr(AsyncioExecutorFactory, "create_executor"))
        self.assertFalse(hasattr(AsyncioExecutorFactory, "EXECUTOR_CLASSES"))

    def test_creates_the_requested_pool_type(self) -> None:
        """
        Each type maps to its own pool class.
        """
        pool = AsyncioExecutorFactory.create_pool(AsyncioExecutorTypes.THREADED, reuse_mode=False)
        try:
            self.assertIsInstance(pool, AsyncioExecutorPool)
        finally:
            pool.shutdown()

        shared_pool = AsyncioExecutorFactory.create_pool(AsyncioExecutorTypes.SHARED_LOOP)
        self.assertIsInstance(shared_pool, SharedLoopAsyncioExecutorPool)

    def test_defaults_to_threaded(self) -> None:
        """
        Callers predating the factory got the threaded implementation, and a
        caller that names no type still does.
        """
        pool = AsyncioExecutorFactory.create_pool()
        try:
            self.assertIsInstance(pool, AsyncioExecutorPool)
        finally:
            pool.shutdown()

    def test_pool_hands_out_the_matching_executor(self) -> None:
        """
        A pool's executors are of the kind its type names, and arrive started,
        so callers never call start() themselves.
        """
        pool = AsyncioExecutorFactory.create_pool(AsyncioExecutorTypes.THREADED, reuse_mode=False)
        executor = pool.get_executor()
        try:
            self.assertIsInstance(executor, AsyncioExecutor)
            self.assertTrue(executor.get_event_loop().is_running())
        finally:
            pool.return_executor(executor)
            pool.shutdown()

    def test_pool_of_one_costs_no_gc_thread(self) -> None:
        """
        reuse_mode=False is how a long-lived caller holds exactly one executor.
        It must not start a GC thread, or every such caller would add one.
        """
        pool = AsyncioExecutorFactory.create_pool(AsyncioExecutorTypes.THREADED, reuse_mode=False)
        try:
            # pylint: disable=protected-access
            self.assertIsNone(pool._gc_thread)
        finally:
            pool.shutdown()

    def test_pool_arguments_are_passed_through(self) -> None:
        """
        create_pool() forwards the AsyncioExecutorPool arguments unchanged.
        """
        pool = AsyncioExecutorFactory.create_pool(AsyncioExecutorTypes.THREADED,
                                                  reuse_mode=True,
                                                  idle_timeout_seconds=11.0,
                                                  gc_sweep_interval_seconds=13.0,
                                                  max_workers=3)
        try:
            self.assertTrue(pool.reuse_mode)
            self.assertEqual(pool.idle_timeout_seconds, 11.0)
            self.assertEqual(pool.gc_sweep_interval_seconds, 13.0)
            self.assertEqual(pool.max_workers, 3)
        finally:
            pool.shutdown()

    def test_unknown_type_names_the_known_ones(self) -> None:
        """
        An unknown type fails loudly, and the message says what would work.
        """
        with self.assertRaises(ValueError) as pool_error:
            AsyncioExecutorFactory.create_pool("no-such-executor")
        self.assertIn(AsyncioExecutorTypes.SHARED_LOOP, str(pool_error.exception))
        self.assertIn(AsyncioExecutorTypes.THREADED, str(pool_error.exception))

    def test_every_declared_type_is_registered(self) -> None:
        """
        AsyncioExecutorTypes and the pool registry cannot drift apart.
        """
        declared = set(AsyncioExecutorTypes.ASYNCIO_EXECUTOR_TYPES)
        self.assertEqual(declared, set(AsyncioExecutorFactory.POOL_CLASSES.keys()))


class AsyncioExecutorFactorySharedLoopTest(IsolatedAsyncioTestCase):
    """
    Tests that the SHARED_LOOP type really is thread-free, which is the whole
    reason for it to exist.
    """

    async def test_shared_loop_type_starts_no_threads(self) -> None:
        """
        Building a shared-loop pool and using the executor it hands out touches
        no thread, and borrows the loop the caller is already on.
        """
        import asyncio  # pylint: disable=import-outside-toplevel

        with patch("threading.Thread.start", side_effect=AssertionError("No threads")):
            pool = AsyncioExecutorFactory.create_pool(AsyncioExecutorTypes.SHARED_LOOP,
                                                      max_workers=4)
            executor = pool.get_executor()
            self.assertIsInstance(executor, SharedLoopAsyncioExecutor)
            self.assertIs(executor.get_event_loop(), asyncio.get_running_loop())
            self.assertEqual(await executor.submit("request", lambda: 42), 42)
            pool.return_executor(executor)
            await executor.ashutdown(cancel_futures=False)
