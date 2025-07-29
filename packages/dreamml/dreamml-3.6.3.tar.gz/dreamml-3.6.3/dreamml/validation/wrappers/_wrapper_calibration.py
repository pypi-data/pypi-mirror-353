from typing import Optional, List

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from dreamml.validation.wrappers._wrapper_catboost import _CatBoostWrapper
from dreamml.validation.wrappers._wrapper_lightgbm import _LightGBMWrapper
from dreamml.validation.wrappers._wrapper_xgboost import _XGBoostWrapper
from dreamml.validation.wrappers._wrapper_automl import _WBAutoMLWrapper

models_wrappers = dict(
    lightgbm=_LightGBMWrapper,
    xgboost=_XGBoostWrapper,
    catboost=_CatBoostWrapper,
    autowoe=_WBAutoMLWrapper,
)


class _CalibrationWrapper(BaseEstimator, TransformerMixin):
    """A universal estimator object for a calibrated model.

    This wrapper is used to compute validation tests and prepare reports for
    a calibrated model.

    Args:
        estimator (callable): An estimator object after the `fit` method has been applied.
        used_features (Optional[List[str]], optional): A list of features used by the model. Defaults to None.
        categorical_features (Optional[List[str]], optional): A list of categorical features used by the model. Defaults to None.
        task (str, optional): The type of task, e.g., "binary". Defaults to "binary".
        metric_name (str, optional): The name of the metric, e.g., "gini". Defaults to "gini".
    
    Attributes:
        estimator (callable): The provided estimator object.
        used_features (Optional[List[str]]): The list of used features.
        categorical_features (Optional[List[str]]): The list of categorical features.
        task (str): The task type.
        model: The underlying model extracted from the estimator.
        model_wrapper_class: The wrapper class corresponding to the model.
        model_wrapper: An instance of the model wrapper.
        metric_name (str): The name of the metric used.
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
        self.model = estimator.model.estimator
        self.model_wrapper_class = [
            v for k, v in models_wrappers.items() if k in self.model.__module__
        ][-1]
        self.model_wrapper = self.model_wrapper_class(
            self.model, used_features, categorical_features
        )
        self.metric_name = metric_name

    def _validate_input_data(self, X):
        """Prepare input data for the model by selecting the required features.

        This method filters the input DataFrame to include only the features
        required by the model.

        Args:
            X (pd.DataFrame): The feature matrix to be used by the model.

        Returns:
            pd.DataFrame: The transformed feature matrix ready for prediction.

        Raises:
            ValueError: If the input data is not a pandas DataFrame.
        """
        X_ = self.model_wrapper._validate_input_data(X)
        return X_

    @property
    def get_estimator_params(self):
        """Retrieve the model's hyperparameters.

        This property accesses the hyperparameters of the underlying model
        using the model wrapper.

        Returns:
            dict: A dictionary of the model's hyperparameters.

        Raises:
            AttributeError: If the model wrapper does not have a `get_estimator_params` attribute.
        """
        params = self.model_wrapper.get_estimator_params
        return params

    def get_shap_importance(self, X: pd.DataFrame) -> pd.DataFrame:
        """Compute feature importance based on SHAP values.

        This method calculates the SHAP values for the given feature matrix
        and returns both the SHAP values and their corresponding feature importance.

        Args:
            X (pd.DataFrame): The feature matrix for which to calculate SHAP values.

        Returns:
            tuple:
                - np.array: The SHAP values with shape [n_samples, n_features].
                - pd.DataFrame: The feature importance based on SHAP values with shape [n_features, 2].

        Raises:
            ValueError: If the input data is not suitable for SHAP computation.
            RuntimeError: If SHAP values cannot be computed due to model limitations.
        """
        shap_values, shap_importance = self.model_wrapper.get_shap_importance(X)
        return shap_values, shap_importance

    def transform(self, X):
        """Apply the model to the input data to generate predictions.

        This method validates and transforms the input data, then uses the
        estimator to generate predictions.

        Args:
            X (pd.DataFrame): The feature matrix to apply the model on.

        Returns:
            np.array: The model's predictions for the input data.

        Raises:
            ValueError: If the input data is invalid or the transformation fails.
            AttributeError: If the estimator does not have a `transform` method.
        """
        data = self._validate_input_data(X)
        if isinstance(data, tuple):
            data = data[0]
        if hasattr(self.estimator, "transform"):
            return self.estimator.transform(data)
        else:
            raise AttributeError("The estimator does not have a 'transform' method.")