from typing import Any
from typing import Dict

from pandas import DataFrame
from pandas import Float64Dtype
from pandas import Int64Dtype

import numpy as np


class DataFrameUtil:
    """
    Utility methods for use with DataFrames.
    """

    @staticmethod
    def copy_dataframe_structure(in_df: DataFrame) -> DataFrame:
        """
        :param in_df: The dataframe whose structure we want to copy
        :return: A dataframe of same structure/column names/typing as in_df
                but is empty
        """
        out_df = in_df.iloc[:0].copy()
        return out_df

    @staticmethod
    def count_nan(test_df: DataFrame, column_name: str = None) -> int:
        """
        :param test_df: The dataframe whose NaN values we want to count
        :param column_name: An optional column name to narrow the nan search to
                        Value of None (default) implies looking at the entire dataframe
        :return: The number of NaN values in the dataframe
        """
        if column_name is None:
            # From: https://sparkbyexamples.com/pandas/count-nan-values-in-pandas/
            is_na = test_df.isna()
            first_sum = is_na.sum()
        else:
            column = test_df.loc[:, column_name]
            first_sum = column.isna()

        count = first_sum.sum()

        return count

    @staticmethod
    def cast_cell(value, src_dtype, dest_dtype):
        """
        Casts a cell value to a potentially more correct type.
        :param value: The value to potentially cast
        :param src_dtype: The Pandas/Numpy data type of the value
        :param dest_dtype: The Pandas/Numpy data type of the column
                        where we want the casted value to live.
        """
        casted = value

        if src_dtype == dest_dtype:
            casted = value
        elif dest_dtype == np.dtype.str:
            casted = str(value)
        elif isinstance(dest_dtype, (np.int64, Int64Dtype)):
            casted = int(value)
        elif isinstance(dest_dtype, (np.float64, Float64Dtype)):
            casted = float(value)
        elif dest_dtype == np.bool_:
            casted = bool(value)
        else:
            # Unknown: Pray
            casted = value

        return casted

    @staticmethod
    def value_counts_dict(test_df: DataFrame, column_name: str) -> Dict[Any, int]:
        """
        Creates a value counts dictionary where keys are specific values found in
        the column and values are a count for how many times that value has been seen.

        :param test_df: The DataFrame to test
        :param column_name: The string name of the column to test.
        :return: A dictionary whose keys are specific values found for the column
                and whose values are counts for that column value
        """
        if test_df is None:
            return None

        if column_name is None:
            return None

        return test_df[column_name].value_counts().to_dict()
