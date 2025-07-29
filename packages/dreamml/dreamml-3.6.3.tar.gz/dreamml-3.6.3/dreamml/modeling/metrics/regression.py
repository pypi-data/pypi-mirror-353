import numpy as np

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_percentage_error,
    mean_absolute_error,
    median_absolute_error,
    r2_score,
    mean_squared_log_error,
)

from dreamml.modeling.metrics._base_metric import BaseMetric, OptimizableMetricMixin
from dreamml.modeling.metrics.metric_functions import (
    symmetric_mean_absolute_percentage_error,
    mean_log_error,
    PyBoostQuantileLoss,
    PyBoostQuantileMetric,
    PyBoostMAPELoss,
    PyBoostMAPEMetric,
    PyBoostMSELoss,
    PyBoostMSEMetric,
)


class RegressionMetric(BaseMetric):
    """Base class for regression metrics.

    Inherits from `BaseMetric` and sets the task type to regression.

    Attributes:
        _task_type (str): The type of task, set to "regression".
    """

    _task_type: str = "regression"

    def __call__(self, y_true, y_pred):
        """Calculate the regression metric.

        Args:
            y_true (array-like): Ground truth target values.
            y_pred (array-like): Estimated target values.

        Returns:
            float: The calculated metric score.

        Raises:
            ValueError: If input arrays cannot be cast to numpy arrays.
        """
        y_true, y_pred = self._cast_to_numpy(y_true, y_pred)

        return self._score_function(y_true, y_pred)


class RMSE(RegressionMetric, OptimizableMetricMixin):
    """Root Mean Squared Error (RMSE) metric.

    Inherits from `RegressionMetric` and `OptimizableMetricMixin`.
    Used to evaluate the standard deviation of the residuals (prediction errors).

    Attributes:
        name (str): The name of the metric, set to "rmse".
        maximize (bool): Indicates whether to maximize the metric, set to False.
    """

    name = "rmse"
    maximize = False

    def _score_function(self, y_true, y_pred):
        """Compute the Root Mean Squared Error.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The RMSE value.
        """
        return mean_squared_error(y_true, y_pred, squared=False)


class MSE(RegressionMetric, OptimizableMetricMixin):
    """Mean Squared Error (MSE) metric.

    Inherits from `RegressionMetric` and `OptimizableMetricMixin`.
    Measures the average of the squares of the errors.

    Attributes:
        name (str): The name of the metric, set to "mse".
        maximize (bool): Indicates whether to maximize the metric, set to False.
    """

    name = "mse"
    maximize = False

    def _score_function(self, y_true, y_pred):
        """Compute the Mean Squared Error.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The MSE value.
        """
        return mean_squared_error(y_true, y_pred, squared=True)

    def _get_pyboost_custom_objective(self):
        """Get the custom objective function for PyBoost.

        Returns:
            PyBoostMSELoss: The custom MSE loss object.
        """
        _objective = PyBoostMSELoss()
        return _objective

    def _get_pyboost_custom_metric(self):
        """Get the custom metric for PyBoost.

        Returns:
            PyBoostMSEMetric: The custom MSE metric object.
        """
        _metric = PyBoostMSEMetric()
        return _metric


class RMSLE(RegressionMetric, OptimizableMetricMixin):
    """Root Mean Squared Logarithmic Error (RMSLE) metric.

    Inherits from `RegressionMetric` and `OptimizableMetricMixin`.
    Measures the square root of the average of squared differences between log-transformed predictions and actual values.

    Attributes:
        name (str): The name of the metric, set to "rmsle".
        maximize (bool): Indicates whether to maximize the metric, set to False.
    """

    maximize = False
    name = "rmsle"

    def _score_function(self, y_true, y_pred):
        """Compute the Root Mean Squared Logarithmic Error.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The RMSLE value.
        """
        return mean_squared_log_error(y_true, y_pred, squared=False)


class MSLE(RegressionMetric):
    """Mean Squared Logarithmic Error (MSLE) metric.

    Inherits from `RegressionMetric`.
    Measures the average of the squares of the differences between log-transformed predictions and actual values.

    Attributes:
        name (str): The name of the metric, set to "msle".
        maximize (bool): Indicates whether to maximize the metric, set to False.
    """

    maximize = False
    name = "msle"

    def _score_function(self, y_true, y_pred):
        """Compute the Mean Squared Logarithmic Error.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The MSLE value.
        """
        return mean_squared_log_error(y_true, y_pred, squared=True)


class MAE(RegressionMetric, OptimizableMetricMixin):
    """Mean Absolute Error (MAE) metric.

    Inherits from `RegressionMetric` and `OptimizableMetricMixin`.
    Measures the average of the absolute differences between predicted and actual values.

    Attributes:
        name (str): The name of the metric, set to "mae".
        maximize (bool): Indicates whether to maximize the metric, set to False.
        _objective (PyBoostQuantileLoss): Custom objective for PyBoost.
        _metric (PyBoostQuantileMetric): Custom metric for PyBoost.
    """

    name = "mae"
    maximize = False

    def _score_function(self, y_true, y_pred):
        """Compute the Mean Absolute Error.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The MAE value.
        """
        return mean_absolute_error(y_true, y_pred)

    def _get_pyboost_custom_objective(self):
        """Get the custom objective function for PyBoost.

        Returns:
            PyBoostQuantileLoss: The custom MAE loss object with alpha=0.5.
        """
        _objective = PyBoostQuantileLoss(alpha=0.5)  # Quantile(alpha=0.5) == MAE
        return _objective

    def _get_pyboost_custom_metric(self):
        """Get the custom metric for PyBoost.

        Returns:
            PyBoostQuantileMetric: The custom MAE metric object with alpha=0.5.
        """
        _metric = PyBoostQuantileMetric(alpha=0.5)  # Quantile(alpha=0.5) == MAE
        return _metric


class MALE(RegressionMetric):
    """Mean Absolute Logarithmic Error (MALE) metric.

    Inherits from `RegressionMetric`.
    Measures the average of the logarithmic differences between predicted and actual values.

    Attributes:
        name (str): The name of the metric, set to "male".
        maximize (bool): Indicates whether to maximize the metric, set to False.
    """

    name = "male"
    maximize = False

    def _score_function(self, y_true, y_pred):
        """Compute the Mean Absolute Logarithmic Error.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The MALE value.
        """
        return mean_log_error(y_true, y_pred)


class MAPE(RegressionMetric, OptimizableMetricMixin):
    """Mean Absolute Percentage Error (MAPE) metric.

    Inherits from `RegressionMetric` and `OptimizableMetricMixin`.
    Measures the average of the absolute percentage differences between predicted and actual values.

    Attributes:
        name (str): The name of the metric, set to "mape".
        maximize (bool): Indicates whether to maximize the metric, set to False.
        multiplier (int): Multiplier applied to the gradient, set to 10.
    """

    name = "mape"
    maximize = False

    multiplier = 10

    def _score_function(self, y_true, y_pred):
        """Compute the Mean Absolute Percentage Error.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The MAPE value.
        """
        return mean_absolute_percentage_error(y_true, y_pred)

    def _get_gradient(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Compute the gradient for MAPE.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            np.ndarray: The gradient array.

        Raises:
            None
        """
        n = len(y_true)
        less = y_pred < y_true
        more = y_pred > y_true

        grad = np.zeros(len(y_true), dtype=y_true.dtype)
        grad[less] = -1.0 * self.multiplier
        grad[more] = 1.0 * self.multiplier

        grad = np.array(grad, dtype=np.float32)
        return grad

    def _get_hessian(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Compute the hessian for MAPE.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            np.ndarray: The hessian array.

        Raises:
            None
        """
        return np.ones(len(y_true), dtype=y_true.dtype)

    def _get_pyboost_custom_objective(self):
        """Get the custom objective function for PyBoost.

        Returns:
            PyBoostMAPELoss: The custom MAPE loss object.
        """
        _objective = PyBoostMAPELoss()
        return _objective

    def _get_pyboost_custom_metric(self):
        """Get the custom metric for PyBoost.

        Returns:
            PyBoostMAPEMetric: The custom MAPE metric object.
        """
        _metric = PyBoostMAPEMetric()
        return _metric


class SMAPE(RegressionMetric):
    """Symmetric Mean Absolute Percentage Error (SMAPE) metric.

    Inherits from `RegressionMetric`.
    Measures the symmetric average of the absolute percentage differences between predicted and actual values.

    Attributes:
        name (str): The name of the metric, set to "smape".
        maximize (bool): Indicates whether to maximize the metric, set to False.
    """

    name = "smape"
    maximize = False

    def _score_function(self, y_true, y_pred):
        """Compute the Symmetric Mean Absolute Percentage Error.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The SMAPE value.
        """
        return symmetric_mean_absolute_percentage_error(y_true, y_pred)


class HuberLoss(RegressionMetric, OptimizableMetricMixin):
    """Huber Loss metric.

    Inherits from `RegressionMetric` and `OptimizableMetricMixin`.
    Combines the properties of MAE and MSE, less sensitive to outliers than MSE.

    Attributes:
        name (str): The name of the metric, set to "huber_loss".
        maximize (bool): Indicates whether to maximize the metric, set to False.
    """

    name = "huber_loss"
    maximize = False

    def _score_function(self, y_true, y_pred):
        """Compute the Huber Loss.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The Huber Loss value.
        """
        return mean_absolute_percentage_error(y_true, y_pred)


class MdAE(RegressionMetric):
    """Median Absolute Error (MdAE) metric.

    Inherits from `RegressionMetric`.
    Measures the median of the absolute differences between predicted and actual values.

    Attributes:
        name (str): The name of the metric, set to "mdae".
        maximize (bool): Indicates whether to maximize the metric, set to False.
    """

    name = "mdae"
    maximize = False

    def _score_function(self, y_true, y_pred):
        """Compute the Median Absolute Error.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The MdAE value.
        """
        return median_absolute_error(y_true, y_pred)


class MdAPE(RegressionMetric):
    """Median Absolute Percentage Error (MdAPE) metric.

    Inherits from `RegressionMetric`.
    Measures the median of the absolute percentage differences between predicted and actual values.

    Attributes:
        name (str): The name of the metric, set to "mdape".
        maximize (bool): Indicates whether to maximize the metric, set to False.
    """

    name = "mdape"
    maximize = False

    def _score_function(self, y_true, y_pred):
        """Compute the Median Absolute Percentage Error.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The MdAPE value.
        """
        return median_absolute_error(np.ones_like(y_true), y_pred / y_true)


class R2(RegressionMetric):
    """R-squared (R2) metric.

    Inherits from `RegressionMetric`.
    Represents the proportion of the variance for the dependent variable that's explained by the independent variables.

    Attributes:
        name (str): The name of the metric, set to "r2".
        maximize (bool): Indicates whether to maximize the metric, set to True.
    """

    name = "r2"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """Compute the R-squared score.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The R2 score.
        """
        return r2_score(y_true, y_pred)


class Quantile(RegressionMetric, OptimizableMetricMixin):
    """Quantile Regression metric.

    Inherits from `RegressionMetric` and `OptimizableMetricMixin`.
    Measures the quantile loss for a specified quantile level.

    Attributes:
        name (str): The name of the metric, set to "quantile".
        maximize (bool): Indicates whether to maximize the metric, set to False.
        alpha (float): The quantile level, set to 0.5 by default.
    """

    name: str = "quantile"  # должно совпадать с "loss_function" в конфиге
    maximize: bool = False

    alpha = 0.5  # пример определения параметра в функции потерь, если требуется для кастомных метрик и лоссов

    def _score_function(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute the Quantile loss.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            float: The Quantile loss value.
        """
        ix = y_true < y_pred
        loss = np.zeros_like(y_pred)
        loss[ix] = (1 - self.alpha) * np.abs(y_true[ix] - y_pred[ix])
        loss[~ix] = self.alpha * np.abs(y_true[~ix] - y_pred[~ix])
        return np.average(loss)

    def _get_gradient(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> np.ndarray:
        """Compute the gradient for Quantile loss.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            np.ndarray: The gradient array.
        """
        ix = y_true < y_pred
        grad = np.zeros_like(y_pred)
        ix_x = y_true[ix] - y_pred[ix]
        not_ix_x = y_true[~ix] - y_pred[~ix]
        grad[ix] = (1 - self.alpha) * ((ix_x >= 0) * ix_x + (ix_x < 0) * ix_x * -1)
        grad[~ix] = (self.alpha) * (
            (not_ix_x >= 0) * not_ix_x + (not_ix_x < 0) * not_ix_x * -1
        )
        return -grad

    def _get_hessian(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> np.ndarray:
        """Compute the hessian for Quantile loss.

        Args:
            y_true (np.ndarray): Ground truth target values.
            y_pred (np.ndarray): Predicted target values.

        Returns:
            np.ndarray: The hessian array.
        """
        ix = y_true < y_pred
        hess = np.zeros_like(y_pred)
        ix_x = y_true[ix] - y_pred[ix]
        not_ix_x = y_true[~ix] - y_pred[~ix]
        hess[ix] = (1 - self.alpha) * ((ix_x >= 0) + (ix_x < 0) * -1)
        hess[~ix] = (self.alpha) * ((not_ix_x >= 0) + (not_ix_x < 0) * -1)
        return hess

    def _get_pyboost_custom_objective(self):
        """Get the custom objective function for PyBoost.

        Returns:
            PyBoostQuantileLoss: The custom Quantile loss object with alpha=0.5.
        """
        _objective = PyBoostQuantileLoss(alpha=0.5)
        return _objective

    def _get_pyboost_custom_metric(self):
        """Get the custom metric for PyBoost.

        Returns:
            PyBoostQuantileMetric: The custom Quantile metric object with alpha=0.5.
        """
        _metric = PyBoostQuantileMetric(alpha=0.5)
        return _metric


class MultiRMSE(RegressionMetric, OptimizableMetricMixin):
    """Multi-target Root Mean Squared Error (MultiRMSE) metric.

    Inherits from `RegressionMetric` and `OptimizableMetricMixin`.
    Computes the RMSE across multiple targets and returns the average RMSE.

    Attributes:
        name (str): The name of the metric, set to "multirmse".
        maximize (bool): Indicates whether to maximize the metric, set to False.
    """

    name = "multirmse"
    maximize = False

    def _score_function(self, y_true, y_pred):
        """Compute the Multi-target Root Mean Squared Error.

        Args:
            y_true (np.ndarray): Ground truth target values with shape (n_samples, n_targets).
            y_pred (np.ndarray): Predicted target values with shape (n_samples, n_targets).

        Returns:
            float: The average RMSE across all targets.
        """
        mse_per_target = np.mean((y_true - y_pred) ** 2, axis=0)
        rmse_per_target = np.sqrt(mse_per_target)

        return np.mean(rmse_per_target)