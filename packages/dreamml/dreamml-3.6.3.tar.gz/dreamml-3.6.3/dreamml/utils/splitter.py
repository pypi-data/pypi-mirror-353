# coding=utf-8
"""Module implementing a transformer for splitting datasets into train, validation, and test sets.

Available entities:
- DataSplitter: a splitter for train, validation, and test sets.
"""

from typing import List, Dict, Tuple, Sequence, Optional
import warnings

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split
from skmultilearn.model_selection import IterativeStratification

from dreamml.utils.warnings import DMLWarning


def check_input_lengths(split_fractions: List[float]) -> None:
    """Validate the split fractions for dataset splitting.

    Args:
        split_fractions (List[float]): List of fractions for splitting the dataset.
            It should contain either 2 or 3 float values representing the proportions
            for train, validation, and test splits. If only two fractions are provided,
            the test fraction is computed automatically.

    Raises:
        AssertionError: If the number of split fractions is not 2 or 3,
                        or if the sum of split fractions does not equal 1.
    """
    assert len(split_fractions) in (2, 3), (
        f"The specified split rule must contain 2 or 3 classes. "
        f"Provided {len(split_fractions)}."
    )
    if len(split_fractions) == 2:
        assert (
            sum(split_fractions) < 1 - 1e-5
        ), "The sum of the provided fractions must be less than 1, and the test fraction must be greater than 0."
        split_fractions.append(1 - sum(split_fractions))

    assert (
        abs(1 - sum(split_fractions)) <= 1e-5
    ), "The provided fractions must sum to 1."


class DataSplitter(BaseEstimator, TransformerMixin):
    """Transformer for splitting datasets into train, validation, and test sets.

    Args:
        split_fractions (List[float]): List of fractions for splitting the dataset into train, validation, and test sets.
            For example, [0.6, 0.3, 0.1]. The test fraction must be greater than 0.
            If only two fractions are provided, the test fraction is determined automatically.
        shuffle (bool, optional): Whether to shuffle the data before splitting. Defaults to True.
        group_column (Optional[str], optional): The name of the column to group by before splitting. Defaults to None.
        target_name (Optional[str], optional): The name of the target column to stratify by if group_column is not specified. Defaults to None.
        stratify (bool, optional): Whether to perform stratified splitting based on the target. Defaults to False.
        task (Optional[str], optional): The type of task, e.g., "timeseries". Defaults to None.
        time_column (Optional[str], optional): The name of the time column for time series tasks. Defaults to None.
        split_by_group (bool, optional): Whether to split based on groups. Defaults to False.
    """

    def __init__(
        self,
        split_fractions: List[float],
        shuffle: bool = True,
        group_column: Optional[str] = None,
        target_name: Optional[str] = None,
        stratify: bool = False,
        task: Optional[str] = None,
        time_column: Optional[str] = None,
        split_by_group: bool = False,
    ) -> None:

        check_input_lengths(split_fractions)

        self.split_fractions = split_fractions
        self.n_samples = len(split_fractions)
        self.group_column = group_column
        self.split_by_group = split_by_group
        self.target_name = target_name
        self.shuffle = shuffle
        self.stratify = stratify
        self.task = task
        self.time_column = time_column

    def transform(
        self, data: pd.DataFrame, target: Optional[Sequence] = None
    ) -> Tuple[Sequence, Sequence, Sequence]:
        """Split the dataset into train, validation, and test sets.

        Args:
            data (pd.DataFrame): The dataset to split.
            target (Optional[Sequence], optional): The target variable for stratified splitting.
                If provided, it overrides the `target_name` provided during initialization.
                Defaults to None.

        Returns:
            Tuple[Sequence, Sequence, Sequence]: Indices for the train, validation, and test sets.
        """
        splitter = self.get_splitter()

        if target is None:
            indexes = splitter(data)
        else:
            # For backward compatibility
            original_target_name = self.target_name
            self.target_name = "__tmp__"

            data["__tmp__"] = target
            indexes = splitter(data)
            data.pop("__tmp__")

            self.target_name = original_target_name

        return indexes

    def get_splitter(self) -> callable:
        """Select the method for splitting the dataset.

        Returns:
            callable: The selected splitting method.
        """
        if self.group_column and self.split_by_group:
            return self._column_split
        elif self.target_name:
            return self._random_stratify_split
        else:
            return self._random_split

    def _random_stratify_split(
        self, data: pd.DataFrame
    ) -> Tuple[Sequence, Sequence, Sequence]:
        """Random and stratified splitting based on the target variable.

        Applied when the target is a binary or multi-label vector.

        Args:
            data (pd.DataFrame): The dataset to split.

        Returns:
            Tuple[Sequence, Sequence, Sequence]: Indices for the train, validation, and test sets.
        """
        target = data.get(self.target_name)

        if self.stratify:
            if target is None:
                warnings.warn(
                    f"Cannot perform stratified split with {self.target_name}. Performing random split",
                    DMLWarning,
                    stacklevel=3,
                )
            elif isinstance(target, pd.DataFrame):
                return self._calculate_multilabel_stratify_split_idx(
                    data=data,
                    target=target,
                )
            else:
                return self._calculate_split_idx(data.index, target, self.shuffle)

        return self._random_split(data)

    def _random_split(self, data: pd.DataFrame) -> Tuple[Sequence, Sequence, Sequence]:
        """Randomly split the dataset into train, validation, and test sets.

        Applied when the target is a continuous variable.

        Args:
            data (pd.DataFrame): The dataset to split.

        Returns:
            Tuple[Sequence, Sequence, Sequence]: Indices for the train, validation, and test sets.
        """
        return self._calculate_split_idx(data.index, shuffle=self.shuffle)

    def _column_split(self, data: pd.DataFrame) -> Tuple[Sequence, Sequence, Sequence]:
        """Split the dataset into train, validation, and test sets based on a specific column.

        Applied when `group_column` is specified and splitting by group is required (e.g., by customer).

        Args:
            data (pd.DataFrame): The dataset to split.

        Returns:
            Tuple[Sequence, Sequence, Sequence]: Indices for the train, validation, and test sets.
        """
        values = data[self.group_column].unique()
        if self.task is not None and self.task == "timeseries":
            train_idx, valid_idx, test_idx = self._timeseries_segment_split(data)
            return train_idx, valid_idx, test_idx

        train_idx, valid_idx, test_idx = self._calculate_split_idx(
            values, shuffle=self.shuffle
        )

        train_mask = data[self.group_column].isin(train_idx)
        train_idx = data.loc[train_mask].index

        valid_mask = data[self.group_column].isin(valid_idx)
        valid_idx = data.loc[valid_mask].index

        test_mask = data[self.group_column].isin(test_idx)
        test_idx = data.loc[test_mask].index

        return train_idx, valid_idx, test_idx

    def _timeseries_segment_split(self, data: pd.DataFrame) -> Tuple[pd.Index, pd.Index, pd.Index]:
        """Split the dataset into train, validation, and test sets for time series tasks based on a specific column.

        Applied when `group_column` is specified and splitting by group is required for time series tasks.

        Args:
            data (pd.DataFrame): The dataset to split.

        Returns:
            Tuple[pd.Index, pd.Index, pd.Index]: Indices for the train, validation, and test sets.
        """
        train_segmented, test_segmented, val_segmented = [], [], []

        for segment in data[self.group_column].unique():
            segment_data = data[data[self.group_column] == segment]
            if self.time_column is not None and self.time_column in data.columns:
                segment_data = segment_data.sort_values(by=[self.time_column])
            else:
                segment_data = segment_data.sort_index()

            train_size = int(len(segment_data) * self.split_fractions[0])
            test_size = int(len(segment_data) * self.split_fractions[2])

            train = segment_data.iloc[:train_size].index.to_list()
            test = segment_data.iloc[
                train_size : train_size + test_size
            ].index.to_list()
            valid = segment_data.iloc[train_size + test_size :].index.to_list()

            train_segmented.extend(train)
            test_segmented.extend(test)
            val_segmented.extend(valid)

        return (
            pd.Index(train_segmented),
            pd.Index(test_segmented),
            pd.Index(val_segmented),
        )

    def _calculate_split_idx(
        self,
        idx_array: Sequence,
        target: Optional[Sequence] = None,
        shuffle: bool = False,
    ) -> Tuple[Sequence, Sequence, Sequence]:
        """Calculate the indices for train, validation, and test sets.

        Args:
            idx_array (Sequence): The indices to split.
            target (Optional[Sequence], optional): The target variable for stratification. Defaults to None.
            shuffle (bool, optional): Whether to shuffle the data before splitting. Defaults to False.

        Returns:
            Tuple[Sequence, Sequence, Sequence]: Indices for the train, validation, and test sets.
        """
        train_idx, valid_idx = train_test_split(
            idx_array,
            train_size=self.split_fractions[0],
            stratify=target,
            shuffle=shuffle,
        )

        if (
            isinstance(self.split_fractions[0], float)
            and sum(self.split_fractions) <= 1
        ):
            size = self.split_fractions[1] / (
                self.split_fractions[1] + self.split_fractions[2]
            )
        else:
            size = self.split_fractions[1]

        if isinstance(target, pd.Series):
            target = target.loc[valid_idx]

        valid_idx, test_idx = train_test_split(
            valid_idx,
            train_size=size,
            stratify=target,
            random_state=10,
            shuffle=shuffle,
        )

        return train_idx, valid_idx, test_idx

    def _calculate_multilabel_stratify_split_idx(
        self,
        data: pd.DataFrame,
        target: pd.DataFrame,
    ) -> Tuple[Sequence, Sequence, Sequence]:
        """Calculate the indices for multilabel train, validation, and test sets.

        Args:
            data (pd.DataFrame): The feature data to split.
            target (pd.DataFrame): The multilabel target data.

        Returns:
            Tuple[Sequence, Sequence, Sequence]: Indices for the train, validation, and test sets.
        """
        if target.isna().sum().sum():
            target = target.fillna(value=-1)

        train_indexes, test_indexes = iterative_train_test_split(
            data.values,
            target.values,
            test_size=self.split_fractions[2],
        )
        if (
            isinstance(self.split_fractions[0], float)
            and sum(self.split_fractions) <= 1
        ):
            size = self.split_fractions[1] / (
                self.split_fractions[1] + self.split_fractions[2]
            )
        else:
            size = self.split_fractions[1]

        test_indexes, valid_indexes = iterative_train_test_split(
            data.values[test_indexes],
            target.values[test_indexes],
            test_size=size,
        )
        return train_indexes, valid_indexes, test_indexes


def iterative_train_test_split(X: Sequence, y: Sequence, test_size: float) -> Tuple[Sequence, Sequence]:
    """Perform an iteratively stratified train/test split.

    Args:
        X (Sequence): Feature data.
        y (Sequence): Target labels.
        test_size (float): The proportion of the dataset to include in the test split, in the range (0, 1).

    Returns:
        Tuple[Sequence, Sequence]: Stratified train and test indices.
    """
    stratifier = IterativeStratification(
        n_splits=2, order=2, sample_distribution_per_fold=[test_size, 1.0 - test_size]
    )
    train_indexes, test_indexes = next(stratifier.split(X, y))
    return train_indexes, test_indexes


def concatenate_all_samples(eval_set: Dict[str, Tuple[pd.DataFrame, Sequence]]) -> pd.DataFrame:
    """Concatenate all samples from evaluation sets into a single DataFrame.

    Args:
        eval_set (Dict[str, Tuple[pd.DataFrame, Sequence]]): A dictionary where each key is a sample name
            and the value is a tuple containing a DataFrame and a sequence.

    Returns:
        pd.DataFrame: A concatenated DataFrame containing all samples.
    """
    all_data = pd.DataFrame()
    for sample_name, (X_sample, _) in eval_set.items():
        all_data = pd.concat([all_data, X_sample], axis=0)
    return all_data