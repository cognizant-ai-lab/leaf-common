from unittest import TestCase

from leaf_common.data.util.sanitizer_util import SanitizeUtil


class TestSanitizerUtil(TestCase):
    """
    Tests the SanitizerUtil class
    """

    def test_sanitize_list_no_sanitization(self):
        """
        Test case where no sanitization happens in a list
        """
        input_list = ["PassengerId", "Survived", "Pclass"]

        sanitized_input_list = SanitizeUtil.sanitize_list(input_list)
        self.assertListEqual(input_list, sanitized_input_list)

    def test_sanitize_list_with_sanitization(self):
        """
        Test case where sanitization happens in a list
        """
        input_list = ["Passenger/Id", " Sur vived ", "@Pclass#"]
        expected_output_list = ["PassengersolId", "Sur_vived", "commatPclassnum"]

        sanitized_input_list = SanitizeUtil.sanitize_list(input_list)
        self.assertListEqual(expected_output_list, sanitized_input_list)

    def test_sanitize_dict_keys_no_sanitization(self):
        """
        Test case where no sanitization happens in dictionary keys
        """
        input_dict = {"PassengerId": [1, 2, 3], "Survived": [4, 5, 6], "Pclass": [7, 8, 9]}

        sanitized_input_dict = SanitizeUtil.sanitize_dict_keys(input_dict)
        print(f"sanitized_input_dict: {sanitized_input_dict}")
        self.assertDictEqual(input_dict, sanitized_input_dict)

    def test_sanitize_dict_keys_with_sanitization(self):
        """
        Test case where sanitization happens in dictionary keys
        """
        input_dict = {"Passenger/Id": [1, 2, 3], " Sur vived ": [4, 5, 6], "@Pclass#": [7, 8, 9]}
        expected_output_dict = {"PassengersolId": [1, 2, 3], "Sur_vived": [4, 5, 6], "commatPclassnum": [7, 8, 9]}

        sanitized_input_dict = SanitizeUtil.sanitize_dict_keys(input_dict)
        print(f"sanitized_input_dict: {sanitized_input_dict}")
        self.assertDictEqual(expected_output_dict, sanitized_input_dict)

    def test_sanitize_cao_mapping_no_sanitization(self):
        """
        Test case where no sanitization happens in a cao mapping
        """

        input_cao_mapping = {"context": ["PassengerId", "Pclass", "Name", "Sex", "Age"],
                             "actions": ["Fare"],
                             "outcomes": ["Survived"]}

        sanitized_input_cao_mapping = SanitizeUtil.sanitize_cao_mapping(input_cao_mapping)
        self.assertDictEqual(input_cao_mapping, sanitized_input_cao_mapping)

    def test_sanitize_cao_mapping_with_sanitization(self):
        """
        Test case where sanitization happens in a cao mapping
        """

        input_cao_mapping = {"context": ["Passenger/Id", "@Pclass#", "Name", "Sex", "Age"],
                             "actions": ["!Fare!"],
                             "outcomes": [" Sur vived "]}
        expected_output_cao_mapping = {"context": ["PassengersolId", "commatPclassnum", "Name", "Sex", "Age"],
                                       "actions": ["notFarenot"],
                                       "outcomes": ["Sur_vived"]}

        sanitized_input_cao_mapping = SanitizeUtil.sanitize_cao_mapping(input_cao_mapping)
        self.assertDictEqual(expected_output_cao_mapping, sanitized_input_cao_mapping)
