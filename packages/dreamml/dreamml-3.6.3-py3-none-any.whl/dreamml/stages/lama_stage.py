from typing import List, Union, Optional

from dreamml.configs.config_storage import ConfigStorage
from dreamml.data._dataset import DataSet
from dreamml.modeling.models.estimators import BaseModel
from dreamml.modeling.models.estimators._lightautoml import LAMA
from dreamml.stages.algo_info import AlgoInfo
from dreamml.stages.model_based_stage import ModelBasedStage
from dreamml.stages.stage import BaseStage
from dreamml.pipeline.fitter import FitterBase


class LAMAStage(ModelBasedStage):
    """A stage in the machine learning pipeline that utilizes the LAMA estimator.

    This stage is responsible for training and evaluating models using the LAMA
    estimator based on the provided configuration and algorithm information.
    """

    name = "LAMA"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: Optional[FitterBase] = None,
        vectorization_name: str = None,
    ):
        """Initializes the LAMAStage with algorithm information and configuration.

        Args:
            algo_info (AlgoInfo): Information about the algorithm to be used.
            config (ConfigStorage): Configuration storage containing pipeline settings.
            fitter (Optional[FitterBase], optional): An optional fitter instance. Defaults to None.
            vectorization_name (str, optional): The name of the vectorization method. Defaults to None.
        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
        )
        self.lama_time = config.pipeline.alt_mode.lama_time
        self.loss_function = config.pipeline.loss_function
        self.eval_metric = config.pipeline.eval_metric
        self.lama_conf = {
            "lama_time": self.lama_time,
            "loss_function": self.loss_function,
            "eval_metric": self.eval_metric,
        }

    def _set_used_features(self, data_storage: DataSet, used_features: List = None):
        """Determines and sets the features to be used for training.

        If no features are provided, it retrieves the feature list from the training data.
        Text features are excluded from the used features.

        Args:
            data_storage (DataSet): The dataset storage containing training and evaluation data.
            used_features (List, optional): A list of feature names to be used. Defaults to None.

        Returns:
            List: A list of feature names that will be used for training.
        """
        if not used_features:
            data = data_storage.get_eval_set(vectorization_name=self.vectorization_name)
            used_features = data["train"][0].columns.tolist()

        used_features = self._drop_text_features(data_storage, used_features)
        return used_features

    def _fit(
        self,
        model: BaseModel,
        used_features: List[str],
        data_storage: DataSet,
        models: List[BaseModel] = None,
    ) -> BaseStage:
        """Fits the LAMA model using the specified features and data.

        This method sets the used features, initializes the LAMA model with the
        configuration, fits the model on the training and validation data, and
        prepares the prediction output.

        Args:
            model (BaseModel): The base model to be used for training.
            used_features (List[str]): A list of feature names to be used for training.
            data_storage (DataSet): The dataset storage containing training and evaluation data.
            models (List[BaseModel], optional): A list of additional models. Defaults to None.

        Returns:
            BaseStage: The current instance of the stage after fitting the model.
        """
        self.used_features = self._set_used_features(
            data_storage=data_storage, used_features=used_features
        )
        self.start_model = LAMA(self.lama_conf)
        data = data_storage.get_eval_set(vectorization_name=self.vectorization_name)
        train = data["train"][0][self.used_features], data["train"][1]
        valid = data["valid"][0][self.used_features], data["valid"][1]
        self.start_model.fit(*train, *valid)
        self.final_model = self.start_model
        self.prediction = self.prediction_out(data_storage)

        return self