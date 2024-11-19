from unittest import TestCase

from leaf_common.data.profiling.field_info_util import FieldInfoUtil


class TestFieldInfoUtil(TestCase):
    """
    Tests the FieldInfoUtil class
    """

    field_infos = {
        "empty_dict": {
            "valued": "CATEGORICAL",
            "discrete_categorical_values": {
            }
        },
        "empty_list": {
            "valued": "CATEGORICAL",
            "discrete_categorical_values": [
            ]
        },
        "histogram": {
            "valued": "CATEGORICAL",
            "data_type": "STRING",
            "discrete_categorical_values": {
                "A": 1,
                "B": 2,
                "C": 3
            }
        },
        "error": {
            "valued": "CATEGORICAL",
            "data_type": "STRING",
            "discrete_categorical_values": [
                "<Column contains 47 categories. Please refine your dataset to have no more than 20 categories>"
            ]
        },
        "string_list": {
            "valued": "CATEGORICAL",
            "data_type": "STRING",
            "discrete_categorical_values": [
                "a",
                "b",
                "c"
            ]
        },
        "int_list": {
            "valued": "CATEGORICAL",
            "data_type": "INT",
            "discrete_categorical_values": [
                1,
                2,
                3
            ]
        },
        "big_range": {
            "valued": "CONTINUOUS",
            "data_type": "INT",
            "range": [
                -100,
                100
            ]
        },
        "small_range": {
            "valued": "CONTINUOUS",
            "data_type": "FLOAT",
            "range": [
                -1.0,
                1.0
            ]
        },
        "string_only": {
            "data_type": "STRING",
            "discrete_categorical_values": [
                "a",
                "b",
                "c"
            ]
        },
        "int_only": {
            "data_type": "INT",
            "discrete_categorical_values": [
                1,
                2,
                3
            ],
            "range": [
                1,
                3
            ]
        }
    }

    def test_is_categorical(self):
        """
        Tests FieldInfoUtil.is_categorical()
        """

        self.assertFalse(FieldInfoUtil.is_categorical("no_field_infos", None))
        self.assertFalse(FieldInfoUtil.is_categorical(None, self.field_infos))
        self.assertFalse(FieldInfoUtil.is_categorical("field_does_not_exist", self.field_infos))

        self.assertFalse(FieldInfoUtil.is_categorical("small_range", self.field_infos))
        self.assertFalse(FieldInfoUtil.is_categorical("big_range", self.field_infos))

        self.assertTrue(FieldInfoUtil.is_categorical("error", self.field_infos))
        self.assertTrue(FieldInfoUtil.is_categorical("string_list", self.field_infos))
        self.assertTrue(FieldInfoUtil.is_categorical("int_list", self.field_infos))
        self.assertTrue(FieldInfoUtil.is_categorical("string_only", self.field_infos))

        self.assertFalse(FieldInfoUtil.is_categorical("int_only", self.field_infos))

    def test_get_unique_values(self):
        """
        Tests FieldInfoUtil.get_unique_values()
        """

        self.assertIsNone(FieldInfoUtil.get_unique_values("no_field_infos", None))
        self.assertIsNone(FieldInfoUtil.get_unique_values(None, self.field_infos))
        self.assertIsNone(FieldInfoUtil.get_unique_values("field_does_not_exist", self.field_infos))

        self.assertIsNone(FieldInfoUtil.get_unique_values("small_range", self.field_infos))
        self.assertIsNone(FieldInfoUtil.get_unique_values("big_range", self.field_infos))

        self.assertIsNotNone(FieldInfoUtil.get_unique_values("error", self.field_infos))
        self.assertIsNotNone(FieldInfoUtil.get_unique_values("string_list", self.field_infos))
        self.assertIsNotNone(FieldInfoUtil.get_unique_values("int_list", self.field_infos))
        self.assertIsNotNone(FieldInfoUtil.get_unique_values("string_only", self.field_infos))

        self.assertIsNone(FieldInfoUtil.get_unique_values("int_only", self.field_infos))
