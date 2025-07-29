import logging
from typing import Dict, Any, List, Optional

import pandas as pd
from xgboost import XGBClassifier, XGBRegressor

from dreamml.modeling.models.callbacks.callbacks import XGBoostLoggingCallback
from dreamml.modeling.models.estimators import BoostingBaseModel
from dreamml.modeling.models.estimators._multioutput_wrappers import (
    OneVsRestClassifierWrapper,
)
from dreamml.features.feature_extraction._transformers import LogTargetTransformer


class XGBoostModel(BoostingBaseModel):
    """
    XGBoost Model with a standardized API for dreamml_base.

    This model wraps XGBoost classifiers and regressors, providing a unified interface
    for different machine learning tasks such as binary classification, multiclass
    classification, multilabel classification, regression, and time series forecasting.

    Args:
        estimator_params (Dict[str, Any]): Dictionary of hyperparameters for the estimator.
        task (str): The name of the task (e.g., 'regression', 'binary', 'multiclass', 'multilabel', 'timeseries').
        used_features (List[str]): List of feature names selected based on a specific metric.
        categorical_features (List[str]): List of categorical feature names.
        metric_name (Any): The name of the evaluation metric.
        metric_params (Any): Parameters for the evaluation metric.
        weights (Optional[Any], optional): Sample weights. Defaults to None.
        target_with_nan_values (bool, optional): Indicates if the target contains NaN values. Defaults to False.
        log_target_transformer (LogTargetTransformer, optional): Transformer for log-transforming the target. Defaults to None.
        parallelism (int, optional): Degree of parallelism. Defaults to -1.
        train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
        **params: Additional keyword arguments.

    Attributes:
        params (Dict[str, Any]): Dictionary of hyperparameters.
        task (str): The name of the task.
        model_name (str): The name of the algorithm ('XGBoost').
        used_features (List[str]): List of selected feature names.
        estimator_class (Callable): The estimator class corresponding to the task.
        estimator (Optional[Callable]): The trained estimator instance.
        categorical_features (List[str]): List of categorical feature names.
        early_stopping_rounds (int): Number of training iterations without improvement to trigger early stopping.
    """

    model_name = "XGBoost"

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str],
        categorical_features: List[str],
        metric_name,
        metric_params,
        weights=None,
        target_with_nan_values: bool = False,
        log_target_transformer: LogTargetTransformer = None,
        parallelism: int = -1,
        train_logger: Optional[logging.Logger] = None,
        **params,
    ):
        """
        Initializes the XGBoostModel with the given parameters.

        Args:
            estimator_params (Dict[str, Any]): Dictionary of hyperparameters for the estimator.
            task (str): The name of the task (e.g., 'regression', 'binary', 'multiclass', 'multilabel', 'timeseries').
            used_features (List[str]): List of feature names selected based on a specific metric.
            categorical_features (List[str]): List of categorical feature names.
            metric_name (Any): The name of the evaluation metric.
            metric_params (Any): Parameters for the evaluation metric.
            weights (Optional[Any], optional): Sample weights. Defaults to None.
            target_with_nan_values (bool, optional): Indicates if the target contains NaN values. Defaults to False.
            log_target_transformer (LogTargetTransformer, optional): Transformer for log-transforming the target. Defaults to None.
            parallelism (int, optional): Degree of parallelism. Defaults to -1.
            train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
            **params: Additional keyword arguments.
        """
        super().__init__(
            estimator_params,
            task,
            used_features,
            categorical_features,
            metric_name,
            metric_params,
            weights=weights,
            target_with_nan_values=target_with_nan_values,
            log_target_transformer=log_target_transformer,
            parallelism=parallelism,
            **params,
            train_logger=train_logger,
        )
        self.estimator_class = self._estimators.get(self.task)
        self.verbose = self.params.pop("verbose", 100)
        self.callback = XGBoostLoggingCallback(train_logger)

    @property
    def _estimators(self):
        """
        Dictionary mapping task names to their corresponding XGBoost estimator classes.

        Returns:
            Dict[str, Callable]: A dictionary where keys are task names and values are XGBoost estimator classes.
        """
        estimators = {
            "binary": XGBClassifier,
            "multiclass": XGBClassifier,
            "multilabel": XGBClassifier,
            "regression": XGBRegressor,
            "timeseries": XGBRegressor,
        }
        return estimators

    def _create_fit_params(
        self, data: pd.DataFrame, target: pd.Series, weights: pd.Series, *eval_set
    ):
        """
        Creates a dictionary of parameters to be passed to the fit method of the estimator.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            weights (pd.Series): Sample weights.
            *eval_set: Validation datasets.

        Returns:
            Dict[str, Any]: Dictionary of fit parameters.
        """
        return {
            "eval_set": self._create_eval_set(data, target, *eval_set),
            "sample_weight": weights,
            "verbose": self.verbose,
        }

    def fit(self, data, target, *eval_set):
        """
        Trains the XGBoost model on the provided data and target.

        Args:
            data (pd.DataFrame): Training feature matrix.
            target (pd.Series): Training target vector.
            *eval_set (Tuple[pd.DataFrame, pd.Series]): One or more validation datasets.

        Raises:
            ValueError: If the estimator class for the given task is not found.
        """
        if self.categorical_features is not None:
            if len(self.categorical_features) != 0:
                self.params["enable_categorical"] = True
                for feature_name in self.categorical_features:
                    data[f"{feature_name}"] = data[f"{feature_name}"].astype("category")

        data, eval_set = self._pre_fit(data, *eval_set)

        if self.weights is not None:
            weights = self.weights.copy()
            weights = weights.loc[data.index]
        else:
            weights = None

        params = {
            key: value
            for key, value in self.params.items()
            if key not in ["objective", "eval_metric", "n_estimators"]
        }
        params["callbacks"] = [self.callback]
        n_estimators = self.params.get("n_estimators")

        eval_metric = self.eval_metric.get_model_metric()
        objective = self.objective.get_model_objective()
        self.estimator = self.estimator_class(
            objective=objective,
            eval_metric=eval_metric,
            n_estimators=n_estimators,
            **params,
        )
        if self.task == "multilabel" and self.target_with_nan_values:
            self.estimator = OneVsRestClassifierWrapper(
                estimator=self.estimator,
                n_jobs=self.parallelism,
                get_best_iteration_func=self._get_best_iteration,
                n_estimators=n_estimators,
            )

        if self.task == "regression" and isinstance(
            self.log_target_transformer, LogTargetTransformer
        ):
            target = self.log_target_transformer.fit_transform(target)

        fit_params = self._create_fit_params(data, target, weights, *eval_set)

        self.estimator.fit(
            X=data,
            y=target,
            **fit_params,
        )

        self.fitted = True

    def transform(self, data):
        """
        Applies the trained model to the provided data to generate predictions.

        This method should be called after the model has been fitted using the `fit` method.

        Args:
            data (pd.DataFrame): Feature matrix for which to generate predictions.

        Returns:
            Union[pd.Series, np.ndarray]: The model's predictions.

        Raises:
            AttributeError: If the model has not been fitted yet.
        """
        data = self.validate_input_data(data)
        if self.task == "binary":
            prediction = self.estimator.predict_proba(data)
            return prediction[:, 1]
        elif self.task in ("multilabel", "multiclass"):
            prediction = self.estimator.predict_proba(data)
            return prediction
        elif self.task in ["regression", "timeseries"]:
            prediction = self.estimator.predict(data)
            if self.task == "regression" and isinstance(
                self.log_target_transformer, LogTargetTransformer
            ):
                prediction = self.log_target_transformer.inverse_transform(prediction)
            return prediction

    def _serialize(
        self,
        init_data=None,
        additional_data=None,
    ):
        """
        Serializes the model, preparing it for storage or transmission.

        It handles the removal of non-serializable components such as metrics and callbacks.

        Args:
            init_data (Optional[Any], optional): Initial data for serialization. Defaults to None.
            additional_data (Optional[Dict[str, Any]], optional): Additional data to include in serialization. Defaults to None.

        Returns:
            Dict[str, Any]: Serialized representation of the model.
        """
        estimator = additional_data["estimator"]

        true_estimator = (
            estimator.estimator
            if isinstance(estimator, OneVsRestClassifierWrapper)
            else estimator
        )

        # avoid non-serializable metrics
        true_estimator.eval_metric = None

        # avoid non-serializable callbacks
        true_estimator.callbacks = [
            callback
            for callback in true_estimator.callbacks
            if not isinstance(callback, XGBoostLoggingCallback)
        ]

        if isinstance(estimator, OneVsRestClassifierWrapper):
            estimator = estimator.serialize()

        additional_data["estimator"] = estimator

        return super()._serialize(init_data, additional_data)

    @staticmethod
    def _get_best_iteration(estimator) -> int:
        """
        Retrieves the best iteration number from the estimator.

        Args:
            estimator: The trained estimator instance.

        Returns:
            int: The best iteration number.
        """
        return estimator.best_iteration