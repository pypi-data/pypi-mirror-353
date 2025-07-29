from copy import deepcopy
from typing import List, Union

import numpy as np
import pandas as pd

from dreamml.logging import get_logger
from dreamml.modeling.metrics import BaseMetric
from dreamml.modeling.models.estimators import BaseModel

_logger = get_logger(__name__)


def make_cv(
    estimator: BaseModel,
    x_train_cv,
    y_train_cv,
    cv,
    splitter_df: pd.DataFrame,
    metric: BaseMetric,
):
    """
    Perform cross-validation to evaluate model performance and determine the optimal number of training iterations.

    Args:
        estimator (BaseModel): An instance of the model to be trained.
        x_train_cv (pd.DataFrame): Feature matrix for training the model.
        y_train_cv (pd.Series): Target variable vector for training the model.
        cv: Cross-validator generator for splitting the data into training and validation sets.
        splitter_df (pd.DataFrame): DataFrame used for splitting the data.
        metric (BaseMetric): Metric used to evaluate the model's performance.

    Returns:
        Tuple[
            List[BaseModel],
            float,
            List[float],
            Union[int, List[int]],
            List[int],
            Union[pd.DataFrame, pd.Series]
        ]: A tuple containing:
            - estimators (List[BaseModel]): List of trained model instances.
            - cv_score (float): Mean cross-validation score.
            - folds_score (List[float]): List of scores for each fold.
            - mean_fold_trees (Union[int, List[int]]): Mean number of training iterations across folds.
            - folds_trees_ (List[int]): Number of training iterations for each fold.
            - oof_predictions (pd.DataFrame or pd.Series): Out-of-fold predictions.

    Raises:
        ValueError: If the task type is not recognized.
    """
    logger = estimator._logger or _logger
    task = estimator.task

    x_train_cv = x_train_cv.reset_index(drop=True)

    initial_y_indexes = y_train_cv.index
    y_train_cv = y_train_cv.reset_index(drop=True)

    if task in ("multilabel", "multiregression"):
        oof_predictions = pd.DataFrame(np.zeros_like(y_train_cv))
    elif task == "multiclass":
        oof_predictions = pd.DataFrame(
            np.empty((y_train_cv.shape[0], y_train_cv.nunique()))
        )
    else:
        oof_predictions = pd.Series(np.zeros_like(y_train_cv))

    estimators = []
    folds_score = []
    folds_trees_: Union[int, List[int]] = []

    for fold_number, (train_index, valid_index) in enumerate(cv.split(splitter_df)):
        logger.info(f"Cross-Validation, Fold {fold_number + 1}")
        logger.info(f"{fold_number + 1} {train_index.shape, valid_index.shape}")

        y_pred, score, fold_estimator = fold_calculate(
            x_train_cv,
            estimator,
            metric,
            train_index,
            valid_index,
            y_train_cv,
        )

        folds_trees_.append(fold_estimator.best_iteration)
        estimators.append(fold_estimator)
        folds_score.append(score)

        oof_predictions.loc[valid_index] = y_pred

        logger.info(f"\nCV oof score: {round(score, 2)}")
        logger.info("*" * 111)

    oof_predictions.index = initial_y_indexes

    cv_score, cv_std = round(np.mean(folds_score), 5), round(np.std(folds_score), 5)
    logger.info(f"Total CV-score = {cv_score} +/- {cv_std}")
    logger.info("-" * 111)

    if isinstance(folds_trees_[0], int):
        mean_fold_trees = int(np.mean(folds_trees_))
    else:
        mean_fold_trees = [
            int(classifier_trees) for classifier_trees in np.mean(folds_trees_, axis=0)
        ]

    return (
        estimators,
        np.mean(folds_score),
        folds_score,
        mean_fold_trees,
        folds_trees_,
        oof_predictions,
    )


def fold_calculate(
    x_train_cv,
    estimator,
    metric: BaseMetric,
    train_index,
    valid_index,
    y_train_cv,
):
    """
    Train the estimator on the training subset and evaluate it on the validation subset.

    Args:
        x_train_cv (pd.DataFrame): Feature matrix for cross-validation.
        estimator (BaseModel): The model instance to be trained.
        metric (BaseMetric): Metric to evaluate the model's performance.
        train_index: Indices for the training subset.
        valid_index: Indices for the validation subset.
        y_train_cv (pd.Series): Target variable vector for cross-validation.

    Returns:
        Tuple[pd.DataFrame or pd.Series, float, BaseModel]: A tuple containing:
            - y_pred (pd.DataFrame or pd.Series): Predictions for the validation subset.
            - score (float): Evaluation score based on the provided metric.
            - fold_estimator (BaseModel): The trained model instance for this fold.

    Raises:
        Exception: If training or prediction fails.
    """
    x_train, x_valid = x_train_cv.loc[train_index], x_train_cv.loc[valid_index]
    y_train, y_valid = y_train_cv.loc[train_index], y_train_cv.loc[valid_index]
    fold_estimator = deepcopy(estimator)

    fold_estimator.fit(x_train, y_train, x_valid, y_valid)
    y_pred = fold_estimator.transform(x_valid)

    score = metric(y_pred=y_pred, y_true=y_valid)

    return y_pred, score, fold_estimator