from typing import Optional, List

import shap
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class _CatBoostWrapper(BaseEstimator, TransformerMixin):
    """A universal estimator wrapper for CatBoost models.

    This wrapper is used for performing validation tests and preparing reports
    based on the CatBoost estimator.

    Attributes:
        estimator (callable): The estimator object after fitting.
        used_features (Optional[List[str]]): List of feature names to be used.
        categorical_features (Optional[List[str]]): List of categorical feature names.
        task (str): The type of task, e.g., "binary".
        metric_name (str): The name of the evaluation metric, e.g., "gini".
    """

    def __init__(
        self,
        estimator: callable,
        used_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        task: str = "binary",
        metric_name: str = "gini",
    ):
        """Initializes the _CatBoostWrapper with the given parameters.

        Args:
            estimator (callable): The estimator object to be wrapped.
            used_features (Optional[List[str]], optional): List of features to use. Defaults to None.
            categorical_features (Optional[List[str]], optional): List of categorical features. Defaults to None.
            task (str, optional): The type of task, e.g., "binary". Defaults to "binary".
            metric_name (str, optional): The name of the evaluation metric. Defaults to "gini".
        """
        self.estimator = estimator
        self.used_features = used_features
        self.categorical_features = categorical_features
        self.task = task
        self.metric_name = metric_name

    def _validate_input_data(self, X):
        """Prepares the input data for the model by selecting the required features.

        This method selects the specified features from the input DataFrame. If 
        no specific features are provided, it returns a copy of the original DataFrame.

        Args:
            X (pd.DataFrame): The feature matrix to be used by the model.

        Returns:
            pd.DataFrame: The transformed feature matrix containing only the used features.
        """
        if self.used_features:
            X_ = X[self.used_features]
        else:
            X_ = X.copy()

        return X_

    @property
    def get_estimator_params(self):
        """Retrieves the hyperparameters of the estimator.

        This property fetches all the hyperparameters of the wrapped estimator and 
        updates the evaluation metric to the specified metric name.

        Returns:
            dict: A dictionary of the estimator's hyperparameters, including the updated evaluation metric.
        """
        params = self.estimator.get_all_params()
        params["eval_metric"] = self.metric_name.upper()
        return params

    def get_shap_importance(self, X: pd.DataFrame) -> pd.DataFrame:
        """Calculates feature importance using SHAP values.

        This method computes the SHAP values for the given feature matrix and 
        returns both the SHAP values and a DataFrame containing feature importances.

        Args:
            X (pd.DataFrame): The feature matrix for which to calculate SHAP values.

        Returns:
            tuple:
                - np.ndarray: The SHAP values with shape [n_samples, n_features].
                - pd.DataFrame: A DataFrame with feature names and their corresponding importance scores.
        """
        x = self._validate_input_data(X)
        explainer = shap.TreeExplainer(self.estimator)
        shap_values = explainer.shap_values(x)

        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        shap_importance = pd.DataFrame(
            {
                "feature": list(x.columns),
                "importance": np.round(np.abs(shap_values).mean(axis=0), 5),
            }
        )
        shap_importance = shap_importance.sort_values(by="importance", ascending=False)
        shap_importance = shap_importance.reset_index(drop=True)

        return shap_values, shap_importance

    def transform(self, X):
        """Applies the estimator to the input data to generate predictions.

        Depending on the estimator's capabilities, this method either transforms the data, 
        predicts probabilities, or generates class predictions.

        Args:
            X (pd.DataFrame): The feature matrix to apply the model to.

        Returns:
            np.ndarray: The model's predictions. Returns prediction probabilities for 
                        multi-class or multi-label tasks, and class probabilities or classes otherwise.
        """
        data = self._validate_input_data(X)
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