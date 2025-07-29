from typing import List, Optional

import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.tree import DecisionTreeClassifier
from sklearn.exceptions import NotFittedError
from sklearn.metrics import roc_auc_score

from dreamml.modeling.metrics.metrics_mapping import metrics_mapping
from dreamml.utils.errors import MissedColumnError


CATEGORY = "категориальный признак"


class GiniFeatureImportance(BaseEstimator, TransformerMixin):
    """Compute GINI score for each feature and select features based on the scores.

    This transformer calculates the GINI score for each feature in the dataset and selects
    features that meet the specified threshold or are part of the remaining_features list.

    Attributes:
        scores_ (Dict[str, float]): Dictionary containing GINI scores for each feature.
        used_features (List[str] or None): List of selected features after transformation.
    """

    def __init__(self, threshold: float, remaining_features: List[str] = [], cat_features: Optional[List[str]] = None):
        """Initialize the GiniFeatureImportance transformer.

        Args:
            threshold (float): Threshold for selecting features based on GINI scores.
                Features with GINI scores above this threshold are selected.
            remaining_features (List[str], optional): List of features to always include.
                Defaults to an empty list.
            cat_features (List[str], optional): List of categorical features.
                Defaults to None.
        """
        self.threshold = threshold
        self.remaining_features = remaining_features
        self.cat_features = cat_features
        self.used_features = None
        self.scores = {}

    @property
    def check_is_fitted(self) -> bool:
        """Check if the transformer has been fitted.

        Raises:
            NotFittedError: If the transformer has not been fitted yet.

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

    def fit(self, data: pd.DataFrame, target: pd.Series):
        """Fit the transformer by computing GINI scores for each feature.

        Args:
            data (pd.DataFrame): Feature matrix for training, shape [n_samples, n_features].
            target (pd.Series): Target vector, shape [n_samples].

        Raises:
            MissedColumnError: If any categorical features are missing in the data.

        Returns:
            self: Fitted transformer.
        """
        if self.cat_features:
            missed_columns = list(set(self.cat_features) - set(data.columns))
            if missed_columns:
                raise MissedColumnError(
                    f"Missed {list(missed_columns)} columns in data."
                )

            numeric_features = list(set(data.columns) - set(self.cat_features))
        else:
            numeric_features = data.columns

        for feature in tqdm(numeric_features, desc="Calculating GINI scores"):
            auc = roc_auc_score(target, data[feature].fillna(-9999))
            self.scores[feature] = (2 * np.abs(auc - 0.5)) * 100

        return self

    def transform(self, data: pd.DataFrame, target: Optional[pd.Series] = None) -> pd.DataFrame:
        """Select features based on the computed GINI scores and the specified threshold.

        Features with GINI scores above the threshold or in the remaining_features list are marked for selection.

        Args:
            data (pd.DataFrame): Feature matrix for transformation, shape [n_samples, n_features].
            target (Optional[pd.Series], optional): Target vector. Defaults to None.

        Raises:
            NotFittedError: If the transformer has not been fitted yet.

        Returns:
            pd.DataFrame: DataFrame containing feature names, GINI scores, and selection flags.
        """
        self.check_is_fitted
        scores = pd.Series(self.scores)
        scores = pd.DataFrame({"Variable": scores.index, "GINI": scores.values})
        scores["Selected"] = scores.apply(
            lambda row: (
                1
                if row["GINI"] > self.threshold
                or row["Variable"] in self.remaining_features
                else 0
            ),
            axis=1,
        )
        scores = scores.sort_values(by="GINI", ascending=False)

        if self.cat_features:
            cat_features_scores = pd.DataFrame(
                {"Variable": self.cat_features, "GINI": CATEGORY, "Selected": 1}
            )
            scores = scores.append(cat_features_scores, ignore_index=True)

        mask = scores["Selected"] == 1
        self.used_features = scores.loc[mask, "Variable"].tolist()

        return scores.reset_index(drop=True)


def compare_gini_features(eval_sets: dict, config: dict) -> (pd.DataFrame, List[str]):
    """Select features from the training dataset based on GINI score differences.

    Features are selected if their absolute GINI difference is below `gini_absolute_diff` and
    their relative GINI difference is below `gini_relative_diff` compared to a validation set.

    Args:
        eval_sets (dict): Dictionary containing evaluation datasets.
            Keys are dataset names (e.g., 'train', 'valid'), and values are tuples of (data, target).
        config (dict): Configuration dictionary with parameters for feature selection.

    Returns:
        pd.DataFrame: DataFrame containing feature importances, absolute and relative differences,
            and selection flags.
        List[str]: List of selected features.
    """
    transformer = GiniFeatureImportance(
        threshold=config["gini_threshold"],
        remaining_features=config["data"].columns.remaining_features,
        cat_features=config["categorical_features"],
    )
    u_features = {}
    valid_name = config.get("valid_sample", "valid")
    train = transformer.fit_transform(*eval_sets["train"])
    u_features["train"] = transformer.used_features
    valid = transformer.transform(*eval_sets[valid_name])
    u_features[valid_name] = transformer.used_features

    g_merge = train.merge(valid, on="Variable", suffixes=("_train", f"_{valid_name}"))
    g_merge, used_features = compute_difference(g_merge, config, u_features)

    g_merge["Selected"] = 0
    mask = g_merge["Variable"].isin(used_features)
    g_merge.loc[mask, "Selected"] = 1
    g_merge = g_merge.drop(["Selected_train", f"Selected_{valid_name}"], axis=1)
    g_merge.fillna("Не применяется", inplace=True)

    cols = [
        "Variable",
        "GINI_train",
        f"GINI_{valid_name}",
        "absolute_diff",
        "relative_diff",
        "Selected",
    ]
    g_merge = g_merge[cols]

    return g_merge, used_features


def compute_difference(g_merge: pd.DataFrame, config: dict, u_features: dict) -> (pd.DataFrame, List[str]):
    """Compute absolute and relative differences in GINI scores between training and validation sets.

    Args:
        g_merge (pd.DataFrame): Merged DataFrame containing GINI scores for training and validation sets.
        config (dict): Configuration dictionary with difference thresholds.
        u_features (dict): Dictionary containing lists of selected features for each dataset.

    Returns:
        pd.DataFrame: Updated DataFrame with absolute and relative differences.
        List[str]: List of features that meet the selection criteria.
    """
    absolute_diff = config.get("gini_absolute_diff", 5)
    relative_diff = config.get("gini_relative_diff", 30)
    valid_name = config.get("valid_sample", "valid")

    mask = g_merge["GINI_train"] == "категориальный признак"
    cat_merge = g_merge.loc[mask]
    num_merge = g_merge.loc[~mask]
    num_merge["GINI_train"] = num_merge["GINI_train"].replace(0, np.nan)

    num_merge["absolute_diff"] = np.abs(
        num_merge[f"GINI_{valid_name}"] - num_merge["GINI_train"]
    )
    num_merge["relative_diff"] = (
        100 * num_merge["absolute_diff"] / (num_merge["GINI_train"])
    )
    num_merge.fillna(0, inplace=True)
    num_merge.sort_values("GINI_train", ascending=False, inplace=True)

    mask = (num_merge["absolute_diff"] >= absolute_diff) | (
        num_merge["relative_diff"] >= relative_diff
    )
    bad_features = num_merge.loc[mask, "Variable"].tolist()
    used_features = [
        feature
        for feature in u_features["train"]
        if feature not in bad_features and feature in u_features[valid_name]
    ]

    g_merge = pd.concat((num_merge, cat_merge), ignore_index=True)
    return g_merge, used_features


class GiniFeatureSelectionCV(BaseEstimator, TransformerMixin):
    """Feature selection using GINI metric within cross-validation.

    This transformer performs feature selection based on GINI scores computed across cross-validation folds.
    It ensures that the selected features maintain consistent importance across different data splits.

    Attributes:
        const (float): Constant value used to replace missing data.
        used_features (List[str] or None): List of selected features after transformation.
        scores (pd.DataFrame or None): DataFrame containing GINI metrics for features.
    """

    def __init__(
        self,
        cv,
        threshold: float = 5,
        cat_features: Optional[List[str]] = None,
        abs_difference: float = 10,
        rel_difference: float = 30,
    ):
        """Initialize the GiniFeatureSelectionCV transformer.

        Args:
            cv: Cross-validation generator.
                Determines the splits to be used for cross-validation.
            threshold (float, optional): Threshold for selecting features based on GINI scores.
                Defaults to 5.
            cat_features (List[str], optional): List of categorical features.
                Defaults to None.
            abs_difference (float, optional): Maximum allowed absolute difference in GINI scores
                between training and validation folds. Defaults to 10.
            rel_difference (float, optional): Maximum allowed relative difference in GINI scores
                between training and validation folds. Defaults to 30.
        """
        self.cv = cv
        self.threshold = threshold
        self.abs_difference = abs_difference
        self.rel_difference = rel_difference
        self.cat_features = cat_features
        self.const = np.finfo(np.float32).min
        self.used_features = None
        self.scores = None

    @staticmethod
    def _to_frame(data: dict, prefix: str = "train") -> pd.DataFrame:
        """Convert a dictionary of feature importances to a DataFrame with a prefix.

        Args:
            data (dict): Dictionary of feature importances.
            prefix (str, optional): Prefix to add to the importance column name.
                Defaults to "train".

        Returns:
            pd.DataFrame: DataFrame with 'Variable' and '{prefix}importance' columns.
        """
        if prefix:
            prefix = f"{prefix}-"

        importance = pd.Series(data)
        importance = importance.to_frame().reset_index()
        importance.columns = ["Variable", f"{prefix}importance"]

        return importance

    def _calculate_fold_metric(self, data: pd.DataFrame, target: pd.Series) -> pd.DataFrame:
        """Calculate average GINI metrics across all cross-validation folds.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector.

        Returns:
            pd.DataFrame: DataFrame containing average GINI metrics and differences.
        """
        importance = pd.DataFrame()
        for train_idx, valid_idx in tqdm(self.cv.split(data), desc="Calculating fold metrics"):
            x_train, x_valid = data.iloc[train_idx], data.iloc[valid_idx]
            y_train, y_valid = target.iloc[train_idx], target.iloc[valid_idx]

            fold_train_importance = self._calculate_metric(data=x_train, target=y_train)
            fold_valid_importance = self._calculate_metric(data=x_valid, target=y_valid)
            fold_train_importance = self._to_frame(
                fold_train_importance, prefix="train"
            )
            fold_valid_importance = self._to_frame(
                fold_valid_importance, prefix="valid"
            )

            fold_importance = pd.concat(
                [fold_train_importance, fold_valid_importance], axis=1
            )
            importance = pd.concat([importance, fold_importance], ignore_index=True)

        importance = importance.groupby("Variable").mean().reset_index().sort_values(
            by="valid-importance", ascending=False
        )
        importance["abs_delta"] = (
            importance["train-importance"] - importance["valid-importance"]
        ).abs()
        importance["rel_delta"] = (
            100 * importance["abs_delta"] / importance["train-importance"]
        )
        importance = importance.fillna(0)

        return importance

    def _calculate_metric(self, data: pd.DataFrame, target: pd.Series) -> dict:
        """Calculate GINI scores for each feature.

        Args:
            data (pd.DataFrame): Feature matrix.
            target (pd.Series): Target vector.

        Returns:
            dict: Dictionary mapping feature names to their GINI scores.
        """
        scores = {}
        for feature in data.columns:
            score = metrics_mapping["gini"]()(
                y_true=target,
                y_pred=data[feature].fillna(self.const),
            )
            scores[feature] = 100 * np.abs(score)

        return scores

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """Fit the transformer by computing GINI metrics across cross-validation folds.

        Args:
            X (pd.DataFrame): Feature matrix, shape [n_samples, n_features].
            y (pd.Series): Target vector, shape [n_samples].

        Raises:
            MissedColumnError: If any categorical features are missing in the data.

        Returns:
            self: Fitted transformer.
        """
        if self.cat_features:
            missed_columns = list(set(self.cat_features) - set(X.columns))
            if missed_columns:
                raise MissedColumnError(
                    f"Missed {list(missed_columns)} columns in data."
                )
            numeric_features = list(set(X.columns) - set(self.cat_features))
        else:
            numeric_features = X.columns

        self.scores = self._calculate_fold_metric(data=X[numeric_features], target=y)
        return self

    def transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> (pd.DataFrame, List[str]):
        """Select features based on GINI scores and differences from cross-validation.

        Args:
            X (pd.DataFrame): Feature matrix to transform, shape [n_samples, n_features].
            y (Optional[pd.Series], optional): Target vector. Defaults to None.

        Raises:
            NotFittedError: If the transformer has not been fitted yet.

        Returns:
            pd.DataFrame: DataFrame containing GINI metrics and selection flags.
            List[str]: List of selected features.
        """
        scores = self.scores.copy()
        scores["Selected"] = 0
        mask = (scores[["train-importance", "valid-importance"]] >= self.threshold).max(
            axis=1
        )
        additive_mask = (scores["abs_delta"] <= self.abs_difference) & (
            scores["rel_delta"] <= self.rel_difference
        )
        mask = mask & additive_mask
        scores.loc[mask, "Selected"] = 1
        scores = scores.fillna(0)

        if self.cat_features:
            cat_scores = pd.DataFrame(
                {
                    "Variable": self.cat_features,
                    "train-importance": CATEGORY,
                    "valid-importance": CATEGORY,
                    "abs_delta": CATEGORY,
                    "rel_delta": CATEGORY,
                    "Selected": 1,
                }
            )
            scores = scores.append(cat_scores, ignore_index=True)

        mask = scores["Selected"] == 1
        self.used_features = scores.loc[mask, "Variable"].tolist()

        return scores, self.used_features


class DecisionTreeFeatureSelectionCV(BaseEstimator, TransformerMixin):
    """Feature selection using Decision Tree importance within cross-validation.

    This transformer selects features based on their importance as determined by a Decision Tree classifier
    across cross-validation folds. It ensures that selected features maintain consistent importance across splits.

    Attributes:
        const (float): Constant value used to replace missing data.
        used_features (List[str] or None): List of selected features after transformation.
        scores (pd.DataFrame or None): DataFrame containing decision tree importance metrics for features.
    """

    def __init__(
        self,
        cv,
        group_column: str,
        threshold: float = 5,
        cat_features: Optional[List[str]] = None,
        abs_difference: float = 10,
        rel_difference: float = 30,
    ):
        """Initialize the DecisionTreeFeatureSelectionCV transformer.

        Args:
            cv: Cross-validation generator.
                Determines the splits to be used for cross-validation.
            group_column (str): Column name used for grouping data during cross-validation.
            threshold (float, optional): Threshold for selecting features based on importance scores.
                Defaults to 5.
            cat_features (List[str], optional): List of categorical features.
                Defaults to None.
            abs_difference (float, optional): Maximum allowed absolute difference in importance scores
                between training and validation folds. Defaults to 10.
            rel_difference (float, optional): Maximum allowed relative difference in importance scores
                between training and validation folds. Defaults to 30.
        """
        self.cv = cv
        self.group_column = group_column
        self.threshold = threshold
        self.cat_features = cat_features
        self.const = np.finfo(np.float32).min
        self.abs_difference = abs_difference
        self.rel_difference = rel_difference
        self.used_features = None
        self.scores = None

    @staticmethod
    def _to_frame(data: dict, prefix: str = "train") -> pd.DataFrame:
        """Convert a dictionary of feature importances to a DataFrame with a prefix.

        Args:
            data (dict): Dictionary of feature importances.
            prefix (str, optional): Prefix to add to the importance column name.
                Defaults to "train".

        Returns:
            pd.DataFrame: DataFrame with 'Variable' and '{prefix}importance' columns.
        """
        if prefix:
            prefix = f"{prefix}-"

        importance = pd.Series(data)
        importance = importance.to_frame().reset_index()
        importance.columns = ["Variable", f"{prefix}importance"]

        return importance

    def _calculate_metric(self, data: pd.DataFrame, target: pd.Series) -> dict:
        """Calculate Decision Tree-based importance scores for each feature.

        Args:
            data (pd.DataFrame): Feature matrix.
            target (pd.Series): Target vector.

        Returns:
            dict: Dictionary mapping feature names to their importance scores.
        """
        scores = {}
        for feature in data.columns:
            feature_ = data[feature].fillna(self.const).values.reshape(-1, 1)
            tree = DecisionTreeClassifier(max_depth=3, random_state=27)
            tree.fit(feature_, target)

            prediction = tree.predict_proba(feature_)[:, 1]

            score = metrics_mapping["gini"]()(y_true=target, y_pred=prediction)
            scores[feature] = 100 * np.abs(score)

        return scores

    def fold_calculate(self, data: pd.DataFrame, importance: pd.DataFrame, target: pd.Series, train_idx: np.ndarray, valid_idx: np.ndarray) -> pd.DataFrame:
        """Calculate feature importances for a single fold and update the importance DataFrame.

        Args:
            data (pd.DataFrame): Feature matrix.
            importance (pd.DataFrame): DataFrame to store importance scores.
            target (pd.Series): Target vector.
            train_idx (np.ndarray): Indices for the training split.
            valid_idx (np.ndarray): Indices for the validation split.

        Returns:
            pd.DataFrame: Updated importance DataFrame with scores from the current fold.
        """
        x_train, x_valid = data.iloc[train_idx], data.iloc[valid_idx]
        y_train, y_valid = target.iloc[train_idx], target.iloc[valid_idx]
        fold_train_importance = self._calculate_metric(data=x_train, target=y_train)
        fold_valid_importance = self._calculate_metric(data=x_valid, target=y_valid)
        fold_train_importance = self._to_frame(
            fold_train_importance, prefix="train"
        )
        fold_valid_importance = self._to_frame(
            fold_valid_importance, prefix="valid"
        )
        fold_importance = pd.concat(
            [fold_train_importance, fold_valid_importance], axis=1
        )
        importance = pd.concat([importance, fold_importance], ignore_index=True)
        return importance

    def _calculate_fold_metric(self, data: pd.DataFrame, target: pd.Series) -> pd.DataFrame:
        """Calculate average Decision Tree importance metrics across all cross-validation folds.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector.

        Returns:
            pd.DataFrame: DataFrame containing average importance metrics and differences.
        """
        importance = pd.DataFrame()
        if self.group_column:
            for train_idx, valid_idx in tqdm(self.cv.split(data, groups=data[self.group_column]), desc="Calculating fold metrics"):
                importance = self.fold_calculate(
                    data, importance, target, train_idx, valid_idx
                )
        else:
            for train_idx, valid_idx in tqdm(self.cv.split(data), desc="Calculating fold metrics"):
                importance = self.fold_calculate(
                    data, importance, target, train_idx, valid_idx
                )

        importance = importance.groupby("Variable").mean().reset_index().sort_values(
            by="valid-importance", ascending=False
        )
        importance["abs_delta"] = (
            importance["train-importance"] - importance["valid-importance"]
        ).abs()
        importance["rel_delta"] = (
            100 * importance["abs_delta"] / importance["train-importance"]
        )
        importance = importance.fillna(0)

        return importance

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """Fit the transformer by computing Decision Tree importance metrics across cross-validation folds.

        Args:
            X (pd.DataFrame): Feature matrix, shape [n_samples, n_features].
            y (pd.Series): Target vector, shape [n_samples].

        Raises:
            MissedColumnError: If any categorical features are missing in the data.

        Returns:
            self: Fitted transformer.
        """
        if self.cat_features:
            missed_columns = list(set(self.cat_features) - set(X.columns))
            if missed_columns:
                raise MissedColumnError(
                    f"Missed {list(missed_columns)} columns in data."
                )
            numeric_features = list(set(X.columns) - set(self.cat_features))
        else:
            numeric_features = X.columns

        self.scores = self._calculate_fold_metric(data=X[numeric_features], target=y)
        return self

    def transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> (pd.DataFrame, List[str]):
        """Select features based on Decision Tree importance scores and their consistency across folds.

        Args:
            X (pd.DataFrame): Feature matrix to transform, shape [n_samples, n_features].
            y (Optional[pd.Series], optional): Target vector. Defaults to None.

        Raises:
            NotFittedError: If the transformer has not been fitted yet.

        Returns:
            pd.DataFrame: DataFrame containing importance metrics and selection flags.
            List[str]: List of selected features.
        """
        scores = self.scores.copy()
        scores["Selected"] = 0
        mask = (scores[["train-importance", "valid-importance"]] >= self.threshold).max(
            axis=1
        )
        additive_mask = (scores["abs_delta"] <= self.abs_difference) & (
            scores["rel_delta"] <= self.rel_difference
        )
        mask = mask & additive_mask
        scores.loc[mask, "Selected"] = 1
        scores = scores.fillna(0)

        if self.cat_features:
            cat_scores = pd.DataFrame(
                {
                    "Variable": self.cat_features,
                    "train-importance": CATEGORY,
                    "valid-importance": CATEGORY,
                    "abs_delta": CATEGORY,
                    "rel_delta": CATEGORY,
                    "Selected": 1,
                }
            )
            scores = scores.append(cat_scores, ignore_index=True)

        mask = scores["Selected"] == 1
        self.used_features = scores.loc[mask, "Variable"].tolist()

        return scores, self.used_features