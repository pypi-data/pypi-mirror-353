from __future__ import annotations
from enum import Enum
import abc
import logging
from abc import ABC
from collections.abc import Mapping
from copy import deepcopy
from typing import Tuple, Dict, Optional, List, Any

import pandas as pd

from dreamml.logging import get_logger, get_propagate
from dreamml.features.feature_extraction._transformers import LogTargetTransformer
from dreamml.modeling.models.estimators import BaseModel
from dreamml.pipeline.fitter import FitterBase
from dreamml.stages.algo_info import AlgoInfo
from dreamml.data._dataset import DataSet
from dreamml.utils import ValidationType

from dreamml.configs.config_storage import ConfigStorage

_logger = get_logger(__name__)


class StageStatus(Enum):
    """
    Enumeration representing the status of a pipeline stage.

    Attributes:
        FITTED (str): Indicates that the stage has been successfully fitted.
        NOT_FITTED (str): Indicates that the stage has not been fitted yet.
        ERROR (str): Indicates that an error occurred during the fitting process.
    """

    FITTED = "fitted"
    NOT_FITTED = "not_fitted"
    ERROR = "error"  # TODO: currently not used. For future error handling in stages


class BaseStage(ABC):
    """
    Abstract base class for pipeline stages.

    All stages should inherit from this class and implement all abstract methods.
    Stages should be capable of accepting user configurations.
    Stages must have default configurations if user configurations are not provided.
    Stages should operate with an instance of the DataSet class.

    Attributes:
        name (str): The name of the stage.
    """

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: Optional[FitterBase] = None,
        vectorization_name: str = None,
    ):
        """
        Initializes the BaseStage with algorithm information and configuration.

        Args:
            algo_info (AlgoInfo): Information about the algorithm to be used.
            config (ConfigStorage): Configuration settings for the pipeline.
            fitter (Optional[FitterBase], optional): Fitter instance for model training. Defaults to None.
            vectorization_name (str, optional): Name of the vectorization method. Defaults to None.
        """
        self.experiment_path = None
        self.task = config.pipeline.task
        self.start_model = None
        self.final_model = None
        self.models = None
        # TODO Must be populated with used_features, possibly via an abstract set_used_features method
        self.used_features = None
        # TODO Must be populated with feature_importance
        self.feature_importance = None
        self.model_type = None
        self.prediction = None
        self.algo_info = algo_info
        self.random_stage = config.pipeline.reproducibility.random_seed
        self.is_fitted = False
        self.cv_mean_score = 0
        self.fitter = fitter
        self.metric_name = config.pipeline.eval_metric
        self.metric_params = config.pipeline.metric_params
        self.weights = None
        self.target_with_nan_values = (
            config.pipeline.task_specific.multilabel.target_with_nan_values
        )
        self._log_target_transformer = (
            LogTargetTransformer() if config.pipeline.preprocessing.log_target else None
        )
        self.parallelism = config.pipeline.parallelism
        self.vectorization_name = vectorization_name

        self._status: StageStatus = StageStatus.NOT_FITTED
        self._id: Optional[str] = None
        self._logger: Optional[logging.Logger] = None

    @property
    @abc.abstractmethod
    def name(self):
        """
        Abstract property that should return the name of the stage.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        raise NotImplementedError

    @property
    def id(self):
        """
        Gets the unique identifier of the stage.

        Raises:
            ValueError: If the `id` has not been set.

        Returns:
            Optional[str]: The unique identifier of the stage.
        """
        if self._id is None:
            raise ValueError(f"You must set `id` first.")
        return self._id

    @id.setter
    def id(self, new_id):
        """
        Sets the unique identifier of the stage.

        Args:
            new_id (str): The new unique identifier to be set.
        """
        self._id = new_id

    @property
    def status(self):
        """
        Gets the current status of the stage.

        Returns:
            StageStatus: The current status of the stage.
        """
        return self._status

    @status.setter
    def status(self, new_status: StageStatus):
        """
        Sets the current status of the stage.

        Args:
            new_status (StageStatus): The new status to be set.

        Raises:
            ValueError: If `new_status` is not an instance of StageStatus.
        """
        if isinstance(new_status, StageStatus):
            self._status = new_status
        else:
            raise ValueError(
                f"{new_status=} is expected to be an instance of {StageStatus}"
            )

    def _init_model(
        self,
        used_features: list,
        hyperparams: Mapping[str, Any] = None,
        fix_stage: bool = None,
    ) -> BaseModel:
        """
        Initializes a model based on the algorithm information.

        Args:
            used_features (list): List of features to be used by the model.
            hyperparams (Mapping[str, Any], optional): Hyperparameters for the model. Defaults to None.
            fix_stage (bool, optional): If True, fixed parameters are used. Defaults to None.

        Returns:
            BaseModel: The initialized model.

        Raises:
            Any exceptions raised by the model initialization process.
        """
        self.model_type = self.algo_info.algo_class

        if fix_stage:
            estimator_params = deepcopy(self.algo_info.fixed_params)
        else:
            estimator_params = deepcopy(self.algo_info.algo_params)

        if hyperparams:
            for param in hyperparams:
                if param == "n_estimators":
                    logging.debug(
                        f"{estimator_params.get(param)=} left as is. Skipping value in _init_model {hyperparams[param]=}."
                    )

                    continue

                estimator_params[param] = hyperparams[param]

        return self.model_type(
            estimator_params=estimator_params,
            task=self.task,
            used_features=used_features,
            categorical_features=self.algo_info.cat_features,
            metric_name=self.metric_name,
            metric_params=self.metric_params,
            weights=self.weights,
            target_with_nan_values=self.target_with_nan_values,
            log_target_transformer=self._log_target_transformer,
            parallelism=self.parallelism,
            train_logger=self._logger,
            vectorization_name=self.vectorization_name,
            text_features=self.algo_info.text_features,
            augmentation_params=self.algo_info.augmentation_params,
        )

    def init_logger(self, log_file: Optional[str] = None):
        """
        Initializes the logger for the stage.

        Args:
            log_file (Optional[str], optional): Path to the log file. If provided, logs will be written to this file. Defaults to None.

        Raises:
            ValueError: If the stage `id` has not been set prior to initializing the logger.
        """
        if self._id is None:
            raise ValueError(
                "To initialize stage logger you must set stage.id to some unique value in the current run."
            )

        self._logger = logging.getLogger(f"{__name__}.{self.id}")
        self._logger.propagate = get_propagate()

        if len(self._logger.handlers) > 0:
            handlers = self._logger.handlers
            for handler in handlers:
                self._logger.removeHandler(handler)

        if log_file is not None:
            formatter = logging.Formatter(
                fmt="[%(asctime)s] - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler = logging.FileHandler(log_file, delay=True)
            file_handler.setFormatter(formatter)

            self._logger.addHandler(file_handler)

    def fit_transform(
        self,
        model: BaseModel,
        used_features: list,
        data_storage: DataSet,
        models: list = None,
    ) -> Tuple[BaseModel, list, pd.DataFrame, pd.DataFrame, list]:
        """
        Fits the model and transforms the data during pipeline execution.

        This method is called for each stage during pipeline execution.

        Args:
            model (BaseModel): An instance of the model.
            used_features (list): List of features used for training.
            data_storage (DataSet): Data for training the model.
            models (list, optional): List of models obtained from cross-validation folds. Defaults to None.

        Returns:
            Tuple[BaseModel, list, pd.DataFrame, pd.DataFrame, list]:
                - Trained model.
                - List of used features.
                - Feature importance DataFrame.
                - Predictions DataFrame.
                - List of models from cross-validation.
        """
        return self.fit(
            model=model,
            used_features=used_features,
            data_storage=data_storage,
            models=models,
        ).transform()

    @abc.abstractmethod
    def _fit(
        self,
        model: BaseModel,
        used_features: List[str],
        data_storage: DataSet,
        models: List[BaseModel] = None,
    ) -> BaseStage:
        """
        Abstract factory method to fit the stage.

        This method is called by the `fit` method and should be implemented by each stage.

        Args:
            model (BaseModel): Wrapper over sklearn-like models.
            used_features (List[str]): List of features used for training.
            data_storage (DataSet): Object containing information about training and testing datasets.
            models (List[BaseModel], optional): List of models obtained from each cross-validation fold. Defaults to None.

        Returns:
            BaseStage: The fitted stage instance.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        # TODO Retrieve cv_score in each stage within this method
        raise NotImplementedError

    def fit(
        self,
        model: BaseModel,
        used_features: Optional[list],
        data_storage: DataSet,
        models=None,
    ) -> BaseStage:
        """
        Fits the stage using the provided model and data.

        This method calls the `_fit` factory method and sets the `is_fitted` flag upon successful fitting.
        It is invoked by the `fit_transform` method.

        Args:
            model (BaseModel): Wrapper over sklearn-like models.
            used_features (Optional[list]): List of features used for training.
            data_storage (DataSet): Object containing information about training and testing datasets.
            models (list, optional): List of models obtained from cross-validation folds. Defaults to None.

        Returns:
            BaseStage: The current instance of the stage.

        Raises:
            Any exceptions raised during the fitting process.
        """
        if self.is_fitted:
            return self

        logger = self._logger or _logger
        # logger.monitor("Start fitting stage")
        self._fit(
            model=model,
            used_features=used_features,
            data_storage=data_storage,
            models=models,
        )
        if self.fitter is not None and self.fitter.validation_type == ValidationType.CV:
            self.cv_mean_score = self.fitter.cv_mean_score
        self.is_fitted = True
        return self

    def transform(self) -> Tuple[BaseModel, list, pd.DataFrame, pd.DataFrame, list]:
        """
        Transforms the data after fitting.

        Returns:
            Tuple[BaseModel, list, pd.DataFrame, pd.DataFrame, list]:
                - Final trained model.
                - List of used features.
                - Feature importance DataFrame.
                - Predictions DataFrame.
                - List of models from cross-validation.
        """
        return (
            self.final_model,
            self.used_features,
            self.feature_importance,
            self.prediction,
            self.models,
        )

    def prediction_out(self, dataset: DataSet) -> Dict[str, Any]:
        """
        Generates predictions for the provided dataset.

        Args:
            dataset (DataSet): Dictionary where the key is the name of the sample and the value is a tuple containing
                               the feature matrix and the true target values.

        Returns:
            Dict[str, Any]: Dictionary containing predictions for each sample.

        Raises:
            Any exceptions raised during the prediction process.
        """
        prediction_dict = {}
        used_features = self.used_features
        eval_set = dataset.get_eval_set(
            used_features, vectorization_name=self.vectorization_name
        )

        if self.task in ("amts", "amts_ad"):
            if self.final_model.model_name == "nbeats_revin":
                return prediction_dict
            eval_set = dataset.get_amts_data()

        if ("valid" in eval_set) and (len(eval_set["valid"][0]) == 0):
            del eval_set["valid"]
        for sample in eval_set:
            data, target = eval_set[sample]
            prediction = self.final_model.transform(data)
            prediction_dict[sample] = prediction
        return prediction_dict

    def _drop_text_features(
        self, data_storage: DataSet, used_features: Optional[List[str]]
    ) -> Optional[List[str]]:
        """
        Drops text features from the list of used features.

        Args:
            data_storage (DataSet): The data storage containing feature information.
            used_features (Optional[List[str]]): The current list of used features.

        Returns:
            Optional[List[str]]: The updated list of used features with text features removed, or None if no features remain.
        """
        if used_features is not None:
            drop_text_features = (
                data_storage.text_features_preprocessed + data_storage.text_features
            )
            used_features = [
                feature
                for feature in used_features
                if feature not in drop_text_features
            ]
            if len(used_features) == 0:
                used_features = None
        return used_features