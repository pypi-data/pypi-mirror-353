from typing import List, Literal, Optional

from pydantic import model_validator, typing

from dreamml.config._base_config import BaseConfig
from dreamml.config.pipeline.reproducibility import ReproducibilityConfig
from dreamml.config.models import AvailableEstimtors
from dreamml.config.pipeline.saving import SavingConfig
from dreamml.modeling.metrics.metrics_mapping import MetricsMapping

AvailableTasks = Literal[
    "regression",
    "binary",
    "multiclass",
    "multilabel",
    "multiregression",
    "timeseries",
    "amts",
    "amts_ad",
    "topic_modeling",
    "phrase_retrieval",
    "anomaly_detection",
]

AvailableVectorizationAlgos = Literal[
    "tfidf", "word2vec", "fasttext", "glove", "bert", "bow"
]

estimators_by_task = {
    "regression": ["xgboost", "lightgbm", "catboost", "pyboost", "linear_reg"],
    "binary": ["xgboost", "lightgbm", "catboost", "pyboost", "log_reg"],
    "multiclass": ["xgboost", "lightgbm", "catboost", "pyboost", "log_reg"],
    "multilabel": ["xgboost", "lightgbm", "catboost", "pyboost"],
    "multiregression": ["catboost"],
    "timeseries": ["xgboost", "lightgbm", "catboost", "pyboost"],
    "amts": ["prophet", "linear_reg", "nbeats_revin"],
    "amts_ad": ["nbeats_revin"],
    "topic_modeling": ["lda", "ensembelda", "bertopic"],
    "phrase_retrieval": ["lda", "ensembelda", "bertopic"],
    "anomaly_detection": ["vae", "ae", "iforest"],
}

eval_metric_by_estimator = {
    "xgboost": [
        "rmse",
        "rmsle",
        "mape",
        "mae",
        "huber_loss",
        "mean_average_precision",
        "roc_auc",
        "precision_recall_auc",
        "f1_score",
        "logloss",
        "gini",
        "recall",
        "precision",
        "accuracy",
    ],
    "lightgbm": [
        "rmse",
        "mse",
        "mape",
        "mae",
        "huber_loss",
        "fair_loss",
        "poisson",
        "gamma",
        "gamma_deviance",
        "tweedie",
        "ndcg",
        "mean_average_precision",
        "average_precision",
        "roc_auc",
        "cross-entropy",
        "kullback_leibler",
        "quantile",
        "f1_score",
        "gini",
        "logloss",
        "recall",
        "precision",
        "accuracy",
        "precision_recall_auc",
    ],
    "catboost": [
        "rmse",
        "msle",
        "r2",
        "mape",
        "smape",
        "mdae",
        "mae",
        "huber_loss",
        "fair_loss",
        "poisson",
        "tweedie",
        "mean_average_precision",
        "roc_auc",
        "accuracy",
        "precision",
        "recall",
        "precision_recall_auc",
        "cross-entropy",
        "quantile",
        "f1_score",
        "logloss",
        "gini",
        "multirmse",
    ],
    "pyboost": [
        "rmse",
        "rmsle",
        "r2",
        "roc_auc",
        "accuracy",
        "precision",
        "recall",
        "cross-entropy",
        "f1_score",
        "logloss",
        "gini",
        "precision_recall_auc",
    ],
    "linear_reg": ["mse", "rmse", "rmsle", "mape", "mae", "huber_loss", "gini"],
    "log_reg": [
        "mean_average_precision",
        "roc_auc",
        "precision_recall_auc",
        "f1_score",
        "logloss",
        "gini",
        "recall",
        "precision",
        "accuracy",
    ],
    "lda": ["log_perplexity", "coherence", "average_distance"],
    "ensembelda": ["log_perplexity", "coherence", "average_distance"],
    "bertopic": ["average_distance", "silhouette_score"],
    "prophet": ["mape"],
    "nbeats_revin": ["mse"],
    "ae": ["mse", "mae"],
    "vae": ["mse", "mae"],
    "iforest": ["mse", "mae", "avg_anomaly_score"],
}

loss_function_by_estimator = {
    "xgboost": [
        "mse",
        "rmse",
        "rmlse",
        "mae",
        "huber_loss",
        "quantile",
        "logloss",
        "gini",
    ],
    "lightgbm": [
        "mse",
        "rmse",
        "mape",
        "mae",
        "huber_loss",
        "fair_loss",
        "poisson",
        "quantile",
        "gamma",
        "tweedie",
        "logloss",
        "cross-entropy",
        "gini",
    ],
    "catboost": [
        "mse",
        "rmse",
        "mape",
        "mae",
        "huber_loss",
        "poisson",
        "quantile",
        "gamma",
        "tweedie",
        "logloss",
        "cross-entropy",
        "gini",
        "multirmse",
    ],
    "pyboost": ["mse", "logloss", "gini"],
    "linear_reg": ["mse"],
    "log_reg": ["logloss"],
    "lda": ["log_perplexity", "coherence", "average_distance"],
    "ensembelda": ["log_perplexity", "coherence", "average_distance"],
    "bertopic": ["average_distance", "silhouette_score"],
    "prophet": ["mape"],
    "nbeats_revin": ["mse"],
    "ae": ["mse", "mae"],
    "vae": ["mse", "mae"],
}


class VectorizerConfig(BaseConfig):
    params: dict


class VectorizationConfig(BaseConfig):
    vectorization_algos: List[AvailableVectorizationAlgos]
    tfidf: VectorizerConfig
    word2vec: VectorizerConfig
    fasttext: VectorizerConfig
    glove: VectorizerConfig

    @model_validator(mode="after")
    def _check_vectorization_algos(self):
        if "bert" in self.vectorization_algos:
            if len(self.vectorization_algos) != 1:
                raise ValueError(
                    f"You can select just only 'bert' in 'vectorization_algos' "
                    f"or choose another vectorization algorithms: {typing.get_args(AvailableVectorizationAlgos)}"
                )

        return self


class PreprocessingConfig(BaseConfig):
    min_percentile: int
    max_percentile: int
    log_target: bool


class AltModeConfig(BaseConfig):
    use_lama: bool
    lama_time: float
    use_etna: bool
    use_whitebox_automl: bool


class PipelineConfig(BaseConfig):
    reproducibility: ReproducibilityConfig
    saving: SavingConfig
    task: AvailableTasks
    subtask: Optional[Literal["tabular", "nlp"]]
    stage_list: List[str]
    model_list: List[AvailableEstimtors]
    eval_metric: str
    metric_params: dict
    loss_function: str
    device: Literal["cuda", "cpu"]
    parallelism: int
    validation_type: Literal["auto", "hold-out", "cv"]
    vectorization: VectorizationConfig
    preprocessing: PreprocessingConfig
    use_oot_potential: bool
    alt_mode: AltModeConfig

    @model_validator(mode="after")
    def _check_task_estimator_compatibility(self):
        task = self.task
        estimators = self.model_list

        if task not in estimators_by_task:
            return self

        available_estimators = estimators_by_task[task]
        for estimator in estimators:
            if estimator not in available_estimators:
                raise ValueError(
                    f"{estimator=} is not supported. Available estimators for `{task}` task: {available_estimators}"
                )

        return self

    @model_validator(mode="after")
    def _check_metric_estimator_compatibility(self):
        eval_metric = self.eval_metric
        loss_function = self.loss_function
        estimators = self.model_list

        for estimator in estimators:
            if estimator not in eval_metric_by_estimator:
                continue

            available_eval_metrics = eval_metric_by_estimator[estimator]
            available_eval_metrics += MetricsMapping.custom_metrics

            if eval_metric not in available_eval_metrics:
                raise ValueError(
                    f"{eval_metric=} is not supported. Available metrics for {estimator=}: {available_eval_metrics}"
                )

        for estimator in estimators:
            if estimator not in loss_function_by_estimator:
                continue

            available_loss_functions = loss_function_by_estimator[estimator]
            available_loss_functions += MetricsMapping.custom_metrics
            if loss_function not in available_loss_functions:
                raise ValueError(
                    f"{loss_function=} is not supported. "
                    f"Available loss functions for {estimator=}: {available_loss_functions}"
                )

        return self

    @model_validator(mode="after")
    def _check_single_estimator_for_bert(self):
        if "bert" in self.vectorization.vectorization_algos:
            if len(self.model_list) != 1:
                raise ValueError(
                    "You can use only one model in 'pipeline.model_list' "
                    "if you have chosen 'bert' as vectorization_algos"
                )

        return self

    @model_validator(mode="after")
    def _check_log_target_for_multiregression(self):
        task = self.task
        if self.preprocessing.log_target and task not in ("regression", "timeseries"):
            raise ValueError(
                f"Log target is not supported for `{task}` task'. "
                "Log target is only available for 'regression' and 'timeseries' tasks."
            )

        return self

    @model_validator(mode="after")
    def _check_alt_mode_supported_tasks(self):
        supported_alt_modes_by_task = {
            "regression": ["whitebox", "lama"],
            "binary": ["whitebox", "lama", "oot_potential"],
            "multiclass": ["lama"],
            "timeseries": ["etna"],
        }

        supported_alt_modes = supported_alt_modes_by_task.get(self.task, [])
        error_alt_modes = []

        use_mapping = {
            "oot_potential": self.use_oot_potential,
            "lama": self.alt_mode.use_lama,
            "whitebox": self.alt_mode.use_whitebox_automl,
            "etna": self.alt_mode.use_etna,
        }
        for alt_mode, use in use_mapping.items():
            if use:
                if alt_mode not in supported_alt_modes:
                    error_alt_modes.append(alt_mode)

        if len(error_alt_modes) > 0:
            raise ValueError(
                f"Alt modes {error_alt_modes} are not supported for {self.task} task. "
                f"Supported alt modes for this task: {supported_alt_modes}"
            )

        return self
