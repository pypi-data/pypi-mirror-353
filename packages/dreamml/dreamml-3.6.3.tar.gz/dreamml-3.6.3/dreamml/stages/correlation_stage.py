from typing import List, Optional

from dreamml.configs.config_storage import ConfigStorage
from dreamml.data._dataset import DataSet
from dreamml.features.feature_extraction import DecisionTreeFeatureImportance
from dreamml.features.feature_selection._correlation_feature_selection import (
    CorrelationFeatureSelection,
)
from dreamml.modeling.models.estimators import BoostingBaseModel
from dreamml.pipeline.fitter import FitterBase
from dreamml.stages.algo_info import AlgoInfo
from dreamml.stages.stage import BaseStage
from dreamml.stages.feature_based_stage import FeatureBasedStage


class DecisionTreeFeatureImportanceStage(FeatureBasedStage):
    """Stage for selecting features based on decision tree feature importance.

    This stage utilizes a decision tree to determine the importance of features
    and selects those that meet a specified threshold.

    Attributes:
        name (str): The name identifier for this stage.
        threshold (float): The correlation threshold for feature selection.
        remaining_features (List[str]): List of features available for selection.
        feature_importance (List[float]): Importance scores of the selected features.
        used_features (List[str]): List of features that have been selected.
        final_model (BoostingBaseModel): The final model after feature selection.
    """

    name = "dtree"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: Optional[FitterBase] = None,
        vectorization_name: str = None,
    ):
        """Initializes the DecisionTreeFeatureImportanceStage.

        Args:
            algo_info (AlgoInfo): Information about the algorithm.
            config (ConfigStorage): Configuration storage object.
            fitter (Optional[FitterBase], optional): Fitter instance. Defaults to None.
            vectorization_name (str, optional): Name for vectorization. Defaults to None.
        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
        )
        self.threshold = config.stages.corr_selection.corr_threshold
        self.remaining_features = config.data.columns.remaining_features

    def _fit(
        self,
        model: BoostingBaseModel,
        used_features: List[str],
        data_storage: DataSet,
        models: List[BoostingBaseModel] = None,
    ) -> BaseStage:
        """Fits the stage by selecting features based on decision tree importance.

        Args:
            model (BoostingBaseModel): The boosting model to be used.
            used_features (List[str]): List of features currently in use.
            data_storage (DataSet): The dataset storage containing training and evaluation sets.
            models (List[BoostingBaseModel], optional): Additional models if any. Defaults to None.

        Returns:
            BaseStage: The current instance of the stage after fitting.

        Raises:
            ValueError: If the feature selection fails due to invalid parameters.
        """
        corr_transformer = DecisionTreeFeatureImportance(
            self.threshold, self.remaining_features
        )
        eval_sets = data_storage.get_eval_set(used_features)
        self.feature_importance = corr_transformer.fit_transform(*eval_sets["train"])
        self.used_features = sorted(corr_transformer.used_features)
        self.final_model = model
        return self


class CorrelationFeatureSelectionStage(FeatureBasedStage):
    """Stage for selecting features based on correlation coefficients.

    This stage selects features by evaluating their correlation coefficients
    and retaining those that meet the specified criteria.

    Attributes:
        name (str): The name identifier for this stage.
        coef (float): The correlation coefficient threshold for feature selection.
        remaining_features (List[str]): List of features available for selection.
        used_features (List[str]): List of features that have been selected.
        final_model (BoostingBaseModel): The final model after feature selection.
    """

    name = "corr"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: Optional[FitterBase] = None,
        vectorization_name: str = None,
    ):
        """Initializes the CorrelationFeatureSelectionStage.

        Args:
            algo_info (AlgoInfo): Information about the algorithm.
            config (ConfigStorage): Configuration storage object.
            fitter (Optional[FitterBase], optional): Fitter instance. Defaults to None.
            vectorization_name (str, optional): Name for vectorization. Defaults to None.
        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
        )
        self.coef = config.stages.corr_selection.corr_coef
        self.remaining_features = config.data.columns.remaining_features

    def _fit(
        self,
        model: BoostingBaseModel,
        used_features: List[str],
        data_storage: DataSet,
        models: List[BoostingBaseModel] = None,
    ) -> BaseStage:
        """Fits the stage by selecting features based on correlation coefficients.

        Args:
            model (BoostingBaseModel): The boosting model to be used.
            used_features (List[str]): List of features currently in use.
            data_storage (DataSet): The dataset storage containing training and evaluation sets.
            models (List[BoostingBaseModel], optional): Additional models if any. Defaults to None.

        Returns:
            BaseStage: The current instance of the stage after fitting.

        Raises:
            ValueError: If the feature selection fails due to invalid parameters.
        """
        corr_coef_selection = CorrelationFeatureSelection(
            self.coef, used_features, self.remaining_features
        )
        eval_sets = data_storage.get_eval_set(used_features)
        corr_coef_selection.fit(*eval_sets["train"])
        self.used_features = sorted(corr_coef_selection.used_features)
        self.final_model = model
        return self