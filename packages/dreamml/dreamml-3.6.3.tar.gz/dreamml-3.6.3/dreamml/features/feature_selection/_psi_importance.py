from typing import Optional, List

import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.exceptions import NotFittedError
from dreamml.utils.errors import MissedColumnError


class PSI(BaseEstimator, TransformerMixin):
    """Calculate PSI and select features based on PSI.

    PSI (Population Stability Index) is used to measure the stability of a feature
    over time or across different datasets. Features with PSI above a threshold are
    marked for exclusion, while those below are retained for further analysis.

    Args:
        threshold (float): The threshold for selecting features based on PSI.
            Features with PSI above this threshold are marked as 0 (exclude),
            and those below are marked as 1 (include).
        categorical_features (Optional[List[str]], optional): List of categorical feature names.
            Defaults to None.
        remaining_features (List[str], optional): List of features to always include.
            Defaults to an empty list.
        bin_type (str, optional): Method for binning the data. 
            Options are "quantiles", "bins", or "continuous".
            Defaults to "quantiles".
        min_value (float, optional): Value to substitute when PSI is zero.
            Defaults to 0.005.
        n_bins (int, optional): Number of bins to divide the data into.
            Defaults to 20.
        used_features (Optional[List[str]], optional): List of features to consider.
            If None, all features are used. Defaults to None.

    Attributes:
        scores_ (Dict[str, float]): Dictionary containing PSI scores for each feature.
        used_features (List[str]): List of selected features based on PSI.
    """

    def __init__(
        self,
        threshold: float,
        categorical_features: Optional[List[str]] = None,
        remaining_features: List[str] = [],
        bin_type: str = "quantiles",
        min_value: float = 0.005,
        n_bins: int = 20,
        used_features=None,
    ):
        self.threshold = threshold
        self.categorical_features = categorical_features
        self.remaining_features = remaining_features
        self.min_value = min_value
        self.n_bins = n_bins
        if bin_type in ["quantiles", "bins", "continuous"]:
            self.bin_type = bin_type
        else:
            raise ValueError(
                "Incorrect bin_type value. Expected 'quantiles', 'bins' or 'continuous', "
                f"but {bin_type} is transferred."
            )
        self.scores = {}
        self.used_features = used_features

    @property
    def check_is_fitted(self):
        """Check if the estimator has been fitted.

        Raises:
            NotFittedError: If the estimator has not been fitted yet.

        Returns:
            bool: Always returns True if fitted.
        """
        if not self.scores:
            msg = (
                "This estimator is not fitted yet. Call 'fit' with "
                "appropriate arguments before using this estimator."
            )
            raise NotFittedError(msg)
        return True

    def calculate_bins(
        self, expected: pd.Series, actual: pd.Series, threshold: float = 0.05
    ) -> np.array:
        """Calculate bin edges for splitting the dataset.

        Depending on the binning strategy, this function determines the
        bin edges for PSI calculation.

        Args:
            expected (pd.Series): Observations from the training dataset.
            actual (pd.Series): Observations from the testing dataset.
                Required for "continuous" binning strategy.
            threshold (float, optional): Minimum proportion of samples per bin.
                Required for "continuous" binning strategy. Defaults to 0.05.

        Returns:
            np.array: Array of unique bin edges.
        
        Raises:
            ValueError: If an invalid binning strategy is provided.
        """
        if self.bin_type == "quantiles":
            bins = np.linspace(0, 100, self.n_bins + 1)
            bins = [np.nanpercentile(expected, x) for x in bins]
        elif self.bin_type == "continuous":
            min_expected_len = (
                int(len(expected) * threshold)
                if len(expected) * threshold > 5
                else len(expected)
            )
            min_actual_len = (
                int(len(actual) * threshold)
                if len(actual) * threshold > 5
                else len(actual)
            )
            bins = sorted(
                self.calculate_continuous_bins(
                    expected, actual, min_expected_len, min_actual_len
                )
            )
        else:
            bins = np.linspace(expected.min(), expected.max(), self.n_bins + 1)

        return np.unique(bins)

    def calculate_continuous_bins(
        self,
        expected: pd.Series,
        actual: pd.Series,
        min_expected_len: int,
        min_actual_len: int,
        result: List = None,
    ):
        """Calculate bin edges using the "continuous" strategy.

        Splits the dataset into bins with uniform boundaries across both
        expected and actual datasets, ensuring each bin contains at least
        a specified minimum proportion of samples.

        Args:
            expected (pd.Series): Observations from the training dataset.
            actual (pd.Series): Observations from the testing dataset.
            min_expected_len (int): Minimum number of samples in each bin for the expected dataset.
            min_actual_len (int): Minimum number of samples in each bin for the actual dataset.
            result (List, optional): List to store the resulting bin edges. Defaults to None.

        Returns:
            List: List of bin edges.
        """
        if not result:
            result = []

        median_value = np.median(expected)

        left_test = expected[expected <= median_value]
        left_oot = actual[actual <= median_value]
        right_test = expected[expected > median_value]
        right_oot = actual[actual > median_value]
        if (
            len(left_test) >= min_expected_len
            and len(left_oot) >= min_actual_len
            and len(right_test) >= min_expected_len
            and len(right_oot) >= min_actual_len
        ):
            if median_value not in result:
                result.append(median_value)
            result = self.calculate_continuous_bins(
                left_test, left_oot, min_expected_len, min_actual_len, result
            )
            result = self.calculate_continuous_bins(
                right_test, right_oot, min_expected_len, min_actual_len, result
            )

        return result

    def calculate_psi_in_bin(self, expected_score, actual_score) -> float:
        """Calculate the PSI value for a single bin.

        Handles cases where expected or actual scores are zero by substituting
        them with a minimum value to avoid division by zero.

        Args:
            expected_score (float): Expected proportion in the bin.
            actual_score (float): Actual proportion in the bin.

        Returns:
            float: PSI value for the bin.
        """
        if expected_score == 0:
            expected_score = self.min_value
        if actual_score == 0:
            actual_score = self.min_value

        value = expected_score - actual_score
        value = value * np.log(expected_score / actual_score)

        return value

    def calculate_psi(self, expected: pd.Series, actual: pd.Series, bins) -> float:
        """Calculate the PSI for a single feature.

        Args:
            expected (pd.Series): Observations from the training dataset.
            actual (pd.Series): Observations from the testing dataset.
            bins (array-like): Bin edges for PSI calculation.

        Returns:
            float: PSI score for the feature.
        """
        expected_score = np.histogram(expected.fillna(-9999), bins)[0]
        expected_score = expected_score / expected.shape[0]

        actual_score = np.histogram(actual.fillna(-9999), bins)[0]
        actual_score = actual_score / actual.shape[0]

        psi_score = np.sum(
            self.calculate_psi_in_bin(exp_score, act_score)
            for exp_score, act_score in zip(expected_score, actual_score)
        )

        return psi_score

    def calculate_numeric_psi(self, expected: pd.Series, actual: pd.Series) -> float:
        """Calculate PSI for a numerical feature.

        Args:
            expected (pd.Series): Observations from the training dataset.
            actual (pd.Series): Observations from the testing dataset.

        Returns:
            float: PSI score for the numerical feature.
        """
        bins = self.calculate_bins(expected, actual)
        psi_score = self.calculate_psi(expected, actual, bins)
        return psi_score

    def calculate_categorical_psi(
        self, expected: pd.Series, actual: pd.Series
    ) -> float:
        """Calculate PSI for a categorical feature.

        PSI is calculated for each unique category.

        Args:
            expected (pd.Series): Observations from the training dataset.
            actual (pd.Series): Observations from the testing dataset.

        Returns:
            float: PSI score for the categorical feature.
        """
        bins = np.unique(expected).tolist()
        expected_score = expected.value_counts(normalize=True)
        actual_score = actual.value_counts(normalize=True)

        expected_score = expected_score.sort_index().values
        actual_score = actual_score.sort_index().values

        psi_score = np.sum(
            self.calculate_psi_in_bin(exp_score, act_score)
            for exp_score, act_score in zip(expected_score, actual_score)
        )
        return psi_score

    def fit(self, data, target=None):
        """Compute PSI scores for all features.

        Args:
            data (pd.DataFrame): Training feature matrix.
            target (pd.DataFrame): Testing feature matrix.

        Raises:
            MissedColumnError: If there are missing columns in the target data.

        Returns:
            self: Fitted estimator.
        """
        missed_columns = list(set(data.columns) - set(target.columns))

        if missed_columns:
            raise MissedColumnError(f"Missed {list(missed_columns)} columns in data.")

        if self.categorical_features:
            numeric_features = list(set(data.columns) - set(self.categorical_features))
            self.categorical_features = list(
                set(data.columns) & set(self.categorical_features)
            )
            for feature in self.categorical_features:
                self.scores[feature] = self.calculate_categorical_psi(
                    data[feature], target[feature]
                )
        else:
            numeric_features = data.columns

        if self.used_features is not None:
            numeric_features = [f for f in numeric_features if f in self.used_features]

        for feature in tqdm(numeric_features):
            self.scores[feature] = self.calculate_numeric_psi(
                data[feature], target[feature]
            )
        return self

    def transform(self, data, target=None) -> pd.DataFrame:
        """Select features based on the PSI threshold.

        Features with PSI below the threshold or listed in remaining_features
        are marked for inclusion, while others are excluded.

        Args:
            data (pd.DataFrame): Training feature matrix.
            target (pd.DataFrame): Testing feature matrix.

        Raises:
            NotFittedError: If the estimator has not been fitted.

        Returns:
            pd.DataFrame: DataFrame containing PSI analysis with selection flags.
        """
        self.check_is_fitted
        scores = pd.Series(self.scores)
        scores = pd.DataFrame({"Variable": scores.index, "PSI": scores.values})
        scores["Selected"] = scores.apply(
            lambda row: (
                1
                if row["PSI"] < self.threshold
                or row["Variable"] in self.remaining_features
                else 0
            ),
            axis=1,
        )
        scores = scores.sort_values(by="PSI")

        mask = scores["Selected"] == 1
        # self.used_features = scores.loc[mask, "Variable"].tolist()

        return scores.reset_index(drop=True)


def choose_psi_sample(eval_sets: dict, config: dict) -> dict:
    """Select the dataset for PSI calculation based on configuration.

    The selection is based on the `psi_sample` parameter in the experiment
    configuration. If the value is `valid` or `test`, the corresponding dataset
    is used entirely. If the value is `OOT`, the dataset is split into two
    non-overlapping subsets, one for PSI calculation and the other for independent
    quality assessment.

    Args:
        eval_sets (dict): Dictionary containing evaluation datasets.
            Expected format: {str: Tuple[pd.DataFrame, pd.Series]}.
        config (dict): Configuration dictionary for the experiment.

    Raises:
        ValueError: If an unknown psi_sample name is provided.

    Returns:
        Tuple[dict, pd.DataFrame]: 
            - Updated eval_sets dictionary.
            - Dataset used for PSI calculation.
    """
    psi_sample_name = config.get("psi_sample", "OOT")

    if psi_sample_name in [None, "train"]:
        return eval_sets, eval_sets["train"][0]

    if psi_sample_name in ["valid", "test"]:
        return eval_sets, eval_sets[psi_sample_name][0]

    elif psi_sample_name == "OOT":
        oot_evaluate, oot_psi = train_test_split(
            eval_sets["OOT"][0], train_size=0.5, random_state=1
        )
        oot_target_evaluate, oot_target_psi = train_test_split(
            eval_sets["OOT"][1], train_size=0.5, random_state=1
        )
        eval_sets["OOT"] = (oot_evaluate, oot_target_evaluate)
        eval_sets["OOT_psi"] = (oot_psi, oot_target_psi)

        return eval_sets, oot_psi

    else:
        raise ValueError(f"Unknown psi-sample name! Please choose: {eval_sets.keys()}")