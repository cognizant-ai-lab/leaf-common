from typing import List
from typing import Dict

from pandas import DataFrame

from leaf_common.data.interfaces.dataframe_transformation \
    import DataFrameTransformation
from leaf_common.data.transformations.column_rename_transformation \
    import ColumnRenameTransformation
from leaf_common.filters.tensorflow_field_name_filter import TensorFlowFieldNameFilter
from leaf_common.filters.string_filter import StringFilter
from leaf_common.progress.progress_reporter import ProgressReporter


class ColumnNameSanitizerTransformation(DataFrameTransformation):
    """
    An implementation of the DataFrameTransformation interface which sanitizes
    all the column names.
    """

    def transform(self, input_df: DataFrame, progress: ProgressReporter = None) -> DataFrame:
        """
        :param input_df: A Pandas DataFrame to operate on
        :progress: the ProgressReporter to use to update the status
        :return: A new Pandas DataFrame that has gone through the transformation operation
        """
        column_names = list(input_df.columns)

        sanitizer = TensorFlowFieldNameFilter()
        sanitized = self.sanitize_column_names(column_names, sanitizer)

        renamer = ColumnRenameTransformation(sanitized)
        output_df = renamer.transform(input_df)
        return output_df

    @staticmethod
    def sanitize_column_names(column_names: List[str],
                              sanitizer: StringFilter) -> Dict[str, str]:
        """
        Creates a dictionary of unsanitized column names to sanitized column
        names where the column name values are sanitized by some specified
        criteria.

        :param column_names: A List of column names to sanitize.
        :param sanitizer: A StringFilter implementation that will sanitize
                        the column name.
        :return: A new dictionary where the keys are old column names and the
                 values are new sanitized column names.  If no sanitization
                 needs to be done, then the value will be the same as they key.
        """

        # Per https://stackoverflow.com/questions/39980323/are-dictionaries-ordered-in-python-3-6
        # Dictionary keys are returned in the order they are inserted, so if we do depend on
        # ordering of the new dictionary we should be ok.
        sanitized = {}
        for column_name in column_names:
            sanitized_column_name = sanitizer.filter(column_name)
            sanitized[column_name] = sanitized_column_name

        return sanitized
