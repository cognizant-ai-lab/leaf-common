
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
from typing import List

from leaf_common.parsers.parser import Parser


class BooleanParser(Parser):
    """
    Parser implementation getting a boolean from an object.

    String input is matched case-insensitively against a fixed set of
    truthy spellings ("true", "1", "on", "yes") and falsy spellings
    ("false", "0", "off", "no"), ignoring any leading or trailing whitespace.
    Strings that match neither set parse as False.

    None parses as False. Any other non-string input falls back to
    standard Python truthiness via bool().
    """

    def parse(self, input_obj: Any) -> bool:
        """
        Parses a boolean value from the given object.

        :param input_obj: the object to parse
        :return: a boolean parsed from that object
        """

        if input_obj is None:
            return False

        if isinstance(input_obj, str):
            # Strip surrounding whitespace before matching.
            # A primary use of this parser is environment-variable and config
            # parsing, where leading/trailing whitespace is easy to introduce
            # and invisible (a trailing space in a .env line, a docker-compose
            # environment entry, a copy-pasted "export FOO=true ").
            # Without the strip, "true " would silently parse as False.
            # See https://github.com/cognizant-ai-lab/leaf-common/issues/182
            lower: str = input_obj.strip().lower()

            true_values: List[str] = ['true', '1', 'on', 'yes']
            if lower in true_values:
                return True

            false_values: List[str] = ['false', '0', 'off', 'no']
            if lower in false_values:
                return False

            # Unrecognized strings (including empty / whitespace-only)
            # are treated as False rather than raising.
            return False

        return bool(input_obj)
