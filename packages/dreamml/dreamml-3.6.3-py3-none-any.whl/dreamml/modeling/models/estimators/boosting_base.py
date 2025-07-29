import warnings
from abc import abstractmethod
import time
from typing import Any, Tuple, List, Dict, Union

import pandas as pd
from sklearn.exceptions import NotFittedError

from dreamml.logging import get_logger
from dreamml.modeling.models.estimators import BaseModel
from dreamml.modeling.models.estimators._multioutput_wrappers import (
    OneVsRestClassifierWrapper,
)
from dreamml.features.feature_extraction._transformers import LogTargetTransformer

_logger = get_logger(__name__)


class BoostingBaseModel(BaseModel):
    """Base wrapper class for boosting algorithms.

    This class serves as a foundational wrapper for various boosting algorithms,
    providing common functionalities and interfaces for model training and transformation.

    Attributes:
        model_name (str): The name of the boosting algorithm (e.g., 'xgboost', 'lightgbm').
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
        **params,
    ):
        """Initializes the BoostingBaseModel with the given parameters.

        Args:
            estimator_params (Dict[str, Any]): Configuration parameters for the estimator.
            task (str): The name of the task (e.g., 'regression', 'binary', 'multi').
            used_features (List[str], optional): List of features selected based on specific metric values.
                Defaults to None.
            categorical_features (List[str], optional): List of categorical features. Defaults to None.
            metric_name (optional): The name of the metric to be used. Defaults to None.
            metric_params (Dict, optional): Parameters for the metric. Defaults to None.
            weights (optional): Sample weights. Defaults to None.
            target_with_nan_values (bool, optional): Indicates if the target contains NaN values.
                Defaults to False.
            log_target_transformer (LogTargetTransformer, optional): Transformer for log target.
                Defaults to None.
            parallelism (int, optional): Degree of parallelism. Defaults to -1.
            **params: Additional keyword arguments.

        Raises:
            ValueError: If invalid parameters are provided.
        """
        super().__init__(
            estimator_params=estimator_params,
            task=task,
            used_features=used_features,
            categorical_features=categorical_features,
            metric_name=metric_name,
            metric_params=metric_params,
            weights=weights,
            target_with_nan_values=target_with_nan_values,
            log_target_transformer=log_target_transformer,
            parallelism=parallelism,
            **params,
        )

    @abstractmethod
    def fit(self, data, target, *eval_set):
        """Abstract method to train the model on the provided data and target.

        Args:
            data: The input data for training.
            target: The target variable.
            *eval_set: Optional evaluation datasets.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        pass

    @abstractmethod
    def transform(self, data):
        """Abstract method to apply the model to the provided data.

        Args:
            data: The input data to be transformed.

        Returns:
            The transformed data.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        pass

    def _create_eval_set(
        self, data: pd.DataFrame, target: pd.Series, *eval_set, asnumpy: bool = False
    ) -> List[Tuple[pd.DataFrame, pd.Series]]:
        """Creates an evaluation set in sklearn format.

        Args:
            data (pd.DataFrame): The training data.
            target (pd.Series): The target variable for training.
            *eval_set: Optional evaluation datasets.
            asnumpy (bool, optional): Whether to return the evaluation set as NumPy arrays.
                Defaults to False.

        Returns:
            List[Tuple[pd.DataFrame, pd.Series]]: A list of tuples containing evaluation data and targets.

        Raises:
            ValueError: If the input data validation fails.
        """
        data = self.validate_input_data(data)
        if eval_set:
            valid_data = self.validate_input_data(eval_set[0])
            if self.task == "regression" and isinstance(
                self.log_target_transformer, LogTargetTransformer
            ):
                return [
                    (data, target),
                    (valid_data, self.log_target_transformer.transform(eval_set[1])),
                ]
            return [(data, target), (valid_data, eval_set[1])]

        return [(data, target)]

    @staticmethod
    @abstractmethod
    def _get_best_iteration(estimator) -> int:
        """Abstract static method to retrieve the best iteration of the estimator.

        Args:
            estimator: The trained estimator.

        Returns:
            int: The best iteration number.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        raise NotImplementedError

    @property
    def best_iteration(self) -> Union[int, List[int]]:
        """Retrieves the best iteration number of the estimator.

        Returns:
            Union[int, List[int]]: The best iteration number or a list of best iterations for multi-output estimators.
        """
        if isinstance(self.estimator, OneVsRestClassifierWrapper):
            best_iter: List[int] = self.estimator.best_iteration
        else:
            best_iter: int = self._get_best_iteration(self.estimator)

        if best_iter is None:
            best_iter = 0

        return best_iter


class MissedColumnError(IndexError):
    """Exception raised when expected columns are missing in a pandas DataFrame.

    This error is used to identify discrepancies between expected and actual columns in the DataFrame.
    """

    pass