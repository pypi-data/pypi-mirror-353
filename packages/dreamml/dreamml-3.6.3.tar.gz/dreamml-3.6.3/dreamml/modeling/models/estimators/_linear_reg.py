import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

from sklearn.linear_model import ElasticNet
from dreamml.modeling.models.estimators import BaseModel
from dreamml.features.feature_extraction._transformers import LogTargetTransformer


class LinearRegModel(BaseModel):
    """Linear Regression Model with a standardized API for dreamml_base.

    This model utilizes linear regression with optional log target transformation
    and supports different tasks such as regression and AMTS.

    Attributes:
        model_name (str): The name of the model algorithm.
        params (dict): Dictionary of hyperparameters.
        task (str): The name of the task (e.g., 'regression', 'binary', 'multi').
        used_features (list): List of features selected based on specific metric values.
        estimator_class: The class of the model estimator (e.g., ElasticNet).
        estimator: An instance of the trained model.
        categorical_features (list): List of categorical features.
        fitted (bool): Indicates whether the model has been fitted.
    """

    model_name = "linear_reg"

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
        """Initialize the LinearRegModel.

        Args:
            estimator_params (Dict[str, Any]): Dictionary of hyperparameters for the estimator.
            task (str): The name of the task (e.g., 'regression', 'binary', 'multi').
            used_features (List[str]): List of features selected based on specific metric values.
            categorical_features (List[str]): List of categorical features.
            metric_name: Name of the metric to evaluate.
            metric_params: Parameters for the metric.
            weights: Sample weights (optional).
            target_with_nan_values (bool, optional): Indicates if the target contains NaN values. Defaults to False.
            log_target_transformer (LogTargetTransformer, optional): Transformer for log-transforming the target. Defaults to None.
            parallelism (int, optional): Degree of parallelism. Defaults to -1.
            train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
            **params: Additional parameters.
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
        self.estimator_class = self._estimators.get(self.task, ElasticNet)

    @property
    def _estimators(self):
        """Get the dictionary of sklearn wrappers for linear regression.

        Returns:
            dict: A dictionary where the key is the task name and the value is the corresponding estimator class.
        """
        estimators = {
            "regression": ElasticNet,
        }
        return estimators

    def _create_eval_set(
        self, data: pd.DataFrame, target: pd.Series, *eval_set, asnumpy: bool = False
    ) -> List[Tuple[pd.DataFrame]]:
        """Create evaluation set in sklearn format.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            *eval_set: Optional evaluation sets as tuples of (features, target).
            asnumpy (bool, optional): Whether to convert the evaluation set to numpy arrays. Defaults to False.

        Returns:
            List[Tuple[pd.DataFrame]]: A list of evaluation sets formatted for sklearn.

        Raises:
            ValueError: If the task is unsupported or if the evaluation set format is incorrect.
        """
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

    def fit(self, data, target=None, *eval_set):
        """Train the model on the provided data and target.

        For regression tasks, it fits the model using the provided training data.
        For AMTS tasks, it delegates to the `fit_amts` method.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series, optional): Target vector for training. Defaults to None.
            *eval_set: Optional evaluation sets as tuples of (features, target).

        Raises:
            ValueError: If the task is unsupported or if fitting fails.
        """
        if self.task == "amts":
            self.fit_amts(data)
            return

        data = self._fill_nan_values(data)
        data, eval_set = self._pre_fit(data, *eval_set)
        self.estimator = self.estimator_class()

        if self.task == "regression" and isinstance(
            self.log_target_transformer, LogTargetTransformer
        ):
            target = self.log_target_transformer.fit_transform(target)

        self.estimator.fit(X=data, y=target)
        self.fitted = True

    def fit_amts(self, atms_data: Dict):
        """Train the model on AMTS-specific data.

        Args:
            atms_data (Dict): Dictionary containing AMTS data with keys like "train".

        Raises:
            KeyError: If the required keys are missing in the `atms_data`.
            ValueError: If the data format is incorrect.
        """
        y_train = np.array(atms_data["train"][1])
        X_train = np.array(atms_data["train"][0]["trend"]).reshape(-1, 1)

        self.estimator = self.estimator_class()
        self.estimator.fit(X=X_train, y=y_train)
        self.fitted = True

    def transform(self, data):
        """Apply the trained model to new data to generate predictions.

        The model must be fitted before calling this method.

        Args:
            data (pd.DataFrame): Feature matrix for making predictions.

        Returns:
            np.ndarray: Predictions made by the model.

        Raises:
            AttributeError: If the model has not been fitted.
            ValueError: If the input data is invalid.
        """
        self.check_is_fitted

        if self.task == "regression":
            data = self.validate_input_data(data)
            data = self._fill_nan_values(data)
            prediction = self.estimator.predict(data)
            if isinstance(self.log_target_transformer, LogTargetTransformer):
                prediction = self.log_target_transformer.inverse_transform(prediction)
            return prediction
        elif self.task == "amts":
            X_train = np.array(data["trend"]).reshape(-1, 1)
            prediction = self.estimator.predict(X_train)
            return prediction

    @staticmethod
    def _get_best_iteration(estimator) -> int:
        """Get the best iteration number for the estimator.

        Args:
            estimator: The trained estimator.

        Returns:
            int: The best iteration number.
        """
        return 1

    @property
    def best_iteration(self) -> int:
        """Get the best iteration number.

        Returns:
            int: The best iteration number.
        """
        return 1