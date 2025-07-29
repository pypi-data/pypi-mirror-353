from typing import Optional, List, Union, Tuple

import numpy as np
import pandas as pd

from sklearn.metrics import (
    roc_auc_score,
    fbeta_score,
    auc,
    roc_curve,
    precision_recall_curve,
    precision_score,
    recall_score,
    accuracy_score,
    log_loss,
    f1_score,
)
from sklearn.preprocessing import LabelBinarizer

from dreamml.modeling.metrics._base_metric import BaseMetric, OptimizableMetricMixin
from dreamml.modeling.metrics.metric_functions import (
    precision_at_k_score_,
    recall_at_k_score_,
    gini_at_k_score_,
    roc_auc_at_k_score_,
    precision_recall_auc_at_k_score_,
    sensitivity_specificity_auc_at_k_score_,
    PyBoostBCEWithNanLoss,
    PyBoostNanAuc,
    PyBoostBCEWithNanMetric,
    PyBoostGini,
    PyBoostAucMulticlass,
    PyBoostGiniMulticlass,
    PyBoostPRAUCMulticlass,
    PyBoostPRAUC,
)


def _set_average(task: str):
    """
    Set the default average type based on the classification task.

    Args:
        task (str): The type of classification task. Expected values are
            'binary', 'multilabel', or 'multiclass'.

    Returns:
        str: The default averaging method corresponding to the task.

    Raises:
        KeyError: If the task type is not one of 'binary', 'multilabel', or 'multiclass'.
    """
    default_average = {
        "binary": "binary",
        "multilabel": "macro",
        "multiclass": "macro",
    }
    return default_average[task]


def _reshape_estimator_preds(task, y_true: np.ndarray, y_pred: np.array):
    """
    Reshape the prediction array based on the task type.

    Args:
        task: The type of classification task.
        y_true (np.ndarray): The true labels.
        y_pred (np.array): The predicted labels or probabilities.

    Returns:
        np.ndarray: The reshaped prediction array.
    """
    if task in ["multiclass", "multilabel"] and len(y_pred.shape) == 1:
        return y_pred.reshape(y_true.shape[0], -1)
    return y_pred


class ClassificationMetric(BaseMetric):
    """
    Base class for classification metrics.

    Inherits from BaseMetric and provides functionality specific to classification tasks.
    """

    _task_type: str = "classification"

    def __init__(
        self,
        model_name: Optional[str] = None,
        task: Optional[str] = None,
        target_with_nan_values: bool = False,
        labels: Optional[List[Union[int, str, float]]] = None,
        average: Optional[str] = "binary",
        **params,
    ):
        """
        Initialize the ClassificationMetric.

        Args:
            model_name (Optional[str]): The name of the model.
            task (Optional[str]): The type of classification task.
            target_with_nan_values (bool): Indicates if the target contains NaN values.
            labels (Optional[List[Union[int, str, float]]]): List of class labels.
            average (Optional[str]): Averaging method for multi-class metrics.
            **params: Additional parameters.

        Raises:
            KeyError: If the average parameter is not valid for the task.
        """
        super().__init__(
            model_name=model_name,
            task=task,
            target_with_nan_values=target_with_nan_values,
            **params,
        )
        self.average = _set_average(self._task) if average == "binary" else average
        self.multi_class = "ovr"
        # For multiclass tasks, apply label_encoder to y_true, classes range from 0 to n_classes
        self.arange_labels = (
            np.arange(len(labels)) if self._task == "multiclass" else None
        )

    def __call__(self, y_true, y_pred):
        """
        Calculate the metric based on true and predicted labels.

        Args:
            y_true: True labels.
            y_pred: Predicted labels or probabilities.

        Returns:
            float or List[float]: Calculated metric value or list of metric values per class.
        """
        y_true, y_pred = self._cast_to_numpy(y_true, y_pred)

        # FIXME: _detailed_model_statisitics.py multilabel_detailed_model_stats
        if self._task == "multilabel":
            if self.average is not None:
                self.average = "binary"
            return self._calculate_macro_score_with_nan_values(y_true, y_pred)
        else:
            return self._score_function(y_true, y_pred)

    def _calculate_macro_score_with_nan_values(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ):
        """
        Calculate macro metric with or without NaN values for MultiLabel Classification.

        Args:
            y_true (np.ndarray): Target matrix of shape (n_samples, n_classes).
            y_pred (np.ndarray): Predicted probabilities matrix of shape (n_samples, n_classes).

        Returns:
            Union[float, List[float]]: Macro metric averaged over all classes or a list of metrics per class.
        """
        y_true_flatten, y_pred_flatten = [], []
        metric_list = []
        num_classes = y_true.shape[1]
        mask = ~np.isnan(y_true)  # Mask to exclude NaN values

        for class_idx in range(num_classes):
            mask_by_class_idx = mask[:, class_idx]
            y_true_idx_class = y_true[mask_by_class_idx, class_idx]
            y_pred_idx_class = y_pred[mask_by_class_idx, class_idx]

            # Metrics like "logloss" and "accuracy" do not support averaging, so calculate micro
            if self.name in ["logloss", "accuracy"]:
                # y_true_flatten.append(y_true_idx_class)
                # y_pred_flatten.append(y_pred_idx_class)

                # For the new version of numpy:
                y_true_flatten = np.append(y_true_flatten, np.array(y_true_idx_class))
                y_pred_flatten = np.append(y_pred_flatten, np.array(y_pred_idx_class))
            else:
                # Calculate metric for the current class
                metric = self._score_function(y_true_idx_class, y_pred_idx_class)

                # Metrics like "roc_auc" and "gini" return the metric for one class when average=None
                if self.average is None and self.name not in ["roc_auc", "gini"]:
                    metric_list.append(metric[1])
                else:
                    metric_list.append(metric)

        if self.name in ["logloss", "accuracy"]:
            return self._score_function(
                np.array(y_true_flatten).T, np.array(y_pred_flatten).T
            )

        # If average is None, calculate binary metric for each class with average=None
        if self.average is None and self.name not in ["logloss", "accuracy"]:
            return metric_list

        # Return the mean metric (macro)
        return np.mean(metric_list) if metric_list else 0.0

    def _calculate_multiclass_macro_metric(
        self, y_true, y_pred_proba, metric="roc_auc"
    ):
        """
        Calculate macro metric for multiclass classification, handling unequal class distributions.

        Args:
            y_true: True labels.
            y_pred_proba: Predicted probabilities.
            metric (str): The metric to calculate. Defaults to "roc_auc".

        Returns:
            float or np.ndarray: Calculated metric value(s).

        Raises:
            ValueError: If an unsupported metric is specified.
        """
        result = []
        labels_in_y_true = np.unique(y_true)
        lb = LabelBinarizer(sparse_output=False).fit(self.arange_labels)
        y_true_binarizerd = lb.transform(y_true)

        for class_idx in self.arange_labels:
            if class_idx in labels_in_y_true:
                if metric == "roc_auc":
                    score = roc_auc_score(
                        y_true_binarizerd[:, class_idx],
                        y_pred_proba[:, class_idx],
                        average=self.average,
                    )
                    score = np.array(score)
                elif metric == "precision_recall_auc":
                    precision, recall, _ = precision_recall_curve(
                        y_true_binarizerd[:, class_idx],
                        y_pred_proba[:, class_idx],
                    )
                    score = auc(recall, precision)
                else:
                    score = np.nan
                result = np.append(result, score)
            else:
                result = np.append(result, np.nan)

        if self.average is None:
            return result
        return np.nanmean(result)


class LogLoss(ClassificationMetric, OptimizableMetricMixin):
    """
    Log Loss metric for classification tasks.
    """

    name = "logloss"
    maximize = False

    def _score_function(self, y_true, y_pred):
        """
        Calculate the log loss between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities.

        Returns:
            float: Log loss value.
        """
        y_pred = _reshape_estimator_preds(self._task, y_true, y_pred)

        if self._task == "multiclass":
            return log_loss(y_true, y_pred, labels=self.arange_labels)
        return log_loss(y_true, y_pred)

    def _get_pyboost_custom_objective(
        self,
    ):
        """
        Get the custom objective function for PyBoost.

        Returns:
            PyBoostBCEWithNanLoss: Custom loss object.
        """
        _objective = PyBoostBCEWithNanLoss()
        return _objective

    def _get_pyboost_custom_metric(
        self,
    ):
        """
        Get the custom metric function for PyBoost.

        Returns:
            PyBoostBCEWithNanMetric: Custom metric object.
        """
        _metric = PyBoostBCEWithNanMetric()
        return _metric


class Gini(ClassificationMetric):
    """
    Gini coefficient metric for classification tasks.
    """

    name = "gini"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate the Gini coefficient between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities.

        Returns:
            float: Gini coefficient value.
        """
        y_pred = _reshape_estimator_preds(self._task, y_true, y_pred)

        if self._task == "multiclass":
            if len(np.unique(y_true)) != len(np.unique(y_pred)):
                return (
                    2
                    * self._calculate_multiclass_macro_metric(
                        y_true, y_pred, metric="roc_auc"
                    )
                    - 1
                )
            return (
                2
                * roc_auc_score(
                    y_true,
                    y_pred,
                    average=self.average,
                    multi_class=self.multi_class,
                    labels=self.arange_labels,
                )
                - 1
            )
        return 2 * roc_auc_score(y_true, y_pred, average="macro") - 1

    def _get_pyboost_custom_metric(
        self,
    ):
        """
        Get the custom metric function for PyBoost.

        Returns:
            PyBoostGini or PyBoostGiniMulticlass: Custom metric object based on task type.
        """
        if self._task == "multiclass":
            _metric = PyBoostGiniMulticlass()
        else:
            _metric = PyBoostGini()
        return _metric


class ROCAUC(ClassificationMetric):
    """
    Receiver Operating Characteristic Area Under Curve (ROC AUC) metric for classification tasks.
    """

    name = "roc_auc"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate the ROC AUC between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities.

        Returns:
            float: ROC AUC value.
        """
        y_pred = _reshape_estimator_preds(self._task, y_true, y_pred)

        if self._task == "multiclass":
            if len(np.unique(y_true)) != len(np.unique(y_pred)):
                return self._calculate_multiclass_macro_metric(
                    y_true, y_pred, metric="roc_auc"
                )
            return roc_auc_score(
                y_true,
                y_pred,
                average=self.average,
                multi_class=self.multi_class,
                labels=self.arange_labels,
            )
        return roc_auc_score(y_true, y_pred, average="macro")

    def _get_pyboost_custom_metric(
        self,
    ):
        """
        Get the custom metric function for PyBoost.

        Returns:
            PyBoostAucMulticlass or PyBoostNanAuc: Custom metric object based on task type.
        """
        if self._task == "multiclass":
            _metric = PyBoostAucMulticlass()
        else:
            _metric = PyBoostNanAuc()
        return _metric


class SSAUC(ClassificationMetric):
    """
    Sensitivity Specificity Area Under Curve (SSAUC) metric for classification tasks.
    """

    name = "sensitivity_specificity_auc"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate the SSAUC between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities.

        Returns:
            float: SSAUC value.
        """
        y_pred = _reshape_estimator_preds(self._task, y_true, y_pred)

        fpr, tpr, _ = roc_curve(y_true, y_pred)
        return auc(1 - fpr, tpr)


class PRAUC(ClassificationMetric):
    """
    Precision-Recall Area Under Curve (PRAUC) metric for classification tasks.
    """

    name = "precision_recall_auc"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate the PRAUC between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities.

        Returns:
            float: PRAUC value.
        """
        y_pred = _reshape_estimator_preds(self._task, y_true, y_pred)

        if self._task == "multiclass":
            return self._calculate_multiclass_macro_metric(
                y_true, y_pred, metric="precision_recall_auc"
            )
        precision, recall, _ = precision_recall_curve(y_true, y_pred)
        return auc(recall, precision)

    def _get_pyboost_custom_metric(
        self,
    ):
        """
        Get the custom metric function for PyBoost.

        Returns:
            PyBoostPRAUCMulticlass or PyBoostPRAUC: Custom metric object based on task type.
        """
        if self._task == "multiclass":
            _metric = PyBoostPRAUCMulticlass()
        else:
            _metric = PyBoostPRAUC()
        return _metric


class Precision(ClassificationMetric):
    """
    Precision metric for classification tasks.
    """

    name = "precision"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate precision between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities or labels.

        Returns:
            float: Precision value.
        """
        y_pred = _reshape_estimator_preds(self._task, y_true, y_pred)

        if self._task == "multiclass":
            y_pred_round = (
                np.argmax(y_pred, axis=1) if len(y_pred.shape) != 1 else y_pred
            )
            return precision_score(
                y_true, y_pred_round, average=self.average, labels=self.arange_labels
            )
        else:
            threshold = self.params.get("threshold", 0.5)
            y_pred_round = np.where(y_pred > threshold, 1, 0)
            return precision_score(y_true, y_pred_round, average=self.average)


class Recall(ClassificationMetric):
    """
    Recall metric for classification tasks.
    """

    name = "recall"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate recall between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities or labels.

        Returns:
            float: Recall value.
        """
        y_pred = _reshape_estimator_preds(self._task, y_true, y_pred)

        if self._task == "multiclass":
            y_pred_round = (
                np.argmax(y_pred, axis=1) if len(y_pred.shape) != 1 else y_pred
            )
            return recall_score(
                y_true, y_pred_round, average=self.average, labels=self.arange_labels
            )
        else:
            threshold = self.params.get("threshold", 0.5)
            y_pred_round = np.where(y_pred > threshold, 1, 0)
            return recall_score(y_true, y_pred_round, average=self.average)


class Accuracy(ClassificationMetric):
    """
    Accuracy metric for classification tasks.
    """

    name = "accuracy"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate accuracy between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities or labels.

        Returns:
            float: Accuracy value.
        """
        y_pred = _reshape_estimator_preds(self._task, y_true, y_pred)

        if self._task == "multiclass":
            y_pred_round = (
                np.argmax(y_pred, axis=1) if len(y_pred.shape) != 1 else y_pred
            )
        else:
            threshold = self.params.get("threshold", 0.5)
            y_pred_round = np.where(y_pred > threshold, 1, 0)

        return accuracy_score(y_true, y_pred_round)


class FBeta(ClassificationMetric):
    """
    F-beta score metric for classification tasks.
    """

    name = "fbeta"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate the F-beta score between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities or labels.

        Returns:
            float: F-beta score value.
        """
        y_pred = _reshape_estimator_preds(self._task, y_true, y_pred)
        beta = self.params.get("beta", 1)

        if self._task == "multiclass":
            y_pred_round = (
                np.argmax(y_pred, axis=1) if len(y_pred.shape) != 1 else y_pred
            )
            return fbeta_score(
                y_true,
                y_pred_round,
                average=self.average,
                beta=beta,
                labels=self.arange_labels,
            )
        else:
            threshold = self.params.get("threshold", 0.5)
            y_pred_round = np.where(y_pred > threshold, 1, 0)
            return fbeta_score(
                y_true=y_true, y_pred=y_pred_round, average=self.average, beta=beta
            )

    def _get_catboost_metric_name(self):
        """
        Get the CatBoost metric name with beta parameter.

        Returns:
            str: CatBoost metric name including beta value.
        """
        name = super()._get_catboost_metric_name()
        params = f"beta={self.params['beta']}"

        return f"{name}:{params}"


class F1Score(ClassificationMetric):
    """
    F1 Score metric for classification tasks.
    """

    name = "f1_score"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate the F1 score between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities or labels.

        Returns:
            float: F1 score value.
        """
        y_pred = _reshape_estimator_preds(self._task, y_true, y_pred)

        if self._task == "multiclass":
            y_pred_round = (
                np.argmax(y_pred, axis=1) if len(y_pred.shape) != 1 else y_pred
            )
            return f1_score(
                y_true, y_pred_round, average=self.average, labels=self.arange_labels
            )
        else:
            threshold = self.params.get("threshold", 0.5)
            y_pred_round = np.where(y_pred > threshold, 1, 0)
            return f1_score(y_true, y_pred_round, average=self.average)


class PrecisionAtK(ClassificationMetric):
    """
    Precision at K metric for classification tasks.
    """

    name = "precision_at_k"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate Precision at K between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities or rankings.

        Returns:
            float: Precision at K value.
        """
        at_k = self.params.get("at_k", 5)

        return precision_at_k_score_(y_true, y_pred, {"at_k": at_k})


class RecallAtK(ClassificationMetric):
    """
    Recall at K metric for classification tasks.
    """

    name = "recall_at_k"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate Recall at K between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities or rankings.

        Returns:
            float: Recall at K value.
        """
        at_k = self.params.get("at_k", 5)

        return recall_at_k_score_(y_true, y_pred, {"at_k": at_k})


class GiniAtK(ClassificationMetric):
    """
    Gini at K metric for classification tasks.
    """

    name = "gini_at_k"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate Gini at K between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities or rankings.

        Returns:
            float: Gini at K value.
        """
        at_k = self.params.get("at_k", 5)

        return gini_at_k_score_(y_true, y_pred, {"at_k": at_k})


class ROCAUCAtK(ClassificationMetric):
    """
    ROC AUC at K metric for classification tasks.
    """

    name = "roc_auc_at_k"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate ROC AUC at K between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities or rankings.

        Returns:
            float: ROC AUC at K value.
        """
        at_k = self.params.get("at_k", 5)

        return roc_auc_at_k_score_(y_true, y_pred, {"at_k": at_k})


class PRAUCAtK(ClassificationMetric):
    """
    Precision-Recall AUC at K metric for classification tasks.
    """

    name = "precision_recall_auc_at_k"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate Precision-Recall AUC at K between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities or rankings.

        Returns:
            float: Precision-Recall AUC at K value.
        """
        at_k = self.params.get("at_k", 5)

        return precision_recall_auc_at_k_score_(y_true, y_pred, {"at_k": at_k})


class SSAUCAtK(ClassificationMetric):
    """
    Sensitivity-Specificity AUC at K metric for classification tasks.
    """

    name = "sensitivity_specificity_auc_at_k"
    maximize = True

    def _score_function(self, y_true, y_pred):
        """
        Calculate Sensitivity-Specificity AUC at K between true and predicted labels.

        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities or rankings.

        Returns:
            float: Sensitivity-Specificity AUC at K value.
        """
        at_k = self.params.get("at_k", 5)

        return sensitivity_specificity_auc_at_k_score_(y_true, y_pred, {"at_k": at_k})