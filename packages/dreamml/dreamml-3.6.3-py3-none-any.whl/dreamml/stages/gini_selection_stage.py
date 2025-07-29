from typing import Type, List, Optional

from dreamml.configs.config_storage import ConfigStorage
from dreamml.features.feature_selection._gini_importance import compare_gini_features
from dreamml.pipeline.fitter import FitterBase
from dreamml.stages.algo_info import AlgoInfo
from dreamml.stages.stage import BaseStage
from dreamml.data._dataset import DataSet
from dreamml.stages.feature_based_stage import FeatureBasedStage
from dreamml.modeling.models.estimators import BoostingBaseModel


class GiniSelectionStage(FeatureBasedStage):
    """Feature selection stage based on Gini Importance.

    This stage selects features by evaluating their importance using the Gini
    importance metric. It filters out less important features based on predefined
    thresholds and differences.

    Attributes:
        name (str): The name of the stage.
        gini_threshold (float): The threshold for Gini importance.
        categorical_features (List[str]): List of categorical feature names.
        remaining_features (List[str]): List of remaining feature names after selection.
        valid_sample (int): The size of the valid sample for selection.
        gini_absolute_diff (float): The absolute difference threshold for Gini importance.
        gini_relative_diff (float): The relative difference threshold for Gini importance.
        final_model (BoostingBaseModel): The final fitted model.
        feature_importance (dict): Importance scores of the features.
        used_features (List[str]): List of features used after selection.
    """

    name = "gini"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: Optional[FitterBase] = None,
        vectorization_name: str = None,
    ):
        """Initializes the GiniSelectionStage.

        Args:
            algo_info (AlgoInfo): Information about the algorithm.
            config (ConfigStorage): Configuration storage containing various settings.
            fitter (Optional[FitterBase], optional): Fitter object for model training. Defaults to None.
            vectorization_name (str, optional): Name of the vectorization process. Defaults to None.
        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
        )
        self.gini_threshold = config.stages.gini_selection.gini_threshold
        self.categorical_features = []
        self.remaining_features = config.data.columns.remaining_features
        self.valid_sample = config.stages.gini_selection.gini_selector_valid_sample
        self.gini_absolute_diff = (
            config.stages.gini_selection.gini_selector_abs_difference
        )
        self.gini_relative_diff = (
            config.stages.gini_selection.gini_selector_rel_difference
        )

    def _set_params(self, params: dict):
        """Sets parameters for the Gini selection stage.

        Args:
            params (dict): A dictionary of parameters to set.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError

    def _fit(
        self,
        model: BoostingBaseModel,
        used_features: List[str],
        data_storage: DataSet,
        models: List[BoostingBaseModel] = None,
    ) -> BaseStage:
        """Fits the Gini selection stage using the provided model and data.

        This method evaluates feature importance based on Gini importance and
        selects the most significant features according to the configured thresholds
        and differences.

        Args:
            model (BoostingBaseModel): The boosting model used for feature importance evaluation.
            used_features (List[str]): A list of feature names to consider for selection.
            data_storage (DataSet): The dataset containing the data for evaluation.
            models (List[BoostingBaseModel], optional): A list of additional models. Defaults to None.

        Returns:
            BaseStage: The fitted Gini selection stage instance.
        """
        eval_sets = data_storage.get_eval_set(
            used_features, vectorization_name=self.vectorization_name
        )
        self.final_model = model
        self.categorical_features = data_storage.cat_features
        conf = {
            "gini_threshold": self.gini_threshold,
            "categorical_features": self.categorical_features,
            "valid_sample": self.valid_sample,
            "gini_absolute_diff": self.gini_absolute_diff,
            "gini_relative_diff": self.gini_relative_diff,
            "remaining_features": self.remaining_features,
        }
        feature_importance, u_features = compare_gini_features(eval_sets, conf)
        final_features = list(sorted(u_features))
        self.feature_importance = feature_importance
        self.used_features = final_features
        return self