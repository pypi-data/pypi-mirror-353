import warnings
from abc import ABC, abstractmethod
from collections.abc import Sequence
from functools import partial
from typing import Dict, Any, List, Optional, Union, Tuple

import numpy as np
import pandas as pd

from dreamml.logging import get_logger
from dreamml.modeling.metrics._custom_factory import (
    _xgboost_custom_objective_factory,
    _xgboost_custom_metric_factory,
    _CatBoostCustomMetricFactory,
    _CatboostCustomObjective,
    _CatboostCustomMultiObjective,
    _pyboost_custom_objective_factory,
    _pyboost_custom_metric_factory,
    _lightgbm_custom_metric_factory,
    _lightgbm_custom_objective_factory,
    _CatBoostMultiTargetMetricFactory,
)
from dreamml.modeling.metrics.names_mapping import (
    metric_name_mapping,
    objective_name_mapping,
)
from dreamml.utils.warnings import DMLWarning

_logger = get_logger(__name__)


class BaseMetric(ABC):
    """Abstract base class for defining evaluation metrics.

    This class provides a foundation for creating custom metrics, including methods
    for converting inputs to NumPy arrays, retrieving model-specific metric and
    objective functions, and handling optimization properties.

    Attributes:
        name (str): The name of the metric.
        maximize (bool): Indicates whether the metric should be maximized.
        params (Dict[str, Any]): Additional parameters for the metric.
        _is_resetting_indexes_required (bool): Flag indicating if resetting indexes is required.
        _is_optimizable (bool): Flag indicating if the metric is optimizable.
        _data_indexes (Dict[str, Sequence]): Data indexes associated with the metric.
        _required_columns (List[str]): List of required columns for the metric.
        _task_type (str): The type of task (e.g., regression, classification).
    """

    name: str
    maximize: bool
    params: Dict[str, Any]
    _is_resetting_indexes_required: bool
    _is_optimizable: bool
    _data_indexes: Dict[str, Sequence]
    _required_columns: List[str]
    _task_type: str

    def __init__(
        self,
        model_name: Optional[str] = None,
        task: Optional[str] = None,
        target_with_nan_values: bool = False,
        **params,
    ):
        """Initializes the BaseMetric.

        Args:
            model_name (Optional[str]): The name of the model. Defaults to None.
            task (Optional[str]): The type of task (e.g., regression, classification). Defaults to None.
            target_with_nan_values (bool): Indicates if the target contains NaN values. Defaults to False.
            **params: Additional keyword arguments for the metric.
        """
        self.params: Dict[str, Any] = params
        self._model_name = model_name.lower() if model_name is not None else None
        self._task = task
        self._target_with_nan_values = target_with_nan_values

    @staticmethod
    def _cast_to_numpy(
        y_true: Union[pd.DataFrame, np.ndarray], y_pred: Union[pd.DataFrame, np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Converts input data to NumPy arrays.

        Args:
            y_true (Union[pd.DataFrame, np.ndarray]): The true target values.
            y_pred (Union[pd.DataFrame, np.ndarray]): The predicted target values.

        Returns:
            Tuple[np.ndarray, np.ndarray]: A tuple containing the converted true and predicted values.
        """
        y_true = (
            y_true.values if isinstance(y_true, (pd.DataFrame, pd.Series)) else y_true
        )
        y_pred = (
            y_pred.values if isinstance(y_pred, (pd.DataFrame, pd.Series)) else y_pred
        )
        return y_true, y_pred

    def get_model_metric(self):
        """Retrieves the metric function specific to the model.

        Raises:
            ValueError: If the model_name is not specified.
            NotImplementedError: If the metric is not implemented for the specified model.

        Returns:
            Union[str, Callable]: The model-specific metric name or a custom metric function.
        """
        if self._model_name is None:
            raise ValueError(
                f"Metic has to be initialized with `model_name` parameter."
            )

        if self._model_name in [
            "amts",
            "prophet",
            "linear_reg",
            "log_reg",
            "ae",
            "vae",
            "iforest",
        ]:
            return self

        implemented_name = metric_name_mapping.get(self.name, {}).get(
            self._model_name, None
        )
        if isinstance(implemented_name, Dict):
            implemented_name = implemented_name.get(self._task, None)

        if implemented_name is not None:
            return implemented_name

        if self._model_name == "catboost":
            implemented_func = self._get_catboost_custom_metric()
        elif self._model_name == "lightgbm":
            implemented_func = self._get_lightgbm_custom_metric()
        elif self._model_name == "xgboost":
            implemented_func = self._get_xgboost_custom_metric()
        elif self._model_name == "pyboost":
            implemented_func = self._get_pyboost_custom_metric()
        else:
            implemented_func = None

        if implemented_func is not None:
            _logger.warning(
                f"Warning! Metric {self.name} is not implemented in {self._model_name}. "
                f"Custom metrics may experience speed reductions due to lack of optimization."
            )
            return implemented_func
        else:
            raise NotImplementedError(
                f"Metric {self.name} is not implemented for {self._model_name} model."
            )

    def get_model_objective(self):
        """Retrieves the objective function specific to the model.

        Raises:
            TypeError: If the metric is not optimizable or if model_name/task is not specified.
            NotImplementedError: If the objective is not implemented for the specified model.

        Returns:
            Union[str, Callable]: The model-specific objective name or a custom objective function.
        """
        if not self.is_optimizable:
            raise TypeError(
                f"Metic {self.__class__.__name__} is not optimizable and can't be used as an objective."
            )

        if self._model_name in [
            "amts",
            "prophet",
            "linear_reg",
            "log_reg",
            "ae",
            "vae",
            "iforest",
        ]:
            return self

        if self._model_name is None:
            raise TypeError(
                f"Metic can't be optimized without specifying `model_name`."
            )

        if self.name == "logloss" and self._task is None:
            raise TypeError(f"`task` needs to be specified for logloss.")

        if self._model_name == "catboost":
            implemented_name = self._get_catboost_objective_name()
        elif self._model_name == "lightgbm":
            implemented_name = self._get_lightgbm_objective_name()
        elif self._model_name == "xgboost":
            implemented_name = self._get_xgboost_objective_name()
        elif self._model_name == "pyboost":
            implemented_name = self._get_pyboost_objective_name()
        elif self._model_name in ("lda", "ensembelda", "bertopic"):
            implemented_name = self._get_topic_modeling_objective_name()
        elif self._model_name == "nbeats_revin":
            implemented_name = self._get_mbeats_revin_objective_name()
        else:
            implemented_name = None

        if implemented_name is not None:
            return implemented_name

        if self._model_name == "catboost":
            implemented_func = self._get_catboost_custom_objective()
        elif self._model_name == "lightgbm":
            implemented_func = self._get_lightgbm_custom_objective()
        elif self._model_name == "xgboost":
            implemented_func = self._get_xgboost_custom_objective()
        elif self._model_name == "pyboost":
            implemented_func = self._get_pyboost_custom_objective()
        else:
            implemented_func = None

        if implemented_func is not None:
            _logger.warning(
                f"Warning! Loss function {self.name} is not implemented in {self._model_name}. "
                f"Custom loss functions may experience speed reductions due to lack of optimization."
            )
            return implemented_func
        else:
            raise NotImplementedError(
                f"Objective {self.name} is not implemented for {self._model_name} model."
            )

    @property
    def is_resetting_indexes_required(self) -> bool:
        """Indicates whether resetting indexes is required.

        Returns:
            bool: True if resetting indexes is required, False otherwise.
        """
        return getattr(self, "_is_resetting_indexes_required", False)

    @property
    def is_optimizable(self) -> bool:
        """Indicates whether the metric is optimizable.

        Returns:
            bool: True if the metric is optimizable, False otherwise.
        """
        return getattr(self, "_is_optimizable", False)

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the metric.

        Raises:
            NotImplementedError: If the property is not implemented in the subclass.

        Returns:
            str: The name of the metric.
        """
        raise NotImplementedError

    @property
    def task_type(self) -> str:
        """The type of task associated with the metric.

        Returns:
            str: The task type.
        """
        return self._task_type

    @property
    @abstractmethod
    def maximize(self) -> bool:
        """Indicates whether the metric should be maximized.

        Raises:
            NotImplementedError: If the property is not implemented in the subclass.

        Returns:
            bool: True if the metric should be maximized, False otherwise.
        """
        raise NotImplementedError

    def __call__(self, y_true, y_pred):
        """Evaluates the metric on the given true and predicted values.

        Args:
            y_true (Union[pd.DataFrame, np.ndarray]): The true target values.
            y_pred (Union[pd.DataFrame, np.ndarray]): The predicted target values.

        Returns:
            float: The computed metric score.
        """
        return self._score_function(y_true, y_pred)

    @abstractmethod
    def _score_function(self, y_true, y_pred):
        """Computes the metric score.

        Args:
            y_true (Union[pd.DataFrame, np.ndarray]): The true target values.
            y_pred (Union[pd.DataFrame, np.ndarray]): The predicted target values.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.

        Returns:
            float: The computed metric score.
        """
        raise NotImplementedError

    def _get_pyboost_custom_metric(self):
        """Retrieves the custom metric function for PyBoost.

        Raises:
            NotImplementedError: Always, since the metric is not implemented for PyBoost.

        Returns:
            None: This method does not return a value.
        """
        raise NotImplementedError(
            f"Metric {self.name} for PyBoost is not implemented, please choose another one."
        )

    def _get_catboost_custom_metric(self):
        """Retrieves the custom metric function for CatBoost.

        Returns:
            Union[_CatBoostMultiTargetMetricFactory, _CatBoostCustomMetricFactory]: The CatBoost custom metric factory.
        """
        if self._task == "multilabel":
            return _CatBoostMultiTargetMetricFactory(_custom_metric_parent=self)
        return _CatBoostCustomMetricFactory(_custom_metric_parent=self)

    def _get_xgboost_custom_metric(self):
        """Retrieves the custom metric function for XGBoost.

        Issues a warning if the metric is set to be maximized and returns a partially applied
        custom metric function.

        Raises:
            DMLWarning: If the metric with maximize=True is used due to potential speed issues.

        Returns:
            Callable: The custom metric function for XGBoost.
        """
        if self.maximize:
            warnings.warn(
                f"Warning! Metric {self.name} is not implemented in XGBoost. "
                f"For metrics with maximize=True, XGBoost currently performs suboptimally due to inherent limitations.\n"
                "Unlike the scoring parameter commonly used in scikit-learn, "
                "when a callable object is provided, it’s assumed to be a cost function "
                "and by default XGBoost will minimize the result during early stopping.",
                DMLWarning,
                stacklevel=2,
            )

        func = partial(_xgboost_custom_metric_factory, self)

        # AttributeError: 'functools.partial' object has no attribute '__name__'
        func.__name__ = self.name
        return func

    def _get_lightgbm_custom_metric(self):
        """Retrieves the custom metric function for LightGBM.

        Returns:
            Callable: The custom metric function for LightGBM.
        """
        func = partial(_lightgbm_custom_metric_factory, self)
        return func


class CustomMetricMixin:
    """Mixin class providing additional functionalities for custom metrics.

    This mixin adds capabilities to handle index resetting and required columns for custom metrics.

    Attributes:
        _is_resetting_indexes_required (bool): Indicates if resetting indexes is required.
        _data_indexes (Dict[str, Sequence]): Data indexes associated with the metric.
        _required_columns (List[str]): List of required columns for the metric.
    """

    _is_resetting_indexes_required: bool = True
    _data_indexes: Dict[str, Sequence]
    _required_columns: List[str]

    def set_indexes(self, **new_indexes):
        """Sets new data indexes for the metric.

        Args:
            **new_indexes: Key-value pairs representing the new indexes.
        """
        self._data_indexes = new_indexes

    @property
    def required_columns(self) -> Optional[List[str]]:
        """Retrieves the list of required columns for the metric.

        Returns:
            Optional[List[str]]: The list of required columns if defined, else None.
        """
        if hasattr(self, "_required_columns"):
            return self._required_columns
        else:
            return None


class OptimizableMetricMixin:
    """Mixin class providing functionalities for optimizable metrics.

    This mixin adds methods to compute gradients and Hessians, and to retrieve
    model-specific objective names and functions for various machine learning frameworks.

    Attributes:
        _is_optimizable (bool): Indicates if the metric is optimizable.
        _task (str): The type of task (e.g., regression, classification).
        name (str): The name of the metric.
    """

    _is_optimizable: bool = True
    _task: str
    name: str

    def _get_gradient(self, y_true, y_pred):
        """Computes the gradient for the metric.

        Args:
            y_true (Union[pd.DataFrame, np.ndarray]): The true target values.
            y_pred (Union[pd.DataFrame, np.ndarray]): The predicted target values.

        Raises:
            NotImplementedError: If the gradient computation is not implemented.

        Returns:
            Any: The computed gradient.
        """
        raise NotImplementedError(
            f"Gradient function for {self.name} metric is not implemented"
        )

    def _get_hessian(self, y_true, y_pred):
        """Computes the Hessian for the metric.

        Args:
            y_true (Union[pd.DataFrame, np.ndarray]): The true target values.
            y_pred (Union[pd.DataFrame, np.ndarray]): The predicted target values.

        Raises:
            NotImplementedError: If the Hessian computation is not implemented.

        Returns:
            Any: The computed Hessian.
        """
        raise NotImplementedError(
            f"Hessian function for {self.name} metric is not implemented"
        )

    def _get_catboost_objective_name(self) -> Optional[str]:
        """Retrieves the CatBoost-specific objective name for the metric.

        Returns:
            Optional[str]: The CatBoost objective name if available, else None.
        """
        key = self.name if self.name != "logloss" else f"{self._task}_logloss"
        name = objective_name_mapping.get(key, {}).get("catboost")
        return name

    def _get_catboost_custom_objective(self):
        """Retrieves the custom objective function for CatBoost.

        Raises:
            NotImplementedError: If the task type is unsupported for custom objectives in CatBoost.

        Returns:
            Union[_CatboostCustomObjective, _CatboostCustomMultiObjective]: The CatBoost custom objective.
        """
        if self._task in ["regression", "timeseries"]:
            return _CatboostCustomObjective(self)

        elif self._task in ["binary", "multiclass", "multilabel"]:
            return _CatboostCustomMultiObjective(self)

        else:
            raise NotImplementedError(
                f"CatBoost custom objectives are not implemented for {self._task}. Remove CatBoost from the pipeline.model_list."
            )

    def _get_xgboost_objective_name(self) -> Optional[str]:
        """Retrieves the XGBoost-specific objective name for the metric.

        Returns:
            Optional[str]: The XGBoost objective name if available, else None.
        """
        key = self.name if self.name != "logloss" else f"{self._task}_logloss"
        name = objective_name_mapping.get(key, {}).get("xgboost")
        return name

    def _get_xgboost_custom_objective(self):
        """Retrieves the custom objective function for XGBoost.

        Returns:
            Callable: The custom objective function for XGBoost.
        """
        func = partial(_xgboost_custom_objective_factory, self)

        # AttributeError: 'functools.partial' object has no attribute '__name__'
        func.__name__ = self.name
        return func

    def _get_pyboost_objective_name(self) -> Optional[str]:
        """Retrieves the PyBoost-specific objective name for the metric.

        Returns:
            Optional[str]: The PyBoost objective name if available and applicable, else None.
        """
        if self._task == "multilabel":
            return None
        key = self.name if self.name != "logloss" else f"{self._task}_logloss"
        name = objective_name_mapping.get(key, {}).get("pyboost")
        return name

    def _get_pyboost_custom_objective(self):
        """Retrieves the custom objective function for PyBoost.

        Raises:
            NotImplementedError: Always, since the objective is not implemented for PyBoost.

        Returns:
            None: This method does not return a value.
        """
        raise NotImplementedError(
            f"Loss {self.name} for PyBoost is not implemented, please choose another one."
        )

    def _get_lightgbm_objective_name(self) -> Optional[str]:
        """Retrieves the LightGBM-specific objective name for the metric.

        Returns:
            Optional[str]: The LightGBM objective name if available, else None.
        """
        key = self.name if self.name != "logloss" else f"{self._task}_logloss"
        name = objective_name_mapping.get(key, {}).get("lightgbm")
        return name

    def _get_lightgbm_custom_objective(self):
        """Retrieves the custom objective function for LightGBM.

        Returns:
            Callable: The custom objective function for LightGBM.
        """
        func = partial(_lightgbm_custom_objective_factory, self)
        return func

    def _get_topic_modeling_objective_name(self) -> Optional[str]:
        """Retrieves the topic modeling-specific objective name for the metric.

        Returns:
            Optional[str]: The topic modeling objective name if available, else None.
        """
        key = self.name
        name = objective_name_mapping.get(key, {}).get("lda")
        return name

    def _get_mbeats_revin_objective_name(self) -> Optional[str]:
        """Retrieves the MBEATS RevIN-specific objective name for the metric.

        Returns:
            Optional[str]: The MBEATS RevIN objective name if available, else None.
        """
        key = self.name
        name = objective_name_mapping.get(key, {}).get("nbeats_revin")
        return name