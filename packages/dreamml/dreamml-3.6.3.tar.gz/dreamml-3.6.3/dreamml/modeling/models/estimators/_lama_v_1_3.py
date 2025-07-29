"""Wrapper for the new version of WhiteBox AutoML (22.03.22)"""

import time
import logging
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd

from autowoe import AutoWoE

from dreamml.logging import get_logger
from dreamml.modeling.models.estimators import BaseModel

_logger = get_logger(__name__)


class WBAutoML(BaseModel):
    """WhiteBox AutoML model with a standardized API for dreamml_base.

    Args:
        estimator_params (Dict[str, Any]): Dictionary of hyperparameters.
        task (str): Name of the task (e.g., 'regression', 'binary', 'multi').
        used_features (List[str]): List of features selected based on a specific metric.
        categorical_features (List[str], optional): List of categorical features. Defaults to None.
        metric_name (Any, optional): Name of the metric. Defaults to None.
        metric_params (Any, optional): Parameters for the metric. Defaults to None.
        weights (Any, optional): Weights for the model. Defaults to None.
        train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
        **params: Additional parameters.

    Attributes:
        params (Dict[str, Any]): Dictionary of hyperparameters.
        task (str): Name of the task.
        model_name (str): Name of the algorithm (e.g., 'xgboost', 'lightgbm').
        used_features (List[str]): List of selected features based on a specific metric.
        estimator_class (AutoWoE): Class of the model (e.g., LightGBMModel, XGBoostModel).
        estimator (Any): Instance of the trained model.
        categorical_features (List[str]): List of categorical features.
        fitted (bool): Indicates whether the model has been trained. True if trained, False otherwise.
    """

    model_name = "WBAutoML"

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str],
        categorical_features: List[str] = None,
        metric_name=None,
        metric_params=None,
        weights=None,
        train_logger: Optional[logging.Logger] = None,
        **params,
    ):
        super().__init__(
            estimator_params,
            task,
            used_features,
            categorical_features,
            metric_name,
            metric_params,
            weights=weights,
            **params,
            train_logger=train_logger,
        )
        self.estimator_class = self._estimators.get(self.task)

    @property
    def _estimators(self):
        """Dictionary mapping tasks to their respective estimator classes.

        Returns:
            Dict[str, AutoWoE]: Mapping of task names to AutoWoE instances.
        """
        estimators = {
            "binary": AutoWoE(task="BIN", **self.params),
            "regression": AutoWoE(task="REG", **self.params),
        }
        return estimators

    def prepare_dtypes(self, data: pd.DataFrame, target_name: str) -> dict:
        """Prepare data types for model training.

        Args:
            data (pd.DataFrame): Dataset for model training.
            target_name (str): Name of the target variable.

        Returns:
            Dict[str, str]: Dictionary where keys are feature names and values are their types.

        Raises:
            None
        """
        if not self.categorical_features:
            self.categorical_features = {}

        num_features = set(data.columns) - set(self.categorical_features)
        num_features = num_features - set([target_name])

        cat_features = {x: "cat" for x in self.categorical_features}
        num_features = {x: "real" for x in num_features}

        return dict(**num_features, **cat_features)

    def _create_fit_params(self, data: pd.DataFrame, target: pd.Series):
        """Create training parameters in AutoWoE format.

        Args:
            data (pd.DataFrame): Dataset for model training.
            target (pd.Series): Target variable.

        Returns:
            Dict[str, Any]: Dictionary of fit parameters.

        Raises:
            None
        """
        data = self.validate_input_data(data)
        features_type = self.prepare_dtypes(data, target.name)

        params = {
            "features_type": features_type,
            "target_name": target.name,
        }

        return params

    def fit(self, data: pd.DataFrame, target: pd.Series, *eval_set) -> None:
        """Train the model on the provided data and target.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target variable.
            *eval_set: Optional evaluation datasets.

        Returns:
            None

        Raises:
            None
        """
        data = self.validate_input_data(data)
        fit_params = self._create_fit_params(data, target)
        _logger.info(
            f"{time.ctime()}, start fitting WhiteBox AutoML, "
            f"train.shape: {data.shape[0]} rows, {data.shape[1]} cols."
        )
        dtrain = pd.concat([data, target], axis=1)
        self.estimator = self.estimator_class
        self.estimator.fit(train=dtrain, **fit_params)
        self.used_features = self.estimator.features_fit.index.tolist()
        self.fitted = True

    def transform(self, data: pd.DataFrame) -> np.array:
        """Apply the trained model to the provided data.

        The model must be trained beforehand by calling the fit method. If fit is not called, an exception is raised.

        Args:
            data (pd.DataFrame): Feature matrix for making predictions.

        Returns:
            np.array: Array of model predictions.

        Raises:
            ValueError: If the task is not supported.

        """
        if self.task == "binary":
            prediction = self.estimator.predict_proba(data)
        elif self.task == "regression":
            prediction = self.estimator.predict(data)
        else:
            raise ValueError(f"{self.task} task is not supported.")

        return prediction