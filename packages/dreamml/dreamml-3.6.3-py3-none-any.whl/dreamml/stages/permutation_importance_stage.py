from __future__ import annotations

from typing import List

import pandas as pd
from tqdm.auto import tqdm

from dreamml.logging.logger import CombinedLogger
from dreamml.logging import get_logger
from dreamml.modeling.cv import BaseCrossValidator
from dreamml.modeling.metrics import BaseMetric

from dreamml.features.feature_selection._permutation_importance import (
    select_subset_features,
    calculate_permutation_feature_importance,
)

from dreamml.data._dataset import DataSet

from dreamml.modeling.models.estimators import BoostingBaseModel
from dreamml.stages.algo_info import AlgoInfo
from dreamml.stages.model_based_stage import ModelBasedStage
from dreamml.stages.stage import BaseStage
from dreamml.pipeline.fitter import FitterBase
from dreamml.utils import ValidationType
from dreamml.configs.config_storage import ConfigStorage

_logger = get_logger(__name__)


class PermutationImportanceStage(ModelBasedStage):
    """
    A stage for performing feature selection based on permutation importance.

    This stage evaluates the importance of features by measuring the decrease in model performance when
    feature values are randomly shuffled. It supports both cross-validation and holdout validation methods.

    Args:
        algo_info (AlgoInfo): Information about the algorithm being used.
        config (ConfigStorage): Configuration storage containing stage parameters.
        fitter (FitterBase): The fitter responsible for training the model.
        vectorization_name (str, optional): Name of the vectorization method. Defaults to None.
    """

    name = "permutation"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: FitterBase,
        vectorization_name: str = None,
    ):
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
        )
        self.threshold = config.stages.permuation.permutation_threshold
        self.top_n = config.stages.permuation.permutation_top_n
        self.sampling_flag = config.data.use_sampling
        self.remaining_features = config.data.columns.remaining_features

    def _set_params(self, params: dict):
        """
        Sets the parameters for the permutation importance stage.

        This method is not implemented and should be overridden by subclasses.

        Raises:
            NotImplementedError: Always raised to indicate the method is not implemented.
        """
        raise NotImplementedError

    def _fit(
        self,
        model: BoostingBaseModel,
        used_features: List[str],
        data_storage: DataSet,
        models: List[BoostingBaseModel] = None,
    ) -> BaseStage:
        """
        Fits the permutation importance stage by training models and selecting important features.

        This method trains models using either cross-validation or holdout validation to compute
        the permutation importance of features. It then selects a subset of features based on
        the computed importance and retrains the model if necessary.

        Args:
            model (BoostingBaseModel): The base model to evaluate.
            used_features (List[str]): List of feature names currently in use.
            data_storage (DataSet): The dataset containing training and validation data.
            models (List[BoostingBaseModel], optional): List of trained models for cross-validation.
                Defaults to None.

        Returns:
            BaseStage: Returns the instance of the stage after fitting.

        Raises:
            ValueError: If the validation type is unsupported.
        """
        if self.fitter.validation_type == ValidationType.CV:
            x, y = data_storage.get_cv_data_set(
                used_features, vectorization_name=self.vectorization_name
            )
        else:
            eval_set = data_storage.get_eval_set(
                used_features, vectorization_name=self.vectorization_name
            )
            x, y = eval_set["valid"][0], eval_set["valid"][1]

        if self.fitter.validation_type == ValidationType.CV:
            importance = make_cv_importance(
                models,
                x,
                y,
                self.fitter.cv,
                splitter_df=data_storage.get_cv_splitter_df(
                    self.fitter.cv.get_required_columns()
                ),
                metric=self.eval_metric,
            )
        elif self.fitter.validation_type == ValidationType.HOLDOUT:
            importance = make_ho_importance(
                x,
                y,
                estimator=model,
                metric=self.eval_metric,
            )
        else:
            raise ValueError(
                f"Can't get importance function for validation type = {self.fitter.validation_type.value}."
            )

        best_model_info = [model, 0, models, used_features, 0]
        thresholds = self.threshold
        thresholds = (
            thresholds if isinstance(thresholds, (tuple, list)) else [thresholds]
        )
        retrained = False
        for threshold in tqdm(thresholds):
            perm_features = select_subset_features(
                importance, self.remaining_features, threshold, self.top_n
            )
            if (len(perm_features) > 0) and (len(perm_features) < len(used_features)):
                estimator = self._init_model(perm_features, model.params)
                perm_model, estimators, predictions = self.fitter.train(
                    estimator=estimator,
                    data_storage=data_storage,
                    metric=self.eval_metric,
                    used_features=perm_features,
                    sampling_flag=self.sampling_flag,
                    vectorization_name=self.vectorization_name,
                )

                perm_score = self.eval_metric(y, predictions)

                model_info = (
                    perm_model,
                    perm_score,
                    estimators,
                    perm_features,
                    threshold,
                )
                if best_model_info[1] < model_info[1]:
                    best_model_info = model_info

                retrained = True

        logger = CombinedLogger([self._logger, _logger])

        if retrained:
            old_num_features = len(used_features)
            new_num_features = len(best_model_info[3])
            logger.info(
                f"\033[7mUsing permutation with threshold {self.threshold}, "
                f"{old_num_features - new_num_features} features were removed.\n"
                f"Number of selected features: {new_num_features}\033[0m"
            )
        else:
            logger.info(
                f"\033[7mUsing permutation with threshold {self.threshold}, no features were removed.\033[0m"
            )
        self.used_features = best_model_info[3]
        self.final_model = best_model_info[0]
        self.feature_importance = importance
        self.prediction = self.prediction_out(data_storage)
        self.models = best_model_info[2]

        return self


def make_cv_importance(
    estimators: list,
    x,
    y,
    cv: BaseCrossValidator,
    splitter_df: pd.DataFrame,
    metric: BaseMetric,
) -> pd.DataFrame:
    """
    Calculates permutation feature importance using cross-validation.

    This function evaluates the importance of each feature by measuring the decrease in model
    performance when the feature values are permuted. It aggregates the importance scores
    across all cross-validation folds.

    Args:
        estimators (list): List of trained model estimators for each fold.
        x (pd.DataFrame): Feature matrix.
        y (pd.Series): Target variable.
        cv (BaseCrossValidator): Cross-validator for splitting the data.
        splitter_df (pd.DataFrame): DataFrame used for splitting the data.
        metric (BaseMetric): Metric to evaluate model performance.

    Returns:
        pd.DataFrame: DataFrame containing the mean permutation importance for each feature.
    """
    importance = pd.DataFrame()

    x = x.reset_index(drop=True)
    y = y.reset_index(drop=True)

    for fold_number, (train_index, valid_index) in enumerate(cv.split(splitter_df)):
        x_train, x_valid = x.loc[train_index], x.loc[valid_index]
        y_train, y_valid = y.loc[train_index], y.loc[valid_index]
        fold_importance = calculate_permutation_feature_importance(
            estimator=estimators[fold_number],
            metric=metric,
            maximize=metric.maximize,
            data=x_valid,
            target=y_valid,
            fraction_sample=0.8,
        )
        importance = pd.concat([importance, fold_importance], axis=0)

    importance = (
        importance.groupby(["feature"])["permutation_importance"].mean().reset_index()
    )
    importance = importance.sort_values(by="permutation_importance", ascending=False)

    return importance


def make_ho_importance(
    data: pd.DataFrame,
    target: pd.Series,
    estimator: BoostingBaseModel,
    metric: BaseMetric,
) -> pd.DataFrame:
    """
    Calculates permutation feature importance using holdout validation.

    This function evaluates the importance of each feature by measuring the decrease in model
    performance when the feature values are permuted on the holdout validation set.

    Args:
        data (pd.DataFrame): Feature matrix of the holdout validation set.
        target (pd.Series): Target variable of the holdout validation set.
        estimator (BoostingBaseModel): Trained model estimator.
        metric (BaseMetric): Metric to evaluate model performance.

    Returns:
        pd.DataFrame: DataFrame containing the permutation importance for each feature.
    """
    importance = calculate_permutation_feature_importance(
        estimator=estimator,
        metric=metric,
        maximize=metric.maximize,
        data=data,
        target=target,
        fraction_sample=0.8,
    )

    return importance