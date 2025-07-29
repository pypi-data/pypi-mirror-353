import numpy as np
import pandas as pd
import os

from sklearn.metrics import (
    precision_score,
    recall_score,
    precision_recall_curve,
    auc,
    roc_auc_score,
    roc_curve,
    average_precision_score,
)
from sklearn.metrics._regression import _check_reg_targets, mean_absolute_error
from sklearn.preprocessing import label_binarize
from sklearn.utils import check_consistent_length

try:
    import cupy as cp
except ImportError:
    cp = None

from py_boost.gpu.losses import BCELoss, BCEMetric, Loss, Metric
from py_boost.gpu.losses import auc as pyboost_auc


class PyBoostBCEWithNanLoss(BCELoss):
    """Binary Cross-Entropy Loss with NaN Handling for PyBoost.

    This loss function extends the standard BCE loss by handling NaN values in the target
    labels. It ensures that predictions at positions with NaN targets do not contribute
    to the gradient updates.

    Attributes:
        alias (str): Alias name for the loss function.
        clip_value (float): Minimum and maximum value to clip the target mean to prevent
            division by zero or log of zero.
    """

    alias = "BCE"
    clip_value = 1e-7

    def __init__(self, *args, **kwargs):
        """Initialize the PyBoostBCEWithNanLoss.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super().__init__(*args, **kwargs)

    def base_score(self, y_true):
        """Compute the base score from true labels.

        Args:
            y_true (np.ndarray): True labels.

        Returns:
            cp.ndarray: Base score computed as the log odds of the mean of y_true.
        """
        means = cp.clip(
            cp.nanmean(y_true, axis=0), self.clip_value, 1 - self.clip_value
        )
        return cp.log(means / (1 - means))

    def __get_grad_hess(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Compute the gradient and hessian with NaN handling.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.

        Returns:
            Tuple[cp.ndarray, cp.ndarray]: Gradient and hessian.
        """
        # first, get nan mask for y_true
        mask = cp.isnan(y_true)
        # then, compute loss with any values at nan places just to prevent the exception
        grad, hess = super().get_grad_hess(cp.where(mask, 0, y_true), y_pred)
        # invert mask
        mask = (~mask).astype(cp.float32)
        # multiply grad and hess on inverted mask
        # now grad and hess eq. 0 on NaN points
        # that actually means that prediction on that place sould not be updated
        grad = grad * mask
        hess = hess * mask

        return grad, hess

    def get_grad_hess(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ):
        """Get the gradient and hessian for the loss.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.

        Returns:
            Tuple[cp.ndarray, cp.ndarray]: Gradient and hessian.
        """
        return self.__get_grad_hess(y_true, y_pred)


class PyBoostBCEWithNanMetric(BCEMetric):
    """Binary Cross-Entropy Metric with NaN Handling for PyBoost.

    This metric computes the average BCE over all classes, ignoring NaN values in the target labels.

    Attributes:
        alias (str): Alias name for the metric.
    """

    alias = "logloss"

    def __init__(self, *args, **kwargs):
        """Initialize the PyBoostBCEWithNanMetric.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super(BCEMetric, self).__init__(*args, **kwargs)

    def __call__(self, y_true, y_pred, sample_weight=None):
        """Compute the average BCE metric.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Average BCE metric.
        """
        bces = []
        mask = ~cp.isnan(y_true)

        for i in range(y_true.shape[1]):
            m = mask[:, i]
            w = None if sample_weight is None else sample_weight[:, 0][m]
            bces.append(cp.mean(self.error(y_true[:, i][m], y_pred[:, i][m])).get())

        return np.mean(bces)


class PyBoostNanAuc(Metric):
    """Normalized AUC Metric with NaN Handling for PyBoost.

    Computes the average ROC AUC across multiple classes, ignoring NaN values in the true labels.

    Attributes:
        alias (str): Alias name for the metric.
    """

    alias = "roc_auc_multilabel"

    def __init__(self, *args, **kwargs):
        """Initialize the PyBoostNanAuc.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super().__init__(*args, **kwargs)

    def __call__(self, y_true, y_pred, sample_weight=None):
        """Compute the average ROC AUC metric.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Average ROC AUC.
        """
        aucs = []
        mask = ~cp.isnan(y_true)

        for i in range(y_true.shape[1]):
            m = mask[:, i]
            w = None if sample_weight is None else sample_weight[:, 0][m]
            aucs.append(pyboost_auc(y_true[:, i][m], y_pred[:, i][m], w))

        return np.mean(aucs)

    def compare(self, v0, v1):
        """Compare two metric values.

        Args:
            v0 (float): First value.
            v1 (float): Second value.

        Returns:
            bool: True if v0 is greater than v1, else False.
        """
        return v0 > v1


class PyBoostAucMulticlass(Metric):
    """Multiclass ROC AUC Metric for PyBoost.

    Computes the average ROC AUC across multiple classes in a multiclass setting.

    Attributes:
        alias (str): Alias name for the metric.
    """

    alias = "roc_auc_multiclass"

    def __init__(self, *args, **kwargs):
        """Initialize the PyBoostAucMulticlass.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super().__init__(*args, **kwargs)

    def __call__(self, y_true, y_pred, sample_weight=None):
        """Compute the average multiclass ROC AUC.

        Args:
            y_true (np.ndarray): True class labels.
            y_pred (np.ndarray): Predicted probabilities for each class.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Average multiclass ROC AUC.
        """
        aucs = []
        n_classes = y_pred.shape[1]
        y_true_np = cp.float32(y_true.get())
        y_true_binarized = cp.array(
            label_binarize(y_true_np, classes=np.arange(n_classes))
        )

        for class_idx in range(n_classes):
            w = None if sample_weight is None else sample_weight[:, 0]
            y_true_i = y_true_binarized[:class_idx]
            y_pred_i = y_pred[:class_idx]

            aucs.append(pyboost_auc(y_true_i, y_pred_i, w))
        return np.mean(aucs)

    def compare(self, v0, v1):
        """Compare two metric values.

        Args:
            v0 (float): First value.
            v1 (float): Second value.

        Returns:
            bool: True if v0 is greater than v1, else False.
        """
        return v0 > v1


class PyBoostMAPELoss(Loss):
    """Mean Absolute Percentage Error (MAPE) Loss for PyBoost.

    This loss function computes the MAPE between true and predicted values, scaled by a multiplier.

    Attributes:
        alias (str): Alias name for the loss function.
        multiplier (int): Scaling factor for the gradients.
    """

    alias = "mape"
    multiplier: int = 10

    def __init__(self, *args, **kwargs):
        """Initialize the PyBoostMAPELoss.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super(Loss).__init__(*args, **kwargs)

    def base_score(self, y_true):
        """Compute the base score from true labels.

        Args:
            y_true (np.ndarray): True labels.

        Returns:
            cp.ndarray: Mean of y_true along axis 0.
        """
        return y_true.mean(axis=0)

    def __get_grad_hess(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Compute the gradient and hessian for MAPE loss.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.

        Returns:
            Tuple[cp.ndarray, cp.ndarray]: Gradient and hessian.
        """
        n = len(y_true)
        less = (y_pred < y_true).reshape(-1, 1)
        more = (y_pred > y_true).reshape(-1, 1)

        grad = cp.zeros(len(y_true), dtype=y_true.dtype).reshape(-1, 1)
        grad[less] = -1 * self.multiplier
        grad[more] = 1 * self.multiplier

        grad = cp.array(grad, dtype=cp.float32)
        hess = cp.ones(len(y_true), dtype=y_true.dtype).reshape(-1, 1)

        return grad, hess

    def postprocess_output(self, y_pred):
        """Post-process the output predictions.

        Args:
            y_pred (np.ndarray): Predicted labels.

        Returns:
            np.ndarray: Reshaped predictions.
        """
        return y_pred.reshape(-1, 1)

    def get_grad_hess(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ):
        """Get the gradient and hessian for the loss.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.

        Returns:
            Tuple[cp.ndarray, cp.ndarray]: Gradient and hessian.
        """
        return self.__get_grad_hess(y_true, y_pred)


class PyBoostMAPEMetric(Metric):
    """Mean Absolute Percentage Error (MAPE) Metric for PyBoost.

    This metric computes the average MAPE between true and predicted values.

    Attributes:
        alias (str): Alias name for the metric.
    """

    alias = "mape"

    def __init__(self, *args, **kwargs):
        """Initialize the PyBoostMAPEMetric.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super(Metric, self).__init__(*args, **kwargs)

    def error(self, y_true, y_pred):
        """Calculate the MAPE error.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.

        Returns:
            cp.ndarray: MAPE error for each sample.
        """
        epsilon = cp.finfo(cp.float64).eps
        mape = cp.abs(y_pred - y_true) / cp.maximum(cp.abs(y_true), epsilon)
        output = cp.average(mape, axis=0)
        return output

    def __call__(self, y_true, y_pred, sample_weight=None):
        """Compute the average MAPE metric.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Average MAPE.
        """
        err = self.error(y_true, y_pred)
        return cp.average(err)

    def compare(self, v0, v1):
        """Compare two metric values.

        Args:
            v0 (float): First value.
            v1 (float): Second value.

        Returns:
            bool: True if v0 is less than v1, else False.
        """
        return v0 < v1


class PyBoostQuantileLoss(Loss):
    """Quantile Loss for PyBoost.

    This loss function computes the quantile loss, which is useful for quantile regression.

    Attributes:
        alias (str): Alias name for the loss function.
        alpha (float): Quantile level.
    """

    alias = "quantile"
    alpha: float = 0.5

    def __init__(self, alpha, *args, **kwargs):
        """Initialize the PyBoostQuantileLoss.

        Args:
            alpha (float): Quantile level.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super(Loss).__init__(*args, **kwargs)

        self.alpha = alpha

    def base_score(self, y_true):
        """Compute the base score from true labels.

        Args:
            y_true (np.ndarray): True labels.

        Returns:
            cp.ndarray: Mean of y_true along axis 0.
        """
        return y_true.mean(axis=0)

    def __get_grad_hess(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Compute the gradient and hessian for Quantile loss.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.

        Returns:
            Tuple[cp.ndarray, cp.ndarray]: Gradient and hessian.
        """
        grad = cp.zeros_like(y_pred)
        hess = cp.zeros_like(y_pred)

        ix = y_true < y_pred
        ix_x = y_true[ix] - y_pred[ix]
        not_ix_x = y_true[~ix] - y_pred[~ix]

        grad[ix] = (1 - self.alpha) * ((ix_x >= 0) * ix_x + (ix_x < 0) * ix_x * -1)
        grad[~ix] = (self.alpha) * (
            (not_ix_x >= 0) * not_ix_x + (not_ix_x < 0) * not_ix_x * -1
        )

        hess[ix] = (1 - self.alpha) * ((ix_x >= 0) + (ix_x < 0) * -1)
        hess[~ix] = (self.alpha) * ((not_ix_x >= 0) + (not_ix_x < 0) * -1)

        grad = -1 * cp.array(grad, dtype=cp.float32).reshape(-1, 1)
        hess = cp.array(hess, dtype=cp.float32).reshape(-1, 1)
        return grad, hess

    def postprocess_output(self, y_pred):
        """Post-process the output predictions.

        Args:
            y_pred (np.ndarray): Predicted labels.

        Returns:
            np.ndarray: Reshaped predictions.
        """
        return y_pred.reshape(-1, 1)

    def get_grad_hess(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ):
        """Get the gradient and hessian for the loss.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.

        Returns:
            Tuple[cp.ndarray, cp.ndarray]: Gradient and hessian.
        """
        return self.__get_grad_hess(y_true, y_pred)


class PyBoostQuantileMetric(Metric):
    """Quantile Metric for PyBoost.

    Computes the average quantile loss between true and predicted values.

    Attributes:
        alias (str): Alias name for the metric.
        alpha (float): Quantile level.
    """

    alias = "quantile"
    alpha: float = 0.5

    def __init__(self, alpha, *args, **kwargs):
        """Initialize the PyBoostQuantileMetric.

        Args:
            alpha (float): Quantile level.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super(Metric, self).__init__(*args, **kwargs)

        self.alpha = alpha

    def error(self, y_true, y_pred):
        """Calculate the quantile error.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.

        Returns:
            cp.ndarray: Quantile error for each sample.
        """
        y_pred = y_pred.reshape(-1, 1)
        ix = y_true < y_pred
        loss = cp.zeros_like(y_pred)
        loss[ix] = (1 - self.alpha) * cp.abs(y_true[ix] - y_pred[ix])
        loss[~ix] = self.alpha * cp.abs(y_true[~ix] - y_pred[~ix])
        output = cp.average(loss, axis=0)
        return output

    def postprocess_output(self, y_pred):
        """Post-process the output predictions.

        Args:
            y_pred (np.ndarray): Predicted labels.

        Returns:
            np.ndarray: Reshaped predictions.
        """
        return y_pred.reshape(-1, 1)

    def __call__(self, y_true, y_pred, sample_weight=None):
        """Compute the average quantile metric.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Average quantile loss.
        """
        err = self.error(y_true, y_pred)
        return cp.average(err)

    def compare(self, v0, v1):
        """Compare two metric values.

        Args:
            v0 (float): First value.
            v1 (float): Second value.

        Returns:
            bool: True if v0 is less than v1, else False.
        """
        return v0 < v1


class PyBoostMSELoss(Loss):
    """Mean Squared Error (MSE) Loss for PyBoost.

    This loss function computes the MSE between true and predicted values.

    Attributes:
        alias (str): Alias name for the loss function.
    """

    alias = "mse"

    def __init__(self, *args, **kwargs):
        """Initialize the PyBoostMSELoss.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super(Loss).__init__(*args, **kwargs)

    def base_score(self, y_true):
        """Compute the base score from true labels.

        Args:
            y_true (np.ndarray): True labels.

        Returns:
            cp.ndarray: Mean of y_true along axis 0.
        """
        return y_true.mean(axis=0)

    def __get_grad_hess(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Compute the gradient and hessian for MSE loss.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.

        Returns:
            Tuple[cp.ndarray, cp.ndarray]: Gradient and hessian.
        """
        grad = y_pred - y_true
        hess = cp.ones(len(y_true), dtype=y_true.dtype).reshape(-1, 1)

        return grad, hess

    def postprocess_output(self, y_pred):
        """Post-process the output predictions.

        Args:
            y_pred (np.ndarray): Predicted labels.

        Returns:
            np.ndarray: Reshaped predictions.
        """
        return y_pred.reshape(
            -1,
        )

    def get_grad_hess(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ):
        """Get the gradient and hessian for the loss.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.

        Returns:
            Tuple[cp.ndarray, cp.ndarray]: Gradient and hessian.
        """
        return self.__get_grad_hess(y_true, y_pred)


class PyBoostMSEMetric(Metric):
    """Mean Squared Error (MSE) Metric for PyBoost.

    This metric computes the average MSE between true and predicted values.

    Attributes:
        alias (str): Alias name for the metric.
    """

    alias = "mse"

    def __init__(self, *args, **kwargs):
        """Initialize the PyBoostMSEMetric.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super(Metric, self).__init__(*args, **kwargs)

    def error(self, y_true, y_pred):
        """Calculate the MSE error.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.

        Returns:
            cp.ndarray: MSE error for each sample.
        """
        mse = (y_true - y_pred) ** 2
        output = cp.average(mse, axis=0)
        return output

    def __call__(self, y_true, y_pred, sample_weight=None):
        """Compute the average MSE metric.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Average MSE.
        """
        err = self.error(y_true, y_pred)
        return cp.average(err)

    def compare(self, v0, v1):
        """Compare two metric values.

        Args:
            v0 (float): First value.
            v1 (float): Second value.

        Returns:
            bool: True if v0 is less than v1, else False.
        """
        return v0 < v1


class PyBoostGini(Metric):
    """Gini Coefficient Metric for PyBoost.

    Computes the Gini coefficient based on the ROC AUC across multiple classes, ignoring NaN values.

    Attributes:
        alias (str): Alias name for the metric.
    """

    alias = "gini"

    def __init__(self, *args, **kwargs):
        """Initialize the PyBoostGini.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super().__init__(*args, **kwargs)

    def __call__(self, y_true, y_pred, sample_weight=None):
        """Compute the average Gini coefficient.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Average Gini coefficient.
        """
        aucs = []
        mask = ~cp.isnan(y_true)

        for i in range(y_true.shape[1]):
            m = mask[:, i]
            w = None if sample_weight is None else sample_weight[:, 0][m]
            aucs.append(self.error(y_true[:, i][m], y_pred[:, i][m], w))

        return np.mean(aucs)

    def error(self, y_true, y_pred, sample_weight=None):
        """Calculate the Gini coefficient for a single class.

        Args:
            y_true (np.ndarray): True labels for a class.
            y_pred (np.ndarray): Predicted labels for a class.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Gini coefficient.
        """
        auc = pyboost_auc(y_true, y_pred, sample_weight)
        return 2 * auc - 1

    def compare(self, v0, v1):
        """Compare two metric values.

        Args:
            v0 (float): First value.
            v1 (float): Second value.

        Returns:
            bool: True if v0 is greater than v1, else False.
        """
        return v0 > v1


class PyBoostGiniMulticlass(Metric):
    """Multiclass Gini Coefficient Metric for PyBoost.

    Computes the average Gini coefficient across multiple classes in a multiclass setting.

    Attributes:
        alias (str): Alias name for the metric.
    """

    alias = "gini_multiclass"

    def __init__(self, *args, **kwargs):
        """Initialize the PyBoostGiniMulticlass.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super().__init__(*args, **kwargs)

    def __call__(self, y_true, y_pred, sample_weight=None):
        """Compute the average multiclass Gini coefficient.

        Args:
            y_true (np.ndarray): True class labels.
            y_pred (np.ndarray): Predicted probabilities for each class.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Average multiclass Gini coefficient.
        """
        aucs = []
        n_classes = y_pred.shape[1]
        y_true_np = cp.float32(y_true.get())
        y_true_binarized = cp.array(
            label_binarize(y_true_np, classes=np.arange(n_classes))
        )

        for class_idx in range(n_classes):
            w = None if sample_weight is None else sample_weight[:, 0]
            y_true_i = y_true_binarized[:class_idx]
            y_pred_i = y_pred[:class_idx]
            aucs.append(self.error(y_true_i, y_pred_i, w))

        return np.mean(aucs)

    def error(self, y_true, y_pred, sample_weight=None):
        """Calculate the Gini coefficient for a single class.

        Args:
            y_true (np.ndarray): True labels for a class.
            y_pred (np.ndarray): Predicted labels for a class.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Gini coefficient.
        """
        auc = pyboost_auc(y_true, y_pred, sample_weight)
        return 2 * auc - 1

    def compare(self, v0, v1):
        """Compare two metric values.

        Args:
            v0 (float): First value.
            v1 (float): Second value.

        Returns:
            bool: True if v0 is greater than v1, else False.
        """
        return v0 > v1


class PyBoostPRAUC(Metric):
    """Precision-Recall AUC Metric for PyBoost.

    Computes the average Precision-Recall AUC across multiple classes, ignoring NaN values.

    Attributes:
        alias (str): Alias name for the metric.
    """

    alias = "pr_auc_pyboost"

    def __init__(self, *args, **kwargs):
        """Initialize the PyBoostPRAUC.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super().__init__(*args, **kwargs)

    def __call__(self, y_true, y_pred, sample_weight=None):
        """Compute the average Precision-Recall AUC metric.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted labels.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Average Precision-Recall AUC.
        """
        aucs = []
        mask = ~cp.isnan(y_true)
        y_true_np = cp.asnumpy(cp.float32(y_true.get()))
        y_pred_np = cp.asnumpy(cp.float32(y_pred.get()))

        for i in range(y_true_np.shape[1]):
            m = cp.asnumpy(mask[:, i])
            w = None if sample_weight is None else sample_weight[:, 0][m]
            y_true_i = y_true_np[:, i][m]
            y_pred_i = y_pred_np[:, i][m]

            aucs.append(self.error(y_true_i, y_pred_i, w))

        return np.mean(aucs)

    def error(self, y_true, y_pred, sample_weight=None):
        """Calculate the Precision-Recall AUC for a single class.

        Args:
            y_true (np.ndarray): True labels for a class.
            y_pred (np.ndarray): Predicted labels for a class.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Precision-Recall AUC.
        """
        y_true = cp.array(y_true) if isinstance(y_true, np.ndarray) else y_true
        y_pred = cp.array(y_pred) if isinstance(y_pred, np.ndarray) else y_pred
        auc = pyboost_auc(y_true, y_pred, sample_weight)
        return auc

    def compare(self, v0, v1):
        """Compare two metric values.

        Args:
            v0 (float): First value.
            v1 (float): Second value.

        Returns:
            bool: True if v0 is greater than v1, else False.
        """
        return v0 > v1


class PyBoostPRAUCMulticlass(Metric):
    """Multiclass Precision-Recall AUC Metric for PyBoost.

    Computes the macro-averaged Precision-Recall AUC across multiple classes.

    Attributes:
        alias (str): Alias name for the metric.
    """

    alias = "pr_auc_pyboost_multiclass"

    def __init__(self, *args, **kwargs):
        """Initialize the PyBoostPRAUCMulticlass.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ImportError: If CuPy is not installed.
        """
        if cp is None:
            raise ImportError("cupy is required to use py_boost")

        super().__init__(*args, **kwargs)

    def __call__(self, y_true, y_pred, sample_weight=None):
        """Compute the macro-averaged Precision-Recall AUC.

        Args:
            y_true (np.ndarray): True class labels.
            y_pred (np.ndarray): Predicted probabilities for each class.
            sample_weight (Optional[np.ndarray], optional): Sample weights. Defaults to None.

        Returns:
            float: Macro-averaged Precision-Recall AUC.
        """
        n_classes = y_pred.shape[1]
        y_true_np = cp.float32(y_true.get())
        y_pred_np = cp.float32(y_pred.get())
        y_true_binarized = label_binarize(y_true_np, classes=np.arange(n_classes))
        aps = average_precision_score(y_true_binarized, y_pred_np, average="macro")
        return aps

    def compare(self, v0, v1):
        """Compare two metric values.

        Args:
            v0 (float): First value.
            v1 (float): Second value.

        Returns:
            bool: True if v0 is greater than v1, else False.
        """
        return v0 > v1


def mean_log_error(
    y_true, y_pred, *, sample_weight=None, multioutput="uniform_average", squared=True
):
    """Compute the Mean Log Error between true and predicted values.

    The Mean Log Error is computed by taking the mean absolute error between the logarithm
    of true and predicted values. This metric cannot handle negative values in the targets.

    Args:
        y_true (array-like): True target values.
        y_pred (array-like): Predicted target values.
        sample_weight (Optional[array-like], optional): Sample weights. Defaults to None.
        multioutput (str or array-like, optional): Defines how to aggregate multiple outputs. Defaults to "uniform_average".
        squared (bool, optional): Whether to square the error. Defaults to True.

    Returns:
        float: Mean Log Error.

    Raises:
        ValueError: If any of the target values are negative.
    """
    y_type, y_true, y_pred, multioutput = _check_reg_targets(
        y_true, y_pred, multioutput
    )
    check_consistent_length(y_true, y_pred, sample_weight)

    if (y_true < 0).any() or (y_pred < 0).any():
        raise ValueError(
            "Mean Squared Logarithmic Error cannot be used when "
            "targets contain negative values."
        )

    return mean_absolute_error(
        np.log1p(y_true),
        np.log1p(y_pred),
        sample_weight=sample_weight,
        multioutput=multioutput,
    )


def symmetric_mean_absolute_percentage_error(
    y_true, y_pred, *, sample_weight=None, multioutput="uniform_average"
):
    """Compute the Symmetric Mean Absolute Percentage Error (SMAPE) between true and predicted values.

    SMAPE is a measure of accuracy based on relative absolute error. It is symmetric and bounded.

    Args:
        y_true (array-like): True target values.
        y_pred (array-like): Predicted target values.
        sample_weight (Optional[array-like], optional): Sample weights. Defaults to None.
        multioutput (str or array-like, optional): Defines how to aggregate multiple outputs. Defaults to "uniform_average".

    Returns:
        float: Symmetric Mean Absolute Percentage Error.
    """
    y_type, y_true, y_pred, multioutput = _check_reg_targets(
        y_true, y_pred, multioutput
    )
    check_consistent_length(y_true, y_pred, sample_weight)
    epsilon = np.finfo(np.float64).eps
    mape = np.abs(y_pred - y_true) / np.maximum(np.abs(y_true + y_pred) / 2, epsilon)
    output_errors = np.average(mape, weights=sample_weight, axis=0)
    if isinstance(multioutput, str):
        if multioutput == "raw_values":
            return output_errors
        elif multioutput == "uniform_average":
            # pass None as weights to np.average: uniform mean
            multioutput = None

    return np.average(output_errors, weights=multioutput)


def cut_at_k(y_true, y_pred, at_k):
    """Select the top-k predictions and assign them a score of 1.

    This function extracts the top-k predicted values and sets their corresponding
    true labels to 1, effectively creating a binary relevance vector for the top-k items.

    Args:
        y_true (array-like): True labels, shape [n_samples, ].
        y_pred (array-like): Predicted scores, shape [n_samples, ].
        at_k (int or float): Number of top predictions to select. If float, interpreted as a proportion.

    Returns:
        Tuple[np.ndarray, np.ndarray]: 
            - y_true_new: True labels for the top-k predictions.
            - y_pred_new: Predicted scores for the top-k predictions, all set to 1.
    """
    if at_k < 1:
        at_k = round(at_k * y_pred.shape[0])
    zipped = np.dstack((y_true, y_pred))[0]
    zipped = zipped[np.argsort(zipped[:, 1])][-at_k:, :]
    zipped[:, 1] = 1
    y_true_new = zipped[:, 0]
    y_pred_new = zipped[:, 1]
    return y_true_new, y_pred_new


def recall_at_k_score_(y_true, y_pred, metric_params):
    """Calculate the Recall@K metric.

    Recall@K measures the proportion of relevant items that are present in the top-k predictions.

    Args:
        y_true (array-like): True labels, shape [n_samples, ].
        y_pred (array-like): Predicted scores, shape [n_samples, ].
        metric_params (dict): Parameters containing 'at_k' which specifies the k value.

    Returns:
        float: Recall@K score.
    """
    at_k = metric_params["at_k"]
    if at_k < 1:
        at_k = round(at_k * y_pred.shape[0])
    zipped = np.dstack((y_true, y_pred))[0]
    zipped = zipped[np.argsort(zipped[:, 1])]
    zipped[-at_k:, 1] = 1
    zipped[:-at_k, 1] = 0
    return recall_score(zipped[:, 0], zipped[:, 1])


def precision_at_k_score_(y_true, y_pred, metric_params):
    """Calculate the Precision@K metric.

    Precision@K measures the proportion of top-k predictions that are relevant.

    Args:
        y_true (array-like): True labels, shape [n_samples, ].
        y_pred (array-like): Predicted scores, shape [n_samples, ].
        metric_params (dict): Parameters containing 'at_k' which specifies the k value.

    Returns:
        float: Precision@K score.
    """
    y_true_new, y_pred_new = cut_at_k(y_true, y_pred, metric_params["at_k"])
    return precision_score(y_true_new, y_pred_new)


def gini_at_k_score_(y_true, y_pred, metric_params):
    """Calculate the Gini@K metric.

    Gini@K is derived from the ROC AUC and measures the inequality among values of a frequency distribution.

    Args:
        y_true (array-like): True labels, shape [n_samples, ].
        y_pred (array-like): Predicted scores, shape [n_samples, ].
        metric_params (dict): Parameters containing 'at_k' which specifies the k value.

    Returns:
        float: Gini@K score.
    """
    at_k = metric_params["at_k"]
    if at_k < 1:
        at_k = round(at_k * y_pred.shape[0])
    zipped = np.dstack((y_true, y_pred))[0]
    zipped = zipped[np.argsort(zipped[:, 1])]
    y_true_new = zipped[-at_k:, 0]
    y_pred_new = zipped[-at_k:, 1]
    if y_true_new.sum() == 0:
        result = 0
    else:
        try:
            result = 2 * roc_auc_score(y_true_new, y_pred_new) - 1
        except ValueError:
            result = 1
    return result


def roc_auc_at_k_score_(y_true, y_pred, metric_params):
    """Calculate the ROC AUC@K metric.

    ROC AUC@K measures the Area Under the ROC Curve for the top-k predictions.

    Args:
        y_true (array-like): True labels, shape [n_samples, ].
        y_pred (array-like): Predicted scores, shape [n_samples, ].
        metric_params (dict): Parameters containing 'at_k' which specifies the k value.

    Returns:
        float: ROC AUC@K score.
    """
    at_k = metric_params["at_k"]
    if at_k < 1:
        at_k = round(at_k * y_pred.shape[0])
    zipped = np.dstack((y_true, y_pred))[0]
    zipped = zipped[np.argsort(zipped[:, 1])]
    y_true_new = zipped[-at_k:, 0]
    y_pred_new = zipped[-at_k:, 1]
    if y_true_new.sum() == 0:
        result = 0
    else:
        try:
            result = roc_auc_score(y_true_new, y_pred_new)
        except ValueError:
            result = 1
    return result


def precision_recall_auc_at_k_score_(y_true, y_pred, metric_params):
    """Calculate the Precision-Recall AUC@K metric.

    Precision-Recall AUC@K measures the area under the Precision-Recall curve for the top-k predictions.

    Args:
        y_true (array-like): True labels, shape [n_samples, ].
        y_pred (array-like): Predicted scores, shape [n_samples, ].
        metric_params (dict): Parameters containing 'at_k' which specifies the k value.

    Returns:
        float: Precision-Recall AUC@K score.
    """
    y_true_new, y_pred_new = cut_at_k(y_true, y_pred, metric_params["at_k"])
    precision, recall, _ = precision_recall_curve(y_true_new, y_pred_new)
    return auc(recall, precision)


def sensitivity_specificity_auc_at_k_score_(y_true, y_pred, metric_params):
    """Calculate the Sensitivity-Specificity AUC@K metric.

    This metric measures the area under the Sensitivity-Specificity curve for the top-k predictions.

    Args:
        y_true (array-like): True labels, shape [n_samples, ].
        y_pred (array-like): Predicted scores, shape [n_samples, ].
        metric_params (dict): Parameters containing 'at_k' which specifies the k value.

    Returns:
        float: Sensitivity-Specificity AUC@K score.
    """
    y_true_new, y_pred_new = cut_at_k(y_true, y_pred, metric_params["at_k"])
    try:
        fpr, tpr, _ = roc_curve(y_true_new, y_pred_new)
        result = auc(1 - fpr, tpr)
    except ValueError:
        result = 1
    return result


def precision_at_k_group_avg_score_(y_true, y_pred, metric_params):
    """Calculate the average Precision@K across groups.

    This metric computes Precision@K for each group defined by `group_col` and averages the results.

    Args:
        y_true (array-like): True labels, shape [n_samples, ].
        y_pred (array-like): Predicted scores, shape [n_samples, ].
        metric_params (dict): Parameters containing:
            - 'group_col_dev' (pd.Series): Column for grouping.
            - 'index' (pd.Series): Indices to select from the group column.
            - 'at_k' (int or float): Number of top predictions to select.

    Returns:
        float: Average Precision@K across groups.
    """
    group_col = metric_params["group_col_dev"]
    index = metric_params["index"]
    group_col = group_col.loc[index]
    zipped = np.dstack((y_true, y_pred, group_col))[0]
    zipped = zipped[np.argsort(zipped[:, 2])]
    groups = np.array(
        np.split(zipped[:, :2], np.unique(zipped[:, 2], return_index=True)[1][1:])
    )
    precs = []
    for group in groups:
        precs.append(precision_at_k_score_(group[:, 0], group[:, 1], metric_params))
    return np.mean(precs)


def gini_at_k_group_avg_score_(y_true, y_pred, metric_params):
    """Calculate the average Gini@K across groups.

    This metric computes Gini@K for each group defined by `group_col` and averages the results.

    Args:
        y_true (array-like): True labels, shape [n_samples, ].
        y_pred (array-like): Predicted scores, shape [n_samples, ].
        metric_params (dict): Parameters containing:
            - 'group_col_dev' (pd.Series): Column for grouping.
            - 'index' (pd.Series): Indices to select from the group column.
            - 'at_k' (int or float): Number of top predictions to select.

    Returns:
        float: Average Gini@K across groups.
    """
    group_col = metric_params["group_col_dev"]
    index = metric_params["index"]
    group_col = group_col.loc[index]
    zipped = np.dstack((y_true, y_pred, group_col))[0]
    zipped = zipped[np.argsort(zipped[:, 2])]
    groups = np.array(
        np.split(zipped[:, :2], np.unique(zipped[:, 2], return_index=True)[1][1:])
    )
    precs = []
    for group in groups:
        precs.append(gini_at_k_score_(group[:, 0], group[:, 1], metric_params))
    return np.mean(precs)


def precision_at_k_group_max_score_(y_true, y_pred, metric_params):
    """Calculate the maximum Precision@K across groups.

    For each group defined by `group_col`, selects the top-k predictions and computes Precision@K.

    Args:
        y_true (array-like): True labels, shape [n_samples, ].
        y_pred (array-like): Predicted scores, shape [n_samples, ].
        metric_params (dict): Parameters containing:
            - 'group_col_dev' (pd.Series): Column for grouping.
            - 'index' (pd.Series): Indices to select from the group column.
            - 'at_k' (int or float): Number of top predictions to select.

    Returns:
        float: Maximum Precision@K across groups.
    """
    at_k = metric_params["at_k"]
    group_col = metric_params["group_col_dev"]
    index = metric_params["index"]
    group_col = group_col.loc[index]
    zipped = np.dstack((y_true, y_pred, group_col))[0]
    zipped = zipped[np.argsort(zipped[:, 2])]
    groups = np.array(
        np.split(zipped[:, :2], np.unique(zipped[:, 2], return_index=True)[1][1:])
    )
    if at_k < 1:
        at_k = round(at_k * y_pred.shape[0])
    trues = []
    for group in groups:
        trues.append(group[np.argsort(group[:, -1])][-at_k:, :][:, 0])
    trues = np.array(
        [el for sublist in trues for el in sublist]
    )  # only true labels for top-k
    return precision_score(trues, [1] * len(trues))


def gini_at_k_group_max_score_(y_true, y_pred, metric_params):
    """Calculate the maximum Gini@K across groups.

    For each group defined by `group_col`, selects the top-k predictions and computes Gini@K.

    Args:
        y_true (array-like): True labels, shape [n_samples, ].
        y_pred (array-like): Predicted scores, shape [n_samples, ].
        metric_params (dict): Parameters containing:
            - 'group_col_dev' (pd.Series): Column for grouping.
            - 'index' (pd.Series): Indices to select from the group column.
            - 'at_k' (int or float): Number of top predictions to select.

    Returns:
        float: Maximum Gini@K across groups.
    """
    at_k = metric_params["at_k"]
    group_col = metric_params["group_col_dev"]
    index = metric_params["index"]
    group_col = group_col.loc[index]
    zipped = np.dstack((y_true, y_pred, group_col))[0]
    zipped = zipped[np.argsort(zipped[:, 2])]
    groups = np.array(
        np.split(zipped[:, :2], np.unique(zipped[:, 2], return_index=True)[1][1:])
    )
    if at_k < 1:
        at_k = round(at_k * y_pred.shape[0])
    trues = []
    scores = []
    for group in groups:
        trues.append(group[np.argsort(group[:, -1])][-at_k:, :][:, 0])
        scores.append(group[np.argsort(group[:, -1])][-at_k:, :][:, 1])
    trues = np.array([el for sublist in trues for el in sublist])
    scores = np.array([el for sublist in scores for el in sublist])
    if trues.sum() == 0:
        result = 0
    else:
        try:
            result = 2 * roc_auc_score(trues, scores) - 1
        except ValueError:
            result = 1
    return result


def custom_metric_score_(y_true, y_pred, metric_params):
    """Calculate a custom metric based on a user-defined function.

    This function allows the use of any custom metric function provided by the user.

    Args:
        y_true (array-like): True labels.
        y_pred (array-like): Predicted labels.
        metric_params (dict): Parameters containing 'custom_metric' which is the custom function.

    Returns:
        float: Result of the custom metric function.
    """
    metric = metric_params["custom_metric"]
    return metric(y_true, y_pred)