
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
from typing import Callable
from typing import Optional

import asyncio
import sys

from asyncio import AbstractEventLoop


class EventLoopFactory:
    """
    Factory for creating asyncio event loops with a platform-appropriate type.

    On Windows the factory produces SelectorEventLoop instances; on other
    platforms it defers to asyncio's platform default. This is the
    forward-compatible replacement for the asyncio.set_event_loop_policy()
    pattern (using asyncio.WindowsSelectorEventLoopPolicy on Windows), which
    is deprecated in Python 3.14 and slated for removal.

    Two entry points are provided so callers can pick what matches their
    existing call site:
      - loop_factory(): returns a callable suitable for the loop_factory=
            keyword on asyncio.run() (Python 3.12+) and asyncio.Runner()
            (Python 3.11+). Returns None on platforms where asyncio's
            default is appropriate; None is the documented sentinel for
            "use default", so the result can be passed through unchanged
            on any platform.
      - new_event_loop(): drop-in replacement for asyncio.new_event_loop()
            at sites that construct a loop directly. Combine with
            asyncio.set_event_loop() to install the loop for the current
            thread before frameworks (e.g. Tornado) wrap it.
    """

    @staticmethod
    def loop_factory() -> Optional[Callable[[], AbstractEventLoop]]:
        """
        :return: A callable that constructs a platform-appropriate event
                 loop, or None if asyncio's default is appropriate. None is
                 the documented value asyncio.run() and asyncio.Runner()
                 accept to mean "use the default factory", so the return
                 value of this method can be forwarded unchanged on any
                 platform.
        """
        if sys.platform == "win32":
            return asyncio.SelectorEventLoop
        return None

    @staticmethod
    def new_event_loop() -> AbstractEventLoop:
        """
        :return: A newly-constructed event loop appropriate for the current
                 platform. On Windows this is a SelectorEventLoop; on other
                 platforms it is the loop type returned by
                 asyncio.new_event_loop().
        """
        factory: Optional[Callable[[], AbstractEventLoop]] = EventLoopFactory.loop_factory()
        if factory is not None:
            return factory()
        return asyncio.new_event_loop()
