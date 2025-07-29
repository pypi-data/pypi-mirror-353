import logging
from typing import Dict, Any, List, Optional, Tuple

from catboost import CatBoostClassifier, CatBoostRegressor
import pandas as pd

from dreamml.modeling.models.estimators import BoostingBaseModel
from dreamml.modeling.models.estimators._multioutput_wrappers import (
    OneVsRestClassifierWrapper,
)
from dreamml.modeling.models.callbacks.callbacks import CatBoostLoggingCallback
from dreamml.features.feature_extraction._transformers import LogTargetTransformer


class CatBoostModel(BoostingBaseModel):
    """CatBoost model with a standardized API for dreamml_base.

    This class provides an interface for training and using CatBoost models
    within the dreamml_base framework, supporting various tasks such as regression,
    classification, and multi-output predictions.

    Attributes:
        model_name (str): The name of the algorithm, set to "CatBoost".
        params (Dict[str, Any]): Dictionary of hyperparameters.
        task (str): The name of the task (e.g., "regression", "binary", "multi").
        used_features (List[str]): List of features selected based on specific metrics.
        estimator_class (Type): The class of the estimator (e.g., CatBoostClassifier, CatBoostRegressor).
        estimator (Optional[Callable]): An instance of the trained model.
        categorical_features (List[str]): List of categorical feature names.
        fitted (bool): Indicates whether the model has been fitted.
        callback (CatBoostLoggingCallback): Callback for logging during training.
    """

    model_name = "CatBoost"

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str],
        categorical_features: List[str],
        metric_name: str,
        metric_params: Dict[str, Any],
        weights: Optional[pd.Series] = None,
        target_with_nan_values: bool = False,
        log_target_transformer: Optional[LogTargetTransformer] = None,
        parallelism: int = -1,
        train_logger: Optional[logging.Logger] = None,
        **params,
    ):
        """Initializes the CatBoostModel with specified parameters.

        Args:
            estimator_params (Dict[str, Any]): Dictionary of hyperparameters.
            task (str): The name of the task (e.g., "regression", "binary", "multi").
            used_features (List[str]): List of features selected based on specific metrics.
            categorical_features (List[str]): List of categorical feature names.
            metric_name (str): Name of the evaluation metric.
            metric_params (Dict[str, Any]): Parameters for the evaluation metric.
            weights (Optional[pd.Series], optional): Sample weights. Defaults to None.
            target_with_nan_values (bool, optional): Indicates if the target contains NaN values. Defaults to False.
            log_target_transformer (Optional[LogTargetTransformer], optional): Transformer for log-target. Defaults to None.
            parallelism (int, optional): Number of parallel threads. Defaults to -1.
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
            train_logger=train_logger,
            **params,
        )
        self.estimator_class = self._estimators.get(self.task, CatBoostClassifier)
        self.callback = CatBoostLoggingCallback(train_logger)

    @property
    def _estimators(self) -> Dict[str, Any]:
        """Dictionary of sklearn wrappers for CatBoost based on task.

        Returns:
            Dict[str, Any]: A mapping from task names to corresponding CatBoost estimator classes.
        """
        estimators = {
            "binary": CatBoostClassifier,
            "multiclass": CatBoostClassifier,
            "multilabel": CatBoostClassifier,
            "multiregression": CatBoostRegressor,
            "regression": CatBoostRegressor,
            "timeseries": CatBoostRegressor,
        }
        return estimators

    def _create_eval_set(
        self, data: pd.DataFrame, target: pd.Series, *eval_set: Tuple[pd.DataFrame, pd.Series], asnumpy: bool = False
    ) -> List[Tuple[pd.DataFrame, pd.Series]]:
        """Creates evaluation sets in sklearn format.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            *eval_set (Tuple[pd.DataFrame, pd.Series]): Optional evaluation sets.
            asnumpy (bool, optional): Whether to return numpy arrays. Defaults to False.

        Returns:
            List[Tuple[pd.DataFrame, pd.Series]]: A list of tuples containing feature matrices and target vectors.

        Raises:
            ValueError: If the evaluation set format is incorrect.
        """
        # TODO: validate_input_data already called in _pre_fit
        data = self.validate_input_data(data)
        if eval_set:
            valid_data = self.validate_input_data(eval_set[0])
            if self.task == "regression" and isinstance(
                self.log_target_transformer, LogTargetTransformer
            ):
                return [
                    (valid_data, self.log_target_transformer.transform(eval_set[1]))
                ]
            return [(valid_data, eval_set[1])]

        return [(data, target)]

    def _create_fit_params(
        self, data: pd.DataFrame, target: pd.Series, weights: Optional[pd.Series], *eval_set: Tuple[pd.DataFrame, pd.Series]
    ) -> Dict[str, Any]:
        """Creates training parameters in CatBoost format.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            weights (Optional[pd.Series]): Sample weights.
            *eval_set (Tuple[pd.DataFrame, pd.Series]): Optional evaluation sets.

        Returns:
            Dict[str, Any]: A dictionary of parameters for CatBoost's fit method.
        """
        device = self.params.get("task_type", "cpu").lower()
        _fit_params = {
            "eval_set": self._create_eval_set(data, target, *eval_set),
            "sample_weight": weights,
        }
        if device not in ["gpu", "cuda"]:
            _fit_params["callbacks"] = [self.callback]
        return _fit_params

    def fit(self, data: pd.DataFrame, target: pd.Series, *eval_set: Tuple[pd.DataFrame, pd.Series]) -> None:
        """Trains the CatBoost model on the provided data.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            *eval_set (Tuple[pd.DataFrame, pd.Series]): Optional evaluation sets.

        Raises:
            ValueError: If the input data is invalid or training fails.
        """
        data, eval_set = self._pre_fit(data, *eval_set)

        if self.weights is not None:
            weights = self.weights.copy()
            weights = weights.loc[data.index]
        else:
            weights = None

        params = {
            key: value
            for key, value in self.params.items()
            if key not in ["objective", "eval_metric", "loss_function", "n_estimators"]
        }
        n_estimators = self.params.get("n_estimators")

        eval_metric = self.eval_metric.get_model_metric()
        objective = self.objective.get_model_objective()

        self.estimator = self.estimator_class(
            loss_function=objective,
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
            X=data, y=target, cat_features=self.categorical_features, **fit_params
        )
        self.fitted = True

    def transform(self, data: pd.DataFrame) -> Any:
        """Applies the trained model to the provided data to generate predictions.

        The model must be fitted before calling this method.

        Args:
            data (pd.DataFrame): Feature matrix for making predictions.

        Returns:
            Any: Predictions generated by the model. The format depends on the task:
                 - For binary classification: array-like of probabilities for the positive class.
                 - For multiclass classification: array-like of class probabilities.
                 - For regression and related tasks: array-like of predicted values.

        Raises:
            NotFittedError: If the model has not been fitted yet.
            ValueError: If the input data is invalid.
        """
        self.check_is_fitted
        data = self.validate_input_data(data)

        if self.task in ("binary", "multiclass", "multilabel"):
            prediction = self.estimator.predict_proba(data)
            return prediction[:, 1] if self.task == "binary" else prediction
        elif self.task in ("regression", "timeseries", "multiregression"):
            prediction = self.estimator.predict(data)
            if self.task == "regression" and isinstance(
                self.log_target_transformer, LogTargetTransformer
            ):
                prediction = self.log_target_transformer.inverse_transform(prediction)
            return prediction

    def _serialize(
        self,
        init_data: Optional[Any] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Serializes the model for storage or transmission.

        Args:
            init_data (Optional[Any], optional): Initialization data. Defaults to None.
            additional_data (Optional[Dict[str, Any]], optional): Additional data to include in serialization. Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing serialized model data.
        """
        estimator = additional_data["estimator"]

        true_estimator = (
            estimator.estimator
            if isinstance(estimator, OneVsRestClassifierWrapper)
            else estimator
        )

        # avoid non-serializable metrics
        true_estimator._init_params.pop("eval_metric", None)

        if isinstance(estimator, OneVsRestClassifierWrapper):
            estimator = estimator.serialize()

        additional_data["estimator"] = estimator

        return super()._serialize(init_data, additional_data)

    @staticmethod
    def _get_best_iteration(estimator: Any) -> int:
        """Retrieves the best iteration number from the estimator.

        Args:
            estimator (Any): The estimator object.

        Returns:
            int: The best iteration number.
        """
        return estimator.best_iteration_