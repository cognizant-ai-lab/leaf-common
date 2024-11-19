from pandas import DataFrame

from leaf_common.progress.progress_reporter import ProgressReporter


# pylint: disable=too-few-public-methods
class DataFrameTransformation():
    """
    An interface defining a transformation operation on a pandas DataFrame
    """

    def transform(self, input_df: DataFrame, progress: ProgressReporter = None) -> DataFrame:
        """
        :param input_df: A Pandas DataFrame to operate on
        :progress: the ProgressReporter to use to update the status
        :return: A new Pandas DataFrame that has gone through the transformation operation
        """
        raise NotImplementedError
