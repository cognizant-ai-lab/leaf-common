from typing import List
from typing import Type

from pandas import DataFrame

from leaf_common.data.interfaces.dataframe_transformation import DataFrameTransformation
from leaf_common.progress.iterating_progress_reporter import IteratingProgressReporter
from leaf_common.progress.progress_reporter import ProgressReporter


class CompositeDataFrameTransformation(DataFrameTransformation):
    """
    A DataFrameTransformation implementation that handles multiple calls to
    different transform()-s in sequence.
    """

    def __init__(self):
        """
        Constructor
        """
        self.transformations: List[DataFrameTransformation] = []

    def transform(self, input_df: DataFrame, progress: ProgressReporter = None) -> DataFrame:
        """
        :param input_df: A Pandas DataFrame to operate on
        :progress: the ProgressReporter to use to update the status
        :return: A new Pandas DataFrame that has gone through the transformation operation
        """
        output_df = input_df

        if self.get_num_transformations() == 0:
            return output_df

        # Don't do progress reporting if we were not given any progress reporter
        iteration_progress = None
        iteration_report = None
        if progress is not None:
            # Prepare progress reporting
            parent_report = {
                "phase": "Performing Data Transforms",
                "progress": 0.0,
                "subcontexts": None
            }
            iteration_report = {
                "phase": "Performing Data Transform",
                "progress": 0.0,
                "subcontexts": None
            }
            iteration_progress = IteratingProgressReporter(progress,
                                                           self.transformations,
                                                           parent_report)

        # Loop over all transformations
        for transformation in self.transformations:

            # Perhaps report progress
            ProgressReporter.maybe_report(iteration_progress, iteration_report)

            # Do the transformation
            output_df = transformation.transform(output_df, progress)

        return output_df

    def append(self, transformation: DataFrameTransformation):
        """
        :param transformation:  Appends the given DataFrameTransformation
                to the end of the list.
        """
        self.transformations.append(transformation)

    def get_num_transformations(self):
        """
        :return: The number of transformations
        """
        return len(self.transformations)

    def has_transformation(self, transform_type: Type[DataFrameTransformation]) -> bool:
        """
        :param transform_type: A class that derives from DataTransformation
        :return: True if any component is an instance of the type transform_type
        """
        for transform in self.transformations:
            if isinstance(transform, transform_type):
                return True

        return False
