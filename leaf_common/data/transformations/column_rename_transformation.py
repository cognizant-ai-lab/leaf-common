from typing import Dict

from pandas import DataFrame

from leaf_common.progress.progress_reporter import ProgressReporter
from leaf_common.data.interfaces.dataframe_transformation \
    import DataFrameTransformation


# pylint: disable=too-few-public-methods
class ColumnRenameTransformation(DataFrameTransformation):
    """
    An implementation of the DqtaFrameTransformation interface which
    takes a map of old -> new column names and produces a new DataFrame
    that matches the new column names.  Any existing column which is not
    listed in the given name map is left alone.
    """

    def __init__(self, rename_map: Dict[str, str]):
        """
        Constructor

        :param rename_map: A dicitonary of old column name to new column name
        """
        self.rename_map = rename_map

    def transform(self, input_df: DataFrame, progress: ProgressReporter = None) -> DataFrame:
        """
        :param input_df: A Pandas DataFrame to operate on
        :progress: the ProgressReporter to use to update the status
        :return: A new Pandas DataFrame that has gone through the transformation operation
        """
        if input_df is None:
            return None

        output_df = input_df.rename(columns=self.rename_map)
        return output_df
