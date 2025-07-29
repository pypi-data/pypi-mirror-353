import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CorrelationFeatureSelection(BaseEstimator, TransformerMixin):
    """
    Feature selection based on correlation.

    Removes highly correlated features, retaining one feature with the highest correlation
    to the target variable among the correlated features.

    Args:
        threshold (float, optional): Threshold for feature selection. Defaults to 0.9.
        used_features (list, optional): List of features to be used. Defaults to None.
        remaining_features (list, optional): Features that must remain in the dataset after selection. Defaults to [].

    Attributes:
        threshold (float): Threshold for feature selection.
        used_features (list): List of features to be used.
        remaining_features (list): Features that must remain in the dataset after selection.
    """

    def __init__(
        self,
        threshold: float = 0.9,
        used_features: list = None,
        remaining_features: list = [],
    ):
        self.threshold = threshold
        self.used_features = used_features
        self.remaining_features = remaining_features

    def _calculate_correlations(self, X: pd.DataFrame, y: pd.Series) -> list:
        """
        Calculates correlations between features and selects the features to be used.

        Args:
            X (pd.DataFrame): Feature matrix.
            y (pd.Series): Target variable vector.

        Returns:
            list: List of selected features.
        """
        corr_matrix = X.corr().abs()
        upper_tri = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )

        # pd.Series: index - tuple of feature pairs, value - correlation coefficient.
        corr_series = upper_tri.unstack().dropna().sort_values()
        corr_series = corr_series[corr_series > self.threshold]

        # Correlation with the target variable.
        corr_with_target = self._calculate_correlation_with_target(X, y)

        # Select the feature with the highest correlation with the target variable
        # and exclude the others.
        cols_to_drop = set()
        for col_1, col_2 in corr_series.index:
            if corr_with_target[col_1] < corr_with_target[col_2]:
                if col_1 not in self.remaining_features:
                    cols_to_drop.add(col_1)
            else:
                if col_2 not in self.remaining_features:
                    cols_to_drop.add(col_2)

        used_features = set(self.used_features) - cols_to_drop

        return list(used_features)

    @staticmethod
    def _calculate_correlation_with_target(X: pd.DataFrame, y: pd.Series) -> pd.Series:
        """
        Calculates the correlation of each feature with the target variable.

        Args:
            X (pd.DataFrame): Feature matrix.
            y (pd.Series): Target variable vector.

        Returns:
            pd.Series: Series containing the correlation of each feature with the target variable.
        """
        result = X.corrwith(y).abs()

        return result

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """
        Fits the feature selector to the data.

        Args:
            X (pd.DataFrame): Feature matrix.
            y (pd.Series): Target variable vector.

        Returns:
            self: Fitted instance of CorrelationFeatureSelection.
        """
        self.used_features = self.used_features if self.used_features else X.columns
        self.used_features = self._calculate_correlations(X, y)

        return self

    def transform(self, X: pd.DataFrame):
        """
        Transforms the dataset by selecting the chosen features.

        Args:
            X (pd.DataFrame): Feature matrix.

        Returns:
            list: List of selected features.
        """
        return self.used_features