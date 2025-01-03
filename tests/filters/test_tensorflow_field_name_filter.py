
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
Copyright (C) 2021-2023 Cognizant Digital Business, Evolutionary AI.
All Rights Reserved.
Issued under the Academic Public License.

You can be released from the terms, and requirements of the Academic Public
License by purchasing a commercial license.
Purchase of a commercial license is mandatory for any use of the
unileaf-util SDK Software in commercial settings.

END COPYRIGHT
"""


from unittest import TestCase

from leaf_common.filters.tensorflow_field_name_filter import TensorFlowFieldNameFilter


class TestTensorFlowFieldNameFilter(TestCase):
    """
    Tests the TensorFlowFieldNameFilter class
    """

    def test_instantiation(self):
        """
        Tests that the class can be instantiated
        """

        tf_filter = TensorFlowFieldNameFilter()
        self.assertIsNotNone(tf_filter)

    def test_untouched(self):
        """
        Tests that strings that should not be touched are not
        """

        tf_filter = TensorFlowFieldNameFilter()

        instring = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.\\-"
        expected = instring
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)

        instring = ""
        expected = instring
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)

        instring = None
        expected = instring
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)

    def test_trim(self):
        """
        Tests that strings that should be whitespace trimmed are
        """

        tf_filter = TensorFlowFieldNameFilter()

        instring = " Field_Name    "
        expected = "Field_Name"
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)

    def test_single_replacements(self):
        """
        Tests that strings that should have one thing be replaced do
        """

        tf_filter = TensorFlowFieldNameFilter()

        instring = "Field Name"
        expected = "Field_Name"
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)

        instring = "Failure%"
        expected = "Failurepercnt"
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)

        instring = "Array[0]"
        expected = "Arraylsqb0rsqb"
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)

    def test_multiple_replacements(self):
        """
        Tests that strings that should have more than one thing replaced do
        """
        tf_filter = TensorFlowFieldNameFilter()

        instring = "Multi Word Field"
        expected = "Multi_Word_Field"
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)

        instring = "Construction $"
        expected = "Construction_dollar"
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)

        instring = "$ @ time of purchase"
        expected = "dollar_commat_time_of_purchase"
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)

    def test_single_exclusions(self):
        """
        Tests that strings that should have single chars excluded with the catch-all rule
        """
        tf_filter = TensorFlowFieldNameFilter()

        instring = "\u0123\u0127unicode"
        expected = "--unicode"
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)

    def test_multiple_exclusions(self):
        """
        Tests that strings that should have multiple chars excluded with the catch-all rule
        """
        tf_filter = TensorFlowFieldNameFilter()

        instring = "\u0123\u0123unicode"
        expected = "--unicode"
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)

    def test_real_cases(self):
        """
        Tests real cases found in the wild
        ... or approximations thereof to hide the names of the innocent.
        """

        tf_filter = TensorFlowFieldNameFilter()

        instring = "RETAILER PURCHASES/"
        expected = "RETAILER_PURCHASESsol"
        outstring = tf_filter.filter(instring)
        self.assertEqual(outstring, expected)
