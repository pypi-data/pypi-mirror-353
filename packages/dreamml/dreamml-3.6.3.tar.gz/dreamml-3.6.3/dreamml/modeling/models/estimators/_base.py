from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Tuple, List, Dict, Optional, Union
import warnings
import logging
import time

import numpy as np
import pandas as pd

from dreamml.features.feature_extraction._transformers import LogTargetTransformer
from dreamml.features.text.augmentation import AugmentationWrapper
from dreamml.logging.logger import CombinedLogger
from dreamml.logging import get_logger
from dreamml.modeling.metrics import BaseMetric
from dreamml.modeling.metrics.metrics_mapping import metrics_mapping
from dreamml.utils.errors import MissedColumnError
from dreamml.utils.serialize import Serializable, SerializedObject
from dreamml.utils.warnings import DMLWarning

_logger = get_logger(__name__)


class BaseModel(ABC, Serializable):
    """Base wrapper class for machine learning algorithms.

    This abstract base class provides a framework for implementing machine learning models with
    common functionalities such as serialization, input validation, and evaluation.

    Attributes:
        model_name (str): The name of the machine learning algorithm (e.g., xgboost, lightgbm).
        params (dict): A dictionary of hyperparameters.
        task (str): The name of the task (e.g., regression, binary, multi).
        used_features (List[str]): A list of features selected based on specific metric values.
        estimator_class (Optional[Type]): The class of the estimator (e.g., LightGBMModel, XGBoostModel).
        estimator (Optional[Callable]): An instance of the trained model.
        categorical_features (Optional[List[str]]): A list of categorical features.
        text_features (Optional[List[str]]): A list of text features.
        weights (Any): Weights for the model.
        target_with_nan_values (bool): Indicates if the target contains NaN values.
        log_target_transformer (Optional[LogTargetTransformer]): Transformer for log-target.
        parallelism (int): Degree of parallelism.
        metric_name (Optional[str]): Name of the evaluation metric.
        metric_params (Dict): Parameters for the evaluation metric.
        eval_metric (BaseMetric): Evaluation metric instance.
        objective (BaseMetric): Objective metric instance.
        vectorization_name (Optional[str]): Name of the vectorization technique.
        text_augmentations (Optional[List[AugmentationWrapper]]): List of text augmentations.
        aug_p (Optional[float]): Probability of augmentation.
        fillna_value (int): Value to fill NaNs with.
        fitted (bool): Indicates if the model has been fitted.
        _logger (Optional[logging.Logger]): Logger instance for training.
    """

    model_name: str = None

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str] = None,
        categorical_features: List[str] = None,
        metric_name=None,
        metric_params: Dict = None,
        weights=None,
        target_with_nan_values: bool = False,
        log_target_transformer: LogTargetTransformer = None,
        parallelism: int = -1,
        train_logger: Optional[logging.Logger] = None,
        text_features: List[str] = None,
        vectorization_name: str = None,
        augmentation_params: Optional[
            Tuple[Union[List[AugmentationWrapper], float]]
        ] = None,
        **params,
    ):
        """Initializes the BaseModel with the given parameters.

        Args:
            estimator_params (Dict[str, Any]): Configuration dictionary for the model wrapper.
            task (str): The name of the task (e.g., regression, binary, multi).
            used_features (List[str], optional): List of features selected based on metric values.
                Defaults to None.
            categorical_features (List[str], optional): List of categorical features.
                Defaults to None.
            metric_name (optional): Name of the evaluation metric. Defaults to None.
            metric_params (Dict, optional): Parameters for the evaluation metric. Defaults to None.
            weights (optional): Weights for the model. Defaults to None.
            target_with_nan_values (bool, optional): Whether the target contains NaN values.
                Defaults to False.
            log_target_transformer (LogTargetTransformer, optional): Transformer for log-target.
                Defaults to None.
            parallelism (int, optional): Degree of parallelism. Defaults to -1.
            train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
            text_features (List[str], optional): List of text features. Defaults to None.
            vectorization_name (str, optional): Name of the vectorization technique. Defaults to None.
            augmentation_params (Optional[Tuple[Union[List[AugmentationWrapper], float]]], optional):
                Parameters for text augmentation. Defaults to None.
            **params: Additional keyword arguments.

        Raises:
            DMLWarning: If additional parameters are passed but not used.
        """
        self.params = deepcopy(estimator_params)

        self.task = task
        self.used_features = used_features

        if categorical_features is not None and self.used_features is not None:
            categorical_features = list(
                set(categorical_features) & set(self.used_features)
            )
        self.categorical_features = categorical_features
        self.text_features = text_features

        self.weights = weights
        self.target_with_nan_values = target_with_nan_values
        self.log_target_transformer = log_target_transformer
        self.parallelism = parallelism

        self.metric_name = metric_name
        self.metric_params = metric_params.copy()

        self.eval_metric: BaseMetric = metrics_mapping[self.params["eval_metric"]](
            self.model_name,
            task=self.task,
            target_with_nan_values=self.target_with_nan_values,
            **self.metric_params,
        )
        self.objective: BaseMetric = metrics_mapping[self.params["objective"]](
            self.model_name,
            task=self.task,
            target_with_nan_values=self.target_with_nan_values,
            **self.metric_params,
        )

        self.estimator_class = None
        self.estimator = None

        self.vectorization_name = vectorization_name

        if augmentation_params is None:
            self.text_augmentations = None
            self.aug_p = None
        else:
            self.text_augmentations = augmentation_params[0]
            self.aug_p = augmentation_params[1]

        if len(params) > 0:
            warnings.warn(
                f"{params=} are passed to model but not used.",
                DMLWarning,
                stacklevel=2,
            )
        self.fillna_value: int = 0
        self.fitted = False

        self._logger = train_logger

    def _pre_fit(self, data, *eval_set):
        """Preprocessing steps before fitting the model.

        Validates input data, prepares evaluation sets, and logs the start of fitting.

        Args:
            data: Training data.
            *eval_set: Evaluation datasets.

        Returns:
            Tuple containing validated training data and a tuple of validated evaluation sets.
        """
        if self.eval_metric.is_resetting_indexes_required:
            self.eval_metric.set_indexes(train=data.index, valid=eval_set[0].index)

        data = self.validate_input_data(data)

        new_eval_set = []
        for i in range(len(eval_set)):
            if i % 2 == 0:
                new_eval_set.append(self.validate_input_data(eval_set[i]))
            else:
                new_eval_set.append(eval_set[i])

        logger = self._logger or _logger
        logger.info(
            f"{time.ctime()}, start fitting {self.model_name}-Model, "
            f"train.shape: {data.shape[0]} rows, {data.shape[1]} cols.\n"
        )
        return data, tuple(new_eval_set)

    @abstractmethod
    def fit(self, data, target, *eval_set):
        """Abstract method to train the model on the provided data.

        Args:
            data: Feature matrix for training.
            target: Target vector for training.
            *eval_set: Evaluation datasets.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        pass

    @abstractmethod
    def transform(self, data):
        """Abstract method to apply the model to the given data.

        Args:
            data: Feature matrix to transform.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        pass

    def serialize(self) -> dict:
        """Serializes the model instance into a dictionary.

        Handles the serialization of transformers and augmentations.

        Returns:
            dict: Serialized representation of the model.
        """
        if self.log_target_transformer is not None:
            log_target_transformer = self.log_target_transformer.serialize()
        else:
            log_target_transformer = None

        if self.text_augmentations is None:
            augmentation_params = None
        else:
            text_augmentations = [aug.serialize() for aug in self.text_augmentations]
            augmentation_params = (text_augmentations, self.aug_p)

        init_dict = {
            "estimator_params": self.params,
            "task": self.task,
            "used_features": self.used_features,
            "categorical_features": self.categorical_features,
            "metric_name": self.metric_name,
            "metric_params": self.metric_params,
            "weights": self.weights,
            "target_with_nan_values": self.target_with_nan_values,
            "log_target_transformer": log_target_transformer,
            "parallelism": self.parallelism,
            "train_logger": None,  # Not serialized as it is intended for stages that are not serializable
            "text_features": self.text_features,
            "vectorization_name": self.vectorization_name,
            "augmentation_params": augmentation_params,
        }

        additional_dict = {"estimator": self.estimator, "fitted": self.fitted}

        if hasattr(self, "vectorizer_full_name"):
            additional_dict.update(vectorizer_full_name=self.vectorizer_full_name)

        return self._serialize(init_data=init_dict, additional_data=additional_dict)

    @classmethod
    def deserialize(cls, data):
        """Deserializes the model instance from a dictionary.

        Handles the deserialization of transformers and augmentations.

        Args:
            data (dict): Serialized representation of the model.

        Returns:
            BaseModel: Deserialized model instance.
        """
        log_target_transformer = data["init"]["log_target_transformer"]
        if log_target_transformer is not None:
            log_target_transformer = SerializedObject(
                log_target_transformer
            ).deserialize()
            data["init"]["log_target_transformer"] = log_target_transformer

        if data["init"]["augmentation_params"] is not None:
            text_augmentations = data["init"]["augmentation_params"][0]
            text_augmentations = [
                SerializedObject(aug).deserialize() for aug in text_augmentations
            ]
            aug_p = data["init"]["augmentation_params"][1]
            data["init"]["augmentation_params"] = (text_augmentations, aug_p)

        instance = cls._deserialize(data)

        instance.fitted = data["additional"]["fitted"]

        estimator = data["additional"]["estimator"]
        if isinstance(estimator, dict):
            estimator = SerializedObject(estimator).deserialize()

        instance.estimator = estimator

        if "vectorizer_full_name" in data["additional"]:
            instance.vectorizer_full_name = data["additional"]["vectorizer_full_name"]

        return instance

    def validate_input_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validates the input data for required features.

        Checks if the expected features are present in the data. Raises an error if any are missing.

        Args:
            data (pd.DataFrame): Feature matrix to validate.

        Returns:
            pd.DataFrame: Validated feature matrix containing the required features.

        Raises:
            MissedColumnError: If any required features are missing from the data.
        """
        if self.used_features:
            missed_features = list(set(self.used_features) - set(data.columns))
            if missed_features:
                raise MissedColumnError(f"Missed {list(missed_features)} columns.")
            return data[self.used_features]

        return data

    def evaluate_and_print(self, **eval_sets):
        """Evaluates the model on provided evaluation sets and prints the results.

        For classification tasks, the GINI metric is used.
        For regression tasks, MAE, R2, and RMSE metrics are used.

        Args:
            eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): A dictionary where the key is the
                name of the dataset and the value is a tuple containing the feature matrix
                and the true target values.
        """
        metrics_to_eval = {}

        if self.task in ["binary", "multiclass", "multilabel"]:
            metrics_to_eval["GINI"] = metrics_mapping["gini"](
                task=self.task,
                target_with_nan_values=self.target_with_nan_values,
                **self.metric_params,
            )

        elif self.task in ["regression", "timeseries", "anomaly_detection"]:
            metrics_to_eval = {
                "MAE": metrics_mapping["mae"](task=self.task),
                "R2": metrics_mapping["r2"](task=self.task),
                "RMSE": metrics_mapping["rmse"](task=self.task),
            }
        elif self.task == "multiregression":
            metrics_to_eval = {
                self.metric_name.upper(): metrics_mapping[self.metric_name](
                    task=self.task
                )
            }

        if self.eval_metric.name.upper() not in metrics_to_eval:
            metrics_to_eval[self.eval_metric.name.upper()] = self.eval_metric
        if self.objective.name.upper() not in metrics_to_eval:
            metrics_to_eval[self.objective.name.upper()] = self.objective

        for sample in eval_sets:
            if self.model_name in ["ae", "vae"]:
                y_true, _ = eval_sets[sample]
                y_pred = self.transform(y_true, return_output=True)
            else:
                data, y_true = eval_sets[sample]
                y_pred = self.transform(data)

            scores = {}
            for name, metric in metrics_to_eval.items():
                try:
                    scores[name] = metric(y_true, y_pred)
                except (ValueError, KeyError, IndexError):
                    scores[name] = np.nan

            metrics_output = ", ".join(
                [f"{name} = {value:.2f}" for name, value in scores.items()]
            )
            output_per_sample = f"{sample}-score: \t {metrics_output}"

            logger = CombinedLogger([self._logger, _logger])
            logger.info(output_per_sample)

    @property
    def check_is_fitted(self):
        """Checks if the model has been fitted.

        Raises:
            NotFittedError: If the model is not yet fitted.

        Returns:
            bool: True if the model is fitted.
        """
        if not bool(self.estimator):
            msg = (
                "This estimator is not fitted yet. Call 'fit' with"
                " appropriate arguments before using this estimator."
            )
            raise NotFittedError(msg)
        return True

    def _fill_nan_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fills NaN values in the data.

        This method is used for models like logistic regression and linear regression
        that do not have automatic preprocessing for NaN values, unlike models such as
        catboost, xgboost, and lightgbm.

        Args:
            data (pd.DataFrame): Feature matrix with potential NaN values.

        Returns:
            pd.DataFrame: Feature matrix with NaN values filled.
        """
        data = data.fillna(value=self.fillna_value)
        return data