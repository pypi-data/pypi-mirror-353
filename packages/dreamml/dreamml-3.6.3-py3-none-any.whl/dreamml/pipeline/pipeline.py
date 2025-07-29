import time
import warnings
from pathlib import Path

from typing import Optional, Type

from dreamml.data._dataset import DataSet
from dreamml.logging.monitoring import (
    PipelineStartedLogData,
    PipelineFinishedLogData,
    StageFinishedLogData,
)
from dreamml.modeling.cv import BaseCrossValidator
from dreamml.modeling.metrics import metrics_mapping
from dreamml.pipeline.cv_score import CVScores
from dreamml.configs.config_storage import ConfigStorage
from dreamml.stages.stage import StageStatus
from dreamml.stages.stage_generator.registry import estimators_registry
from dreamml.utils.saver import ArtifactSaver
from dreamml.pipeline.check_point import CheckPoint
from dreamml.stages.stage_generator import StageGenerator
from dreamml.utils import ValidationType
from dreamml.utils.warnings import DMLWarning
from dreamml.logging import get_logger, get_root_logger, log_exceptions

_logger = get_logger(__name__)


class MainPipeline:
    """
    MainPipeline manages the execution of the machine learning pipeline, including data transformation,
    model training, and evaluation.

    Attributes:
        config_storage (ConfigStorage): The configuration storage for the pipeline.
        data_storage (DataSet): The dataset used for the pipeline.
        artifact_saver (Optional[ArtifactSaver]): The artifact saver for saving pipeline artifacts.
        custom_cv (Optional[Type[BaseCrossValidator]]): Custom cross-validator class.
        total_estimator_dict (dict): Dictionary to store estimators for each stage.
        total_used_features_dict (dict): Dictionary to store used features for each stage.
        total_feature_importance_dict (dict): Dictionary to store feature importance for each stage.
        total_predictions_dict (dict): Dictionary to store predictions for each stage.
        prepared_model_dict (dict): Dictionary to store prepared models.
        other_model_dict (dict): Dictionary to store additional models.
        oot_potential (tuple): Out-of-time potential metrics.
        experiment_path (Optional[str]): Path to the experiment directory.
        pipeline_params (Optional[dict]): Parameters of the pipeline.
        total_cv_scores (dict): Cross-validation scores for each stage.
        prepared_cv_scores (CVScores): Prepared cross-validation scores.
        total_vectorizers_dict (dict): Dictionary to store vectorizers for each stage.
        text_transformers_dict (dict): Dictionary to store text transformers for each stage.
    """

    def __init__(
        self,
        config_storage: ConfigStorage,
        data_storage: DataSet,
        artifact_saver: Optional[ArtifactSaver] = None,
        custom_cv: Optional[Type[BaseCrossValidator]] = None,
    ):
        """
        Initializes the MainPipeline with the given configuration and data storage.

        Args:
            config_storage (ConfigStorage): The configuration storage for the pipeline.
            data_storage (DataSet): The dataset used for the pipeline.
            artifact_saver (Optional[ArtifactSaver], optional): The artifact saver for saving pipeline artifacts.
                Defaults to None.
            custom_cv (Optional[Type[BaseCrossValidator]], optional): Custom cross-validator class.
                Defaults to None.

        Raises:
            TypeError: If the provided custom_cv is not a subclass of BaseCrossValidator.
        """
        self.config_storage = config_storage
        self.data_storage = data_storage
        self.artifact_saver = artifact_saver
        self.total_estimator_dict = {}
        self.total_used_features_dict = {}
        self.total_feature_importance_dict = {}
        self.total_predictions_dict = {}
        self.prepared_model_dict = {}
        self.other_model_dict = {}
        self.oot_potential = ()
        self.experiment_path = None
        self.pipeline_params = None
        self.total_cv_scores = {}
        self.prepared_cv_scores = CVScores()
        self.custom_cv = custom_cv
        self.total_vectorizers_dict = {}
        self.text_transformers_dict = {}

        if (
            self.config_storage.pipeline.task in ["regression", "timeseries"]
            and "dtree" not in self.config_storage.pipeline.stage_list
        ):
            warnings.warn(
                "Стейдж `dtree` должен быть в списке стейджей для составления отчета.",
                DMLWarning,
                stacklevel=2,
            )

        if (
            self.config_storage.pipeline.subtask == "nlp"
            and self.data_storage.text_transformer
        ):
            self.text_transformers_dict["vectorization_text_transformer"] = (
                self.data_storage.text_transformer
            )

        # Запишем в конфиг, чтобы можно было отследить использование в эксперименте
        self.config_storage.data.splitting.custom_cv = custom_cv is not None

        if self.custom_cv is not None:
            self._check_custom_cv()

    @log_exceptions(_logger)
    def _check_custom_cv(self):
        """
        Validates the custom cross-validator to ensure it inherits from BaseCrossValidator.

        Raises:
            TypeError: If custom_cv does not inherit from BaseCrossValidator.
        """
        if not issubclass(self.custom_cv, BaseCrossValidator):
            raise TypeError(
                f"Класс для кросс-валидации должен быть унаследован от dreamml.modeling.cv.BaseCrossValidator, "
                f"но передан {self.custom_cv.__name__}."
            )

    def transform(self):
        """
        Executes the transformation pipeline, including model fitting, transformation, and evaluation.
        
        This method handles the initialization of artifacts, logging, checkpointing, and the iterative
        processing of each stage in the pipeline. It manages estimators, feature selection, predictions,
        and cross-validation scores.

        Raises:
            Various exceptions that may occur during pipeline execution.
        """
        pipeline_start_time = time.time()

        if self.artifact_saver is None:
            self.artifact_saver = ArtifactSaver(config=self.config_storage)

        if self.config_storage.pipeline.check_point_path:
            self.experiment_path = self.config_storage.pipeline.check_point_path
            self.artifact_saver._experiment_path = self.experiment_path

            name = Path(self.experiment_path).name
            self.artifact_saver._run_number = (
                self.artifact_saver.get_run_number_from_experiment_dir(name)
            )
        else:
            self.artifact_saver.create_experiment_dir()
            self.experiment_path = self.artifact_saver.experiment_path

        experiment_name = Path(self.experiment_path).name

        _logger.monitor(
            f"Starting pipeline. Using directory for saving: {self.experiment_path}",
            extra={
                "log_data": PipelineStartedLogData(
                    experiment_name=experiment_name,
                    from_checkpoint=bool(self.config_storage.pipeline.check_point_path),
                    user_config=self.config_storage._user_config,
                )
            },
        )

        root_logger = get_root_logger()
        log_dir_path = Path(self.experiment_path) / "logs"
        root_logger.set_experiment_log_file(log_dir_path / "run.log")
        _logger.info(f"Saving detailed logs to {log_dir_path}")

        cpt = CheckPoint(experiment_path=self.experiment_path)
        generator = StageGenerator(
            config=self.config_storage,
            experiment_path=self.experiment_path,
            custom_cv=self.custom_cv,
        )

        self.pipeline_params = generator.get_pipeline_params(
            data_storage=self.data_storage
        )

        if self.config_storage.pipeline.check_point_path:
            self.pipeline_params = cpt.load_pipeline_params()

        estimator, used_features, feature_importance, predictions, cv_estimators = (
            None,
            None,
            None,
            None,
            None,
        )

        self._check_available_metrics()

        for i, stage_name in enumerate(self.pipeline_params):
            stage = self.pipeline_params[stage_name]["stage"]

            log_msg = f"Starting stage '{stage.name}'."

            if (
                stage.algo_info.algo_class.model_name.lower() in ["pyboost", "xgboost"]
                and stage.name.find("batch") != -1
            ):
                # заглушка, стейдж BatchN теперь работает для PyBoost через апроксимацию shap_values
                # через permutation, но долгий, поэтому пока используется только для тестирования
                _logger.warning(
                    f"Stage '{stage.name}' for model '{stage.algo_info.algo_class.model_name}' "
                    f"is not supported, skipping..."
                )
                continue

            if i % len(self.config_storage.pipeline.stage_list) == 0 and i != 0:
                log_msg += f"\n\nMoving to '{stage.algo_info.algo_class.model_name}'.\n"

            _logger.info(log_msg)

            stage_start_time = time.time()
            if stage.status == StageStatus.NOT_FITTED:
                (
                    estimator,
                    used_features,
                    feature_importance,
                    predictions,
                    cv_estimators,
                ) = stage.fit_transform(
                    model=estimator,
                    models=cv_estimators,
                    data_storage=self.data_storage,
                    used_features=used_features,
                )
                stage.status = StageStatus.FITTED
                cpt.save_stage(stage_name, stage, self.pipeline_params)

                debug_msg = f"Stage_name: {stage_name} -"
                if used_features is not None:
                    debug_msg += (
                        f" used_features: {len(used_features)} {used_features[:5]}"
                    )
                else:
                    debug_msg += f" Used_features is None"
                _logger.debug(debug_msg)

            elif stage.status == StageStatus.FITTED:
                stage = cpt.load_stage(
                    stage_name
                )  # FIXME: загружается то, что уже загружено в pipeline_params?
                (
                    estimator,
                    used_features,
                    feature_importance,
                    predictions,
                    cv_estimators,
                ) = stage.transform()

            stage_elapsed_time = time.time() - stage_start_time
            _logger.monitor(
                f"Stage {stage.name} finished in {stage_elapsed_time:.1f} seconds.",
                extra={
                    "log_data": StageFinishedLogData(
                        experiment_name=experiment_name,
                        stage_name=stage.name,
                        stage_id=stage.id,
                        elapsed_time=stage_elapsed_time,
                    )
                },
            )

            self.total_estimator_dict[stage_name] = estimator
            self.total_used_features_dict[stage_name] = used_features
            self.total_feature_importance_dict[stage_name] = feature_importance
            self.total_predictions_dict[stage_name] = predictions
            if (
                stage.fitter is not None
                and stage.fitter.validation_type == ValidationType.CV
            ):
                self.total_cv_scores[stage_name] = stage.cv_mean_score

            if hasattr(stage, "stage_all_models_dict"):
                self.other_model_dict.update(stage.stage_all_models_dict)
                self.prepared_cv_scores.other_models.update(stage.all_cv_mean_scores)

            if hasattr(stage, "vectorizer") and stage.vectorizer is not None:
                if (
                    hasattr(stage.vectorizer, "model_path")
                    and stage.vectorizer.model_path is not None
                ):
                    # Удаляем модель для экономии места
                    stage.vectorizer.vectorizer = None
                    log_msg = f"Из векторизатора {stage.vectorizer.name} удалена загруженная модель для экономии места."
                    _logger.debug(log_msg)

                self.total_vectorizers_dict[
                    f"{stage.name}_{stage.vectorizer.name}_vectorizer"
                ] = stage.vectorizer

            if (
                hasattr(stage, "text_transformer")
                and stage.text_transformer is not None
            ):
                self.text_transformers_dict[f"{stage.name}_text_transformer"] = (
                    stage.text_transformer
                )

        for stage_name, model in self.total_estimator_dict.items():
            stage = self.pipeline_params[stage_name]["stage"]
            if model:
                vectorization_name = (
                    model.vectorization_name
                    if hasattr(model, "vectorization_name")
                    else None
                )
                name = f"{model.model_name}.{len(model.used_features)}.{self.pipeline_params[stage_name]['stage'].name}"
                if vectorization_name:
                    name += f".{vectorization_name}"
                if self.config_storage.pipeline.task in ("amts", "amts_ad"):
                    name = f"{model.model_name}"

                name = self._change_duplicating_model_name(name)

                self.prepared_model_dict[name] = model
                if self.total_cv_scores:
                    self.prepared_cv_scores.stage_models[name] = (
                        self.total_cv_scores.get(stage_name)
                    )

                if hasattr(stage, "vectorizer") and stage.vectorizer is not None:
                    print(stage.name, "has vectorizer")
                    vectorizer_full_name = (
                        f"{stage.name}_{stage.vectorizer.name}_vectorizer"
                    )
                    if stage_name == "base":
                        vectorizer_full_name = (
                            f"vectorization_{stage.vectorizer.name}_vectorizer"
                        )
                    setattr(
                        self.total_estimator_dict[stage_name],
                        "vectorizer_full_name",
                        vectorizer_full_name,
                    )

                if (
                    hasattr(stage, "text_transformer")
                    and stage.text_transformer is not None
                ):
                    text_transformer_full_name = f"{stage_name}_text_transformer"
                    if stage_name == "base":
                        text_transformer_full_name = "vectorization_text_transformer"
                    setattr(
                        self.total_estimator_dict[stage_name],
                        "text_transformer_full_name",
                        text_transformer_full_name,
                    )

        pipeline_elapsed_time = time.time() - pipeline_start_time
        _logger.monitor(
            f"Pipeline finished in {pipeline_elapsed_time:.1f} seconds.",
            extra={
                "log_data": PipelineFinishedLogData(
                    experiment_name=Path(self.experiment_path).name,
                    elapsed_time=pipeline_elapsed_time,
                )
            },
        )

    def _change_duplicating_model_name(self, name: str):
        """
        Modifies the model name to avoid duplication by appending a suffix if necessary.

        Args:
            name (str): The original model name.

        Returns:
            str: The modified model name with a unique suffix if duplication was found.
        """
        duplicate_suffix = ""
        duplicate_idx = 1
        while name + duplicate_suffix in self.prepared_model_dict:
            duplicate_idx += 1
            duplicate_suffix = f".{duplicate_idx}"

        name = name + duplicate_suffix

        return name

    def _check_available_metrics(self):
        """
        Validates the availability of metrics and loss functions specified in the pipeline configuration.

        This method ensures that the specified evaluation metrics and loss functions
        are supported for the given models and tasks.

        Raises:
            KeyError: If the specified metric or loss function is not found in metrics_mapping.
        """
        for model_name_from_config in self.config_storage.pipeline.model_list:
            model_name = estimators_registry[model_name_from_config].model_name

            _ = metrics_mapping[self.config_storage.pipeline.eval_metric](
                model_name,
                task=self.config_storage.pipeline.task,
                **self.config_storage.pipeline.metric_params,
            ).get_model_metric()
            _ = metrics_mapping[self.config_storage.pipeline.loss_function](
                model_name,
                task=self.config_storage.pipeline.task,
                **self.config_storage.pipeline.metric_params,
            ).get_model_objective()