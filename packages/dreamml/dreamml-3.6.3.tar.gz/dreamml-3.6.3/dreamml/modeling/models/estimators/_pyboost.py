import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from dreamml.features.feature_extraction._transformers import LogTargetTransformer
from dreamml.modeling.models.estimators import BoostingBaseModel
from dreamml.modeling.models.callbacks.callbacks import PyBoostLoggingCallback

try:
    import cupy as cp
    from py_boost import GradientBoosting, SketchBoost
except ImportError:
    cp = None
    GradientBoosting = None
    SketchBoost = None


class PyBoostModel(BoostingBaseModel):
    """PyBoost model with a standardized API for dreamml_base.

    This model integrates the PyBoost library into dreamml_base, providing a consistent interface
    for boosting algorithms. It supports various tasks such as regression, binary classification,
    multiclass classification, and multilabel classification.

    Attributes:
        params (dict): Dictionary of hyperparameters.
        task (str): Name of the task (e.g., 'regression', 'binary', 'multiclass', 'multilabel').
        model_name (str): Name of the algorithm ('PyBoost').
        used_features (list): List of features selected based on specific metric values.
        estimator_class (callable): Class responsible for training the model for the specific task.
        estimator (callable): Instance of the trained model.
        categorical_features (list): List of categorical features.
        fitted (bool): Indicates whether the model has been trained. True if fitted, False otherwise.
    """

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str],
        categorical_features: List[str],
        metric_name: str,
        metric_params: Dict[str, Any],
        weights: Optional[pd.Series] = None,
        train_logger: Optional[logging.Logger] = None,
        log_target_transformer: Optional[LogTargetTransformer] = None,
        **params,
    ):
        """Initializes the PyBoostModel with the given parameters.

        Args:
            estimator_params (Dict[str, Any]): Dictionary of hyperparameters for the estimator.
            task (str): Name of the task (e.g., 'regression', 'binary', 'multiclass', 'multilabel').
            used_features (List[str]): List of features selected based on specific metric values.
            categorical_features (List[str]): List of categorical features.
            metric_name (str): Name of the evaluation metric.
            metric_params (Dict[str, Any]): Parameters for the evaluation metric.
            weights (Optional[pd.Series], optional): Sample weights. Defaults to None.
            train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
            log_target_transformer (Optional[LogTargetTransformer], optional): Transformer for log targets. Defaults to None.
            **params: Additional keyword arguments for the model.

        """
        super().__init__(
            estimator_params,
            task,
            used_features,
            categorical_features,
            metric_name,
            metric_params,
            weights=weights,
            **params,
            log_target_transformer=log_target_transformer,
            train_logger=train_logger,
        )

        self.estimator_class = self._estimators.get(self.task, GradientBoosting)
        self.verbose = self.params.pop("verbose", 100)
        self.callback = PyBoostLoggingCallback(train_logger)

    @property
    def _estimators(self) -> Dict[str, Any]:
        """Dictionary of Sklearn wrappers over PyBoost.

        Returns:
            Dict[str, Any]: Keys are task names and values are classes responsible for training models for specific tasks.
        """
        estimators = {
            "binary": GradientBoosting,
            "multiclass": GradientBoosting,
            "multilabel": SketchBoost,
            "regression": GradientBoosting,
            # "timeseries": CatBoostRegressor,
        }
        return estimators

    def _create_eval_set(
        self,
        data: pd.DataFrame,
        target: pd.Series,
        *eval_set: Any,
        asnumpy: bool = False,
    ) -> List[Any]:
        """Creates an evaluation set in sklearn format.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            *eval_set (Any): Tuple containing validation data and target.
            asnumpy (bool, optional): Whether to convert data to NumPy arrays. Defaults to False.

        Returns:
            List[Any]: List of tuples representing evaluation sets.

        Raises:
            ValueError: If the task is not supported.

        """
        data = self.validate_input_data(data)

        if asnumpy:
            # Convert pd.DataFrame to numpy array for PyBoost input if needed
            data, target = (
                np.array(data.values, dtype=np.float32),
                np.array(target.values, dtype=np.float32),
            )

        if eval_set:
            valid_data = self.validate_input_data(eval_set[0])
            if self.task == "regression" and isinstance(
                self.log_target_transformer, LogTargetTransformer
            ):
                eval_set = (
                    valid_data,
                    self.log_target_transformer.transform(eval_set[1]),
                )
            else:
                eval_set = (valid_data, eval_set[1])

            if asnumpy:
                return [
                    (data, target),
                    (
                        np.array(valid_data.values, dtype=np.float32),
                        np.array(eval_set[1].values, dtype=np.float32),
                    ),
                ]
            return [(data, target), (valid_data, eval_set[1])]

        return [(data, target)]

    def _create_fit_params(
        self,
        data: pd.DataFrame,
        target: pd.Series,
        weights: pd.Series,
        *eval_set: Any,
        asnumpy: bool = False,
    ) -> Dict[str, Any]:
        """Creates training parameters in PyBoost format.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            weights (pd.Series): Sample weights.
            *eval_set (Any): Tuple containing validation data and target.
            asnumpy (bool, optional): Whether to convert data to NumPy arrays. Defaults to False.

        Returns:
            Dict[str, Any]: Dictionary containing evaluation sets formatted for PyBoost.

        """
        _eval_sets = []
        for _set in self._create_eval_set(data, target, *eval_set, asnumpy=True):
            _eval_set = {"X": _set[0], "y": _set[1], "sample_weight": None}
            _eval_sets.append(_eval_set)

        return {
            "eval_sets": _eval_sets,
        }

    def fit(self, data: pd.DataFrame, target: pd.Series, *eval_set: Any) -> None:
        """Trains the model on the provided data and target.

        Args:
            data (pd.DataFrame): Feature matrix for training, shape = [n_samples, n_features].
            target (pd.Series): Target vector for training, shape = [n_samples, ].
            *eval_set (Any): Tuple containing validation data and target. The first element
                             of the tuple is the feature matrix, and the second element is
                             the target vector.

        Raises:
            ValueError: If there is an issue with the training process.

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
            if key not in ["objective", "eval_metric", "loss_function"]
        }
        params["callbacks"] = [self.callback]
        params["verbose"] = -1 if not self.verbose else 10

        objective = self.objective.get_model_objective()
        eval_metric = self.eval_metric.get_model_metric()

        self.estimator = self.estimator_class(
            loss=objective, metric=eval_metric, **params
        )

        if self.task == "regression" and isinstance(
            self.log_target_transformer, LogTargetTransformer
        ):
            target = self.log_target_transformer.fit_transform(target)

        fit_params = self._create_fit_params(
            data, target, weights, *eval_set, asnumpy=True
        )

        self.estimator.fit(
            X=np.array(data, dtype=np.float32),
            y=np.array(target, dtype=np.float32),
            **fit_params,
        )
        self.fitted = True

    def transform(self, data: pd.DataFrame) -> np.ndarray:
        """Applies the trained model to the provided data.

        The model must be fitted before calling this method. If the `fit` method
        has not been called, an exception will be raised.

        Args:
            data (pd.DataFrame): Feature matrix for prediction, shape = [n_samples, n_features].

        Returns:
            np.ndarray: Array of model predictions, shape = [n_samples, ].

        Raises:
            ValueError: If the task is not supported or the model is not fitted.

        """
        self.check_is_fitted()
        data = self.validate_input_data(data)
        prediction = self.estimator.predict(data)
        if self.task in ["multilabel", "multiclass"]:
            return prediction
        elif self.task in ["regression", "binary", "timeseries"]:
            if self.task == "regression" and isinstance(
                self.log_target_transformer, LogTargetTransformer
            ):
                prediction = self.log_target_transformer.inverse_transform(prediction)
            return prediction.reshape(-1)
        else:
            raise ValueError(f"Task '{self.task}' is not supported.")

    def __call__(self, data: pd.DataFrame) -> np.ndarray:
        """Enables the model instance to be called as a function for predictions.

        Args:
            data (pd.DataFrame): Feature matrix for prediction.

        Returns:
            np.ndarray: Array of model predictions.

        """
        return self.transform(data)

    @staticmethod
    def _get_best_iteration(estimator: Any) -> int:
        """Retrieves the best iteration number from the estimator.

        Args:
            estimator (Any): The trained estimator.

        Returns:
            int: The best iteration number.

        """
        return estimator.best_round