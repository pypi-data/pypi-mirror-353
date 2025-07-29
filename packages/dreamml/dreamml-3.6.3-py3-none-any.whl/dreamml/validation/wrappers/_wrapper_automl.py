from typing import Optional, List

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from lightautoml.dataset.np_pd_dataset import NumpyDataset


class _WBAutoMLWrapper(BaseEstimator, TransformerMixin):
    """A universal estimator wrapper for WhiteBox AutoML.

    This wrapper is used for computing validation tests and preparing reports.

    Args:
        estimator (callable): An estimator object after applying the `fit` method.
        used_features (Optional[List[str]], optional): List of features to be used by the model. Defaults to None.
        categorical_features (Optional[List[str]], optional): List of categorical features used by the model. Defaults to None.
        task (str, optional): The type of machine learning task. Defaults to "binary".
        metric_name (str, optional): The name of the evaluation metric. Defaults to "gini".
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

    @property
    def get_estimator_params(self):
        """Retrieve the parameters of the underlying estimator.

        Returns:
            dict: A dictionary of estimator parameters.
        """
        params_dict = self.estimator.__dict__
        estimator_params = params_dict["_params"]

        return estimator_params

    def _validate_input_data(self, X):
        """Prepare input data for the model by selecting required features.

        This method selects the specified features from the input DataFrame.
        If no features are specified, it returns a copy of the input.

        Args:
            X (pd.DataFrame): Feature matrix to be passed to the model.

        Returns:
            pd.DataFrame: Transformed feature matrix ready for model input.

        Raises:
            KeyError: If any of the `used_features` are not present in `X`.
        """
        if self.used_features:
            X_ = X[self.used_features]
        else:
            X_ = X.copy()

        return X_

    def get_shap_importance(self, X: pd.DataFrame) -> pd.DataFrame:
        """Calculate feature importance based on SHAP values.

        This method computes the importance of each feature using SHAP values.
        Note that `shap_values` are not utilized as the SHAP method is not adapted
        for WhiteBox AutoML.

        Args:
            X (pd.DataFrame): Feature matrix for calculating feature importance.

        Returns:
            Tuple[List, pd.DataFrame]:
                - shap_values (List): An empty list, not used.
                - shap_importance (pd.DataFrame): DataFrame containing feature importances.

        Raises:
            AttributeError: If the estimator does not have `features_fit` attribute.
        """
        shap_values = []

        shap_importance = pd.DataFrame(
            {
                "feature": self.estimator.features_fit.index,
                "importance": self.estimator.features_fit.values,
            }
        )
        shap_importance = shap_importance.sort_values(by="importance", ascending=False)
        shap_importance = shap_importance.reset_index(drop=True)
        return shap_values, shap_importance

    def transform(self, X):
        """Apply the model to the input data X.

        This method transforms the input data using the underlying estimator.
        It handles different estimator methods such as `transform`, `predict_proba`, and `predict`.

        Args:
            X (pd.DataFrame): Feature matrix to be transformed by the model.

        Returns:
            np.ndarray: Model predictions for the input data.

        Raises:
            AttributeError: If the estimator does not have any of the methods `transform`, `predict_proba`, or `predict`.
        """
        if hasattr(self.estimator, "transform"):
            prediction = self.estimator.transform(X)
        elif hasattr(self.estimator, "predict_proba"):
            try:
                prediction = self.estimator.predict_proba(X)
            except AssertionError:
                prediction = self.estimator.predict(X)
        else:
            prediction = self.estimator.predict(X)

        prediction = prediction.data if isinstance(prediction, NumpyDataset) else prediction

        if self.task in ["binary", "regression"]:
            return prediction[:, 0]
        elif self.task == "multiclass":
            return prediction
        else:
            raise ValueError(f"Задача {self.task} не поддерживается.")