from typing import List, Optional
import numpy as np
from sklearn.exceptions import NotFittedError
from xgboost.core import XGBoostError

from dreamml.configs.config_storage import ConfigStorage
from dreamml.data._dataset import DataSet
from dreamml.logging import get_logger
from dreamml.modeling.models.boostaroota import BoostARoota
from dreamml.modeling.models.estimators import BoostingBaseModel
from dreamml.pipeline.fitter import FitterBase
from dreamml.stages.feature_based_stage import FeatureBasedStage
from dreamml.stages.algo_info import AlgoInfo
from dreamml.stages.stage import BaseStage, StageStatus

_logger = get_logger(__name__)


class BoostARootaStage(FeatureBasedStage):
    """Stage for feature selection using the BoostARoota algorithm.

    This stage performs feature selection based on the BoostARoota algorithm,
    integrating it into the machine learning pipeline to select the most
    relevant features for model training.

    Attributes:
        name (str): The name of the stage.
        config_storage (ConfigStorage): Configuration storage instance.
        predictions (Optional[Any]): Predictions made by the model, if any.
        final_model (BoostingBaseModel): The trained boosting model.
        is_fitted (bool): Indicates whether the stage has been fitted.
        used_features (List[str]): List of features selected for model training.
        feature_importance (Optional[Any]): Feature importance metrics.
        models (Optional[List[BoostingBaseModel]]): List of models from cross-validation.
    """

    name = "boostaroota"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: Optional[FitterBase] = None,
        vectorization_name: str = None,
    ):
        """Initializes the BoostARootaStage.

        Args:
            algo_info (AlgoInfo): Information about the algorithm.
            config (ConfigStorage): Configuration storage instance.
            fitter (Optional[FitterBase], optional): Fitter instance. Defaults to None.
            vectorization_name (str, optional): Name for vectorization. Defaults to None.
        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
        )
        self.config_storage = config
        self.predictions = None

    @property
    def check_is_fitted(self):
        """Checks if the estimator has been fitted.

        Raises:
            NotFittedError: If the estimator is not yet fitted.

        Returns:
            bool: True if the estimator is fitted.
        """
        if not self.is_fitted:
            msg = (
                "This estimator is not fitted yet. Call 'fit' with "
                "appropriate arguments before using this estimator."
            )
            raise NotFittedError(msg)
        return True

    def _set_used_features(self, data_storage: DataSet, used_features: List = None) -> List[str]:
        """Sets the used features for the stage.

        If no features are provided, it retrieves the feature list from the
        evaluation set. Text features are dropped from the selected features.

        Args:
            data_storage (DataSet): Instance of the data storage.
            used_features (List, optional): List of features to use. Defaults to None.

        Returns:
            List[str]: List of features to be used after processing.
        """
        if not used_features:
            data = data_storage.get_eval_set(vectorization_name=self.vectorization_name)
            used_features = data["train"][0].columns.tolist()

        used_features = self._drop_text_features(data_storage, used_features)
        return used_features

    def _fit(
        self,
        model: BoostingBaseModel,
        used_features: List[str],
        data_storage: DataSet,
        models: List[BoostingBaseModel] = None,
    ) -> BaseStage:
        """Fits the stage using the provided model and data.

        This method performs feature selection using BoostARoota and fits the
        boosting model. It handles multiple iterations of BoostARoota to refine
        the feature set based on the configured parameters.

        Args:
            model (BoostingBaseModel): Instance of the boosting model to train.
            used_features (List[str]): List of features to use for training.
            data_storage (DataSet): Data storage instance containing the dataset.
            models (List[BoostingBaseModel], optional): List of models from cross-validation. Defaults to None.

        Returns:
            BaseStage: The fitted stage instance.

        Raises:
            XGBoostError: If BoostARoota encounters an error during fitting.
        """
        logger = self._logger or _logger

        if self._status != StageStatus.FITTED:
            np.random.seed(self.config_storage.pipeline.reproducibility.random_seed)
            self.used_features = self._set_used_features(
                data_storage=data_storage, used_features=used_features
            )
            min_n_features_to_stop = (
                self.config_storage.stages.boostaroota.min_n_features_to_stop
            )  # default - 60
            min_n_features_to_start = (
                self.config_storage.stages.boostaroota.min_n_features_to_start
            )  # default - 100
            max_boostaroota_stage_iters = (
                self.config_storage.stages.boostaroota.max_boostaroota_stage_iters
            )  # default - 3
            data = data_storage.get_eval_set(
                self.used_features, vectorization_name=self.vectorization_name
            )
            if (
                self.config_storage.data.use_sampling
                and data_storage.get_dev_n_samples() >= 250000
            ):
                data["train"] = data_storage.sample(
                    self.used_features, vectorization_name=self.vectorization_name
                )
            br = BoostARoota
            br_params, _ = self.config_storage.models.boostaroota.params
            if self.config_storage.stages.boostaroota.boostaroota_type != "default":
                br_params["clf"] = "LGBM"
                br_params["shap_flag"] = True

            if isinstance(min_n_features_to_start, str):
                pass
            elif len(self.used_features) <= min_n_features_to_start:
                logger.info(
                    f"\nNumber of features is less than required for selection. Feature selection was not performed.\n"
                    f"Features available for modeling: {len(self.used_features)}; "
                    f"Selection required if more than: {min_n_features_to_start}\n"
                )
            else:
                i = 0
                selected_features = []
                while i < max_boostaroota_stage_iters:
                    br_model = br(**br_params, logger=self._logger)
                    try:
                        br_model.fit(x=data["train"][0], y=data["train"][1])
                        selected_features = br_model.keep_vars_.values.tolist()
                        if len(selected_features) >= min_n_features_to_stop:
                            break
                    except XGBoostError as e:
                        logger.info(
                            f"{e}\n"
                            f"Parameter 'cutoff' increased to {br_params['cutoff'] * 2}"
                        )
                    br_params["cutoff"] *= 2
                    i += 1

                if len(selected_features) >= min_n_features_to_stop:
                    self.used_features = selected_features

                logger.info(
                    f"\nBoostARoota algorithm selected {len(self.used_features)} features\n"
                    f"With parameters:\n"
                    f"\tcutoff: {br_params['cutoff']}\n"
                    f"\titers: {br_params['iters']}\n"
                    f"\tmax_rounds: {br_params['max_rounds']}\n"
                    f"\tdelta: {br_params['delta']}\n"
                )

            self.final_model = model
            self.is_fitted = True

        return self

    def transform(self):
        """Transforms the data using the fitted stage.

        Checks if the stage has been fitted and then returns the transformed
        components including the final model, selected features, feature
        importance, predictions, and any cross-validation models.

        Returns:
            tuple: A tuple containing:
                - final_model (BoostingBaseModel): The trained boosting model.
                - used_features (List[str]): List of selected features.
                - feature_importance (Optional[Any]): Feature importance metrics.
                - predictions (Optional[Any]): Model predictions.
                - models (Optional[List[BoostingBaseModel]]): List of cross-validation models.
        """
        self.check_is_fitted
        return (
            self.final_model,
            self.used_features,
            self.feature_importance,
            self.predictions,
            self.models,
        )

    def _set_params(self, params: dict):
        """Sets parameters for the stage.

        This method is not implemented and will raise a NotImplementedError
        when called.

        Args:
            params (dict): Dictionary of parameters to set.

        Raises:
            NotImplementedError: Always raised to indicate the method is not implemented.
        """
        raise NotImplementedError