import logging
import os
import re

from typing import Any
from typing import Dict

from pandas import DataFrame
from pandas import Series
from pandas.arrays import FloatingArray
from pandas.arrays import IntegerArray
from numpy import array
from numpy import ndarray

from leaf_common.data.profiling.no_valid_data_error import NoValidDataError
from leaf_common.data.profiling.rejection_reason import RejectionReason

# Maximum possible number of categories before it's "too many".
DEFAULT_MAX_CATEGORIES = 20

# This regex string comes from requirements of Tensorflow scope names.
# Nominally only alphanumerics, underscores, and dashes
# but a few more characters are allowed as well like:
#
#   backslashes,
#   forward slashes,
#   greater than signs
#   periods
#
# ...but definitely no spaces.
# See UN-775 for description of root problem.
COLUMN_REGEX = "^[A-Za-z0-9.][A-Za-z0-9_.\\/>-]*$"


class DataFrameProfiler:
    """
    Class used to profile a pandas DataFramee and measure statistics
    important for data transformation and processing. The main entry point
    for this class is profile_data_frame().
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Constructor

        :param config: Request-time config for how to generate the profile.
                Keys include:
                "allow_nans"        When False, profiling will reject any column
                                    that has a NaN (not-a-number) value in it with
                                    the HAS_NAN RejectionReason. Default False.
                "max_categories"    Maximum number of categories a column can have
                                    before it is rejected with the TOO_MANY_CATEGORIES
                                    RejectionReason.  Default is 20.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or {}
        self.max_categories = self.config.get("max_categories", DEFAULT_MAX_CATEGORIES)

    def profile_data_frame(self, dataframe: DataFrame) -> Dict[str, Any]:
        """
        Main entry point to data profiling.
        Method responsible for getting the essential information required about the CSV

        :param dataframe: A pandas DataFrame from the csv file
        :return: A dictionary representing the data Profile
        """
        # pylint: disable=too-many-branches

        # Note: These exceptions take the form of error fields as the results
        #       are reported back from the service.
        if dataframe.shape[0] == 0:
            raise NoValidDataError("CSV data has no rows!")
        if dataframe.shape[1] == 0:
            raise NoValidDataError("CSV data has no columns!")

        allow_nans = self.config.get("allow_nans", False)

        # Start with a skeleton dictionary representing the data profile
        profile = {
            "headers": dataframe.columns.tolist(),
            "num_rows": dataframe.shape[0],
            "num_cols": dataframe.shape[1],
            "info": {},
        }

        # See definition of COLUMN_REGEX above for details.
        column_regex = re.compile(COLUMN_REGEX)

        # When looping through the columns of the data looking for potential problems,
        # we do 2 things:
        #   1)  We store the complaint in this rejected_columns dictionary mapping
        #       a column name string to a RejectionReason.  This dictionary is raw
        #       data that can be sent back to the UI and/or tested against.
        #   2)  We use a logger to tell a developer via a debug log level (only!)
        #       what went wrong so that an appropriate person (only!) can begin
        #       to debug problems with test data files.
        rejected_columns: Dict[str, int] = {}

        # Initialize the keys with empty data fields
        for column_name in profile["headers"]:

            # CheckMarx does not like the fact that we might be logging information coming
            # directly from a file that used secrets to access it.
            # CHECKMARX RESPONSE:
            #   While is is possible that data that came from a potentially sensitive file
            #   can be passed to a logger and output to a file, these logs are all done
            #   at debug level for precisely that reason - it gives us the ability to
            #   manually debug the algorithms here.  Deployment of this service
            #   never has log-level DEBUG turned on - it only goes up to INFO in deployment,
            #   which programmatically blocks the DEBUG output.
            self.logger.debug("Profiling column %s", column_name)

            # Columns from a Pandas DataFrame are a Series
            column = dataframe[column_name]

            # Initialize data_field dictionary
            has_nan = bool(column.isnull().values.any())

            data_field = {

                # DataType is the data type of the column
                # Options: Bool, Int, Float, String
                "data_type": self.look_up_type(str(column.dtype)),

                # Range of the numerical value if type is continuous
                "range": [],

                # List of categorical values possible
                "discrete_categorical_values": [],

                # HasNan is:
                #   * True if any row was missing a value for the column
                #   * False if every row has a value for the column
                "has_nan": has_nan,

                # Sum is the total of all the rows
                # ignoring missing data
                "sum": 0.0,

                # Mean is the average of all the rows
                # ignoring missing data
                "mean": 0.0,

                # StdDev is the standard deviation of all the rows
                # ignoring missing data
                "std_dev": 0.0
            }

            add_column = True
            column_type = data_field["data_type"]

            # Get the list of unique values. Don't sort it yet, because it might be huge and we might discard it.
            unique_values = column.unique()

            # Discard columns that whose names will cause problems with Tensorflow scopes.
            if not re.fullmatch(column_regex, column_name):
                # Unless ALLOW_SPECIAL_CHARACTERS_IN_COLUMN_NAMES is "True",
                # reject column names with special characters in them
                if os.getenv("ALLOW_SPECIAL_CHARACTERS_IN_COLUMN_NAMES", "False").lower() != "true":
                    # Theoretically if a DataFrame has been put through the
                    # ColumnNameSanitizerTransformation before calling this,
                    # we should never have columns rejected because of their name.
                    rejected_columns[column_name] = RejectionReason.INVALID_COLUMN_NAME
                    # See CHECKMARX RESPONSE above.
                    self.logger.debug("Skipping column %s because it must adhere to the regex '%s'",
                                      column_name, COLUMN_REGEX)
                    add_column = False

            # Discard columns that only have a single value, as these are useless for training
            elif len(unique_values) == 1:
                rejected_columns[column_name] = RejectionReason.SINGLE_VALUED
                # See CHECKMARX RESPONSE above.
                self.logger.debug("Skipping column %s because it contains only a single value (%s)",
                                  column_name, column.iloc[0])
                add_column = False
            elif has_nan and not allow_nans:
                rejected_columns[column_name] = RejectionReason.HAS_NAN
                # See CHECKMARX RESPONSE above.
                self.logger.debug("Skipping column %s because it has missing values (NaN)", column_name)
                add_column = False
            elif column_type in ("INT", "FLOAT"):
                # Numeric field
                # By convention numbers are always reported as floats.
                field_info = self.handle_numeric_column(column, has_nan, unique_values, column_name)
                data_field.update(field_info)
            elif column_type in ("BOOL", "STRING", "UNKNOWN_TYPE"):
                # Text-like field
                add_column, field_info, rejection_reason = self.handle_text_column(column_name, column_type,
                                                                                   unique_values)
                data_field.update(field_info)
                if rejection_reason:
                    rejected_columns[column_name] = rejection_reason
            else:
                add_column = False
                # See CHECKMARX RESPONSE above.
                self.logger.debug("Column %s has unrecognized data type %s (pandas type %s)",
                                  column_name, column_type, str(column.dtype))

            if add_column:
                # Add the data field to the info map
                profile["info"][column_name] = data_field

        if len(rejected_columns) > 0:
            profile["rejected_columns"] = rejected_columns

        return profile

    def handle_text_column(self, column_name: str, column_type: str, unique_values: ndarray) \
            -> (bool, Dict[str, Any], RejectionReason):
        """
        Handles text-like columns from the dataset

        :param column_name: String name of the column from the CSV file
        :param column_type: Data type of the column, as inferred by Pandas
        :param unique_values: Number of unique values within this column
        :return: A Boolean indicate if the column should be included
        :return: A dict containing information about the column
        :return: A rejection reason if the column should be rejected or None if the column is valid
        """
        field_info: Dict[str, Any] = {}
        add_column = True
        rejection_reason = None

        # UN-701: Protect against loooong lists of categories. A `last_name` column for instance.
        if len(unique_values) <= self.max_categories:
            # Note: Converting to string BEFORE sorting because values can contain NaN, which is not
            # comparable.
            field_info["discrete_categorical_values"] = sorted(unique_values.astype(str))
        else:
            add_column = False
            # See CHECKMARX RESPONSE below.
            self.logger.debug("Skipping column %s because it contains more categories (%s) than the maximum "
                              "allowed (%s).",
                              column_name, len(unique_values), self.max_categories)

            # Record rejection reason
            rejection_reason = RejectionReason.TOO_MANY_CATEGORIES

        # Pandas can return UNKNOWN_TYPE for categorical data that is really strings
        if column_type == "UNKNOWN_TYPE":
            field_info["data_type"] = "STRING"

        return add_column, field_info, rejection_reason

    def handle_numeric_column(self, column: Series, has_nan: bool,
                              unique_values: ndarray, column_name: str = None) -> Dict[str, Any]:
        """
        Handles numeric (float, int) columns from the dataset

        :param column: Column from the pandas dataframe
        :param has_nan: `True` if the column has NaN (missing) values
        :param unique_values: Number of unique values within this column
        :param column_name: the name of the column being considered
        :return: A dict with info for the column
        """
        # It's useful to have this for debugging, but too verbose to have that
        # logging on all the time.
        _ = column_name
        field_info: Dict[str, Any] = {}

        # UN-701 Allow using numerical columns as categorical columns
        # as long as they don't contain too many values.
        if len(unique_values) <= self.max_categories:

            # With dtype conversion, Pandas arrays can come in
            if isinstance(unique_values, (IntegerArray, FloatingArray)):
                unique_values = array(list(unique_values))

            # Sort the ndarray values in numerical order, before converting them to string.
            unique_values.sort()
            # UN-701 according to proto/csv_data_description.proto the `discrete_categorical_values` field
            # can only contain a list of strings, not ints or floats.
            field_info["discrete_categorical_values"] = unique_values.astype(str).tolist()
        else:
            # UN-701: This will be displayed only if user tries to switch to "CATEGORICAL"
            field_info["discrete_categorical_values"] = [f"<Column contains {len(unique_values)} categories."
                                                         f" Please refine your dataset to have "
                                                         f"no more than {self.max_categories} categories>"]
        field_info["range"] = [float(column.min()), float(column.max())]

        # Info we can get if we have values in each row.
        if not has_nan:
            field_info["sum"] = float(column.sum())
            field_info["mean"] = float(column.mean())
            field_info["std_dev"] = float(column.std())

        return field_info

    @staticmethod
    def look_up_type(pandas_data_type: str) -> str:
        """
        :param pandas_data_type: The Pandas dtype to translate from
        :return: A String known to the Data Profiler protobufs
                for the given type, or "UNKNOWN_TYPE" if not found.
        """

        data_type_map = {
            "bool": "BOOL",
            "category": "STRING",
            "float64": "FLOAT",
            "int64": "INT",
            "object": "STRING"
        }

        # Note we use the lower() because Pandas now has Int64 and Float64
        # separate from numpy.
        translated_type = data_type_map.get(pandas_data_type.lower(), "UNKNOWN_TYPE")
        return translated_type
