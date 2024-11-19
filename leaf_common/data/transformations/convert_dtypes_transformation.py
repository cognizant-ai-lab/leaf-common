from pandas import DataFrame
from pandas import to_numeric

from leaf_common.data.interfaces.dataframe_transformation import DataFrameTransformation
from leaf_common.progress.progress_reporter import ProgressReporter


# pylint: disable=too-few-public-methods
class ConvertDtypesTransformation(DataFrameTransformation):
    """
    A DataFrameTransformation that uses the Pandas convert_dtypes() method to
    infer the best type for each column.  This ends up doing better with
    columns that have integer data but also has NaNs, as by default, the
    numpy dtypes that are used default to float whenever a NaN is seen
    (because there is no standard int NaN at that level).
    """

    def transform(self, input_df: DataFrame, progress: ProgressReporter = None) -> DataFrame:
        """
        :param input_df: A Pandas DataFrame to operate on
        :progress: the ProgressReporter to use to update the status
        :return: A new Pandas DataFrame that has gone through the transformation operation
        """
        output_df = None
        if input_df is not None:
            output_df = input_df.convert_dtypes()
            # From https://stackoverflow.com/questions/74950933/pandas-
            #   automatically-infer-best-dtype-str-to-int-not-working
            # Gets integers from strings better.
            output_df = output_df.apply(to_numeric, errors="ignore")

        return output_df
