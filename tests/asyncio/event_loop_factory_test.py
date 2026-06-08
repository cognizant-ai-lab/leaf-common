
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
Unit tests for EventLoopFactory's platform-selection behavior.

These tests patch sys.platform so the Windows branch can be exercised on a
non-Windows test runner without requiring a Windows-only CI job.
"""

import asyncio
import sys

from unittest import TestCase
from unittest.mock import patch

from leaf_common.asyncio.event_loop_factory import EventLoopFactory


class EventLoopFactoryTest(TestCase):
    """
    Tests for EventLoopFactory.loop_factory() and EventLoopFactory.new_event_loop()
    under various emulated sys.platform values.
    """

    def test_loop_factory_returns_selector_loop_class_on_windows(self):
        """
        On Windows (sys.platform == 'win32'), loop_factory() returns the
        asyncio.SelectorEventLoop class as the factory callable.
        """
        with patch.object(sys, "platform", "win32"):
            self.assertIs(EventLoopFactory.loop_factory(), asyncio.SelectorEventLoop)

    def test_loop_factory_returns_none_on_linux(self):
        """
        On Linux (sys.platform == 'linux'), loop_factory() returns None so
        callers defer to asyncio's platform default.
        """
        with patch.object(sys, "platform", "linux"):
            self.assertIsNone(EventLoopFactory.loop_factory())

    def test_loop_factory_returns_none_on_macos(self):
        """
        On macOS (sys.platform == 'darwin'), loop_factory() returns None so
        callers defer to asyncio's platform default.
        """
        with patch.object(sys, "platform", "darwin"):
            self.assertIsNone(EventLoopFactory.loop_factory())

    def test_loop_factory_returns_none_on_cygwin(self):
        """
        On Cygwin (sys.platform == 'cygwin', a Unix-like Windows environment),
        loop_factory() returns None: only the exact value 'win32' triggers
        the Selector override.
        """
        with patch.object(sys, "platform", "cygwin"):
            self.assertIsNone(EventLoopFactory.loop_factory())

    def test_new_event_loop_constructs_selector_loop_on_emulated_windows(self):
        """
        new_event_loop() constructs an asyncio.SelectorEventLoop instance
        when sys.platform is emulated as 'win32'.
        """
        with patch.object(sys, "platform", "win32"):
            loop = EventLoopFactory.new_event_loop()
            try:
                self.assertIsInstance(loop, asyncio.SelectorEventLoop)
            finally:
                loop.close()

    def test_new_event_loop_returns_default_loop_on_non_windows(self):
        """
        new_event_loop() returns an AbstractEventLoop instance (the platform
        default) when sys.platform is emulated as a non-Windows value.
        """
        with patch.object(sys, "platform", "linux"):
            loop = EventLoopFactory.new_event_loop()
            try:
                self.assertIsInstance(loop, asyncio.AbstractEventLoop)
            finally:
                loop.close()
