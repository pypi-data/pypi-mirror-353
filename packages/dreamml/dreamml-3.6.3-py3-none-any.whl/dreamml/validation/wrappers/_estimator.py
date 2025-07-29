from typing import Optional, List

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from dreamml.validation.wrappers._wrapper_catboost import _CatBoostWrapper
from dreamml.validation.wrappers._wrapper_lightgbm import _LightGBMWrapper
from dreamml.validation.wrappers._wrapper_xgboost import _XGBoostWrapper
from dreamml.validation.wrappers._wrapper_automl import _WBAutoMLWrapper
from dreamml.validation.wrappers._wrapper_calibration import _CalibrationWrapper
from dreamml.validation.wrappers._wrapper_pyboost import _PyBoostWrapper
from dreamml.validation.wrappers._wrapper_logreg import _LogRegWrapper


# FIXME: выглядит как лишний уровень абстракции, уже имеются классы estimator для каждой модели
class Estimator(BaseEstimator, TransformerMixin):
    """
    A universal estimator object for performing validation tests and preparing reports.

    This class wraps various estimator models to provide a unified interface for
    computing validation metrics and generating reports. It initializes the appropriate
    wrapper based on the type of the provided estimator.

    Attributes:
        estimator (callable): The estimator object after applying the `fit` method.
        vectorizer (callable, optional): A vectorizer to transform input features.
        used_features (List[str], optional): List of features used by the estimator.
        categorical_features (List[str], optional): List of categorical features used by the estimator.
        task (str): The type of task, e.g., "binary".
        metric_name (str): The name of the metric to evaluate, e.g., "gini".
        log_target_transformer: Transformer for the target variable.
        wrapper: The specific wrapper corresponding to the estimator type.
    """

    def __init__(
        self,
        estimator: callable,
        vectorizer: callable = None,
        log_target_transformer=None,
        used_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        task: str = "binary",
        metric_name: str = "gini",
    ):
        """
        Initializes the Estimator with the given parameters.

        Args:
            estimator (callable): The estimator object to be wrapped.
            vectorizer (callable, optional): A vectorizer for transforming input features. Defaults to None.
            log_target_transformer: Transformer for the target variable.
            used_features (List[str], optional): List of feature names used by the estimator. Defaults to None.
            categorical_features (List[str], optional): List of categorical feature names. Defaults to None.
            task (str, optional): The type of task, such as "binary". Defaults to "binary".
            metric_name (str, optional): The evaluation metric name, such as "gini". Defaults to "gini".
        """
        self.estimator = estimator
        self.vectorizer = vectorizer
        self.used_features = used_features
        self.categorical_features = categorical_features
        self.task = task
        self.metric_name = metric_name
        self.log_target_transformer = log_target_transformer
        self.wrapper = self._init_wrapper()

    def _init_wrapper(self):
        """
        Initializes the specific wrapper based on the estimator's module.

        Determines the appropriate wrapper class to use for the estimator by
        inspecting the estimator's module name.

        Returns:
            An instance of a wrapper class corresponding to the estimator type.
        """
        if "lightgbm" in self.estimator.__module__:
            return _LightGBMWrapper(
                self.estimator,
                self.used_features,
                self.categorical_features,
                self.task,
                self.metric_name,
            )
        elif "xgboost" in self.estimator.__module__:
            return _XGBoostWrapper(
                self.estimator,
                self.used_features,
                self.categorical_features,
                self.task,
                self.metric_name,
            )
        elif "catboost" in self.estimator.__module__:
            return _CatBoostWrapper(
                self.estimator,
                self.used_features,
                self.categorical_features,
                self.task,
                self.metric_name,
            )
        elif "calibration" in self.estimator.__module__:
            return _CalibrationWrapper(
                self.estimator,
                self.used_features,
                self.categorical_features,
                self.task,
                self.metric_name,
            )
        elif "py_boost" in self.estimator.__module__:
            return _PyBoostWrapper(
                self.estimator,
                self.used_features,
                self.categorical_features,
                self.task,
            )
        elif (
            "logistic" in self.estimator.__module__
            or "pipeline" in self.estimator.__module__
        ):
            return _LogRegWrapper(
                self.estimator,
                self.used_features,
                self.categorical_features,
                self.task,
                self.metric_name,
            )
        else:
            return _WBAutoMLWrapper(
                self.estimator,
                self.used_features,
                self.categorical_features,
                self.task,
                self.metric_name,
            )

    def get_shap_importance(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Computes feature importance based on SHAP values.

        This method uses the underlying wrapper to calculate SHAP values and
        returns a DataFrame containing feature importances.

        Args:
            X (pd.DataFrame): The feature matrix for which to compute SHAP importance.

        Returns:
            pd.DataFrame: A DataFrame with SHAP importances, indexed by feature names.

        Raises:
            ValueError: If the input DataFrame is invalid or SHAP computation fails.
        """
        return self.wrapper.get_shap_importance(X)

    def transform(self, X):
        """
        Applies the model to the input data X and returns predictions.

        This method transforms the input features using the vectorizer (if provided),
        generates raw predictions using the wrapper, and applies inverse transformation
        to the predictions if a log target transformer is set and fitted.

        Args:
            X (pd.DataFrame): The feature matrix to apply the model on.

        Returns:
            np.array: The model's predictions. If a log target transformer is used and fitted,
                      the predictions are inversely transformed.

        Raises:
            AttributeError: If the vectorizer does not have a transform method.
            Exception: If transformation fails due to unexpected errors.
        """
        if self.vectorizer is not None and hasattr(self.vectorizer, "transform"):
            X = self.vectorizer.transform(X)

        y_pred_raw = self.wrapper.transform(X)
        if (
            self.log_target_transformer is not None
            and self.log_target_transformer.fitted
        ):
            y_pred = self.log_target_transformer.inverse_transform(y_pred_raw)
            return y_pred
        else:
            return y_pred_raw

    @property
    def get_estimator_params(self):
        """
        Retrieves the estimator's hyperparameters.

        This property fetches the hyperparameters from the underlying wrapper and
        returns them as a pandas DataFrame with parameter names and their corresponding values.

        Returns:
            pd.DataFrame: A DataFrame containing hyperparameter names and their values.

        Raises:
            AttributeError: If the wrapper does not have the get_estimator_params attribute.
            Exception: If fetching hyperparameters fails due to unexpected errors.
        """
        params = pd.Series(self.wrapper.get_estimator_params)
        params = pd.DataFrame(
            {"Hyperparameter": params.index, "Value": params.values}
        )
        params["Value"] = params["Value"].astype(str)
        return params