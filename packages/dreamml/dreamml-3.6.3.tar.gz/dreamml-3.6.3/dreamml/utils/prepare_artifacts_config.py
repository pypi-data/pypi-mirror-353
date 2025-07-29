import os
import pickle
from pathlib import Path
from typing import List, Union

import pandas as pd
import yaml
from omegaconf import OmegaConf
from sklearn.preprocessing import LabelBinarizer
import numpy as np
from tqdm.auto import tqdm

from dreamml.features.feature_vectorization._base import BaseVectorization
from dreamml.modeling import AutoModel

from dreamml.configs.config_storage import ConfigStorage
from dreamml.features.categorical import CategoricalFeaturesTransformer
from dreamml.features.feature_enrichment.timeseries_enrichment import (
    split_dml_transforms,
)
from dreamml.features.feature_extraction import LogTargetTransformer
from dreamml.modeling.models.estimators import BaseModel
from dreamml.utils.get_last_experiment_directory import get_experiment_dir_path
from dreamml.logging import get_logger

from etna.core import load

_logger = get_logger(__name__)


class DummyLogTargetTransformer:
    """
    A dummy transformer for logarithmic target transformation.

    Attributes:
        fitted (Any): Indicates whether the transformer has been fitted.
    """

    def __init__(self):
        """
        Initializes the DummyLogTargetTransformer with fitted set to None.
        """
        self.fitted = None


class BaseArtifactsConfig:
    """
    Base configuration class for managing artifacts in experiments.

    Args:
        config (dict): Configuration dictionary.
        experiment_config (ConfigStorage, optional): Experiment configuration storage.
        model (BaseModel, optional): The model used in the experiment.
        encoder (CategoricalFeaturesTransformer, optional): Encoder for categorical features.

    Attributes:
        config (dict): Configuration dictionary.
        model_name (str): Name of the model.
        experiment_dir_path (str): Path to the experiment directory.
        estimator (BaseModel): The estimator/model used.
        vectorizer_name (str or None): Name of the vectorizer.
        vectorizer (BaseVectorization or None): The vectorizer instance.
        experiment_config (ConfigStorage): Experiment configuration storage.
        task (str): Task type of the pipeline.
        data (dict): Evaluation datasets.
        encoder (CategoricalFeaturesTransformer or None): Encoder for categorical features.
        target_name (str): Name of the target column.
        time_column (str or None): Name of the time column.
        time_format (str or None): Format of the time column.
        subtask (str): Subtask of the pipeline.
    """

    def __init__(
        self,
        config: dict,
        experiment_config: ConfigStorage = None,
        model: BaseModel = None,
        encoder: CategoricalFeaturesTransformer = None,
    ):
        """
        Initializes the BaseArtifactsConfig with configuration and dependencies.

        Args:
            config (dict): Configuration dictionary.
            experiment_config (ConfigStorage, optional): Experiment configuration storage.
            model (BaseModel, optional): The model used in the experiment.
            encoder (CategoricalFeaturesTransformer, optional): Encoder for categorical features.
        """
        self.config = config
        self.model_name = self.config["model_name"]
        self.experiment_dir_path = self._get_experiment_dir_path()
        self.estimator = model or self._get_model()
        self.vectorizer_name = self.config.get("vectorizer_name")
        self.vectorizer = (
            self._get_vectorizer() if self.vectorizer_name is not None else None
        )
        self.experiment_config = experiment_config or self._get_config()
        self.task = self.experiment_config.pipeline.task
        self.data = self._get_data()
        self.encoder = encoder or self._get_encoder()
        self.target_name = self.experiment_config.data.columns.target_name
        self.time_column = self.config.get("time_column")
        self.time_format = self.config.get("time_format")
        self.subtask = self.experiment_config.pipeline.subtask

    def prepare_artifacts_config(self):
        """
        Prepares the configuration dictionary for artifacts.

        Returns:
            tuple: A tuple containing the artifacts configuration dictionary and the evaluation set.

        Raises:
            None
        """
        artifacts_config = {
            "estimator": self.estimator,
            "vectorizer": self.vectorizer,
            "used_features": self.estimator.used_features,
            "categorical_features": self.estimator.categorical_features or [],
        }

        if not isinstance(artifacts_config["categorical_features"], list):
            artifacts_config["categorical_features"] = [
                artifacts_config["categorical_features"]
            ]

        artifacts_config["subtask"] = self.subtask
        text_column: Union[List[str], str] = self.config.get("text_column")
        text_preprocessed_column: Union[List[str], str] = self.config.get(
            "text_preprocessed_column"
        )

        if isinstance(text_column, str):
            text_column = [text_column]
        if isinstance(text_preprocessed_column, str):
            text_preprocessed_column = [text_preprocessed_column]

        artifacts_config["text_column"] = text_column
        artifacts_config["text_preprocessed_column"] = text_preprocessed_column

        artifacts_config["group_column"] = self.config.get("group_column")
        artifacts_config["time_column"] = self.time_column

        artifacts_config["path_to_save"] = os.path.join(
            self.experiment_dir_path, "docs", f"val_report_{self.model_name}.xlsx"
        )
        artifacts_config["create_pdf"] = self.config.get("create_pdf", False)

        artifacts_config["images_dir_path"] = os.path.join(
            self.experiment_dir_path, "images"
        )
        artifacts_config["task"] = self.task
        artifacts_config["custom_model"] = False
        artifacts_config["user_config"] = self.config
        artifacts_config["number_of_simulations_1_1"] = self.config.get(
            "number_of_simulations_1_1", 200
        )
        artifacts_config["number_of_simulations_3_2"] = self.config.get(
            "number_of_simulations_3_2", 100
        )

        eval_set = self.get_eval_set()

        if self.subtask == "nlp":
            eval_set, text_preprocessed_column = self._check_preprocessed_columns_nlp(
                eval_set, text_column, text_preprocessed_column
            )
            if len(text_column):
                artifacts_config["text_column"] = text_column[0]
                artifacts_config["text_preprocessed_column"] = text_preprocessed_column[
                    0
                ]

        return artifacts_config, eval_set

    def _check_preprocessed_columns_nlp(
        self, eval_set, text_column: List[str], text_preprocessed_column: List[str]
    ):
        """
        Checks and updates preprocessed columns for NLP tasks.

        Args:
            eval_set (dict): Evaluation datasets.
            text_column (List[str]): List of text column names.
            text_preprocessed_column (List[str]): List of preprocessed text column names.

        Returns:
            tuple: Updated evaluation sets and preprocessed text columns.

        Raises:
            None
        """
        for sample_name, (X_sample, y_sample) in eval_set.items():
            for text_feature_name in text_column:
                preproc_feature_name = f"{text_feature_name}_preprocessed"
                if (
                    preproc_feature_name not in text_preprocessed_column
                    or preproc_feature_name not in X_sample.columns
                ):
                    X_sample[preproc_feature_name] = X_sample[text_column]
                    text_preprocessed_column.append(preproc_feature_name)
        return eval_set, text_preprocessed_column

    def _get_experiment_dir_path(self):
        """
        Retrieves the path to the experiment directory.

        Returns:
            str: Path to the experiment directory.

        Raises:
            None
        """
        experiment_dir_path = get_experiment_dir_path(
            self.config["results_path"],
            experiment_dir_name=self.config.get("dir_name"),
            use_last_experiment_directory=self.config.get(
                "use_last_experiment_directory", False
            ),
        )
        return experiment_dir_path

    def _get_model(self):
        """
        Loads the model from the experiment directory.

        Returns:
            BaseModel: The loaded model.

        Raises:
            None
        """
        self.model_name = (
            self.model_name[:-4]
            if self.model_name.endswith(".pkl")
            else self.model_name
        )

        path = os.path.join(
            self.experiment_dir_path, "models", f"{self.model_name}.pkl"
        )
        model = AutoModel.from_pretrained(path)

        return model

    def _get_vectorizer(self):
        """
        Loads the vectorizer from the experiment directory if applicable.

        Returns:
            BaseVectorization or None: The loaded vectorizer or None if not applicable.

        Raises:
            None
        """
        self.vectorizer_name = (
            self.vectorizer_name[:-4]
            if self.vectorizer_name.endswith(".pkl")
            else self.vectorizer_name
        )
        if self.vectorizer_name == "bert_vectorizer":
            return None

        if hasattr(self.estimator, "vectorizer_full_name"):
            vectorizer_name = self.estimator.vectorizer_full_name
        else:
            vectorizer_name = (
                f"vectorization_{self.estimator.vectorization_name}_vectorizer"
            )

        path = os.path.join(
            self.experiment_dir_path, "models", f"{vectorizer_name}.pkl"
        )
        vectorizer = BaseVectorization.from_pretrained(path)

        return vectorizer

    def _get_data(self):
        """
        Loads and processes the evaluation datasets.

        Returns:
            dict: Processed evaluation datasets.

        Raises:
            None
        """
        with open(
            os.path.join(self.experiment_dir_path, "data", f"eval_sets.pkl"), "rb"
        ) as f:
            data = pickle.load(f)

        if self.task in ["amts", "amts_ad"]:
            return data

        for key, (X, y) in data.items():
            if self.vectorizer is not None:
                embedding_df = self.vectorizer.transform(X)
                X = pd.concat([X, embedding_df], axis=1)
                data[key] = (X, y)
            else:
                data[key] = (X, y)
        return data

    def _get_log_target_transformer(self):
        """
        Loads the log target transformer if applicable.

        Returns:
            LogTargetTransformer or DummyLogTargetTransformer or None: The transformer instance.

        Raises:
            None
        """
        if self.task not in ["regression", "timeseries"]:
            return None

        path = os.path.join(
            self.experiment_dir_path, "models", f"log_target_transformer.pkl"
        )

        if os.path.exists(path):
            log_target_transformer = LogTargetTransformer.from_pretrained(path)
        else:
            log_target_transformer = DummyLogTargetTransformer()

        return log_target_transformer

    def _get_config(self):
        """
        Loads the experiment configuration from storage.

        Returns:
            ConfigStorage: The loaded experiment configuration.

        Raises:
            None
        """
        experiment_config = ConfigStorage.from_pretrained(
            os.path.join(
                self.experiment_dir_path,
                "config",
            )
        )

        return experiment_config

    def _get_encoder(self, default: bool = False):
        """
        Loads the encoder for categorical features.

        Args:
            default (bool, optional): Whether to use the default encoder path. Defaults to False.

        Returns:
            CategoricalFeaturesTransformer or None: The encoder instance.

        Raises:
            None
        """
        if default:
            encoder_path = f"{self.experiment_dir_path}/models/encoder.pkl"
        else:
            encoder_path = self.config.get("encoder")

        if encoder_path is None:
            return None

        if not encoder_path.endswith(".pkl"):
            encoder_path += ".pkl"

        encoder = CategoricalFeaturesTransformer.from_pretrained(encoder_path)

        return encoder

    def _transform_data(self, x, y):
        """
        Transforms the data using the encoder if available.

        Args:
            x (pd.DataFrame): Feature data.
            y (Any): Target data.

        Returns:
            tuple: Transformed feature and target data.

        Raises:
            None
        """
        if self.encoder is not None:
            # By default we shouldn't use any encoder here because eval_sets were saved with already encoded data
            # this function remained just in case of future use
            x = self.encoder.transform(x)

        return x, y

    def get_eval_set(self):
        """
        Retrieves and processes the evaluation set.

        Returns:
            dict: Processed evaluation datasets.

        Raises:
            None
        """
        eval_set = {}
        for sample_name, (x, y) in self.data.items():
            x, y = self._transform_data(x, y)

            if self.time_column is not None:
                try:
                    x[self.time_column] = pd.to_datetime(
                        x[self.time_column], format=self.time_format
                    )
                except Exception as e:
                    _logger.debug(f"Error while processing time_column: {e}")

                try:
                    # Excel не может работать с локализованным форматом
                    x[self.time_column] = x[self.time_column].dt.tz_localize(None)
                except AttributeError:
                    _logger.warning(
                        f"Формат времени колонки {self.time_column} не определен: value at idx=0: {x[self.time_column].iloc[0]}"
                    )

            eval_set[sample_name] = (x, y)
        return eval_set


class RegressionArtifactsConfig(BaseArtifactsConfig):
    """
    Configuration class for regression artifacts.

    Args:
        config (dict): Configuration dictionary.
        experiment_config (ConfigStorage, optional): Experiment configuration storage.
        model (BaseModel, optional): The model used in the experiment.
        encoder (CategoricalFeaturesTransformer, optional): Encoder for categorical features.
        log_target_transformer (LogTargetTransformer, optional): Transformer for log targets.

    Attributes:
        log_target_transformer (LogTargetTransformer or DummyLogTargetTransformer): Transformer for log targets.
    """

    def __init__(
        self,
        config: dict,
        experiment_config: ConfigStorage = None,
        model: BaseModel = None,
        encoder: CategoricalFeaturesTransformer = None,
        log_target_transformer: LogTargetTransformer = None,
    ):
        """
        Initializes the RegressionArtifactsConfig with additional log target transformer.

        Args:
            config (dict): Configuration dictionary.
            experiment_config (ConfigStorage, optional): Experiment configuration storage.
            model (BaseModel, optional): The model used in the experiment.
            encoder (CategoricalFeaturesTransformer, optional): Encoder for categorical features.
            log_target_transformer (LogTargetTransformer, optional): Transformer for log targets.
        """
        super().__init__(
            config,
            experiment_config=experiment_config,
            model=model,
            encoder=encoder,
        )
        self.log_target_transformer = (
            log_target_transformer or self._get_log_target_transformer()
        )

    def _transform_data(self, x, y):
        """
        Transforms the data using the encoder and inverse transforms the target if applicable.

        Args:
            x (pd.DataFrame): Feature data.
            y (Any): Target data.

        Returns:
            tuple: Transformed feature and target data.

        Raises:
            None
        """
        x, y = super()._transform_data(x, y)

        if self.log_target_transformer.fitted:
            y = self.log_target_transformer.inverse_transform(y)

        return x, y

    def prepare_artifacts_config(self):
        """
        Prepares the configuration dictionary for regression artifacts.

        Returns:
            tuple: A tuple containing the artifacts configuration dictionary and the evaluation set.

        Raises:
            None
        """
        artifacts_config, eval_set = super().prepare_artifacts_config()
        artifacts_config["log_target_transformer"] = self.log_target_transformer

        try:
            metric_name = self.config["metric"]["metric"]
        except (KeyError, ValueError):
            metric_name = None

        if metric_name is None:
            metric_name = "rmse"

        artifacts_config["metric_name"] = metric_name

        return artifacts_config, eval_set


class StatisticalArtifactsConfig(BaseArtifactsConfig):
    """
    Configuration class for statistical artifacts.

    Args:
        config (dict): Configuration dictionary.

    Attributes:
        Inherits all attributes from BaseArtifactsConfig.
    """

    def __init__(self, config: dict):
        """
        Initializes the StatisticalArtifactsConfig with the given configuration.

        Args:
            config (dict): Configuration dictionary.
        """
        super().__init__(config)

    def prepare_artifacts_config(self):
        """
        Prepares the configuration dictionary for statistical artifacts.

        Returns:
            tuple: A tuple containing the artifacts configuration dictionary and the evaluation set.

        Raises:
            None
        """
        artifacts_config = {
            "estimator": self.estimator,
            "vectorizer": self.vectorizer,
            "used_features": self.estimator.used_features,
            "categorical_features": self.estimator.categorical_features or [],
        }

        if not isinstance(artifacts_config["categorical_features"], list):
            artifacts_config["categorical_features"] = [
                artifacts_config["categorical_features"]
            ]

        artifacts_config["subtask"] = self.subtask
        text_column: Union[List[str], str] = self.config.get("text_column")
        text_preprocessed_column: Union[List[str], str] = self.config.get(
            "text_preprocessed_column"
        )

        if isinstance(text_column, str):
            text_column = [text_column]
        if isinstance(text_preprocessed_column, str):
            text_preprocessed_column = [text_preprocessed_column]

        artifacts_config["text_column"] = text_column
        artifacts_config["text_preprocessed_column"] = text_preprocessed_column

        artifacts_config["group_column"] = self.config.get("group_column")
        artifacts_config["time_column"] = self.time_column

        artifacts_config["path_to_save"] = os.path.join(
            self.experiment_dir_path, "docs", f"val_report_{self.model_name}.xlsx"
        )
        artifacts_config["create_pdf"] = self.config.get("create_pdf", False)

        artifacts_config["images_dir_path"] = os.path.join(
            self.experiment_dir_path, "images"
        )
        artifacts_config["task"] = self.task
        artifacts_config["custom_model"] = False
        artifacts_config["user_config"] = self.config
        artifacts_config["number_of_simulations_1_1"] = self.config.get(
            "number_of_simulations_1_1", 200
        )
        artifacts_config["number_of_simulations_3_2"] = self.config.get(
            "number_of_simulations_3_2", 100
        )
        eval_set = self.get_eval_set()

        if self.subtask == "nlp":
            eval_set, text_preprocessed_column = self._check_preprocessed_columns_nlp(
                eval_set, text_column, text_preprocessed_column
            )
            if len(text_column):
                artifacts_config["text_column"] = text_column[0]
                artifacts_config["text_preprocessed_column"] = text_preprocessed_column[
                    0
                ]

        return artifacts_config, eval_set

    def get_eval_set(self):
        """
        Retrieves and processes the evaluation set specifically for statistical artifacts.

        Returns:
            dict: Processed evaluation datasets.

        Raises:
            None
        """
        eval_set = {}
        for sample_name, (x, y) in self.data["amts_final_data"].items():
            x, y = self._transform_data(x, y)

            if self.time_column is not None:
                try:
                    x[self.time_column] = pd.to_datetime(
                        x[self.time_column], format=self.time_format
                    )
                except Exception as e:
                    _logger.debug(f"Error while processing time_column: {e}")

                try:
                    x[self.time_column] = x[self.time_column].dt.tz_localize(None)
                except AttributeError:
                    _logger.warning(
                        f"Формат времени колонки {self.time_column} не определен: value at idx=0: {x[self.time_column].iloc[0]}"
                    )

            eval_set[sample_name] = (x, y)
        return eval_set


class ClassificationArtifactsConfig(BaseArtifactsConfig):
    """
    Configuration class for classification artifacts.

    Args:
        config (dict): Configuration dictionary.
        experiment_config (ConfigStorage, optional): Experiment configuration storage.
        model (BaseModel, optional): The model used in the experiment.
        encoder (CategoricalFeaturesTransformer, optional): Encoder for categorical features.

    Attributes:
        Inherits all attributes from BaseArtifactsConfig.
    """

    def __init__(
        self,
        config: dict,
        experiment_config: ConfigStorage = None,
        model: BaseModel = None,
        encoder: CategoricalFeaturesTransformer = None,
    ):
        """
        Initializes the ClassificationArtifactsConfig with configuration and dependencies.

        Args:
            config (dict): Configuration dictionary.
            experiment_config (ConfigStorage, optional): Experiment configuration storage.
            model (BaseModel, optional): The model used in the experiment.
            encoder (CategoricalFeaturesTransformer, optional): Encoder for categorical features.
        """
        super().__init__(
            config,
            experiment_config=experiment_config,
            model=model,
            encoder=encoder,
        )

    def prepare_artifacts_config(self):
        """
        Prepares the configuration dictionary for classification artifacts.

        Returns:
            tuple: A tuple containing the artifacts configuration dictionary and the evaluation set.

        Raises:
            ValueError: If labels are missing for multiclass tasks.
        """
        artifacts_config, eval_set = super().prepare_artifacts_config()

        metric_name, metric_col_name, self.experiment_params = self._get_metric_params()
        artifacts_config["metric_name"] = metric_name
        artifacts_config["metric_col_name"] = metric_col_name
        artifacts_config["metric_params"] = self.experiment_params

        if self.task == "binary":
            if "labels" not in artifacts_config["metric_params"]:
                artifacts_config["metric_params"]["labels"] = [0, 1]

        if self.task == "multiclass":
            artifacts_config["multiclass_artifacts"] = {}

            if "labels" not in artifacts_config["metric_params"]:
                msg = "Missing labels for multiclass."
                raise ValueError(msg)

            labels = artifacts_config["metric_params"]["labels"]
            arange_labels = np.arange(len(labels))
            artifacts_config["multiclass_artifacts"][
                "label_binarizer"
            ] = LabelBinarizer().fit(arange_labels)
            artifacts_config["multiclass_artifacts"]["labels"] = labels
            artifacts_config["multiclass_artifacts"]["task"] = self.task
            artifacts_config["multiclass_artifacts"]["target_name"] = self.target_name

        if self.task == "timeseries":
            artifacts_config["config_storage"] = self._get_config_storage()
            artifacts_config["encoder"] = self._get_encoder(default=True)

        return artifacts_config, eval_set

    def _get_metric_params(self):
        """
        Retrieves metric parameters from the configuration.

        Returns:
            tuple: A tuple containing the metric name, metric column name, and experiment parameters.

        Raises:
            None
        """
        metric_name = self.config.get(
            "eval_metric", self.experiment_config.pipeline.eval_metric
        )
        params = {
            "at_k": self.config.get("at_k"),
            "threshold": self.config.get("threshold"),
            "beta": self.config.get("beta"),
        }
        params.update(self.config.get("metric_params", {}))

        experiment_params = self.experiment_config.pipeline.metric_params
        for key in params:
            if params[key] is not None:
                experiment_params[key] = params[key]

        return metric_name, metric_name, experiment_params

    def get_timeseries_artifacts(self):
        """
        Retrieves artifacts specific to time series tasks.

        Returns:
            tuple: A tuple containing DML transforms, the Etna pipeline, and Etna evaluation sets.

        Raises:
            None
        """
        _, dml_transforms = split_dml_transforms(
            self.experiment_config.pipeline.task_specific.ts_transforms
        )
        try:
            path_to_etna_pipeline = Path(
                self.experiment_dir_path, "etna_pipeline", "etna_pipeline.zip"
            )
            etna_pipeline = load(path_to_etna_pipeline)
        except FileNotFoundError:
            etna_pipeline = None

        try:
            etna_eval_sets = pickle.load(
                open(f"{self.experiment_dir_path}/data/etna_eval_sets.pkl", "rb")
            )
        except FileNotFoundError:
            etna_eval_sets = None
        return dml_transforms, etna_pipeline, etna_eval_sets

    def _get_config_storage(self):
        """
        Retrieves the experiment configuration storage.

        Returns:
            ConfigStorage: The experiment configuration storage.

        Raises:
            None
        """
        return self.experiment_config