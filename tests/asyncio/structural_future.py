
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
from typing import Callable

import asyncio


class StructuralFuture:
    """
    A Future-compatible object that is deliberately NOT an asyncio.Future
    subclass.

    asyncio.isfuture() accepts anything whose type carries a non-None
    _asyncio_future_blocking, so this satisfies the Future protocol
    structurally while failing isinstance(obj, asyncio.Future). That gap is
    what separates a duck-typed check from a subclass check, and this class
    exists to ensure we are doing the right check.

    Work is delegated to an inner asyncio.Future so awaiting and cancelling
    behave normally. cancel_calls records hand-offs from code under test.
    """

    # What asyncio.isfuture() looks for. Must be non-None.
    _asyncio_future_blocking: bool = False

    def __init__(self, loop: asyncio.AbstractEventLoop):
        """
        Constructor

        :param loop: The loop this Future claims to belong to
        """
        self._loop: asyncio.AbstractEventLoop = loop
        self._inner: asyncio.Future = loop.create_future()
        self.cancel_calls: int = 0

    def get_loop(self) -> asyncio.AbstractEventLoop:
        """
        :return: The loop this Future belongs to
        """
        return self._loop

    def done(self) -> bool:
        """
        :return: True if this Future has settled
        """
        return self._inner.done()

    def cancelled(self) -> bool:
        """
        :return: True if this Future was cancelled
        """
        return self._inner.cancelled()

    # msg is part of the Future protocol's signature; this stand-in
    # ignores it.
    # pylint: disable=unused-argument
    def cancel(self, msg: Any = None) -> bool:
        """
        Cancel the inner Future, recording that this was asked for.

        :param msg: Cancellation message, accepted for signature parity
        :return: True if cancellation was requested
        """
        self.cancel_calls += 1
        return self._inner.cancel()

    def result(self) -> Any:
        """
        :return: The settled result
        """
        return self._inner.result()

    def set_result(self, value: Any) -> None:
        """
        Settle this Future with a value.

        :param value: The result to settle with
        """
        self._inner.set_result(value)

    def exception(self) -> BaseException:
        """
        :return: The settled exception, if any
        """
        return self._inner.exception()

    # context is part of the Future protocol's signature; this stand-in
    # has no use for it.
    # pylint: disable=unused-argument
    def add_done_callback(self, callback: Callable, *, context: Any = None) -> None:
        """
        Register a callback, handing it this object rather than the inner one.

        :param callback: The callback to run on completion
        :param context: Accepted for signature parity; ignored
        """
        self._inner.add_done_callback(lambda _inner: callback(self))

    # callback is part of the Future protocol's signature; nothing under
    # test removes a callback, so this stand-in always reports none removed.
    # pylint: disable=unused-argument
    def remove_done_callback(self, callback: Callable) -> int:
        """
        :param callback: The callback to remove
        :return: How many callbacks were removed
        """
        return 0

    def __await__(self) -> Any:
        """
        :return: The inner Future's await iterator
        """
        return self._inner.__await__()
