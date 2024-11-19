from typing import Dict

import os
import unittest

from leaf_common.data.profiling.column_name_sanitizer_transformation \
    import ColumnNameSanitizerTransformation
from leaf_common.data.persistence.dataframe_persistence import DataFramePersistence

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(ROOT_DIR, "..", "..", "fixtures", "heart_failure")


class TestColumnNameSanitizerTransformation(unittest.TestCase):
    """
    Tests the ColumnNameSanitizerTransformation class
    """

    def test_assumptions(self):
        """
        Tests basic constructor of ColumnNameSanitizerTransformation
        """
        sanitizer = ColumnNameSanitizerTransformation()
        self.assertIsNotNone(sanitizer)

    def test_no_sanitize(self):
        """
        Tests that we do no harm
        """
        changed_columns = self.find_changed_column_names("heart_failure_dataset.csv")
        self.assertEqual(0, len(changed_columns.keys()))

    def test_rejectable_column_names(self):
        """
        Tests that we do some good
        """
        changed_columns = self.find_changed_column_names("column_name_rejection_dataset.csv")
        self.assertEqual(3, len(changed_columns.keys()))

    def find_changed_column_names(self, fixture_csv: str) -> Dict[str, str]:
        """
        :param fixture_csv: The file name in tests/fixtures to test.
        :return: A dictionary of mappings of any column that changed where
                keys are the original name and values are the sanitized name
        """
        file_reference = os.path.join(FIXTURES_PATH, fixture_csv)

        # Load the DataFrame
        persistence = DataFramePersistence()
        original_df = persistence.restore(file_reference=file_reference)
        sanitizer = ColumnNameSanitizerTransformation()
        sanitized_df = sanitizer.transform(original_df)

        original_columns = list(original_df.columns)
        sanitized_columns = list(sanitized_df.columns)

        changed_columns = {}
        for index, original_column in enumerate(original_columns):
            sanitized_column = sanitized_columns[index]
            if original_column != sanitized_column:
                changed_columns[original_column] = sanitized_column

        return changed_columns
