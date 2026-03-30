
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
See class comment for details
"""

from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch


from leaf_common.config.resolver_util import ResolverUtil

RESOLVER_PATH = "leaf_common.config.resolver.Resolver.resolve_class_in_module"


class ResolverUtilTest(TestCase):
    """
    Tests for ResolverUtil.
    """

    # -------------------------------------------------------------------------
    # create_class tests
    # -------------------------------------------------------------------------

    def test_create_class_none_returns_none(self):
        """
        None class_name should return None without raising.
        """
        result = ResolverUtil.create_class(None, "test_source", object)
        self.assertIsNone(result)

    def test_create_class_empty_string_returns_none(self):
        """
        Empty class_name should return None without raising.
        """
        result = ResolverUtil.create_class("", "test_source", object)
        self.assertIsNone(result)

    def test_create_class_too_few_parts_raises(self):
        """
        A class_name with no dots (single part) should raise ValueError.
        """
        with self.assertRaises(ValueError):
            ResolverUtil.create_class("ClassName", "test_source", object)

    def test_create_class_two_part_name(self):
        """
        <package_name>.<ClassName> form should resolve correctly.
        """
        mock_class = MagicMock()
        mock_class.__mro__ = [mock_class, object]

        with patch(RESOLVER_PATH, return_value=mock_class) as mock_resolve, \
             patch("builtins.issubclass", return_value=True):
            result = ResolverUtil.create_class("my_package.MyClass", "test_source", object)

        mock_resolve.assert_called_once_with("MyClass", module_name="my_package")
        self.assertIs(result, mock_class)

    def test_create_class_three_part_name(self):
        """
        <package_name>.<module_name>.<ClassName> form should resolve correctly.
        """
        mock_class = MagicMock()

        with patch(RESOLVER_PATH, return_value=mock_class) as mock_resolve, \
             patch("builtins.issubclass", return_value=True):
            result = ResolverUtil.create_class(
                "my_package.my_module.MyClass", "test_source", object
            )

        mock_resolve.assert_called_once_with("MyClass", module_name="my_module")
        self.assertIs(result, mock_class)

    def test_create_class_multi_part_package(self):
        """
        <pkg>.<sub>.<module>.<ClassName> — everything before the last two parts
        is treated as the package path.
        """
        mock_class = MagicMock()

        with patch(RESOLVER_PATH, return_value=mock_class) as mock_resolve, \
             patch("builtins.issubclass", return_value=True):
            result = ResolverUtil.create_class(
                "my_pkg.sub_pkg.my_module.MyClass", "test_source", object
            )

        mock_resolve.assert_called_once_with("MyClass", module_name="my_module")
        self.assertIs(result, mock_class)

    def test_create_class_attribute_error_raises_value_error(self):
        """
        If resolve_class_in_module raises AttributeError, a ValueError is raised.
        """
        with patch(RESOLVER_PATH, side_effect=AttributeError("not found")):
            with self.assertRaises(ValueError):
                ResolverUtil.create_class(
                    "my_package.my_module.MyClass", "test_source", object
                )

    def test_create_class_wrong_type_raises_value_error(self):
        """
        If the resolved class is not a subclass of type_of_class, a ValueError is raised.
        """
        class Base:
            """Base class for type-check testing."""

        class NotBase:
            """Class that does not inherit from Base."""

        with patch(RESOLVER_PATH, return_value=NotBase):
            with self.assertRaises(ValueError):
                ResolverUtil.create_class(
                    "my_package.my_module.NotBase", "test_source", Base
                )

    # -------------------------------------------------------------------------
    # create_instance tests
    # -------------------------------------------------------------------------

    def test_create_instance_none_returns_none(self):
        """
        None class_name propagates through create_class and returns None.
        """
        result = ResolverUtil.create_instance(None, "test_source", object)
        self.assertIsNone(result)

    def test_create_instance_creates_object(self):
        """
        A valid class_name should produce an instance of the resolved class.
        """
        mock_instance = MagicMock()
        mock_class = MagicMock(return_value=mock_instance)

        with patch(RESOLVER_PATH, return_value=mock_class), \
             patch("builtins.issubclass", return_value=True):
            result = ResolverUtil.create_instance(
                "my_package.my_module.MyClass", "test_source", object
            )

        mock_class.assert_called_once_with()
        self.assertIs(result, mock_instance)

    def test_create_instance_no_args_constructor_raises_value_error(self):
        """
        If the class cannot be instantiated without args, a ValueError is raised.
        """
        mock_class = MagicMock(side_effect=TypeError("__init__ requires args"))

        with patch(RESOLVER_PATH, return_value=mock_class), \
             patch("builtins.issubclass", return_value=True):
            with self.assertRaises(ValueError):
                ResolverUtil.create_instance(
                    "my_package.my_module.MyClass", "test_source", object
                )

    # -------------------------------------------------------------------------
    # create_type tests
    # -------------------------------------------------------------------------

    def test_create_type_none_returns_none(self):
        """
        None or empty fully_qualified_name should return None.
        """
        self.assertIsNone(ResolverUtil.create_type(None))
        self.assertIsNone(ResolverUtil.create_type(""))

    def test_create_type_resolves_class(self):
        """
        A fully qualified name should resolve to the correct class via Resolver.
        """
        mock_class = MagicMock()

        with patch(RESOLVER_PATH, return_value=mock_class) as mock_resolve:
            result = ResolverUtil.create_type("my_package.my_module.MyClass")

        mock_resolve.assert_called_once_with(
            "MyClass",
            module_name="my_package.my_module",
            raise_if_not_found=True,
            install_if_missing=None,
        )
        self.assertIs(result, mock_class)

    # -------------------------------------------------------------------------
    # create_type_tuple tests
    # -------------------------------------------------------------------------

    def test_create_type_tuple_empty_list(self):
        """
        An empty or None type_list should return an empty tuple.
        """
        self.assertEqual(ResolverUtil.create_type_tuple([]), ())
        self.assertEqual(ResolverUtil.create_type_tuple(None), ())

    def test_create_type_tuple_resolves_types(self):
        """
        Each resolvable name in the list should appear in the returned tuple.
        """
        mock_class_a = MagicMock()
        mock_class_b = MagicMock()

        side_effects = [mock_class_a, mock_class_b]

        with patch(RESOLVER_PATH, side_effect=side_effects):
            result = ResolverUtil.create_type_tuple([
                "pkg.mod.ClassA",
                "pkg.mod.ClassB",
            ])

        self.assertEqual(len(result), 2)
        self.assertIn(mock_class_a, result)
        self.assertIn(mock_class_b, result)

    def test_create_type_tuple_skips_unresolvable(self):
        """
        Types that cannot be resolved (raise_if_not_found=False) are skipped.
        """
        mock_class_a = MagicMock()

        with patch(RESOLVER_PATH, side_effect=[mock_class_a, None]):
            result = ResolverUtil.create_type_tuple([
                "pkg.mod.ClassA",
                "pkg.mod.Missing",
            ])

        self.assertEqual(len(result), 1)
        self.assertIn(mock_class_a, result)
