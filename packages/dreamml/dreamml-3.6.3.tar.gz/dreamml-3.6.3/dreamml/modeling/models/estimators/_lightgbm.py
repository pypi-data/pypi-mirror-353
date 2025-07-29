from typing import Tuple, Dict, Any, List, Optional
import logging

import pandas as pd
from lightgbm import LGBMRegressor, LGBMClassifier

from dreamml.modeling.models.callbacks.callbacks import LightGBMLoggingCallback
from dreamml.modeling.models.estimators import BoostingBaseModel
from dreamml.modeling.models.estimators._multioutput_wrappers import (
    OneVsRestClassifierWrapper,
)
from dreamml.features.feature_extraction._transformers import LogTargetTransformer


class LightGBMModel(BoostingBaseModel):
    """LightGBM model with a standardized API for dreamml_base.

    This class encapsulates the LightGBM algorithm, providing a consistent interface
    for training and predicting across different types of machine learning tasks
    such as regression, binary classification, multiclass classification, and
    multilabel classification.

    Attributes:
        model_name (str): The name of the algorithm, set to "LightGBM".
        params (dict): Dictionary of hyperparameters for the model.
        task (str): The name of the task (e.g., "regression", "binary", "multiclass", "multilabel").
        used_features (List[str]): List of features selected based on a specific metric.
        estimator_class: The class of the estimator corresponding to the task.
        estimator: Instance of the trained model.
        categorical_features (List[str]): List of categorical features.
        early_stopping_rounds (int): Number of training iterations with no improvement to trigger early stopping.
        fitted (bool): Indicates whether the model has been fitted.
    """

    model_name = "LightGBM"

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
        """Initializes the LightGBMModel with the given parameters.

        Args:
            estimator_params (Dict[str, Any]): Dictionary of hyperparameters for the estimator.
            task (str): The type of task (e.g., "regression", "binary", "multiclass", "multilabel").
            used_features (List[str]): List of features selected based on a specific metric.
            categorical_features (List[str]): List of categorical features.
            metric_name: Name of the metric to be used for evaluation.
            metric_params: Parameters for the evaluation metric.
            weights (optional): Sample weights for the training data.
            target_with_nan_values (bool, optional): Indicates if the target contains NaN values. Defaults to False.
            log_target_transformer (LogTargetTransformer, optional): Transformer for log-transforming the target. Defaults to None.
            parallelism (int, optional): Number of parallel threads. Defaults to -1.
            train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
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
            target_with_nan_values=target_with_nan_values,
            log_target_transformer=log_target_transformer,
            parallelism=parallelism,
            train_logger=train_logger,
            **params,
        )
        self.estimator_class = self._estimators.get(self.task)
        self.early_stopping_rounds = self.params.pop("early_stopping_rounds", 100)
        self.verbose = self.params.pop("verbose", False)
        self.callback = LightGBMLoggingCallback(train_logger)

    @property
    def _estimators(self):
        """Dictionary of Sklearn wrappers for LightGBM based on the task.

        Returns:
            dict: A dictionary where keys are task names and values are the corresponding LightGBM estimator classes.
        """
        estimators = {
            "binary": LGBMClassifier,
            "multiclass": LGBMClassifier,
            "multilabel": LGBMClassifier,
            "regression": LGBMRegressor,
            "timeseries": LGBMRegressor,
        }
        return estimators

    def _create_fit_params(
        self, data: pd.DataFrame, target: pd.Series, weights: pd.Series, *eval_set
    ) -> Dict[str, Any]:
        """Creates training parameters in LightGBM format.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            weights (pd.Series): Sample weights.
            *eval_set: Validation datasets as tuples of (features, target).

        Returns:
            Dict[str, Any]: Dictionary of parameters for LightGBM training.
        """
        return {
            "early_stopping_rounds": self.early_stopping_rounds,
            "eval_set": self._create_eval_set(data, target, *eval_set),
            "sample_weight": weights,
            "verbose": self.verbose,
            "callbacks": [self.callback],
        }

    def fit(self, data, target, *eval_set):
        """Trains the LightGBM model on the provided data.

        Args:
            data (pd.DataFrame): Feature matrix for training, shape = [n_samples, n_features].
            target (pd.Series): Target vector for training, shape = [n_samples, ].
            eval_set (Tuple[pd.DataFrame, pd.Series]): Validation datasets as tuples of (features, target).

        Raises:
            ValueError: If the model parameters are invalid or the training data is not suitable.
        """
        categorical_features = (
            self.categorical_features
            if self.categorical_features is not None
            else "auto"
        )

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
        n_estimators = self.params.get("n_estimators")

        eval_metric = self.eval_metric.get_model_metric()
        objective = self.objective.get_model_objective()
        self.estimator = self.estimator_class(
            objective=objective, n_estimators=n_estimators, **params
        )

        if self.task == "multilabel":
            self.estimator = OneVsRestClassifierWrapper(
                estimator=self.estimator,
                n_jobs=1 if self.parallelism == 0 else self.parallelism,
                get_best_iteration_func=self._get_best_iteration,
                n_estimators=n_estimators,
            )

        if self.task == "regression" and isinstance(
            self.log_target_transformer, LogTargetTransformer
        ):
            target = self.log_target_transformer.fit_transform(target)

        fit_params = self._create_fit_params(data, target, weights, *eval_set)
        fit_params = {
            key: value
            for key, value in fit_params.items()
            if key not in ["objective", "eval_metric"]
        }
        self._logger.debug(f"categorical_features={categorical_features,}")
        self.estimator.fit(
            X=data,
            y=target,
            categorical_feature=categorical_features,
            eval_metric=eval_metric,
            **fit_params,
        )
        self.fitted = True

    def transform(self, data):
        """Applies the trained model to the provided data to generate predictions.

        The model must be fitted before calling this method. If the model is not fitted,
        an exception will be raised.

        Args:
            data (pd.DataFrame): Feature matrix for prediction, shape = [n_samples, n_features].

        Returns:
            array-like: Predictions generated by the model, shape = [n_samples, ].

        Raises:
            NotFittedError: If the model has not been fitted yet.
            ValueError: If the input data is invalid.
        """
        data = self.validate_input_data(data)
        if self.task == "binary":
            prediction = self.estimator.predict_proba(data)
            return prediction[:, 1]
        elif self.task in ("multiclass", "multilabel"):
            prediction = self.estimator.predict_proba(data)
            return prediction
        elif self.task in ("regression", "timeseries"):
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
    ) -> Dict[str, Any]:
        """Serializes the model for storage or transmission.

        Args:
            init_data (optional): Initialization data for serialization.
            additional_data (optional): Additional data to include in the serialization.

        Returns:
            Dict[str, Any]: Serialized representation of the model.

        Raises:
            SerializationError: If serialization fails.
        """
        estimator = additional_data["estimator"]

        if isinstance(estimator, OneVsRestClassifierWrapper):
            estimator = estimator.serialize()

        additional_data["estimator"] = estimator

        return super()._serialize(init_data, additional_data)

    @staticmethod
    def _get_best_iteration(estimator) -> int:
        """Retrieves the best iteration number from the estimator.

        Args:
            estimator: The trained estimator from which to retrieve the best iteration.

        Returns:
            int: The best iteration number.
        """
        return estimator.best_iteration_