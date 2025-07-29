import abc
import warnings
from abc import ABC
from typing import Generator, Tuple, List, Optional

import numpy as np
import pandas as pd
from pandas.core.dtypes.common import is_datetime64_any_dtype
from sklearn.model_selection import (
    StratifiedKFold,
    KFold,
    StratifiedGroupKFold,
    GroupKFold,
    TimeSeriesSplit,
)
from sklearn.model_selection._split import _BaseKFold

from dreamml.utils.warnings import DMLWarning

TIME_PERIOD_FUNCTIONS = {
    "day": lambda series: series.dt.strftime("%Y-%m-%d"),
    "day_of_week": lambda series: series.dt.day_of_week,  # %w
    "day_of_month": lambda series: series.dt.isocalendar()["day"],  # %d
    "day_of_year": lambda series: series.dt.day_of_year,  # %j (zero padded)
    "week": lambda series: series.dt.strftime("%Y-%W"),
    "week_of_year": lambda series: series.dt.isocalendar()["week"],  # %W
    "month": lambda series: series.dt.strftime("%Y-%m"),
    "month_of_year": lambda series: series.dt.month,  # %m
    "year": lambda series: series.dt.isocalendar()["year"],  # %Y or %y
    "hour": lambda series: series.dt.hour,  # %H
    "minute": lambda series: series.dt.minute,  # %M
    "second": lambda series: series.dt.second,  # %S
    "unique_hour": lambda series: series.dt.strftime("%Y-%m-%d_%H"),
    "unique_minute": lambda series: series.dt.strftime("%Y-%m-%d_%H_%M"),
    "unique_second": lambda series: series.dt.strftime("%Y-%m-%d_%H_%M_%S"),
    "min": lambda series: pd.Series(
        series.factorize(sort=False)[0], index=series.index
    ),
}


class BaseCrossValidator(ABC):
    """
    Base class for cross-validation, which splits a pandas DataFrame into folds.

    Attributes:
        n_splits (int): Number of splits/folds.
        _required_columns (List[str]): List of required column names.
    """

    def __init__(self, n_splits: int = 5):
        """
        Initializes the BaseCrossValidator.

        Args:
            n_splits (int, optional): Number of splits/folds. Defaults to 5.
        """
        self.n_splits = n_splits
        self._required_columns = []

    @abc.abstractmethod
    def split(
        self, df: pd.DataFrame
    ) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Splits the DataFrame into train and test indices.

        Args:
            df (pd.DataFrame): The DataFrame to split.

        Yields:
            Generator[Tuple[np.ndarray, np.ndarray], None, None]: A generator of train and test indices.
        """
        raise NotImplementedError

    def get_n_splits(self) -> int:
        """
        Returns the number of splits.

        Returns:
            int: Number of splits.
        """
        return self.n_splits

    def _set_required_columns(self, columns: List[str]):
        """
        Sets the required columns for splitting.

        Args:
            columns (List[str]): List of column names.
        """
        self._required_columns = columns

    def get_required_columns(self) -> List[str]:
        """
        Returns the required columns that must be present in the DataFrame passed to the `split` method.

        Returns:
            List[str]: A list of required column names.
        """
        return self._required_columns


class KFoldCrossValidator(BaseCrossValidator):
    """
    Cross-validator for splitting a pandas DataFrame into folds.

    Inherits from BaseCrossValidator and supports optional stratification based on a specified column.

    Attributes:
        stratify_column (Optional[str]): Column name to stratify splits.
        shuffle (bool): Whether to shuffle the data before splitting.
        random_state (Optional[int]): Random state for shuffling.
        cv (_BaseKFold): The underlying scikit-learn cross-validator.
    """

    def __init__(
        self,
        stratify_column: Optional[str] = None,
        n_splits: int = 5,
        shuffle: bool = False,
        random_state: Optional[int] = None,
    ):
        """
        Initializes the KFoldCrossValidator.

        Args:
            stratify_column (Optional[str], optional): Column name to stratify splits. Defaults to None.
            n_splits (int, optional): Number of splits/folds. Defaults to 5.
            shuffle (bool, optional): Whether to shuffle the data before splitting. Defaults to False.
            random_state (Optional[int], optional): Random state for shuffling. Defaults to None.
        """
        super().__init__(n_splits)
        self.shuffle = shuffle
        self.random_state = random_state
        self.stratify_column = stratify_column

        self.cv: _BaseKFold = self._choose_cv_method()

        required_columns = [stratify_column] if stratify_column is not None else []
        self._set_required_columns(required_columns)

    def split(self, df: pd.DataFrame):
        """
        Splits the DataFrame into train and test indices.

        Args:
            df (pd.DataFrame): The DataFrame to split.

        Returns:
            Generator[Tuple[np.ndarray, np.ndarray], None, None]: A generator of train and test indices.
        """
        if self.stratify_column is not None:
            return self.cv.split(df, y=df[self.stratify_column])
        else:
            return self.cv.split(df, y=None)

    def _get_stratified_cv(self):
        """
        Creates a stratified K-Fold cross-validator.

        Returns:
            StratifiedKFold: A stratified K-Fold cross-validator.
        """
        return StratifiedKFold(
            self.n_splits, shuffle=self.shuffle, random_state=self.random_state
        )

    def _get_unstratified_cv(self):
        """
        Creates an unstratified K-Fold cross-validator.

        Returns:
            KFold: An unstratified K-Fold cross-validator.
        """
        return KFold(
            self.n_splits, shuffle=self.shuffle, random_state=self.random_state
        )

    def _choose_cv_method(self) -> _BaseKFold:
        """
        Chooses the appropriate cross-validator based on stratification.

        Returns:
            _BaseKFold: The chosen cross-validator.
        """
        if self.stratify_column is not None:
            return self._get_stratified_cv()
        else:
            return self._get_unstratified_cv()


class GroupCrossValidator(KFoldCrossValidator):
    """
    Cross-validator for splitting a pandas DataFrame into folds based on groups.

    Inherits from KFoldCrossValidator and ensures that the entire group is assigned to a single fold.

    Attributes:
        group_columns (List[str]): List of columns to define groups.
        _concat_string (str): String used to concatenate group columns.
    """

    def __init__(
        self,
        group_columns: List[str],
        stratify_column: Optional[str] = None,
        n_splits: int = 5,
        shuffle: bool = False,
        random_state: Optional[int] = None,
    ):
        """
        Initializes the GroupCrossValidator.

        Args:
            group_columns (List[str]): List of columns to define groups.
            stratify_column (Optional[str], optional): Column name to stratify splits. Defaults to None.
            n_splits (int, optional): Number of splits/folds. Defaults to 5.
            shuffle (bool, optional): Whether to shuffle the data before splitting. Defaults to False.
            random_state (Optional[int], optional): Random state for shuffling. Defaults to None.

        Raises:
            TypeError: If group_columns is not a list of strings.
        """
        super().__init__(stratify_column, n_splits, shuffle, random_state)
        if not isinstance(group_columns, list) or (
            (len(group_columns) > 0) and not isinstance(group_columns[0], str)
        ):
            raise TypeError("Passed group_columns have to be of List[str] type")

        self.group_columns = group_columns
        self._concat_string = "_G_"

        self.cv = self._choose_cv_method()

        required_columns = group_columns

        if stratify_column is not None:
            required_columns.append(stratify_column)

        self._set_required_columns(required_columns)

    def split(self, df: pd.DataFrame):
        """
        Splits the DataFrame into train and test indices based on groups.

        Args:
            df (pd.DataFrame): The DataFrame to split.

        Returns:
            Generator[Tuple[np.ndarray, np.ndarray], None, None]: A generator of train and test indices.
        """
        groups = self._combine_groups(df)

        if self.stratify_column is not None:
            return self.cv.split(df, y=df[self.stratify_column], groups=groups)
        else:
            return self.cv.split(df, y=None, groups=groups)

    def _get_stratified_cv(self):
        """
        Creates a stratified group K-Fold cross-validator.

        Returns:
            StratifiedGroupKFold: A stratified group K-Fold cross-validator.
        """
        return StratifiedGroupKFold(
            self.n_splits, shuffle=self.shuffle, random_state=self.random_state
        )

    def _get_unstratified_cv(self):
        """
        Creates an unstratified group K-Fold cross-validator.

        Returns:
            GroupKFold: An unstratified group K-Fold cross-validator.
        """
        return GroupKFold(self.n_splits)

    def _combine_groups(self, df: pd.DataFrame) -> pd.Series:
        """
        Combines multiple group columns into a single group identifier.

        Args:
            df (pd.DataFrame): The DataFrame containing the group columns.

        Returns:
            pd.Series: A Series representing combined groups.
        """
        # cast to string and concatenate
        groups = (
            df[self.group_columns]
            .astype(str)
            .apply(lambda row: self._concat_string.join(row), axis=1)
        )

        return groups


class GroupTimePeriodCrossValidator(GroupCrossValidator):
    """
    Cross-validator for splitting a pandas DataFrame into folds based on groups and time periods.

    Time period is used as an additional grouping dimension.

    For example, if the time period is 'month_of_year', during cross-validation, data from the same calendar month
    (e.g., January 2023 and January 2024) will not be in the same fold. If the time period is 'month',
    then data from January 2023 and January 2024 can be in the same fold.

    Attributes:
        time_column (str): Name of the time column.
        time_period (str): Time period for grouping.
    """

    _available_periods = list(TIME_PERIOD_FUNCTIONS.keys())

    def __init__(
        self,
        time_column: str,
        time_period: str,
        group_columns: Optional[List[str]] = None,
        stratify_column: Optional[str] = None,
        n_splits: int = 5,
        shuffle: bool = False,
        random_state: Optional[int] = None,
    ):
        """
        Initializes the GroupTimePeriodCrossValidator.

        Args:
            time_column (str): Name of the time column.
            time_period (str): Time period for grouping.
            group_columns (Optional[List[str]], optional): List of columns to define groups. Defaults to None.
            stratify_column (Optional[str], optional): Column name to stratify splits. Defaults to None.
            n_splits (int, optional): Number of splits/folds. Defaults to 5.
            shuffle (bool, optional): Whether to shuffle the data before splitting. Defaults to False.
            random_state (Optional[int], optional): Random state for shuffling. Defaults to None.

        Raises:
            ValueError: If an invalid time period is provided.
        """
        if group_columns is None:
            group_columns = []

        if time_period not in self._available_periods:
            raise ValueError(
                f"Wrong time period is passed. Expected `time_period` to be one of "
                f"{self._available_periods}, but got time_period={time_period}."
            )

        super().__init__(
            group_columns, stratify_column, n_splits, shuffle, random_state
        )
        self.time_column = time_column
        self.time_period = time_period

        required_columns = group_columns + [time_column]
        if stratify_column is not None and stratify_column not in required_columns:
            required_columns.append(stratify_column)

        self._set_required_columns(required_columns)

    def _get_time_period_group(self, series: pd.Series):
        """
        Generates groups based on the specified time period.

        Args:
            series (pd.Series): The time column series.

        Returns:
            pd.Series: A series representing time period groups.

        Raises:
            ValueError: If the time column is not of datetime64 dtype or an invalid time_period is provided.
        """
        if not is_datetime64_any_dtype(series.dtype):
            raise ValueError(
                f"Expected column {self.time_column} to have type datetime64, but got dtype={series.dtype}"
            )

        if self.time_period in TIME_PERIOD_FUNCTIONS:
            return TIME_PERIOD_FUNCTIONS[self.time_period](series)
        elif "%" in self.time_period:
            return series.dt.strftime(self.time_period)
        else:
            raise ValueError(
                f"Wrong time period is passed. Expected `time_period` to be one of "
                f"{list(TIME_PERIOD_FUNCTIONS.keys())} or strftime format, "
                f"but got time_period={self.time_period}."
            )

    def _combine_groups(self, df: pd.DataFrame) -> pd.Series:
        """
        Combines group columns with time period groups to form a single group identifier.

        Args:
            df (pd.DataFrame): The DataFrame containing group and time columns.

        Returns:
            pd.Series: A combined series representing groups.
        """
        period_groups = self._get_time_period_group(df[self.time_column]).astype(str)

        if len(self.group_columns) > 0:
            combined_groups = super()._combine_groups(df)

            return combined_groups + self._concat_string + period_groups
        else:
            return period_groups


class TimeSeriesGroupTimePeriodCrossValidator(GroupTimePeriodCrossValidator):
    """
    Cross-validator for splitting a pandas DataFrame for time series data.

    Allows groups to overlap across different folds.

    Attributes:
        _available_periods (List[str]): Available time periods for grouping.
    """

    _available_periods = [
        "min",
        "unique_second",
        "unique_minute",
        "unique_hour",
        "day",
        "month",
        "week",
        "year",
    ]

    def __init__(
        self,
        time_column: str,
        time_period: str,
        group_columns: Optional[List[str]] = None,
        n_splits: int = 5,
        sliding_window: bool = False,
        test_size: Optional[int] = None,
        gap: int = 0,
    ):
        """
        Initializes the TimeSeriesGroupTimePeriodCrossValidator.

        Args:
            time_column (str): Name of the time column.
            time_period (str): Time period for grouping.
            group_columns (Optional[List[str]], optional): List of columns to define groups. Defaults to None.
            n_splits (int, optional): Number of splits/folds. Defaults to 5.
            sliding_window (bool, optional): Whether to use a sliding window approach. Defaults to False.
            test_size (Optional[int], optional): Size of the test set. Defaults to None.
            gap (int, optional): Gap between train and test sets. Defaults to 0.

        Raises:
            ValueError: If test_size is not positive.
            NotImplementedError: If sliding_window is set to True.
            Warning: If time_period is set but time_column is not provided.
        """
        super().__init__(
            time_column=time_column,
            time_period=time_period,
            group_columns=group_columns,
            stratify_column=None,
            n_splits=n_splits,
            shuffle=False,
            random_state=None,
        )

        if test_size is not None and test_size <= 0:
            raise ValueError(f"test_size has to be > 0, but got test_size={test_size}")

        self.cv = TimeSeriesSplit(
            n_splits=n_splits, max_train_size=None, test_size=test_size, gap=gap
        )
        self.sliding_window = sliding_window
        self.test_size = test_size
        self.gap = gap

        if sliding_window:
            raise NotImplementedError

        if self.time_period is not None and time_column is None:
            warnings.warn(
                f"time_period={self.time_period} is passed but `time_column` is not provided",
                DMLWarning,
                stacklevel=2,
            )

        required_columns = [time_column]

        if group_columns is not None:
            required_columns += group_columns

        self._set_required_columns(required_columns)

    def split(self, df: pd.DataFrame):
        """
        Splits the DataFrame into train and test indices for time series data.

        Args:
            df (pd.DataFrame): The DataFrame to split.

        Yields:
            Tuple[np.ndarray, np.ndarray]: Train and test indices.
        """
        inverse_argsort = (
            df[self.time_column]
            .argsort()
            .reset_index(drop=True)
            .sort_values()
            .index.values
        )

        time_sorted_df = df.sort_values(by=self.time_column)

        groups = self._combine_groups(time_sorted_df)

        factorized = groups.factorize(sort=False)[0][inverse_argsort]

        unique_factorized = np.unique(factorized)

        indices = np.arange(len(df))
        for train_idx, test_idx in self.cv.split(unique_factorized):
            train_mask = np.isin(factorized, unique_factorized[train_idx])
            test_mask = np.isin(factorized, unique_factorized[test_idx])

            yield indices[train_mask], indices[test_mask]


class TimeSeriesCrossValidator(KFoldCrossValidator):
    """
    Cross-validator for splitting a pandas DataFrame for time series data.

    Utilizes TimeSeriesSplit to ensure temporal ordering of data in splits.
    """

    def __init__(
        self,
        time_column: Optional[str] = None,
        n_splits: int = 5,
        sliding_window: bool = False,
        test_size: Optional[int] = None,
        gap: int = 0,
    ):
        """
        Initializes the TimeSeriesCrossValidator.

        Args:
            time_column (Optional[str], optional): Name of the time column. Defaults to None.
            n_splits (int, optional): Number of splits/folds. Defaults to 5.
            sliding_window (bool, optional): Whether to use a sliding window approach. Defaults to False.
            test_size (Optional[int], optional): Size of the test set. Defaults to None.
            gap (int, optional): Gap between train and test sets. Defaults to 0.

        Raises:
            NotImplementedError: If sliding_window is set to True.
        """
        super().__init__(
            stratify_column=None, n_splits=n_splits, shuffle=False, random_state=None
        )

        self.cv = TimeSeriesSplit(
            n_splits=n_splits, max_train_size=None, test_size=test_size, gap=gap
        )
        self.time_column = time_column
        self.sliding_window = sliding_window
        self.test_size = test_size
        self.gap = gap

        if sliding_window:
            raise NotImplementedError

        required_columns = [time_column] if time_column is not None else []
        self._set_required_columns(required_columns)

    def _split_by_time(self, df: pd.DataFrame):
        """
        Splits the DataFrame based on time ordering.

        Args:
            df (pd.DataFrame): The DataFrame to split.

        Yields:
            Tuple[np.ndarray, np.ndarray]: Train and test indices.
        """
        series = df[self.time_column]

        ascending_order_indices = series.argsort().values

        for train_idx, test_idx in self.cv.split(ascending_order_indices):
            yield ascending_order_indices[train_idx], ascending_order_indices[test_idx]

    def split(self, df: pd.DataFrame):
        """
        Splits the DataFrame into train and test indices for time series data.

        Args:
            df (pd.DataFrame): The DataFrame to split.

        Returns:
            Generator[Tuple[np.ndarray, np.ndarray], None, None]: A generator of train and test indices.
        """
        if self.time_column is None or df[self.time_column].is_monotonic_increasing:
            return super().split(df)
        else:
            return self._split_by_time(df)