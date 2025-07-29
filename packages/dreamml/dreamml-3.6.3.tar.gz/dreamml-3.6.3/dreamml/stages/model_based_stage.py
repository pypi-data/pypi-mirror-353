from __future__ import annotations

from abc import ABC
from typing import List

from dreamml.configs.config_storage import ConfigStorage
from dreamml.stages.algo_info import AlgoInfo
from dreamml.modeling.metrics.metrics_mapping import metrics_mapping
from dreamml.stages.stage import BaseStage

from dreamml.modeling.models.estimators import BaseModel
from dreamml.data._dataset import DataSet
from dreamml.pipeline.fitter import FitterBase


class ModelBasedStage(BaseStage, ABC):
    """
    Abstract class for stages that require a trained model to execute a factory method.
    Utilizes a fitter to train the model either on Hold-Out (HO) or Cross-Validation (CV).

    Args:
        algo_info (AlgoInfo): Information about the algorithm.
        config (ConfigStorage): Configuration storage containing pipeline settings.
        fitter (FitterBase): Fitter instance used to train the model.
        vectorization_name (str, optional): Name of the vectorization technique. Defaults to None.
    """

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
        self.eval_metric = metrics_mapping.get(config.pipeline.eval_metric)(
            task=config.pipeline.task, **config.pipeline.metric_params
        )
        self.metric_params = config.pipeline.metric_params


class BaseModelStage(ModelBasedStage):
    """
    A simple model training stage using the specified features.
    """

    name = "base"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: FitterBase,
        vectorization_name: str,
    ):
        """
        Initializes the BaseModelStage with the provided algorithm information, configuration, fitter, and vectorization name.

        Args:
            algo_info (AlgoInfo): Information about the algorithm.
            config (ConfigStorage): Configuration storage containing pipeline settings.
            fitter (FitterBase): Fitter instance used to train the model.
            vectorization_name (str): Name of the vectorization technique.
        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
        )
        self.config = config

    def _set_used_features(self, data_storage: DataSet, used_features: List[str] = None) -> List[str]:
        """
        Determines and sets the features to be used for training the model based on the data storage and configuration.

        Args:
            data_storage (DataSet): The dataset storage containing training and evaluation data.
            used_features (List[str], optional): A list of features to be used. Defaults to None.

        Returns:
            List[str]: A list of feature names to be used for model training.
        """
        if self.config.task in ["amts", "amts_ad"]:
            data = data_storage.get_eval_set(vectorization_name=self.vectorization_name)
            used_features = data["amts_final_data"]["train"][0].columns.tolist()
            return used_features

        used_features = None
        if not used_features:
            data = data_storage.get_eval_set(vectorization_name=self.vectorization_name)

            if self.vectorization_name == "bow":
                used_features = list(data["train"][0].keys())
            else:
                used_features = data["train"][0].columns.tolist()
        # FIXME 2601
        if self.vectorization_name != "bow":
            used_features = self._drop_text_features(data_storage, used_features)

        if "bertopic" in self.config.pipeline.model_list:
            used_features = data["train"][0].columns.tolist()

        return used_features

    def _fit(
        self,
        model: BaseModel,
        used_features: List[str],
        data_storage: DataSet,
        models: List[BaseModel] = None,
    ) -> BaseStage:
        """
        Fits the model using the specified features and data storage.

        Args:
            model (BaseModel): The model to be trained.
            used_features (List[str]): The list of features to be used for training.
            data_storage (DataSet): The dataset storage containing training data.
            models (List[BaseModel], optional): Additional models for training. Defaults to None.

        Returns:
            BaseStage: The current stage instance after fitting the model.
        """
        self.used_features = self._set_used_features(
            data_storage=data_storage, used_features=used_features
        )
        self.start_model = self._init_model(used_features=self.used_features)
        self.final_model, self.models, _ = self.fitter.train(
            estimator=self.start_model,
            data_storage=data_storage,
            metric=self.eval_metric,
            used_features=self.used_features,
            vectorization_name=self.vectorization_name,
        )
        self.final_model.used_features = self.used_features
        if self.final_model.model_name not in ["bert", "ae", "vae", "iforest"]:
            self.prediction = self.prediction_out(data_storage)
        else:
            self.prediction = {}
        return self

    def _set_params(self):
        """
        Sets the parameters for the model stage.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        raise NotImplementedError