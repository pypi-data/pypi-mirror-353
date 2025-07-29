import time
import uuid
from pathlib import Path
import pandas as pd

from dreamml.data._dataset import DataSet
from dreamml.logging import get_logger
from dreamml.logging.monitoring import ReportStartedLogData, ReportFinishedLogData
from dreamml.pipeline.pipeline import MainPipeline
from dreamml.reports.reports import (
    RegressionDevelopmentReport,
    AMTSDevelopmentReport,
    AMTS_ad_DevelopmentReport,
    TopicModelingDevReport,
    ClassificationDevelopmentReport,
    AnomalyDetectionDevReport,
)
from dreamml.configs.config_storage import ConfigStorage
from dreamml.features.categorical.categorical_encoder import (
    CategoricalFeaturesTransformer,
)
from dreamml.features.feature_extraction._transformers import LogTargetTransformer


_logger = get_logger(__name__)


def get_report(
    pipeline: MainPipeline,
    data_storage: DataSet,
    config_storage: ConfigStorage,
    encoder: CategoricalFeaturesTransformer,
    etna_eval_set=None,
    etna_pipeline=None,
    analysis=None,
) -> None:
    """
    Generates and processes a development report to maintain compatibility between the
    training pipeline version 2.0 and older reports.

    Args:
        pipeline (MainPipeline): The training pipeline object.
        data_storage (DataSet): The data storage object for managing datasets.
        config_storage (ConfigStorage): The configuration storage object for experiment parameters.
        encoder (CategoricalFeaturesTransformer): The transformer for handling categorical features.
        etna_eval_set (Optional[Any], optional): The evaluation set for time series data. Defaults to None.
        etna_pipeline (Optional[Any], optional): The pipeline for time series data processing. Defaults to None.
        analysis (Optional[Any], optional): Additional analysis parameters. Defaults to None.

    Returns:
        None

    Raises:
        KeyError: If the task type in config_storage is not supported.
        Exception: If report generation fails due to unexpected errors.
    """
    prepared_model_dict = {**pipeline.prepared_model_dict, "encoder": encoder}
    other_models_dict = {
        k: v["estimator"] for k, v in pipeline.other_model_dict.items()
    }
    oot_potential = pipeline.oot_potential

    config_for_report = config_storage

    # nlp
    total_vectorizers_dict = pipeline.total_vectorizers_dict
    config_for_report.data.columns.text_features = data_storage.text_features
    config_for_report.data.columns.text_features_preprocessed = (
        data_storage.text_features_preprocessed
    )

    dev_report_dict = {
        "binary": ClassificationDevelopmentReport,
        "multiclass": ClassificationDevelopmentReport,
        "multilabel": ClassificationDevelopmentReport,
        "multiregression": RegressionDevelopmentReport,
        "regression": RegressionDevelopmentReport,
        "timeseries": RegressionDevelopmentReport,
        "amts": AMTSDevelopmentReport,
        "amts_ad": AMTS_ad_DevelopmentReport,
        "topic_modeling": TopicModelingDevReport,
        "anomaly_detection": AnomalyDetectionDevReport,
    }

    report_params_dict = {
        "models": prepared_model_dict,
        "other_models": other_models_dict,
        "oot_potential": oot_potential,
        "experiment_path": pipeline.experiment_path,
        "config": config_for_report,
        "artifact_saver": pipeline.artifact_saver,
        "n_bins": 20,
        "bootstrap_samples": 200,
        "p_value": 0.05,
        "max_feat_per_model": 50,
        "predictions": None,
        "cv_scores": pipeline.prepared_cv_scores,
        "etna_pipeline": etna_pipeline,
        "etna_eval_set": etna_eval_set,
        "analysis": analysis,
        "vectorizers_dict": total_vectorizers_dict,
    }

    if config_storage.task in ("regression", "timeseries", "multiregression"):
        prepare_for_regression(pipeline, prepared_model_dict)

    report = dev_report_dict[config_storage.pipeline.task](**report_params_dict)

    report_id = uuid.uuid4().hex
    start_time = time.time()
    _logger.monitor(
        f"Processing development report for {config_storage.pipeline.task} task.",
        extra={
            "log_data": ReportStartedLogData(
                task=config_storage.pipeline.task,
                development=True,
                custom_model=False,
                experiment_name=Path(pipeline.experiment_path).name,
                report_id=report_id,
                user_config=config_storage._user_config,
            )
        },
    )
    eval_sets = data_storage.get_eval_set()
    report.transform(**eval_sets)
    elapsed_time = time.time() - start_time
    _logger.monitor(
        f"Development report for {config_storage.pipeline.task} task is created in {elapsed_time:.1f} seconds.",
        extra={
            "log_data": ReportFinishedLogData(
                report_id=report_id,
                elapsed_time=elapsed_time,
            )
        },
    )


def prepare_for_regression(pipeline, prepared_model_dict) -> None:
    """
    Prepares the model dictionary for generating a regression development report.

    This function adds correlation importance and log target transformer to the prepared_model_dict
    if applicable.

    Args:
        pipeline: The training pipeline object.
        prepared_model_dict (dict): The dictionary containing prepared models.

    Returns:
        None

    Raises:
        None
    """
    corr_importance = pipeline.total_feature_importance_dict.get("0_dtree", None)
    if corr_importance is not None:
        if isinstance(corr_importance, pd.DataFrame):
            prepared_model_dict["corr_importance"] = corr_importance

    prepared_model_dict["log_target_transformer"] = LogTargetTransformer()