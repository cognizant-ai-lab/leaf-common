from unittest import TestCase

from leaf_common.data.profiling.data_profile_field_integration \
    import DataProfileFieldIntegration


class TestDataProfileFieldIntegration(TestCase):
    """
    Tests the DataProfileFieldIntegration class
    """
    empty_field_info = {
    }
    empty_dict_field_info = {
        "valued": "CATEGORICAL",
        "discrete_categorical_values": {
        }
    }
    empty_list_field_info = {
        "valued": "CATEGORICAL",
        "discrete_categorical_values": [
        ]
    }

    histogram_field_info = {
        "valued": "CATEGORICAL",
        "discrete_categorical_values": {
            "A": 1,
            "B": 2,
            "C": 3
        }
    }
    error_field_info = {
        "valued": "CATEGORICAL",
        "discrete_categorical_values": [
            "<Column contains 47 categories. Please refine your dataset to have no more than 20 categories>"
        ]
    }
    list_field_info = {
        "valued": "CATEGORICAL",
        "discrete_categorical_values": [
            "a",
            "b",
            "c"
        ]
    }

    big_range_field_info = {
        "valued": "CONTINUOUS",
        "data_type": "INT",
        "range": [
            -100,
            100
        ]
    }
    small_range_field_info = {
        "valued": "CONTINUOUS",
        "data_type": "INT",
        "range": [
            -1,
            1
        ]
    }
    mid_range_field_info = {
        "valued": "CONTINUOUS",
        "data_type": "INT",
        "range": [
            0,
            50
        ]
    }

    def test_get_categorical_values_set(self):
        """
        Tests DataProfileFieldIntegration.get_categorical_values_set()
        """

        # Method are static, but this is for convenience
        instance = DataProfileFieldIntegration()

        out_set = instance.get_categorical_values_set(self.empty_field_info)
        self.assertEqual(len(out_set), 0)

        out_set = instance.get_categorical_values_set(self.empty_dict_field_info)
        self.assertEqual(len(out_set), 0)

        out_set = instance.get_categorical_values_set(self.empty_list_field_info)
        self.assertEqual(len(out_set), 0)

        out_set = instance.get_categorical_values_set(self.histogram_field_info)
        self.assertEqual(len(out_set), 3)

        out_set = instance.get_categorical_values_set(self.list_field_info)
        self.assertEqual(len(out_set), 3)

        out_set = instance.get_categorical_values_set(self.error_field_info)
        self.assertEqual(len(out_set), 0)

    def test_integrate_field_infos_categorical(self):
        """
        Tests integrate_field_infos() with categoricals
        """
        # Method are static, but this is for convenience
        instance = DataProfileFieldIntegration()

        field_infos = [self.empty_list_field_info, self.empty_dict_field_info]
        field_info = instance.integrate_field_infos(field_infos)
        self.assertIsNone(field_info)

        field_infos = [self.empty_field_info, self.error_field_info]
        field_info = instance.integrate_field_infos(field_infos)
        self.assertIsNone(field_info)

        field_infos = [self.list_field_info, self.histogram_field_info]
        field_info = instance.integrate_field_infos(field_infos)
        values = field_info.get("discrete_categorical_values")
        self.assertEqual(len(values), 6)

    def test_integrate_field_infos_range(self):
        """
        Tests integrate_field_infos() with ranges
        """
        # Method are static, but this is for convenience
        instance = DataProfileFieldIntegration()

        field_infos = [self.big_range_field_info, self.small_range_field_info]
        field_info = instance.integrate_field_infos(field_infos)
        test_range = field_info.get("range")
        self.assertEqual(len(test_range), 2)
        self.assertEqual(test_range[0], -100)
        self.assertEqual(test_range[1], 100)

        field_infos = [self.mid_range_field_info, self.small_range_field_info]
        field_info = instance.integrate_field_infos(field_infos)
        test_range = field_info.get("range")
        self.assertEqual(len(test_range), 2)
        self.assertEqual(test_range[0], -1)
        self.assertEqual(test_range[1], 50)
