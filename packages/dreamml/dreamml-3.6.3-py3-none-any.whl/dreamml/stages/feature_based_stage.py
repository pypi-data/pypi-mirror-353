from abc import ABC
from typing import Optional

from dreamml.data._dataset import DataSet
from dreamml.modeling.models.estimators import BaseModel
from dreamml.configs.config_storage import ConfigStorage
from dreamml.pipeline.fitter import FitterBase
from dreamml.stages.algo_info import AlgoInfo
from dreamml.stages.stage import BaseStage, StageStatus


class SharedStateMixin:
    """Mixin class to manage shared state across class instances.

    This mixin provides methods to set and get shared state, ensuring that all instances
    of a class share the same state information.
    """

    _shared_state = {}

    @classmethod
    def _set_shared_state(cls, state):
        """Set the shared state for the class.

        Args:
            state (dict): The state to be shared across all instances of the class.
        """
        cls._shared_state[cls] = state

    @classmethod
    def _get_shared_state(cls, default=None):
        """Retrieve the shared state for the class.

        Args:
            default (Optional[dict], optional): The default state to return if no shared state exists. Defaults to None.

        Returns:
            Optional[dict]: The shared state if it exists, otherwise the default value.
        """
        return cls._shared_state.get(cls, default)


class FeatureBasedStage(BaseStage, SharedStateMixin, ABC):
    """Abstract class for stages that do not require a trained model to execute the factory method.

    Models are not trained within these stages, and a single state is maintained across all instances
    of the class.
    """

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: Optional[FitterBase] = None,
        vectorization_name: str = None,
    ):
        """Initialize the FeatureBasedStage.

        Args:
            algo_info (AlgoInfo): Information about the algorithm.
            config (ConfigStorage): Configuration storage object.
            fitter (Optional[FitterBase], optional): Fitter instance. Defaults to None.
            vectorization_name (str, optional): Name of the vectorization method. Defaults to None.
        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
        )
        self.prediction = None

    def fit(
        self,
        model: BaseModel,
        used_features: Optional[list],
        data_storage: DataSet,
        models=None,
    ):
        """Fit the stage with the provided model and data.

        If the stage has already been fitted and the shared state indicates completion, it retrieves
        the stored state. Otherwise, it proceeds to fit the stage and updates the shared state.

        Args:
            model (BaseModel): The model to be used for fitting.
            used_features (Optional[list]): A list of features to be used. Defaults to None.
            data_storage (DataSet): The dataset containing the data.
            models (optional): Additional models if any. Defaults to None.

        Returns:
            self: The instance of the stage after fitting.
        """
        shared_state = self._get_shared_state(default={})

        if shared_state.get("status") == StageStatus.FITTED:
            self._status = shared_state["status"]
            self.final_model = shared_state["final_model"]
            self.used_features = shared_state["used_features"]
            self.feature_importance = shared_state["feature_importance"]
            self.prediction = shared_state["prediction"]
            self.models = shared_state["models"]

            return self
        else:
            super().fit(
                model=model,
                used_features=used_features,
                data_storage=data_storage,
                models=models,
            )

            new_state = {
                "status": self._status,
                "final_model": self.final_model,
                "used_features": self.used_features,
                "feature_importance": self.feature_importance,
                "prediction": self.prediction,
                "models": self.models,
            }

            self._set_shared_state(new_state)

            return self