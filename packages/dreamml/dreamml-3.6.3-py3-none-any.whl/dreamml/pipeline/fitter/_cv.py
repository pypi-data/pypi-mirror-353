import numpy as np
import pandas as pd
from typing import List, Union, Optional, Type
from copy import deepcopy

from dreamml.configs.config_storage import ConfigStorage
from dreamml.features.feature_selection.shap_importance import (
    calculate_shap_feature_importance,
)
from dreamml.data._dataset import DataSet
from dreamml.modeling.metrics import BaseMetric
from dreamml.modeling.models import PyBoostModel
from dreamml.modeling.cv import (
    make_cv,
    BaseCrossValidator,
    KFoldCrossValidator,
    GroupCrossValidator,
    GroupTimePeriodCrossValidator,
    TimeSeriesCrossValidator,
    TimeSeriesGroupTimePeriodCrossValidator,
)
from dreamml.pipeline.fitter import FitterBase
from dreamml.utils import ValidationType
from dreamml.utils.errors import ConfigurationError


class FitterCV(FitterBase):
    """Fitter class that performs cross-validation for model training.

    Attributes:
        validation_type (ValidationType): The type of validation used, set to cross-validation.
    """

    validation_type = ValidationType.CV

    def __init__(self, cv: BaseCrossValidator):
        """Initialize the FitterCV with a cross-validator.

        Args:
            cv (BaseCrossValidator): A generator for performing cross-validation.
        """
        self.cv_mean_score = None
        self.cv = cv

    @staticmethod
    def _fit_final_model(
        estimator,
        x: pd.DataFrame,
        y: pd.Series,
        n_trees_: Union[int, List[int]],
        coef_: float = 1.2,
        **eval_set,
    ):
        """Fine-tune the final model on all observations.

        This method retrains the estimator on the entire dataset using the average number
        of trees from cross-validation, adjusted by a coefficient.

        Args:
            estimator (BaseModel): An instance of the model to be trained.
            x (pd.DataFrame): Feature matrix for model training.
            y (pd.Series): Target variable vector for model training.
            n_trees_ (Union[int, List[int]]): 
                The average number of training iterations from cross-validation or a list for each fold.
            coef_ (float, optional): 
                The coefficient by which to multiply `n_trees_`. Defaults to 1.2.
            **eval_set: 
                Additional evaluation sets for the model.

        Returns:
            BoostingBaseModel: The final model trained with the adjusted number of iterations.

        Raises:
            ValueError: If `n_trees_` is not an integer or list of integers.
        """
        final_estimator = deepcopy(estimator)

        if isinstance(n_trees_, int):
            final_estimator_n_trees = max([int(coef_ * n_trees_), 1])
        else:
            final_estimator_n_trees = (coef_ * np.array(n_trees_)).astype(int)
            final_estimator_n_trees = np.where(
                final_estimator_n_trees < 1,
                np.ones_like(final_estimator_n_trees),
                final_estimator_n_trees,
            )
            final_estimator_n_trees = final_estimator_n_trees.tolist()

        if isinstance(final_estimator, PyBoostModel):
            final_estimator.params["ntrees"] = final_estimator_n_trees
        else:
            final_estimator.params["n_estimators"] = final_estimator_n_trees

        final_estimator.fit(x, y, x, y)
        final_estimator.evaluate_and_print(**eval_set)

        return final_estimator

    @staticmethod
    def get_validation_target(
        data_storage: DataSet, vectorization_name: Optional[str] = None
    ):
        """Retrieve the true target values for metric calculation.

        This method is used when all validation data is handled by the class.

        Args:
            data_storage (DataSet): An instance of the data storage class.
            vectorization_name (Optional[str], optional): 
                The name of the vectorization method used. Defaults to None.

        Returns:
            pd.Series: The true target values for metric calculation.
        """
        _, y_true = data_storage.get_cv_data_set(vectorization_name=vectorization_name)

        return y_true

    def calculate_importance(
        self,
        estimators,
        data_storage: DataSet,
        used_features: List = None,
        splitter_df: pd.DataFrame = None,
        fraction_sample: float = 1,
        vectorization_name: Optional[str] = None,
    ) -> pd.DataFrame:
        """Calculate feature importance based on cross-validation.

        This method evaluates the importance of each feature by calculating SHAP values
        across different cross-validation folds.

        Args:
            estimators (Union[List[BaseModel], BaseModel]): 
                A list of model instances for training or a single instance to be replicated across all folds.
            data_storage (DataSet): An instance of the data storage class.
            used_features (List, optional): 
                A list of features to be used for training. Defaults to None.
            splitter_df (pd.DataFrame, optional): 
                The DataFrame used for splitting data into folds. Defaults to None.
            fraction_sample (float, optional): 
                The fraction of observations to use for evaluating feature importance. Defaults to 1.
            vectorization_name (Optional[str], optional): 
                The name of the vectorization method used. Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame containing the feature importance scores.

        Raises:
            ValueError: If `splitter_df` is not provided.
        """
        if splitter_df is None:
            raise ValueError("Cannot make cv without splitter_df")

        importance = pd.DataFrame()
        x, y = data_storage.get_cv_data_set(
            used_features, vectorization_name=vectorization_name
        )
        x = x.reset_index(drop=True)
        y = y.reset_index(drop=True)
        if not isinstance(estimators, list) and not isinstance(estimators, (np.ndarray, pd.Series)):
            estimators = [estimators for _ in range(self.cv.n_splits)]
        for fold_number, (train_index, valid_index) in enumerate(
            self.cv.split(splitter_df)
        ):
            x_train, x_valid = x.loc[train_index], x.loc[valid_index]
            fold_importance = calculate_shap_feature_importance(
                estimator=estimators[fold_number],
                data=x_train,
                fraction_sample=fraction_sample,
            )

            importance = pd.concat([importance, fold_importance], axis=0)

        column_name = [col for col in importance.columns.tolist() if "importance" in col][0]
        importance = importance.groupby(["feature"])[column_name].mean().reset_index()
        importance = importance.sort_values(by=column_name, ascending=False)

        return importance.reset_index(drop=True)

    def train(
        self,
        estimator,
        data_storage: DataSet,
        metric: BaseMetric,
        used_features: List = None,
        sampling_flag: bool = None,
        vectorization_name: Optional[str] = None,
    ):
        """Train the model using cross-validation.

        This is the main function to execute the training module, performing cross-validation,
        training the model on each fold, and fitting the final estimator.

        Args:
            estimator (BoostingBaseModel): An instance of the model to be trained.
            data_storage (DataSet): An instance of the data storage class.
            metric (BaseMetric): The metric used to evaluate model performance.
            used_features (List, optional): 
                A list of features to be used for training. Defaults to None.
            sampling_flag (bool, optional): 
                A flag for compatibility purposes. Defaults to None.
            vectorization_name (Optional[str], optional): 
                The name of the vectorization method used. Defaults to None.

        Returns:
            Tuple[
                BoostingBaseModel,
                List[BoostingBaseModel],
                List,
                List[int],
                List,
                pd.Series
            ]: 
                A tuple containing:
                - final_estimator: The final model trained with the adjusted number of iterations.
                - cv_estimators: A list of models trained on each fold.
                - used_features: The list of features used for training.
                - mean_folds_trees: The average number of trees across folds.
                - _unused: Placeholder for future use.
                - oof_predictions: Out-of-fold predictions as a pandas Series.
        """
        if data_storage.task == "topic_modeling":
            x = data_storage.get_cv_data_set(
                used_features, vectorization_name=vectorization_name
            )
        else:
            x, y = data_storage.get_cv_data_set(
                used_features, vectorization_name=vectorization_name
            )
        eval_set = data_storage.get_eval_set(
            used_features, vectorization_name=vectorization_name
        )
        splitter_df = data_storage.get_cv_splitter_df(self.cv.get_required_columns())

        estimators, mean_folds_score, _, mean_folds_trees, _, oof_predictions = make_cv(
            estimator,
            x,
            y,
            self.cv,
            splitter_df,
            metric,
        )

        if estimator.task not in ["regression", "timeseries"]:
            mean_folds_score = mean_folds_score * 100
        self.cv_mean_score = mean_folds_score
        if ("valid" in eval_set) and (len(eval_set["valid"][0]) == 0):
            del eval_set["valid"]
        final_estimator = self._fit_final_model(
            estimator, x, y, n_trees_=mean_folds_trees, coef_=1.2, **eval_set
        )

        return final_estimator, estimators, oof_predictions


def _get_cv(
    config: ConfigStorage,
    custom_cv: Optional[Type[BaseCrossValidator]] = None,
) -> BaseCrossValidator:
    """Retrieve the appropriate cross-validator based on the configuration.

    This function determines the type of cross-validator to use based on the task,
    data splitting strategy, and other configuration parameters. It supports custom
    cross-validators and various predefined strategies such as K-Fold, Group,
    Time Series, etc.

    Args:
        config (ConfigStorage): The configuration storage object containing all settings.
        custom_cv (Optional[Type[BaseCrossValidator]], optional): 
            A custom cross-validator class to be used. If provided, it overrides the default selection. 
            Defaults to None.

    Returns:
        BaseCrossValidator: An instance of the selected cross-validator.

    Raises:
        ConfigurationError: If attempting to split by group without a time period in time series.
    """
    if custom_cv is not None:
        cv = custom_cv(**config.data.splitting.validation_params["cv_params"])

        return cv

    if (
        config.pipeline.task in ["binary", "multiclass", "multilabel"]
        and config.data.splitting.stratify
    ):
        stratify_column = config.data.columns.target_name
    else:
        stratify_column = None

    random_state = (
        config.pipeline.reproducibility.random_seed
        if config.data.splitting.shuffle
        else None
    )
    nlp_augs = config.data.augmentation.text_augmentations

    if isinstance(config.data.columns.group_column, str):
        group_columns = [config.data.columns.group_column]
    else:
        group_columns = config.data.columns.group_column

    if nlp_augs is not None and len(nlp_augs) > 0:
        cv = GroupCrossValidator(
            group_columns=[
                col for col in config.service_fields if col.find("nlp_aug") != -1
            ],
            stratify_column=stratify_column,
            n_splits=config.data.splitting.cv_n_folds,
            shuffle=config.data.splitting.shuffle,
            random_state=random_state,
        )
        return cv

    if (
        config.data.splitting.time_series_split
        or config.data.splitting.time_series_window_split
    ):
        sliding_window = (
            True if config.data.splitting.time_series_window_split else False
        )

        if config.data.splitting.split_by_time_period:
            cv = TimeSeriesGroupTimePeriodCrossValidator(
                time_column=config.data.columns.time_column,
                time_period=config.data.columns.time_column_period,
                group_columns=group_columns,
                n_splits=config.data.splitting.cv_n_folds,
                sliding_window=sliding_window,
                test_size=config.data.splitting.time_series_split_test_size,
                gap=config.data.splitting.time_series_split_gap,
            )
        elif config.data.splitting.split_by_group:
            raise ConfigurationError(
                "Can't split by group without time period in time series."
            )
        else:
            cv = TimeSeriesCrossValidator(
                time_column=config.data.columns.time_column,
                n_splits=config.data.splitting.cv_n_folds,
                sliding_window=sliding_window,
                test_size=config.data.splitting.time_series_split_test_size,
                gap=config.data.splitting.time_series_split_gap,
            )

        return cv

    elif config.data.splitting.split_by_time_period:
        cv = GroupTimePeriodCrossValidator(
            time_column=config.data.columns.time_column,
            time_period=config.data.columns.time_column_period,
            group_columns=group_columns,
            stratify_column=stratify_column,
            n_splits=config.data.splitting.cv_n_folds,
            shuffle=config.data.splitting.shuffle,
            random_state=random_state,
        )
    elif config.data.splitting.split_by_group:
        cv = GroupCrossValidator(
            group_columns=group_columns,
            stratify_column=stratify_column,
            n_splits=config.data.splitting.cv_n_folds,
            shuffle=config.data.splitting.shuffle,
            random_state=random_state,
        )
    else:
        cv = KFoldCrossValidator(
            stratify_column=stratify_column,
            n_splits=config.data.splitting.cv_n_folds,
            shuffle=config.data.splitting.shuffle,
            random_state=random_state,
        )

    return cv