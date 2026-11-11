
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

from unittest import TestCase

from leaf_common.config.config_util import ConfigUtil


class TestConfigUtil(TestCase):
    """
    LLM policies and other config-driven sites delegate boolean-key reads to
    ConfigUtil.get_bool(). Thus it must accept the usual boolean-like forms that
    HOCON / JSON / env configs supply, and fall back safely on unknown input.

    Verifies ConfigUtil.get_bool() across:
      - absence (returns default)
      - native bool (returned as-is)
      - recognized string forms (true/yes/on/1/enable/enabled vs
        false/no/off/0/disable/disabled, case-insensitive)
      - int and float (0 is False; non-zero is True)
      - unrecognized values (returns default)

    Also verifies ConfigUtil.is_true(), which get_bool() delegates to.
    """

    # ---- Defaults / absence ---------------------------------------------------

    def test_absent_key_returns_default_false(self) -> None:
        """
        When the key is missing and no default is supplied, returns False.
        """
        self.assertIs(ConfigUtil.get_bool({}, "streaming"), False)

    def test_absent_key_returns_default_true_when_supplied(self) -> None:
        """
        When the key is missing, the explicit default is returned.
        """
        self.assertIs(ConfigUtil.get_bool({}, "streaming", default=True), True)

    def test_unrelated_key_does_not_affect_lookup(self) -> None:
        """
        Only the requested key is consulted; siblings are ignored.
        """
        self.assertIs(ConfigUtil.get_bool({"other": True}, "streaming"), False)

    # ---- Native bool ----------------------------------------------------------

    def test_explicit_true_returns_true(self) -> None:
        """
        A literal Python True is returned as True.
        """
        self.assertIs(ConfigUtil.get_bool({"streaming": True}, "streaming"), True)

    def test_explicit_false_returns_false(self) -> None:
        """
        A literal Python False is returned as False.
        """
        self.assertIs(ConfigUtil.get_bool({"streaming": False}, "streaming"), False)

    # ---- String forms ---------------------------------------------------------

    def test_string_true_yes_resolve_to_true(self) -> None:
        """
        "true" / "yes" (case-insensitive, surrounding whitespace) -> True.
        """
        self.assertIs(ConfigUtil.get_bool({"k": "true"}, "k"), True)
        self.assertIs(ConfigUtil.get_bool({"k": "TRUE"}, "k"), True)
        self.assertIs(ConfigUtil.get_bool({"k": " Yes "}, "k"), True)

    def test_string_false_no_resolve_to_false(self) -> None:
        """
        "false" / "no" (case-insensitive, surrounding whitespace) -> False.
        """
        self.assertIs(ConfigUtil.get_bool({"k": "false"}, "k"), False)
        self.assertIs(ConfigUtil.get_bool({"k": "NO"}, "k"), False)
        self.assertIs(ConfigUtil.get_bool({"k": " False "}, "k"), False)

    def test_unrecognized_string_returns_default(self) -> None:
        """
        Strings that aren't yes/no/true/false fall back to default.
        """
        self.assertIs(ConfigUtil.get_bool({"k": "maybe"}, "k"), False)
        self.assertIs(ConfigUtil.get_bool({"k": "maybe"}, "k", default=True), True)
        self.assertIs(ConfigUtil.get_bool({"k": ""}, "k"), False)

    # ---- Integer forms --------------------------------------------------------

    def test_nonzero_int_is_true(self) -> None:
        """
        Any non-zero int is interpreted as True.
        """
        self.assertIs(ConfigUtil.get_bool({"k": 1}, "k"), True)
        self.assertIs(ConfigUtil.get_bool({"k": -1}, "k"), True)
        self.assertIs(ConfigUtil.get_bool({"k": 42}, "k"), True)

    def test_zero_int_is_false(self) -> None:
        """
        Zero is interpreted as False.
        """
        self.assertIs(ConfigUtil.get_bool({"k": 0}, "k"), False)

    # ---- Unrecognized values --------------------------------------------------

    def test_none_value_returns_default(self) -> None:
        """
        A literal None (e.g. HOCON `null`) falls back to default.
        """
        self.assertIs(ConfigUtil.get_bool({"k": None}, "k"), False)
        self.assertIs(ConfigUtil.get_bool({"k": None}, "k", default=True), True)

    def test_list_value_returns_default(self) -> None:
        """
        Lists are not recognized; fall back to default.
        """
        self.assertIs(ConfigUtil.get_bool({"k": ["true"]}, "k"), False)
        self.assertIs(ConfigUtil.get_bool({"k": []}, "k"), False)

    def test_dict_value_returns_default(self) -> None:
        """
        Dicts are not recognized; fall back to default.
        """
        self.assertIs(ConfigUtil.get_bool({"k": {"true": True}}, "k"), False)

    # ---- Extended string forms ------------------------------------------------

    def test_string_on_1_enable_resolve_to_true(self) -> None:
        """
        "on" / "1" / "enable" / "enabled" (case-insensitive, whitespace) -> True.
        """
        true_strings: list[str] = ["on", "ON", "1", " 1 ", "enable", "Enabled", " ENABLED "]
        # Each true-like string must resolve to True, even when the default is False.
        for true_string in true_strings:
            true_string: str
            self.assertIs(ConfigUtil.get_bool({"k": true_string}, "k", default=False), True, true_string)

    def test_string_off_0_disable_resolve_to_false(self) -> None:
        """
        "off" / "0" / "disable" / "disabled" (case-insensitive, whitespace) -> False.
        """
        false_strings: list[str] = ["off", "OFF", "0", " 0 ", "disable", "Disabled", " DISABLED "]
        # Each false-like string must resolve to False, even when the default is True.
        for false_string in false_strings:
            false_string: str
            self.assertIs(ConfigUtil.get_bool({"k": false_string}, "k", default=True), False, false_string)

    def test_numeric_strings_other_than_0_1_return_default(self) -> None:
        """
        Only "0" and "1" are recognized numeric strings; others fall back to default.
        """
        self.assertIs(ConfigUtil.get_bool({"k": "2"}, "k"), False)
        self.assertIs(ConfigUtil.get_bool({"k": "2"}, "k", default=True), True)
        self.assertIs(ConfigUtil.get_bool({"k": "0.0"}, "k", default=True), True)

    # ---- Float forms ----------------------------------------------------------

    def test_float_zero_is_false_nonzero_is_true(self) -> None:
        """
        A float zero is interpreted as False; any non-zero float as True.
        """
        self.assertIs(ConfigUtil.get_bool({"k": 1.0}, "k"), True)
        self.assertIs(ConfigUtil.get_bool({"k": 0.5}, "k"), True)
        self.assertIs(ConfigUtil.get_bool({"k": -2.5}, "k"), True)
        self.assertIs(ConfigUtil.get_bool({"k": 0.0}, "k", default=True), False)
        self.assertIs(ConfigUtil.get_bool({"k": -0.0}, "k", default=True), False)

    # ---- is_true() directly ---------------------------------------------------

    def test_is_true_recognized_forms(self) -> None:
        """
        Recognized bools, strings and numbers resolve to their boolean meaning, regardless of default.
        """
        self.assertIs(ConfigUtil.is_true(True), True)
        self.assertIs(ConfigUtil.is_true(False, default=True), False)
        self.assertIs(ConfigUtil.is_true("yes"), True)
        self.assertIs(ConfigUtil.is_true(" Enabled "), True)
        self.assertIs(ConfigUtil.is_true("off", default=True), False)
        self.assertIs(ConfigUtil.is_true("0", default=True), False)
        self.assertIs(ConfigUtil.is_true(1), True)
        self.assertIs(ConfigUtil.is_true(0, default=True), False)
        self.assertIs(ConfigUtil.is_true(0.1), True)
        self.assertIs(ConfigUtil.is_true(0.0, default=True), False)

    def test_is_true_unrecognized_returns_default(self) -> None:
        """
        Unrecognized values fall back to the supplied default, which is False when not given.
        """
        self.assertIs(ConfigUtil.is_true("maybe"), False)
        self.assertIs(ConfigUtil.is_true(None), False)
        unrecognized_values: list[object] = [None, "maybe", "", [], {}, ["true"], object()]
        # Each unrecognized value must give back whichever default is supplied.
        for unrecognized_value in unrecognized_values:
            unrecognized_value: object
            self.assertIs(ConfigUtil.is_true(unrecognized_value, default=True), True, repr(unrecognized_value))
            self.assertIs(ConfigUtil.is_true(unrecognized_value, default=False), False, repr(unrecognized_value))
