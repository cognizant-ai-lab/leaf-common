
# Copyright (C) 2021-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# unileaf-util SDK Software in commercial settings.
#
# END COPYRIGHT
import pandas as pd


# pylint: disable=too-few-public-methods
class DataFramePredictor:
    """
    Interface whose concrete implementations use a predict() method on their
    underlying models which takes a Pandas DataFrame and also yields a Pandas
    DataFrame..
    """

    def predict(self, encoded_context_actions_df: pd.DataFrame) -> pd.DataFrame:
        """
        This method uses the trained model to make a prediction for the passed Pandas DataFrame
        of context and actions. Returns the predicted outcomes in a Pandas DataFrame.

        :param encoded_context_actions_df: a Pandas DataFrame containing encoded
                    rows of context and actions for which a prediction is requested.
                    Categorical columns contain one-hot vectors, e.g. [1, 0, 0].
                    Which means a row can be a list of arrays (1 per column), e.g.: [1, 0, 0], [1,0].
        :return: a Pandas DataFrame of the predicted outcomes for each context and actions row.
        """
        raise NotImplementedError
