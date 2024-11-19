from pandas import DataFrame

from leaf_common.data.interfaces.dataframe_transformation import DataFrameTransformation
from leaf_common.progress.progress_reporter import ProgressReporter


# pylint: disable=too-few-public-methods
class RemoveEmptyRowsTransformation(DataFrameTransformation):
    """
    A DataFrameTransformation that removes any row that has no data at all.
    This is common in MS Excel spreadsheets that have been converted
    to CSV files. See UN-1089.
    """

    def __init__(self, how="all"):
        """
        Constructor
        :param how: String describing how the row removal should happen.
                Can be "any" or "all" (default).
                See https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html
        """
        self.how = how

    def transform(self, input_df: DataFrame, progress: ProgressReporter = None) -> DataFrame:
        """
        :param input_df: A Pandas DataFrame to operate on
        :progress: the ProgressReporter to use to update the status
        :return: A new Pandas DataFrame that has gone through the transformation operation
        """
        output_df = None
        if input_df is not None:
            output_df = input_df.dropna(how=self.how)

        return output_df
