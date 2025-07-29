import os
import sys
import subprocess
import shutil
import pickle
import contextlib
from datetime import date
from typing import Optional, List, Dict
from copy import deepcopy
from pathlib import Path
from pyspark.sql import functions as F
from IPython.display import display, Javascript
import uuid
import time
import ipynbname

import dreamml
from dreamml.data._hadoop import create_spark_session, stop_spark_session
from dreamml.configs.config_storage import ConfigStorage
from dreamml.features.feature_vectorization._base import BaseVectorization
from dreamml.features.text import TextFeaturesTransformer
from dreamml.logging import get_logger
from dreamml.utils.temporary_directory import TempDirectory

ETNA_PIPELINE_DIR = "etna_pipeline"
OTHER_MODELS_DIR = "other_models"
_logger = get_logger(__name__)


class BaseSaver:
    """
    Base class for saving experiment artifacts, ensuring backward compatibility between the new classification pipeline and the old regression pipeline. 
    Before saving data, the object checks if the directory exists. If it does not exist, it creates a directory structure 
    ({path} - {experiment_number} - config / docs / images / models), otherwise it creates 
    ({experiment_number} - config / docs / images / models).

    Directory Purpose
    -----------------
    - {path}: Directory for saving output information of all runs.
    - {path}/{experiment_number}: Directory for saving output information of the current experiment.
    - {path}/{experiment_number}/config: Directory for saving configuration files.
    - {path}/{experiment_number}/docs: Directory for saving reports.
    - {path}/{experiment_number}/images: Directory for saving plots.
    - {path}/{experiment_number}/models: Directory for saving models.
    - {path}/{experiment_number}/cpts: Directory for saving pipeline checkpoints.
    - {path}/{experiment_number}/other_models: Directory for saving models from multiple model training stages (batch stage).

    Attributes:
        experiment_path (str): Path with the experiment number.
    """

    def __init__(self, path: str):
        """
        Initializes the BaseSaver with the given path.

        Args:
            path (str): Path for saving experiment output files.
        """
        self._results_path = path
        self._dml_version_file = "dml_version.txt"
        self._experiment_path = None
        self._run_number = None
        self._run_string = "_run_"

    @property
    def run_number(self):
        """
        Gets the current run number.

        Raises:
            ValueError: If the experiment directory has not been created yet.

        Returns:
            int: The current run number.
        """
        if self._run_number is None:
            raise ValueError("Experiment dir is not created yet!")

        return self._run_number

    @property
    def run_prefix(self) -> str:
        """
        Gets the run prefix.

        Returns:
            str: The run prefix.
        """
        return "dml"

    @property
    def experiment_dir_name(self) -> str:
        """
        Constructs the experiment directory name.

        Returns:
            str: The experiment directory name.
        """
        return f"{self.run_prefix}{self._run_string}{self.run_number}"

    def get_run_number_from_experiment_dir(self, name):
        """
        Extracts the run number from the experiment directory name.

        Args:
            name (str): The experiment directory name.

        Returns:
            str: The extracted run number.
        """
        return name.split(self._run_string)[-1]

    @property
    def experiment_path(self):
        """
        Gets the experiment path.

        Raises:
            ValueError: If the experiment directory has not been created yet.

        Returns:
            str: The experiment path.
        """
        if self._experiment_path is None:
            raise ValueError("Experiment dir is not created yet!")

        return self._experiment_path

    def save_dependencies(self) -> None:
        """
        Saves the necessary dependencies for reproducing the model's work by generating a `requirements.txt` file.

        Raises:
            subprocess.SubprocessError: If there's an error during subprocess execution.
            RuntimeError: If there's a runtime error.
        """
        try:
            output = subprocess.check_output(
                [sys.executable, "-m", "pip", "freeze"]
            ).decode("utf-8")
        except (subprocess.SubprocessError, RuntimeError) as e:
            _logger.exception(
                f"Couldn't save requirements for the current experiment: {e}"
            )
            return

        with open(f"{self.experiment_path}/requirements.txt", "w") as f:
            f.write(output)

    @staticmethod
    def get_current_notebook_path(notebook_name: str = None):
        """
        Determines the current path to the Jupyter Notebook.

        Args:
            notebook_name (str, optional): The name of the notebook. Defaults to None.

        Raises:
            RuntimeError: If the notebook name cannot be determined.

        Returns:
            str: The path to the current notebook.
        """
        if notebook_name is not None:
            if not notebook_name.endswith(".ipynb"):
                notebook_name = f"{notebook_name}.ipynb"

            return os.path.join(os.getcwd(), notebook_name)

        try:
            return ipynbname.path()
        except Exception as e:
            _logger.debug(f"Unable to determine notebook_path with ipynbname: {e}")

        magic = str(uuid.uuid1()).replace("-", "")
        print(magic)

        display(Javascript("IPython.notebook.save_checkpoint();"))
        notebook_name = None

        tries = 0
        while notebook_name is None:
            with contextlib.suppress(Exception):
                time.sleep(1)
                notebook_name = subprocess.check_output(
                    f"grep -l {magic} *.ipynb", shell=True
                )
                notebook_name = notebook_name.decode().strip()

            tries += 1

        if notebook_name is None:
            raise RuntimeError(
                "Can't determine the name of the current notebook. "
                "Please, manually specify the name to the current notebook in `get_current_notebook_path` function."
            )

        return os.path.join(os.getcwd(), notebook_name)

    def _is_dml_results_dir(self, path: str) -> bool:
        """
        Checks if the specified path is a dreamml_base experiment directory by verifying the presence of the `dml_version.txt` file.

        Args:
            path (str): Path to check.

        Returns:
            bool: True if the path is a dreamml_base results directory, False otherwise.
        """
        dml_version_path = os.path.join(path, self._dml_version_file)
        return os.path.isdir(path) and os.path.exists(dml_version_path)

    def _save_dml_version(self, path: str) -> None:
        """
        Saves the current dreamml_base version to the specified directory.

        Args:
            path (str): Path where the version file will be saved.
        """
        dml_version_path = os.path.join(path, self._dml_version_file)

        with open(dml_version_path, "w") as f:
            f.write(dreamml.__version__)

    def get_dreamml_experiment_dirs(self) -> List[str]:
        """
        Retrieves a list of dreamml_base experiment directories.

        Returns:
            List[str]: List of dreamml_base experiment directory names.
        """
        dml_dirs = [
            p
            for p in os.listdir(self._results_path)
            if self._is_dml_results_dir(os.path.join(self._results_path, p))
        ]

        return dml_dirs

    def create_experiment_dir(self) -> None:
        """
        Creates the main directory for saving experiment artifacts and subdirectories for specific experiment outputs. 
        If the main directory exists, it finds the next available experiment number and creates a new directory.
        """
        os.makedirs(self._results_path, exist_ok=True)

        dml_dirs = self.get_dreamml_experiment_dirs()

        self._run_number = len(dml_dirs) + 1
        self._experiment_path = os.path.join(
            self._results_path, self.experiment_dir_name
        )

        if os.path.exists(self._experiment_path):
            for try_idx in range(1, 100):
                dir_ = self._experiment_path + f"({try_idx})"
                if not os.path.exists(dir_):
                    self._experiment_path = dir_
                    break

        os.makedirs(self.experiment_path, exist_ok=True)

        dirs_to_create = [
            "models",
            "models/hyperparams",
            "models/used_features",
            "config",
            "images",
            "notebooks",
            "docs",
            "data",
            "cpts",
            "logs",
        ]

        for d in dirs_to_create:
            dir_path = os.path.join(self.experiment_path, d)
            os.mkdir(dir_path)

        self._save_dml_version(self.experiment_path)

    @staticmethod
    def save_dict_to_txt(dictionary, filename, mode):
        """
        Saves a nested dictionary to a text file in a structured format.

        Args:
            dictionary (dict): The dictionary to save.
                Format:
                {
                    model_name1: {
                        'features': list,
                        'hyperparams': dict
                    },
                    model_name2: {
                        'features': list,
                        'hyperparams': dict
                    }
                }
            filename (str): The name of the file to save the dictionary.
            mode (str): The file mode (e.g., 'w' for write).
        """
        with open(filename, mode, encoding="utf-8") as f:
            for model in dictionary:
                f.writelines(model)
                f.writelines(":\n")
                for item in dictionary[model]:
                    f.writelines("\t" + item + " : " + str(dictionary[model][item]))
                    f.writelines("\n")
                f.writelines("\n")
            f.writelines(37 * "#")
            f.writelines("\n\n")


class ArtifactSaver(BaseSaver):
    """
    Saver for storing pipeline output files. Ensures the directory structure is set up correctly 
    before saving data. Inherits from BaseSaver.

    Directory Purpose
    -----------------
    - {path}: Directory for saving output information of all runs.
    - {path}/{experiment_number}: Directory for saving output information of the current experiment.
    - {path}/{experiment_number}/config: Directory for saving configuration files.
    - {path}/{experiment_number}/docs: Directory for saving reports.
    - {path}/{experiment_number}/images: Directory for saving plots.
    - {path}/{experiment_number}/models: Directory for saving models.
    - {path}/{experiment_number}/cpts: Directory for saving pipeline checkpoints.
    - {path}/{experiment_number}/other_models: Directory for saving models from multiple model training stages (batch stage).

    Attributes:
        dir_ (str): Path with the experiment number.
    """

    def __init__(self, config: ConfigStorage) -> None:
        """
        Initializes the ArtifactSaver with the given configuration.

        Args:
            config (ConfigStorage): Configuration class for the experiment.
        """
        super().__init__(config.pipeline.saving.path)
        self.config = config
        self._custom_data_split = self.config.data.dev_path is None
        self.target_name = config.data.columns.target_name
        self.model_id = config.pipeline.model_id.lower()
        self.task = config.pipeline.task

    @property
    def run_prefix(self):
        """
        Constructs the run prefix based on model ID and target/task name.

        Returns:
            str: The constructed run prefix.
        """
        target_part = (
            self.target_name if isinstance(self.target_name, str) else self.task
        )

        return f"{self.model_id}_{target_part}".lower()

    @property
    def dev_report_name(self):
        """
        Constructs the development report name.

        Returns:
            str: The development report name.
        """
        return f"{self.model_id}_dev_report_run_{self.run_number}"

    def create_experiment_dir(self) -> None:
        """
        Creates the main directory for saving experiment artifacts and additional subdirectories 
        specific to ArtifactSaver requirements. Extends the directory creation from BaseSaver.
        """
        super(ArtifactSaver, self).create_experiment_dir()
        os.mkdir(f"{self.experiment_path}/{OTHER_MODELS_DIR}/")
        os.mkdir(f"{self.experiment_path}/{OTHER_MODELS_DIR}/hyperparams/")
        os.mkdir(f"{self.experiment_path}/{OTHER_MODELS_DIR}/used_features/")
        if self.task == "timeseries":
            os.mkdir(f"{self.experiment_path}/{ETNA_PIPELINE_DIR}/")

    def save_data(
        self, data: dict, dropped_data: dict = None, etna_eval_set: dict = None
    ) -> None:
        """
        Saves a dictionary containing datasets after splitting into train/valid/test to ensure full reproducibility 
        of modeling results.

        Args:
            data (dict): Dictionary with datasets where keys are dataset names and values are tuples of feature matrices 
                         and target vectors.
            dropped_data (dict, optional): Dictionary with datasets where keys are dataset names and values are 
                                           DataFrames with features dropped based on `data.columns.drop_features`.
                                           Defaults to None.
            etna_eval_set (dict, optional): Evaluation sets for ETNA. Defaults to None.
        """
        if self.config.pipeline.task != "amts":
            if etna_eval_set is not None:
                pickle.dump(
                    etna_eval_set,
                    open(f"{self.experiment_path}/data/etna_eval_sets.pkl", "wb"),
                )
                _logger.info(f"Saved to {self.experiment_path}/data/etna_eval_sets.pkl")

            if dropped_data and not dropped_data["train"].empty:
                for key in data:
                    for name in list(dropped_data[key].columns):
                        data[key][0][name] = dropped_data[key][name]

        eval_sets_path = os.path.join(self.experiment_path, "data", "eval_sets.pkl")
        _logger.info(f"Saving dict with data to: {eval_sets_path}")
        pickle.dump(data, open(eval_sets_path, "wb"))

        if self.config.pipeline.saving.save_to_ps:
            ps_config = self.config.pipeline.saving.persistent_storage
            self.save_data_to_hdfs(
                data=data,
                storage_name=ps_config.storage_name,
                table_name=ps_config.table_name,
                prefix=ps_config.prefix,
                suffix=ps_config.suffix,
                model_id=ps_config.model_id,
            )

    def save_data_to_hdfs(
        self,
        data: dict,
        spark_config=None,
        storage_name: str = None,
        table_name: str = None,
        prefix: str = "dml",
        suffix: str = date.today().strftime("%Y%m%d"),
        model_id: str = None,
    ) -> None:
        """
        Saves data to HDFS.

        Args:
            data (dict): Dictionary with datasets where keys are dataset names and values are tuples of feature matrices 
                         and target vectors.
            spark_config (SparkConf, optional): Spark session configurations. Defaults to None.
            storage_name (str, optional): Name of the storage to save data. Defaults to None.
            table_name (str, optional): Name of the table to save data. Defaults to None.
            prefix (str, optional): Prefix for the table name. Defaults to "dml".
            suffix (str, optional): Suffix for the table name, typically the current date. Defaults to today's date.
            model_id (str, optional): Model ID for the table name. Defaults to None.
        """
        if not storage_name:
            if self._custom_data_split:
                storage_name = self.config.data.train_path.split(".")[0]
            else:
                storage_name = self.config.data.dev_path.split(".")[0]

        if not table_name:
            if self._custom_data_split:
                table_name = self.config.data.train_path.split(".")[1]
            else:
                table_name = self.config.data.dev_path.split(".")[1]

        prefix = prefix + "_" if prefix else ""
        suffix = "_" + suffix if suffix else ""
        model_id = model_id + "_" if model_id else ""

        temp_dir = TempDirectory(path=self.config.data.spark.temp_dir_path)
        spark = create_spark_session(spark_config=spark_config, temp_dir=temp_dir)
        list_of_tables = spark.catalog.listTables(storage_name)

        list_of_table_names = [x.name for x in list_of_tables]

        data_to_save = {}
        for k in data.keys():
            if k.upper() != "OOT":
                df = data[k][0]
                df[self.config.data.columns.target_name] = data[k][1]
                data_to_save[k] = spark.createDataFrame(df)

        n = 0
        for k in data_to_save.keys():
            result_name = f"{prefix}{model_id}{table_name}_{k}{suffix}"

            if n == 0:
                while result_name in list_of_table_names:
                    n += 1
                    result_name = f"{prefix}{model_id}{table_name}_{k}{suffix}_{n}"
            else:
                result_name = f"{prefix}{model_id}{table_name}_{k}{suffix}_{n}"

            if n == 0:
                table_name_for_comparison = None
            elif n == 1:
                table_name_for_comparison = f"{prefix}{model_id}{table_name}_{k}{suffix}"
            else:
                table_name_for_comparison = f"{prefix}{model_id}{table_name}_{k}{suffix}_{n - 1}"

            if table_name_for_comparison:
                df_for_comparison = spark.table(
                    f"{storage_name}.{table_name_for_comparison}"
                )

                df_for_comparison.cache()
                data_to_save_stats = (
                    data_to_save[k]
                    .select(
                        F.mean(F.col(self.config.data.columns.target_name)).alias(
                            "mean"
                        )
                    )
                    .collect()
                )
                df_for_comparison_stats = df_for_comparison.select(
                    F.mean(F.col(self.config.data.columns.target_name)).alias("mean")
                ).collect()
                stats_df = {
                    "rows": {
                        "old": df_for_comparison.count(),
                        "new": data_to_save[k].count(),
                    },
                    "cols": {
                        "old": len(df_for_comparison.columns),
                        "new": len(data_to_save[k].columns),
                    },
                    "mean": {
                        "old": df_for_comparison_stats[0]["mean"],
                        "new": data_to_save_stats[0]["mean"],
                    },
                }

                if (
                    stats_df["rows"]["new"] == stats_df["rows"]["old"]
                    and stats_df["cols"]["new"] == stats_df["cols"]["old"]
                    and stats_df["mean"]["new"] == stats_df["mean"]["old"]
                ):
                    result_name = table_name_for_comparison

            data_to_save[k].write.saveAsTable(
                f"{storage_name}.{result_name}", mode="Overwrite"
            )
            _logger.info(f"Saved to Persistent Storage: {storage_name}.{result_name}")

        stop_spark_session(spark, temp_dir=temp_dir)

    def save_artifacts(
        self,
        models: dict,
        other_models: dict = None,
        feature_threshold=100,
        encoder=None,
        ipynb_name: Optional[str] = None,
        etna_pipeline: Optional = None,
        vectorizers: Optional = None,
        text_transformers: Optional[Dict[str, TextFeaturesTransformer]] = None,
    ) -> None:
        """
        Saves models and modeling objects necessary for reproducing the model's work, including transformers, encoders, and estimators.

        Args:
            models (dict): Dictionary containing objects necessary for reproducing the model's work. 
                           Keys are stage names (transformer, encoder, etc.), and values are trained objects.
            other_models (dict, optional): Dictionary with models obtained during multiple model training stages (e.g., Batch Stage). Defaults to None.
            feature_threshold (int, optional): Complexity threshold for saving models from other_models. Defaults to 100.
            encoder (optional): Encoder for variables. Defaults to None.
            ipynb_name (str, optional): Path to the Jupyter notebook with the experiment. Defaults to None.
            etna_pipeline (Optional, optional): EtnaPipeline object for timeseries tasks. Defaults to None.
            vectorizers (Optional, optional): Dictionary with text feature vectorizers for multi-class or binary classification tasks. Defaults to None.
            text_transformers (Optional[Dict[str, TextFeaturesTransformer]], optional): Dictionary of transformers for preprocessing text features. Defaults to None.
        """
        models_ = deepcopy(models)
        imp = [col for col in models_ if "importance" in col]
        for col in imp:
            _ = models_.pop(col)

        summary_stages_info = dict()
        for model_name, model in models_.items():
            model.save_pretrained(f"{self.experiment_path}/models/{model_name}.pkl")

            summary_stages_info[model_name] = {
                "used_features": models_[model_name].used_features,
                "hyperparams": models_[model_name].params,
            }

        self.save_dict_to_txt(
            summary_stages_info,
            f"{self.experiment_path}/summary_stages_info.txt",
            mode="w",
        )

        if encoder:
            encoder.save_pretrained(f"{self.experiment_path}/models/encoder.pkl")
        if text_transformers:
            for text_transformer_name, text_transformer in text_transformers.items():
                text_transformer.save_pretrained(
                    f"{self.experiment_path}/models/{text_transformer_name}.pkl"
                )

        if other_models:
            self.save_other_models(other_models, feature_threshold=feature_threshold)
        self.config.save_pretrained(f"{self.experiment_path}/config")

        self.save_dependencies()
        shutil.copy2(
            ipynb_name, f"{self.experiment_path}/notebooks/fit_model_notebook.ipynb"
        )

        if etna_pipeline is not None:
            self.save_etna_pipeline(etna_pipeline)

        if isinstance(vectorizers, dict) and len(vectorizers) != 0:
            self.save_vectorizers(vectorizers)

    def save_other_models(self, other_models: dict, feature_threshold: int = 100):
        """
        Saves models from multiple model training stages that are below a specified complexity threshold.

        Args:
            other_models (dict): Dictionary with models from multiple model training stages.
            feature_threshold (int, optional): Complexity threshold for saving models. Defaults to 100.
        """
        chosen_models = {
            n: m["estimator"]
            for n, m in other_models.items()
            if len(m["estimator"].used_features) <= feature_threshold
        }
        other_models_path = Path(self.experiment_path) / OTHER_MODELS_DIR
        summary_stages_info = dict()
        for model_name, model in chosen_models.items():
            model.save_pretrained(other_models_path / f"{model_name}.pkl")

            summary_stages_info[model_name] = {
                "used_features": model.used_features,
                "hyperparams": model.params,
            }
        self.save_dict_to_txt(
            summary_stages_info,
            f"{self.experiment_path}/summary_stages_info.txt",
            mode="a",
        )

    def save_etna_pipeline(self, etna_pipeline):
        """
        Saves the ETNA pipeline to a zip file.

        Args:
            etna_pipeline (EntaPipeline): EtnaPipeline object to save.
        """
        etna_pipeline.save(
            Path(self.experiment_path) / ETNA_PIPELINE_DIR / "etna_pipeline.zip"
        )

    def save_vectorizers(self, vectorizers: Dict[str, BaseVectorization]):
        """
        Saves the provided vectorizers.

        Args:
            vectorizers (Dict[str, BaseVectorization]): Dictionary of vectorizers to save.
        """
        for vec_name, vectorizer in vectorizers.items():
            vectorizer.save_pretrained(f"{self.experiment_path}/models/{vec_name}.pkl")


class ArtifactSaverCompat(BaseSaver):
    """
    Compatibility saver for older modules not updated in release 2.0. 
    Functions similarly to ArtifactSaver but accepts configurations in dictionary format.

    Directory Purpose
    -----------------
    - {path}: Directory for saving output information of all runs.
    - {path}/{experiment_number}: Directory for saving output information of the current experiment.
    - {path}/{experiment_number}/config: Directory for saving configuration files.
    - {path}/{experiment_number}/docs: Directory for saving reports.
    - {path}/{experiment_number}/images: Directory for saving plots.
    - {path}/{experiment_number}/models: Directory for saving models.

    Attributes:
        dir_ (str): Path with the experiment number.
    """

    def __init__(self, config: dict, path: str = "runs", prefix_name: str = "") -> None:
        """
        Initializes the ArtifactSaverCompat with the given configuration.

        Args:
            config (dict): Dictionary containing experiment configuration.
            path (str, optional): Path for saving experiment output files. Defaults to "runs".
            prefix_name (str, optional): Prefix for the modeling artifacts directory. Defaults to "".
        """
        super().__init__(path)
        self.config = config
        self.target_name = config.get("target_name", "")
        self.model_id = config.get("model_id", "model_id").lower()
        if self.target_name:
            self.target_name = f"{self.model_id}_{self.target_name}{prefix_name}_run_"
            self.target_name = self.target_name.lower()

        self.create_experiment_dir()

    def save_data(self, data: dict, dropped_data: dict) -> None:
        """
        Saves a dictionary containing datasets after splitting into train/valid/test to ensure full reproducibility 
        of modeling results.

        Args:
            data (dict): Dictionary with datasets where keys are dataset names and values are tuples of feature matrices 
                         and target vectors.
            dropped_data (dict): Dictionary with datasets where keys are dataset names and values are DataFrames 
                                 with features dropped based on `target_name`.
        """
        if not dropped_data["train"].empty:
            for key in data.keys():
                for name in list(dropped_data[key].columns):
                    data[key][0][name] = dropped_data[key][name]
        pickle.dump(data, open(f"{self.experiment_path}/data/eval_sets.pkl", "wb"))
        _logger.info(f"Saved to {self.experiment_path}/data/eval_sets.pkl")
        if self.config.get("save_to_ps"):
            self.save_data_to_hdfs(data=data, **self.config["save_to_ps_params"])

    def save_data_to_hdfs(
        self,
        data: dict,
        spark_config=None,
        storage_name: str = None,
        table_name: str = None,
        prefix: str = "dml",
        suffix: str = date.today().strftime("%Y%m%d"),
        model_id: str = None,
    ) -> None:
        """
        Saves data to HDFS.

        Args:
            data (dict): Dictionary with datasets where keys are dataset names and values are tuples of feature matrices 
                         and target vectors.
            spark_config (SparkConf, optional): Spark session configurations. Defaults to None.
            storage_name (str, optional): Name of the storage to save data. Defaults to None.
            table_name (str, optional): Name of the table to save data. Defaults to None.
            prefix (str, optional): Prefix for the table name. Defaults to "dml".
            suffix (str, optional): Suffix for the table name, typically the current date. Defaults to today's date.
            model_id (str, optional): Model ID for the table name. Defaults to None.
        """
        if not storage_name:
            if self.config.data.dev_path:
                storage_name = self.config.data.dev_path.split(".")[0]
            else:
                storage_name = self.config.data.train_path.split(".")[0]

        if not table_name:
            if self.config.data.dev_path:
                table_name = self.config.data.dev_path.split(".")[1]
            else:
                table_name = self.config.data.train_path.split(".")[1]

        prefix = prefix + "_" if prefix else ""
        suffix = "_" + suffix if suffix else ""
        model_id = model_id + "_" if model_id else ""

        spark = create_hive_session(conf=spark_config)
        list_of_tables = spark.catalog.listTables(storage_name)

        list_of_table_names = [x.name for x in list_of_tables]

        data_to_save = {}
        for k in data.keys():
            if k.upper() != "OOT":
                df = deepcopy(data[k][0])
                df[self.config["target_name"]] = deepcopy(data[k][1])
                data_to_save[k] = spark.createDataFrame(df)

        n = 0
        for k in data_to_save.keys():
            result_name = f"{prefix}{model_id}{table_name}_{k}{suffix}"

            if n == 0:
                while result_name in list_of_table_names:
                    n += 1
                    result_name = f"{prefix}{model_id}{table_name}_{k}{suffix}_{n}"
            else:
                result_name = f"{prefix}{model_id}{table_name}_{k}{suffix}_{n}"

            if n == 0:
                table_name_for_comparison = None
            elif n == 1:
                table_name_for_comparison = f"{prefix}{model_id}{table_name}_{k}{suffix}"
            else:
                table_name_for_comparison = f"{prefix}{model_id}{table_name}_{k}{suffix}_{n - 1}"

            if table_name_for_comparison:
                df_for_comparison = spark.table(
                    f"{storage_name}.{table_name_for_comparison}"
                )

                df_for_comparison.cache()
                data_to_save_stats = (
                    data_to_save[k]
                    .select(F.mean(F.col(self.config["target_name"])).alias("mean"))
                    .collect()
                )
                df_for_comparison_stats = df_for_comparison.select(
                    F.mean(F.col(self.config["target_name"])).alias("mean")
                ).collect()
                stats_df = {
                    "rows": {
                        "old": df_for_comparison.count(),
                        "new": data_to_save[k].count(),
                    },
                    "cols": {
                        "old": len(df_for_comparison.columns),
                        "new": len(data_to_save[k].columns),
                    },
                    "mean": {
                        "old": df_for_comparison_stats[0]["mean"],
                        "new": data_to_save_stats[0]["mean"],
                    },
                }

                if (
                    stats_df["rows"]["new"] == stats_df["rows"]["old"]
                    and stats_df["cols"]["new"] == stats_df["cols"]["old"]
                    and stats_df["mean"]["new"] == stats_df["mean"]["old"]
                ):
                    result_name = table_name_for_comparison

            data_to_save[k].write.saveAsTable(
                f"{storage_name}.{result_name}", mode="Overwrite"
            )
            _logger.info(f"Saved to Persistent Storage: {storage_name}.{result_name}")

        spark.stop()