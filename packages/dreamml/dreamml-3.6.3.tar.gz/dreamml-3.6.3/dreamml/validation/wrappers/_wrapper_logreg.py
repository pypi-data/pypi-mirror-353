from typing import Optional, List

import json

import shap
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LogisticRegression


class _LogRegWrapper(BaseEstimator, TransformerMixin):
    """A universal estimator wrapper for Logistic Regression.

    This wrapper is used for computing validation tests and preparing reports.

    Args:
        estimator (callable): An estimator object after applying the `fit` method.
        used_features (Optional[List[str]], optional): List of features to be used. Defaults to None.
        categorical_features (Optional[List[str]], optional): List of categorical features to be used. Defaults to None.
        task (str, optional): The task type, e.g., "binary". Defaults to "binary".
        metric_name (str, optional): The name of the evaluation metric, e.g., "gini". Defaults to "gini".
    """

    def __init__(
        self,
        estimator: callable,
        used_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        task: str = "binary",
        metric_name: str = "gini",
    ):
        self.estimator = estimator
        self.used_features = used_features
        self.categorical_features = categorical_features
        self.task = task
        self.metric_name = metric_name

    def _validate_input_data(self, X):
        """Prepare data for model input by selecting the required features.

        Args:
            X (pd.DataFrame): Feature matrix to be applied to the model.

        Returns:
            pd.DataFrame: Transformed feature matrix ready for model input.
        """
        if self.used_features:
            X_ = X[self.used_features]
        else:
            X_ = X.copy()

        return X_

    @property
    def get_estimator_params(self):
        """Retrieve the hyperparameters of the model.

        Returns:
            dict: Dictionary of the model's hyperparameters.
        """
        params = self.estimator.get_params()
        params["eval_metric"] = self.metric_name.upper()
        return params

    def transform(self, X):
        """Apply the model to the input data X.

        Args:
            X (pd.DataFrame): Feature matrix to be applied to the model.

        Returns:
            np.ndarray: Model predictions on the input sample X.
        """
        data = self._validate_input_data(X)
        data = self._fill_nan_values(data)
        if hasattr(self.estimator, "transform"):
            return self.estimator.transform(data)
        elif hasattr(self.estimator, "predict_proba"):
            predicts = self.estimator.predict_proba(data)
            return (
                predicts
                if self.task in ("multiclass", "multilabel")
                else predicts[:, 1]
            )
        else:
            return self.estimator.predict(data)

    def _fill_nan_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fill NaN values in the dataset using a specified strategy.

        This method is used for logistic regression and linear regression
        models, as these models do not have automatic NaN preprocessing
        unlike models such as CatBoost, XGBoost, and LightGBM.

        Args:
            data (pd.DataFrame): The input data with potential NaN values.

        Returns:
            pd.DataFrame: The data with NaN values filled.

        Raises:
            ValueError: If an unsupported fillna_strategy is provided.
        """
        self.fillna_strategy = "mean"
        used_features = self.used_features if self.used_features else data.columns
        for feature in used_features:
            if isinstance(self.fillna_strategy, (int, float)):
                fill_value = self.fillna_strategy
            elif self.fillna_strategy == "mean":
                fill_value = float(data[feature].fillna(value=0).mean())
            elif self.fillna_strategy == "median":
                fill_value = float(data[feature].fillna(value=0).median())
            else:
                fill_value = 0
            data[feature] = data[feature].fillna(value=fill_value)
        return data