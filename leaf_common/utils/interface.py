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

from abc import ABCMeta


def interface(cls):
    """
    A class decorator that transforms a class into an interface.
    It prevents direct instantiation and ensures it uses ABCMeta
    so that abstract methods are properly enforced.
    """
    # Create a new class with ABCMeta to enforce abstract methods
    # This allows it to be multiply inherited cleanly
    interface_cls = ABCMeta(cls.__name__, cls.__bases__, dict(cls.__dict__))

    # Patch the __init__ to prevent direct instantiation of the interface itself
    def no_init(*args, **kwargs):
        raise TypeError(f"Cannot instantiate interface '{cls.__name__}' directly.")

    interface_cls.__init__ = no_init
    return interface_cls
