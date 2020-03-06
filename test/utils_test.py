"""
Unit tests for list utils code
"""

from unittest import TestCase

from collection_utils.list_utils import split_list


class ListUtilsTest(TestCase):
    """
    Unit tests for list utils code
    """

    def setUp(self):
        self._master_list = self._generate_list(10)

    def test_split_list_normal_case(self):
        """
        Verify we can split a list normally (no edge cases)
        :return: None
        """
        lists = split_list(self._master_list, 5)

        self.assertEqual(2, len(lists))

        expected_sublist0 = self._generate_list(5)
        self.assertEqual(expected_sublist0, lists[0])

        expected_sublist1 = self._generate_list_with_range(5, 10)
        self.assertEqual(expected_sublist1, lists[1])

    def test_split_list_remainder(self):
        """
        Verify we can split a list with items remaining
        :return: None
        """
        lists = split_list(self._master_list, 3)

        self.assertEqual(4, len(lists))

        expected_sublist0 = self._generate_list(3)
        self.assertEqual(expected_sublist0, lists[0])

        expected_sublist1 = self._generate_list_with_range(3, 6)
        self.assertEqual(expected_sublist1, lists[1])

        expected_sublist2 = self._generate_list_with_range(6, 9)
        self.assertEqual(expected_sublist2, lists[2])

        expected_sublist3 = self._generate_list_with_range(9, 10)
        self.assertEqual(expected_sublist3, lists[3])

    def test_split_whole_list(self):
        """
         Verify we can split a list into a single chunk (so, not really splitting)
         :return: None
         """
        lists = split_list(self._master_list, 10)

        self.assertEqual(1, len(lists))
        self.assertEqual(self._master_list, lists[0])

    def test_split_chunk_bigger_than_list(self):
        """
        Verify we can split a list into a single chunk (so, not really splitting)
        :return: None
        """
        lists = split_list(self._master_list, 20)

        self.assertEqual(1, len(lists))
        self.assertEqual(self._master_list, lists[0])

    def test_split_empty_list(self):
        """
        Verify trivial edge case of splitting an empty list
        :return: None
        """
        lists = split_list([], 5)

        self.assertEqual(0, len(lists))

    @staticmethod
    def _generate_list(num_items):
        return ['item' + str(n) for n in range(num_items)]

    @staticmethod
    def _generate_list_with_range(lower, upper):
        return ['item' + str(n) for n in range(lower, upper)]
