from dreamml.utils.spark_utils import spark_conf
import pprint
import pandas as pd


class ZeroDataFrameException(Exception):
    """Exception raised when a Spark DataFrame with zero observations is returned.

    This exception suggests using more powerful Spark session configurations.

    Attributes:
        spark_conf (list): The current Spark configuration settings.
        message (str): Detailed message explaining the exception.
    """

    def __init__(self):
        """Initializes the ZeroDataFrameException with the current Spark configurations.

        Constructs a message indicating that an empty DataFrame was returned and suggests
        using more powerful SparkConf settings.

        Raises:
            ZeroDataFrameException: Always raised when initialized.
        """
        self.spark_conf = list(spark_conf.getAll())
        self.message = f"""A DataFrame with 0 observations was returned.
        Please consider using more powerful Spark session configurations (SparkConf).
        You can base your configuration on our session:
        {pprint.pformat(self.spark_conf)}"""
        super(ZeroDataFrameException, self).__init__(self.message)


class ColumnDoesntExist(Exception):
    """Exception raised when a specified column does not exist in a DataFrame.

    Attributes:
        column_name (str): The name of the missing column.
        data (pd.DataFrame): The DataFrame that was checked for the column.
        msg (str): Detailed message explaining the exception.
    """

    def __init__(self, column_name: str, data: pd.DataFrame, msg: str = None):
        """Initializes the ColumnDoesntExist exception.

        Args:
            column_name (str): The name of the column that was not found.
            data (pd.DataFrame): The DataFrame being checked.
            msg (str, optional): Custom message for the exception. Defaults to a standard message.

        Raises:
            ColumnDoesntExist: Always raised when initialized.
        """
        self.column_name = column_name
        self.data = data
        if msg:
            self.msg = msg
        else:
            self.msg = f"The specified column '{column_name}' does not exist in the given DataFrame."

        super().__init__(self.msg)

    def __str__(self):
        """Returns the exception message.

        Returns:
            str: The exception message.
        """
        return self.msg


class MissingRequiredConfig(Exception):
    """Exception raised when a required configuration is missing or empty.

    Attributes:
        msg (str): Detailed message explaining the exception.
    """

    def __init__(self, config_name: str = None):
        """Initializes the MissingRequiredConfig exception.

        Args:
            config_name (str, optional): The name of the missing configuration. Defaults to None.

        Raises:
            MissingRequiredConfig: Always raised when initialized.
        """
        if config_name:
            self.msg = f"The required configuration '{config_name}' is missing or empty."
        else:
            self.msg = "A required configuration is missing or empty."
        super().__init__(self.msg)

    def __str__(self):
        """Returns the exception message.

        Returns:
            str: The exception message.
        """
        return self.msg