
# Copyright (C) 2019-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# leaf-common SDK Software in commercial settings.
#
# END COPYRIGHT
"""
See class comment for details
"""

from unittest import TestCase

from leaf_common.config.dictionary_overlay import DictionaryOverlay


class DictionaryOverlayTest(TestCase):
    """
    Test for DictionaryOverlay.
    """

    def setUp(self):
        self.overlay = DictionaryOverlay()

    def test_assumptions(self):
        """
        Does the constructor even work?
        """

        self.assertIsNotNone(self.overlay)

    def test_basis_none(self):
        """
        Tests for when basis dictionary is None
        """

        basis = None
        overlay = None
        result = self.overlay.overlay(basis, overlay)
        self.assertIsNone(result)

        overlay = {"foo": 1}
        result = self.overlay.overlay(basis, overlay)
        self.assertIsNotNone(result)
        self.assertIsNot(result, overlay)

    def test_overlay_none(self):
        """
        Tests for when overlay dictionary is None
        """

        basis = None
        overlay = None
        result = self.overlay.overlay(basis, overlay)
        self.assertIsNone(result)

        basis = {"foo": 1}
        result = self.overlay.overlay(basis, overlay)
        self.assertIsNotNone(result)
        self.assertIsNot(result, basis)

    def test_shallow_key(self):
        """
        Tests stuff for non-nested dictionaries
        """

        basis = {"foo": 1}
        overlay = {"foo": 2}
        result = self.overlay.overlay(basis, overlay)
        num_keys = len(result)
        self.assertEqual(num_keys, 1)
        value = result.get("foo")
        self.assertEqual(value, 2)

        overlay = {"bar": 2}
        result = self.overlay.overlay(basis, overlay)
        num_keys = len(result)
        self.assertEqual(num_keys, 2)
        value = result.get("foo")
        self.assertEqual(value, 1)
        value = result.get("bar")
        self.assertEqual(value, 2)

        basis = {"bar": False}
        overlay = {"bar": ' True '}
        result = self.overlay.overlay(basis, overlay)
        num_keys = len(result)
        self.assertEqual(num_keys, 1)
        value = result.get("bar")
        self.assertEqual(value, True)

    def test_deep_key_different_values(self):
        """
        Tests stuff for nested dictionaries
        """

        basis = {"nested": {"foo": 1}}
        overlay = {"nested": {"foo": 2}}
        result = self.overlay.overlay(basis, overlay)
        num_keys = len(result)
        self.assertEqual(num_keys, 1)
        nested = result.get("nested")
        num_keys = len(nested)
        self.assertEqual(num_keys, 1)
        value = nested.get("foo")
        self.assertEqual(value, 2)

        overlay = {"nested": {"bar": 2}}
        result = self.overlay.overlay(basis, overlay)
        num_keys = len(result)
        self.assertEqual(num_keys, 1)
        nested = result.get("nested")
        num_keys = len(nested)
        self.assertEqual(num_keys, 2)
        value = nested.get("foo")
        self.assertEqual(value, 1)
        value = nested.get("bar")
        self.assertEqual(value, 2)

        overlay = {"nested": 3}
        result = self.overlay.overlay(basis, overlay)
        num_keys = len(result)
        self.assertEqual(num_keys, 1)
        nested = result.get("nested")
        self.assertEqual(nested, 3)

    def test_keys_not_from_basis_dictionary(self):
        """
        Tests that we can detect keys not present
        in the basis dictionary and throw an exception.
        """

        basis = {"foo": 1}
        overlay = {"foo1": 2}
        self.assertRaises(ValueError, self.overlay.overlay, basis, overlay, False)

        basis = {"nested": {"foo": 1}}
        overlay = {"nested": {"foo1": 2}}
        self.assertRaises(ValueError, self.overlay.overlay, basis, overlay, False)

        basis = {"nested": {"foo": 1}}
        overlay = {"nested1": {"foo": 2}}
        self.assertRaises(ValueError, self.overlay.overlay, basis, overlay, False)
