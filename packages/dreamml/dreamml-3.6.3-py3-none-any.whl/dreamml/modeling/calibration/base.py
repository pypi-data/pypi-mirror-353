import numpy as np
import pandas as pd

from typing import Callable, Tuple, Iterable, Any, Union

from copy import deepcopy

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics import log_loss, mean_squared_error

from dreamml.modeling.metrics.metrics_mapping import metrics_mapping
from dreamml.modeling.calibration.binary_algorithms import (
    IsotonicCalibration,
    LinearCalibration,
    LogisticCalibration,
    DecisionTreeCalibration,
)
from dreamml.modeling.calibration.multilabel_algorithms import (
    DecisionTreeCalibrationForMultiLabel,
    LogisticCalibrationForMultiLabel,
    IsotonicCalibrationForMultilabel,
    LinearCalibrationForMultilabel,
)
from dreamml.logging import get_logger

_logger = get_logger(__name__)


class Calibration(BaseEstimator, TransformerMixin):
    """
    Calibration interface class providing a unified API to access different calibration implementations.

    This class wraps a given model and applies calibration methods to adjust the model's predictions.
    It supports both binary and multilabel classification tasks with various calibration techniques.

    Attributes:
        model (Callable): The model to be calibrated.
        method (str): The calibration method to use. Defaults to "isotonic".
        is_weighted (bool): Indicates whether to use weighted calibration. Defaults to False.
        used_features (list): List of features selected based on a specific metric. Defaults to None.
        categorical_features (list): List of categorical features used by the model.
        task (str): The type of task determined based on the target variable.

    Args:
        model (Callable): The model to be calibrated. Must support one of the methods: 'predict', 'predict_proba', or 'transform'.
        method (str, optional): The calibration method to use. Defaults to "isotonic".
        is_weighted (bool, optional): Whether to apply weighted calibration. Defaults to False.
        used_features (list, optional): List of features to use for calibration. If None, uses the model's `used_features` attribute.

    Raises:
        AttributeError: If the model does not support the required prediction methods.
    """

    def __init__(
        self,
        model: Callable,
        method: str = "isotonic",
        is_weighted: bool = False,
        used_features: list = None,
    ):
        self.task = None
        if (
            hasattr(model, "predict")
            or hasattr(model, "predict_proba")
            or hasattr(model, "transform")
        ):
            self.model = deepcopy(model)
            self.method = method
            self.is_weighted = is_weighted
            self.used_features = used_features
            if used_features is None:
                self.used_features = getattr(self.model, "used_features", [])
            self.categorical_features = getattr(self.model, "categorical_features", [])
        else:
            raise AttributeError(
                "Model object must support prediction API via"
                " one of the methods: 'predict',"
                " 'predict_proba' or 'transform'"
            )

    def get_task_type(self, y: Union[pd.Series, pd.DataFrame]) -> str:
        """
        Determines the type of task based on the target variable.

        Args:
            y (Union[pd.Series, pd.DataFrame]): The target variable.

        Returns:
            str: The type of task. Can be "binary", "multiclass", or "multilabel".

        Raises:
            ValueError: If the target variable type is unsupported or contains unsupported values.
        """
        if isinstance(y, pd.Series):
            unique_values = y.dropna().nunique()
            task = "binary" if unique_values == 2 else "multiclass"

        elif isinstance(y, pd.DataFrame):
            y_clean = y.dropna()
            if (
                not y_clean.empty
                and y_clean.applymap(lambda x: x in [0, 1]).all().all()
            ):
                task = "multilabel"
            else:
                raise ValueError(
                    f"Task MultiLabel with NaN values in target labels is not supported."
                )
        else:
            raise ValueError(
                f"Expected pd.DataFrame or pd.Series dtype, but got {type(y)}."
            )
        return task

    def get_y_pred(self, x: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """
        Obtains the model's predictions based on the input features.

        Args:
            x (pd.DataFrame): The input features.

        Returns:
            Union[pd.Series, pd.DataFrame]: The model's predictions.

        Raises:
            AttributeError: If the model does not support the required prediction methods.
        """
        is_dreamml_model = (
            True if self.model.__module__.startswith("dreamml.modeling") else False
        )

        x = x[self.used_features] if is_dreamml_model else x

        if hasattr(self.model, "transform"):
            y_pred = self.model.transform(x)

        elif hasattr(self.model, "predict_proba"):
            y_pred = (
                self.model.predict_proba(x)[:, 1]
                if self.task == "binary"
                else self.model.predict_proba(x)
            )

        elif hasattr(self.model, "predict"):
            y_pred = self.model.predict(x)

        else:
            raise AttributeError(
                "Model object must support prediction API via"
                " one of the methods: 'predict',"
                " 'predict_proba' or 'transform'"
            )
        return y_pred

    def fit(self, x: pd.DataFrame, y: Union[pd.Series, pd.DataFrame]) -> None:
        """
        Fits the calibration model based on the input data and target variable.

        Depending on the task type (binary or multilabel), it applies the appropriate calibration method.

        Args:
            x (pd.DataFrame): The input features.
            y (Union[pd.Series, pd.DataFrame]): The target variable.

        Raises:
            ValueError: If the task type is neither binary nor multilabel.
        """
        self.task = self.get_task_type(y)

        if self.task == "binary":
            self._fit_binary(x, y)
        elif self.task == "multilabel":
            self._fit_multilabel(x, y)
        else:
            raise ValueError(
                f"Supports only binary, multilabel tasks, but got {self.task}"
            )

    def _fit_binary(self, x: pd.DataFrame, y: pd.Series) -> None:
        """
        Fits the calibration model for binary classification tasks.

        Applies the specified calibration method to the binary target.

        Args:
            x (pd.DataFrame): The input features.
            y (pd.Series): The binary target variable.

        Raises:
            ValueError: If an unsupported calibration method is specified.
        """
        y_pred = self.get_y_pred(x)

        if self.method == "isotonic":
            self.calibrator = IsotonicCalibration()
            self.calibrator.fit(y_pred, y)

        elif self.method == "logistic":
            self.calibrator = LogisticCalibration()
            self.calibrator.fit(y_pred, y)

        elif self.method == "linear":
            self.calibrator = LinearCalibration(is_weighted=self.is_weighted)
            self.calibrator.fit(y_pred, y)

        elif self.method == "linear-odds":
            self.calibrator = LinearCalibration(
                is_odds=True, is_weighted=self.is_weighted
            )
            self.calibrator.fit(y_pred, y)

        elif self.method == "linear-ln-odds":
            self.calibrator = LinearCalibration(
                is_logit=True, is_weighted=self.is_weighted
            )
            self.calibrator.fit(y_pred, y)

        elif self.method == "logistic-odds":
            self.calibrator = LogisticCalibration(is_odds=True)
            self.calibrator.fit(y_pred, y)

        elif self.method == "logistic-ln-odds":
            self.calibrator = LogisticCalibration(is_logit=True)
            self.calibrator.fit(y_pred, y)

        elif self.method == "dtree":
            self.calibrator = DecisionTreeCalibration(
                self.model,
            )
            self.calibrator.fit(x, y)

        else:
            raise ValueError(f"Unsupported calibration method: {self.method}")

    def _fit_multilabel(self, x: pd.DataFrame, y: pd.DataFrame) -> None:
        """
        Fits the calibration model for multilabel classification tasks.

        Applies the specified calibration method to the multilabel target.

        Args:
            x (pd.DataFrame): The input features.
            y (pd.DataFrame): The multilabel target variable.

        Raises:
            ValueError: If an unsupported calibration method is specified.
        """
        y_pred = self.get_y_pred(x)

        if self.method == "isotonic":
            self.calibrator = IsotonicCalibrationForMultilabel()
            self.calibrator.fit(y_pred, y)

        elif self.method == "dtree-sigmoid":
            check_nan_values(y)
            self.calibrator = DecisionTreeCalibrationForMultiLabel(
                self.model, calib_method="sigmoid"
            )
            self.calibrator.fit(x, y)

        elif self.method == "dtree-isotonic":
            check_nan_values(y)
            self.calibrator = DecisionTreeCalibrationForMultiLabel(
                self.model, calib_method="isotonic"
            )
            self.calibrator.fit(x, y)

        elif self.method == "logistic":
            self.calibrator = LogisticCalibrationForMultiLabel()
            self.calibrator.fit(y_pred, y)

        elif self.method == "logistic-odds":
            self.calibrator = LogisticCalibrationForMultiLabel(is_odds=True)
            self.calibrator.fit(y_pred, y)

        elif self.method == "logistic-ln-odds":
            self.calibrator = LogisticCalibrationForMultiLabel(is_logit=True)
            self.calibrator.fit(y_pred, y)

        elif self.method == "linear":
            self.calibrator = LinearCalibrationForMultilabel(
                is_weighted=self.is_weighted
            )
            self.calibrator.fit(y_pred, y)

        elif self.method == "linear-odds":
            self.calibrator = LinearCalibrationForMultilabel(
                is_odds=True, is_weighted=self.is_weighted
            )
            self.calibrator.fit(y_pred, y)

        elif self.method == "linear-ln-odds":
            self.calibrator = LinearCalibrationForMultilabel(
                is_logit=True, is_weighted=self.is_weighted
            )
            self.calibrator.fit(y_pred, y)

        else:
            raise ValueError(f"Unsupported calibration method: {self.method}")

    def get_equation(self) -> Any:
        """
        Retrieves the calibration equation from the calibrator if available.

        Returns:
            Any: The calibration equation or None if not available.
        """
        if hasattr(self.calibrator, "get_equation"):
            return self.calibrator.get_equation()

    def evaluate(self, **kwargs) -> None:
        """
        Evaluates the calibration performance on provided datasets.

        Calculates and logs Brier and log loss metrics before and after calibration.

        Args:
            **kwargs: Arbitrary keyword arguments where each key is the dataset name and
                      the value is a tuple containing the feature matrix and true labels.
        """
        for ds_name, (x, y) in kwargs.items():
            y_pred = self.get_y_pred(x)
            if (
                self.method in ["dtree-sigmoid", "dtree-isotonic"]
                and self.task == "multilabel"
            ):
                y_calibrated = self.calibrator.transform(x)
            else:
                y_calibrated = self.calibrator.transform(y_pred)

            if self.task in ["multiclass", "multilabel"]:
                y = y.values if isinstance(y, pd.DataFrame) else y
                y_pred = y_pred.values if isinstance(y_pred, pd.DataFrame) else y_pred
                y_calibrated = (
                    y_calibrated.values
                    if isinstance(y_calibrated, pd.DataFrame)
                    else y_calibrated
                )
                brier = np.nanmean(
                    [
                        mean_squared_error(
                            y[~np.isnan(y[:, i]), i], y_pred[~np.isnan(y[:, i]), i]
                        )
                        for i in range(y.shape[1])
                    ]
                )
                brier_calib = np.nanmean(
                    [
                        mean_squared_error(
                            y[~np.isnan(y[:, i]), i],
                            y_calibrated[~np.isnan(y[:, i]), i],
                        )
                        for i in range(y.shape[1])
                    ]
                )
                logloss = np.nanmean(
                    [
                        log_loss(
                            y[~np.isnan(y[:, i]), i],
                            y_pred[~np.isnan(y[:, i]), i],
                            eps=1e-5,
                        )
                        for i in range(y.shape[1])
                    ]
                )
                logloss_calib = np.nanmean(
                    [
                        log_loss(
                            y[~np.isnan(y[:, i]), i],
                            y_calibrated[~np.isnan(y[:, i]), i],
                            eps=1e-5,
                        )
                        for i in range(y.shape[1])
                    ]
                )

            else:
                brier = mean_squared_error(y, y_pred)
                brier_calib = mean_squared_error(y, y_calibrated)
                logloss = log_loss(y, y_pred, eps=1e-5)
                logloss_calib = log_loss(y, y_calibrated, eps=1e-5)

            _logger.info(
                f"{ds_name} \t Brier: {round(brier, 8)} \t "
                f"Brier calibrated: {round(brier_calib, 8)} "
            )
            _logger.info(
                f"{ds_name} \t logloss: {round(logloss, 8)} \t"
                f" logloss calibrated: {round(logloss_calib, 8)} "
            )

    def transform(self, x: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """
        Applies the calibration to the input features and returns calibrated predictions.

        Args:
            x (pd.DataFrame): The input features.

        Returns:
            Union[pd.Series, pd.DataFrame]: The calibrated predictions.
        """
        if (
            self.method in ["dtree-sigmoid", "dtree-isotonic"]
            and self.task == "multilabel"
        ):
            y_calibrated = self.calibrator.transform(x)
        else:
            y_pred = self.get_y_pred(x)
            y_calibrated = self.calibrator.transform(y_pred)

        return y_calibrated

    def evaluate_model(self, reg_metric: bool = False, **eval_sets) -> None:
        """
        Evaluates and logs the model's performance on the provided evaluation sets.

        For binary classification tasks, the GINI coefficient is used.
        For regression tasks, metrics like MAE, R2, and RMSE are used.

        Args:
            reg_metric (bool, optional): Flag indicating whether to use regression metrics. Defaults to False.
            **eval_sets: Arbitrary keyword arguments where each key is the evaluation set name and
                        the value is a tuple containing the feature matrix and true labels.
        """
        metrics_to_eval = {}

        if not reg_metric:
            metrics_to_eval["GINI"] = metrics_mapping["gini"](task=self.task)

        elif reg_metric:
            metrics_to_eval = {
                "MAE": metrics_mapping["mae"](),
                "R2": metrics_mapping["r2"](),
                "RMSE": metrics_mapping["rmse"](),
            }

        for sample in eval_sets:
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

            _logger.info(output_per_sample)


def signal_last(it: Iterable[Any]) -> Iterable[Tuple[bool, Any]]:
    """
    Tracks the last iteration in a loop.

    This function yields each element of the iterable along with a boolean flag indicating
    whether it is the last element.

    Reference:
        https://betterprogramming.pub/is-this-the-last-element-of-my-python-for-loop-784f5ff90bb5

    Args:
        it (Iterable[Any]): Any iterable object.

    Yields:
        Iterable[Tuple[bool, Any]]: A tuple containing a boolean flag and the current element.
            - The flag is True if it's the last element, otherwise False.
            - The second element is the current item from the iterable.
    """
    iterable = iter(it)
    try:
        ret_var = next(iterable)
    except StopIteration:
        return
    for val in iterable:
        yield False, ret_var
        ret_var = val
    yield True, ret_var


def check_nan_values(y_true: pd.DataFrame) -> None:
    """
    Checks for NaN values in the target variable and raises an error if any are found.

    Args:
        y_true (pd.DataFrame): The target variable to check.

    Raises:
        ValueError: If NaN values are present in the target variable.
    """
    if y_true.isna().sum().sum() > 0:
        raise ValueError(
            "Model calibration with NaN values in the target is not supported."
        )


def calculate_macro_score_with_nan_values(
    score_function: Callable,
    y_true: Union[pd.DataFrame, np.ndarray],
    y_pred: Union[pd.DataFrame, np.ndarray],
    eps: float = None,
) -> float:
    """
    Calculates the macro-average score for multilabel classification, handling NaN values.

    This function computes the macro metric across all classes, ignoring any NaN values in the targets.

    Args:
        score_function (Callable): The scoring function to apply.
        y_true (Union[pd.DataFrame, np.ndarray]): The true target values (n_samples, n_classes).
        y_pred (Union[pd.DataFrame, np.ndarray]): The predicted probabilities (n_samples, n_classes).
        eps (float, optional): A small value to avoid numerical issues in certain metrics. Defaults to None.

    Returns:
        float: The macro-averaged metric across all classes.
    """
    y_true = y_true.values if isinstance(y_true, pd.DataFrame) else y_true
    y_pred = y_pred.values if isinstance(y_pred, pd.DataFrame) else y_pred

    metric_list = []
    num_classes = y_true.shape[1]
    mask = ~np.isnan(y_true)

    for class_idx in range(num_classes):
        mask_by_class_idx = mask[:, class_idx]
        y_true_idx_class = y_true[:, class_idx][mask_by_class_idx]
        y_pred_idx_class = y_pred[:, class_idx][mask_by_class_idx]

        if len(np.unique(y_true_idx_class)) == 1:
            continue
        if len(np.unique(y_pred_idx_class)) == 1:
            metric_list.append(0)
            continue
        if eps is not None:
            metric = score_function(
                y_true=y_true_idx_class, y_pred=y_pred_idx_class, eps=eps
            )
        else:
            metric = score_function(y_true=y_true_idx_class, y_pred=y_pred_idx_class)
        metric_list.append(metric)
    return np.mean(metric_list)