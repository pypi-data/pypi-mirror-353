import numpy as np
from catboost import MultiTargetCustomMetric


def _lightgbm_custom_metric_factory(self, y_true, y_pred):
    """Creates a custom metric for LightGBM.

    Computes the metric name, the score result, and whether maximizing the metric is optimal.

    Args:
        y_true (array-like): True labels.
        y_pred (array-like): Predicted labels.

    Returns:
        tuple: A tuple containing:
            - name (str): The name of the metric.
            - result (float): The computed metric value.
            - maximize (bool): Whether a higher metric value is better.

    Raises:
        Exception: If the score function fails.
    """
    result = self._score_function(y_true, y_pred)

    return self.name, result, self.maximize


def _lightgbm_custom_objective_factory(self, y_true, y_pred):
    """Creates a custom objective for LightGBM.

    Computes the gradient and Hessian for the custom objective function.

    Args:
        y_true (array-like): True labels.
        y_pred (array-like): Predicted labels.

    Returns:
        tuple: A tuple containing:
            - grad (array-like): Gradient values.
            - hess (array-like): Hessian values.

    Raises:
        Exception: If gradient or Hessian computation fails.
    """
    grad = self._get_gradient(y_true, y_pred)
    hess = self._get_hessian(y_true, y_pred)

    return grad, hess


def _pyboost_custom_metric_factory(self, y_true, y_pred):
    """Creates a custom metric for PyBoost.

    Computes the metric name, the score result, and whether maximizing the metric is optimal.

    Args:
        y_true (array-like): True labels.
        y_pred (array-like): Predicted labels.

    Returns:
        tuple: A tuple containing:
            - name (str): The name of the metric.
            - result (float): The computed metric value.
            - maximize (bool): Whether a higher metric value is better.

    Raises:
        Exception: If the score function fails.
    """
    result = self._score_function(y_true, y_pred)

    return self.name, result, self.maximize


def _pyboost_custom_objective_factory(self, y_true, y_pred):
    """Creates a custom objective for PyBoost.

    Computes the gradient and Hessian for the custom objective function.

    Args:
        y_true (array-like): True labels.
        y_pred (array-like): Predicted labels.

    Returns:
        tuple: A tuple containing:
            - grad (array-like): Gradient values.
            - hess (array-like): Hessian values.

    Raises:
        Exception: If gradient or Hessian computation fails.
    """
    grad, hess = self._get_gradient(
        y_true, y_pred
    )  # grad and hess is computed in pyboost get_grad_hess method together
    return grad, hess


def _xgboost_custom_metric_factory(self, y_true, y_pred):
    """Creates a custom metric for XGBoost.

    Computes the metric result, adjusting true labels for multilabel tasks if necessary.

    Args:
        y_true (array-like): True labels.
        y_pred (array-like): Predicted labels.

    Returns:
        float: The computed metric value.

    Raises:
        AssertionError: If the length of y_true does not match y_pred for multilabel tasks.
        Exception: If the score function fails.
    """
    if self._task == "multilabel":
        y_true = y_true.reshape(y_pred.shape[0], -1)

    result = self._score_function(y_true, y_pred)

    return result


def _xgboost_custom_objective_factory(self, y_true, y_pred):
    """Creates a custom objective for XGBoost.

    Computes the gradient and Hessian for the custom objective function.

    Args:
        y_true (array-like): True labels.
        y_pred (array-like): Predicted labels.

    Returns:
        tuple: A tuple containing:
            - grad (array-like): Gradient values.
            - hess (array-like): Hessian values.

    Raises:
        Exception: If gradient or Hessian computation fails.
    """
    grad = self._get_gradient(y_true, y_pred)
    hess = self._get_hessian(y_true, y_pred)

    return grad, hess


class _CatBoostCustomMetricFactory:
    """Factory class for creating custom metrics in CatBoost.

    Attributes:
        _custom_metric_parent: The parent object containing metric configuration.
    """

    def __init__(self, *args, _custom_metric_parent=None, **kwargs):
        """Initializes the _CatBoostCustomMetricFactory.

        Args:
            *args: Variable length argument list.
            _custom_metric_parent: The parent metric configuration object.
            **kwargs: Arbitrary keyword arguments.
        """
        self._custom_metric_parent = _custom_metric_parent

    def __repr__(self):
        """Returns the official string representation of the object.

        Returns:
            str: The string representation.
        """
        return f"{self.__class__}: {self._custom_metric_parent.name}"

    def __str__(self):
        """Returns the informal string representation of the object.

        Returns:
            str: The string representation.
        """
        return f"{self.__class__}: {self._custom_metric_parent.name}"

    def is_max_optimal(self):
        """Determines if maximizing the metric is optimal.

        Returns:
            bool: True if higher metric values are better, False otherwise.
        """
        return self._custom_metric_parent.maximize

    def evaluate(self, approxes, target, weight):
        """Evaluates the custom metric.

        Args:
            approxes (list-like): Predicted approximations.
            target (array-like): True target values.
            weight (array-like, optional): Sample weights.

        Returns:
            tuple: A tuple containing:
                - result (float): The computed metric value.
                - weight_sum (float): The sum of weights.

        Raises:
            AssertionError: If the length of target does not match approximations.
            Exception: If the score function fails.
        """
        assert len(target) == len(approxes[0])
        if self._custom_metric_parent._task == "binary":
            approxes = approxes[0]
        else:
            approxes = np.array(approxes).T
        # weight parameter can be None.
        # Returns pair (error, weights sum)
        result = self._custom_metric_parent._score_function(target, approxes)
        return result, 0

    def get_final_error(self, error, weight):
        """Retrieves the final error from evaluation.

        Args:
            error (float): The preliminary error value.
            weight (float): The weight associated with the error.

        Returns:
            float: The final error value.
        """
        return error


class _CatBoostMultiTargetMetricFactory(MultiTargetCustomMetric):
    """Factory class for creating multi-target custom metrics in CatBoost.

    Inherits from MultiTargetCustomMetric.

    Attributes:
        _custom_metric_parent: The parent object containing metric configuration.
    """

    def __init__(self, *args, _custom_metric_parent=None, **kwargs):
        """Initializes the _CatBoostMultiTargetMetricFactory.

        Args:
            *args: Variable length argument list.
            _custom_metric_parent: The parent metric configuration object.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self._custom_metric_parent = _custom_metric_parent

    def __repr__(self):
        """Returns the official string representation of the object.

        Returns:
            str: The string representation.
        """
        return f"{self.__class__}: {self._custom_metric_parent.name}"

    def __str__(self):
        """Returns the informal string representation of the object.

        Returns:
            str: The string representation.
        """
        return f"{self.__class__}: {self._custom_metric_parent.name}"

    def get_final_error(self, error, weight):
        """Retrieves the final error from evaluation.

        Args:
            error (float): The cumulative error value.
            weight (float): The sum of weights.

        Returns:
            float: The normalized final error value.
        """
        return error / (weight + 1e-38)

    def is_max_optimal(self):
        """Determines if maximizing the metric is optimal.

        Returns:
            bool: True if higher metric values are better, False otherwise.
        """
        return self._custom_metric_parent.maximize

    def evaluate(self, approxes, target, weight=None):
        """Evaluates the multi-target custom metric.

        Args:
            approxes (list-like): Predicted approximations for multiple targets.
            target (list-like): True target values for multiple targets.
            weight (list-like, optional): Sample weights for each target.

        Returns:
            tuple: A tuple containing:
                - error_sum_normalized (float): The normalized sum of errors across all targets.
                - weight_sum (float): The sum of weights (always 0 in this implementation).

        Raises:
            AssertionError: If the dimensions of target and approxes do not match.
            Exception: If the score function fails.
        """
        assert len(target) == len(approxes)
        assert len(target[0]) == len(approxes[0])
        error_sum = 0.0
        weight_sum = 0.0

        for i in range(len(approxes)):
            w = 1.0 if weight is None else weight[i]
            weight_sum += w
            approx_i = approxes[i]
            target_i = target[i]
            result = self._custom_metric_parent._score_function(target_i, approx_i)
            error_sum += result
        return error_sum / len(approxes), 0


class _CatboostCustomObjective(object):
    """Custom objective class for CatBoost.

    Attributes:
        outer_parent: The parent object containing objective configuration.
    """

    def __init__(self, outer_parent):
        """Initializes the _CatboostCustomObjective.

        Args:
            outer_parent: The parent objective configuration object.
        """
        self.outer_parent = outer_parent

    def calc_ders_range(self, approxes, targets, weights):
        """Calculates the derivatives for a range of samples.

        Args:
            approxes (array-like): Predicted approximations.
            targets (array-like): True target values.
            weights (array-like, optional): Sample weights.

        Returns:
            list of tuples: A list where each tuple contains the gradient and Hessian for a sample.

        Raises:
            AssertionError: If the length of approxes does not match targets or weights.
            Exception: If gradient or Hessian computation fails.
        """
        assert len(approxes) == len(targets)
        if weights is not None:
            assert len(weights) == len(approxes)

        der1 = -self.outer_parent._get_gradient(
            targets, approxes
        )  # Negative gradient to align with XGBoost and LightGBM formats
        der2 = -self.outer_parent._get_hessian(targets, approxes)

        if weights is not None:
            der1 *= weights
            der2 *= weights

        result = []
        for index in range(len(targets)):
            result.append((der1[index], der2[index]))

        return result


class _CatboostCustomMultiObjective(object):
    """Custom multi-objective class for CatBoost.

    Attributes:
        outer_parent: The parent object containing multi-objective configuration.
    """

    def __init__(self, outer_parent):
        """Initializes the _CatboostCustomMultiObjective.

        Args:
            outer_parent: The parent multi-objective configuration object.
        """
        self.outer_parent = outer_parent

    def calc_ders_multi(self, approxes, targets, weight):
        """Calculates the derivatives for multiple objectives.

        Args:
            approxes (array-like): Predicted approximations.
            targets (array-like): True target values.
            weight (array-like, optional): Sample weights.

        Returns:
            tuple: A tuple containing:
                - der1 (array-like): Gradient values.
                - der2 (array-like): Hessian values.

        Raises:
            Exception: If gradient or Hessian computation fails.
        """
        der1 = -self.outer_parent._get_gradient(targets, approxes)
        der2 = -self.outer_parent._get_hessian(targets, approxes)

        return der1, der2