"""
Unit tests for list utils code
"""

from unittest import TestCase

from collection_utils.list_utils import split_list


class ListUtilsTest(TestCase):
    def setUp(self):
        self._master_list = self.generate_list(10)

    def test_split_list_normal_case(self):
        lists = split_list(self._master_list, 5)

        self.assertEqual(2, len(lists))

        expected_sublist0 = self.generate_list(5)
        self.assertEqual(expected_sublist0, lists[0])

        expected_sublist1 = self.generate_list_with_range(5, 10)
        self.assertEqual(expected_sublist1, lists[1])

    def test_split_list_remainder(self):
        lists = split_list(self._master_list, 3)

        self.assertEqual(4, len(lists))

        expected_sublist0 = self.generate_list(3)
        self.assertEqual(expected_sublist0, lists[0])

        expected_sublist1 = self.generate_list_with_range(3, 6)
        self.assertEqual(expected_sublist1, lists[1])

        expected_sublist2 = self.generate_list_with_range(6, 9)
        self.assertEqual(expected_sublist2, lists[2])

        expected_sublist3 = self.generate_list_with_range(9, 10)
        self.assertEqual(expected_sublist3, lists[3])

    def test_split_whole_list(self):
        lists = split_list(self._master_list, 10)

        self.assertEqual(1, len(lists))
        self.assertEqual(self._master_list, lists[0])

    def test_split_chunk_bigger_than_list(self):
        lists = split_list(self._master_list, 20)

        self.assertEqual(1, len(lists))
        self.assertEqual(self._master_list, lists[0])

    def test_split_empty_list(self):
        lists = split_list([], 5)

        self.assertEqual(0, len(lists))

    @staticmethod
    def generate_list(num_items):
        return ['item' + str(n) for n in range(num_items)]

    @staticmethod
    def generate_list_with_range(lower, upper):
        return ['item' + str(n) for n in range(lower, upper)]
