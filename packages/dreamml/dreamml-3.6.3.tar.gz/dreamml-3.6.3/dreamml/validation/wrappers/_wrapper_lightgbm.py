from typing import Optional, List

import shap
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class _LightGBMWrapper(BaseEstimator, TransformerMixin):
    """A universal estimator wrapper for LightGBM models.

    This wrapper is used for computing validation tests and preparing reports.

    Args:
        estimator (callable): An estimator object after applying the `fit` method.
        used_features (Optional[List[str]], optional): List of feature names to be used. Defaults to None.
        categorical_features (Optional[List[str]], optional): List of categorical feature names. Defaults to None.
        task (str, optional): The type of task, such as "binary". Defaults to "binary".
        metric_name (str, optional): The name of the evaluation metric. Defaults to "gini".

    Attributes:
        estimator (callable): The estimator used for modeling.
        used_features (Optional[List[str]]): The list of features utilized by the model.
        categorical_features (Optional[List[str]]): The list of categorical features.
        task (str): The type of task for the estimator.
        metric_name (str): The evaluation metric name.
    """

    def __init__(
        self,
        estimator: callable,
        used_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        task: str = "binary",
        metric_name: str = "gini",
    ):
        """
        Initializes the _LightGBMWrapper with the given parameters.

        Args:
            estimator (callable): An estimator object after applying the `fit` method.
            used_features (Optional[List[str]], optional): List of feature names to be used. Defaults to None.
            categorical_features (Optional[List[str]], optional): List of categorical feature names. Defaults to None.
            task (str, optional): The type of task, such as "binary". Defaults to "binary".
            metric_name (str, optional): The name of the evaluation metric. Defaults to "gini".
        """
        self.estimator = estimator
        self.used_features = used_features
        self.categorical_features = categorical_features
        self.task = task
        self.metric_name = metric_name

    def _validate_input_data(self, X: pd.DataFrame) -> pd.DataFrame:
        """Prepares the input data for model application by selecting the required features.

        Args:
            X (pd.DataFrame): The feature matrix to be used for model application.

        Returns:
            pd.DataFrame: The transformed feature matrix ready for model input.

        Raises:
            KeyError: If any of the used_features are not present in X.
        """
        if self.used_features:
            X_ = X[self.used_features]
        else:
            X_ = X.copy()

        return X_

    @property
    def get_estimator_params(self) -> dict:
        """Retrieves the hyperparameters of the estimator.

        Returns:
            dict: A dictionary containing the estimator's hyperparameters.

        Raises:
            AttributeError: If the estimator does not have the expected attributes.
        """
        try:
            params = self.estimator.get_params()
            params["n_estimators"] = self.estimator.n_estimators
        except AttributeError:
            params = self.estimator.params
            params["n_estimators"] = self.estimator.current_iteration()

        return params

    def get_shap_importance(self, X: pd.DataFrame) -> (np.ndarray, pd.DataFrame):
        """Calculates feature importance based on SHAP values.

        Args:
            X (pd.DataFrame): The feature matrix for which to compute feature importance.

        Returns:
            tuple:
                - np.ndarray: The SHAP values matrix with shape [n_samples, n_features].
                - pd.DataFrame: A DataFrame containing feature names and their corresponding importance scores.

        Raises:
            ValueError: If SHAP values cannot be computed for the given estimator.
        """
        if hasattr(self.estimator, "booster_"):
            self.estimator.booster_.params["objective"] = self.estimator.objective

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

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Applies the estimator to the input data to generate predictions.

        Args:
            X (pd.DataFrame): The feature matrix to be used for making predictions.

        Returns:
            np.ndarray: The model's predictions for the input data.

        Raises:
            AttributeError: If the estimator does not have the required prediction methods.
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