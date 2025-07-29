"""
Wrapper for LightAutoML
"""

import logging
import time
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd

from lightautoml.tasks import Task
from lightautoml.automl.presets.tabular_presets import TabularAutoML

from sklearn.metrics import roc_auc_score

from dreamml.logging import get_logger
from dreamml.modeling.models.estimators import BaseModel

_logger = get_logger(__name__)


def gini(y_true, y_pred):
    """
    Calculate the Gini coefficient based on true and predicted values.

    The Gini coefficient is computed as twice the ROC AUC score minus one.

    Args:
        y_true (array-like): True binary labels.
        y_pred (array-like): Predicted scores or probabilities.

    Returns:
        float: Gini coefficient.

    Raises:
        ValueError: If y_true and y_pred have different lengths.
        sklearn.exceptions.UndefinedMetricWarning: If only one class is present in y_true.
    """
    return 2 * roc_auc_score(y_true, y_pred) - 1


class LAMA(BaseModel):
    """
    LightAutoML model wrapper with a standardized API for dreamml_base.

    This class integrates LightAutoML's TabularAutoML into the dreamml_base framework,
    providing functionalities for training and predicting with automated machine learning.

    Attributes:
        model_name (str): Name of the model.
        params (Dict[str, Any]): Hyperparameters for the model.
        task (str): Task type (e.g., 'regression', 'binary', 'multiclass').
        used_features (List[str]): List of features selected based on specific metrics.
        estimator_class (TabularAutoML): The underlying LightAutoML estimator.
        estimator (TabularAutoML): Trained LightAutoML estimator instance.
        categorical_features (List[str]): List of categorical feature names.
        fitted (bool): Indicates whether the model has been fitted.
    """

    model_name: str = "LAMA"

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str],
        categorical_features: List[str] = None,
        metric_name=None,
        metric_params=None,
        weights=None,
        lama_time=None,
        train_logger: Optional[logging.Logger] = None,
        **params,
    ):
        """
        Initialize the LAMA model with specified parameters.

        Args:
            estimator_params (Dict[str, Any]): Dictionary of hyperparameters for the estimator.
            task (str): Type of task to perform ('regression', 'binary', 'multiclass', etc.).
            used_features (List[str]): List of features selected based on specific metrics.
            categorical_features (List[str], optional): List of categorical feature names. Defaults to None.
            metric_name (Any, optional): Name of the evaluation metric. Defaults to None.
            metric_params (Any, optional): Parameters for the evaluation metric. Defaults to None.
            weights (Any, optional): Sample weights. Defaults to None.
            lama_time (Any, optional): Timeout parameter for LightAutoML. Defaults to None.
            train_logger (logging.Logger, optional): Logger for training process. Defaults to None.
            **params: Additional keyword arguments.

        Raises:
            TypeError: If required parameters are missing or of incorrect type.
        """
        super().__init__(
            estimator_params,
            task,
            used_features,
            categorical_features,
            metric_name,
            metric_params,
            weights=weights,
            train_logger=train_logger,
            **params,
        )
        self.timeout = lama_time
        self.estimator_class = self.get_estimator()
        self.fitted = False

    def get_estimator(self) -> TabularAutoML:
        """
        Initialize the TabularAutoML estimator based on the task type.

        Returns:
            TabularAutoML: Configured LightAutoML TabularAutoML estimator.

        Raises:
            NotImplementedError: If the specified task is not supported.
        """
        if self.task == "binary":
            estimator = TabularAutoML(
                Task(
                    name="binary",
                    metric=self.eval_metric,
                ),
                timeout=self.timeout,
            )
        elif self.task == "regression":
            estimator = TabularAutoML(
                Task(
                    name="reg",
                    loss=self.params["loss_function"],
                    metric=self.eval_metric,
                ),
                timeout=self.timeout,
            )
        elif self.task == "multiclass":
            estimator = TabularAutoML(
                Task(
                    name="multiclass",
                    loss="crossentropy",
                    metric="crossentropy",
                ),
                timeout=self.timeout,
            )
        else:
            raise NotImplementedError(f"{self.task} is not supported for LAMA.")

        return estimator

    def fit(self, data: pd.DataFrame, target: pd.Series, *eval_set) -> None:
        """
        Train the LightAutoML model on the provided data and target.

        Args:
            data (pd.DataFrame): Feature matrix for training, shape = [n_samples, n_features].
            target (pd.Series): Target vector, shape = [n_samples, ].
            *eval_set: Optional evaluation datasets.

        Returns:
            None

        Raises:
            ValueError: If data and target dimensions do not align.
            lightautoml.exceptions.LightAutoMLError: If training fails within LightAutoML.
        """
        _logger.info(
            f"{time.ctime()}, start fitting LightAutoML, "
            f"train.shape: {data.shape[0]} rows, {data.shape[1]} cols.",
        )
        dtrain = pd.concat([data, target], axis=1)
        self.estimator = self.estimator_class
        self.estimator.fit_predict(dtrain, roles={"target": target.name}, verbose=1)

        used_features = self.estimator.get_feature_scores("fast")
        if used_features is None:
            self.used_features = data.columns.tolist()
        else:
            self.used_features = list(used_features.iloc[:, 0])

        self.fitted = True

    def transform(self, data: pd.DataFrame) -> np.ndarray:
        """
        Apply the trained model to the provided data to generate predictions.

        The model must be previously trained using the `fit` method.

        Args:
            data (pd.DataFrame): Feature matrix for prediction, shape = [n_samples, n_features].

        Returns:
            np.ndarray: Array of predictions, shape = [n_samples, ] for binary and regression tasks,
                        or [n_samples, n_classes] for multiclass tasks.

        Raises:
            ValueError: If the task type is unsupported.
            AttributeError: If the model has not been fitted yet.
        """
        if not self.fitted:
            raise AttributeError("The model must be fitted before calling transform.")

        prediction = self.estimator.predict(data)

        if self.task in ["binary", "regression"]:
            return prediction.data[:, 0]
        elif self.task == "multiclass":
            prediction = self.estimator.predict(data)
            return prediction.data
        else:
            raise ValueError(f"Task type '{self.task}' is not supported.")