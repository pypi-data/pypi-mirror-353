import os
import pickle
import yaml
from pathlib import Path
from typing import Dict, Union

from dreamml.utils.get_last_experiment_directory import get_experiment_dir_path
from dreamml.data._hadoop import create_spark_session, stop_spark_session
from dreamml.data.store import get_input
from dreamml.utils.splitter import DataSplitter
from dreamml.utils.temporary_directory import TempDirectory


def get_model_path_from_config(config: Dict):
    """
    Retrieves the model path from the configuration dictionary. If the
    "model_path" key is present in the config, it returns its value. Otherwise,
    it constructs the model path based on the experiment directory.

    Args:
        config (Dict): Configuration dictionary containing model and experiment details.

    Returns:
        str: The path to the model file.
    """
    if config.get("model_path"):
        model_path = config["model_path"]
    else:
        experiment_dir_path = get_experiment_dir_path(
            config["results_path"],
            experiment_dir_name=config.get("dir_name"),
            use_last_experiment_directory=config.get(
                "use_last_experiment_directory", False
            ),
        )

        model_path = os.path.join(
            experiment_dir_path, "models", f"{config['model_name']}.pkl"
        )

    return model_path


def get_encoder_path_from_config(config: Dict):
    """
    Retrieves the encoder path from the configuration dictionary. If the
    "encoder_path" key is present in the config, it returns its value. Otherwise,
    it constructs the encoder path based on the experiment directory.

    Args:
        config (Dict): Configuration dictionary containing encoder and experiment details.

    Returns:
        str: The path to the encoder file.
    """
    if config.get("encoder_path"):
        model_path = config["encoder_path"]
    else:
        experiment_dir_path = get_experiment_dir_path(
            config["results_path"],
            experiment_dir_name=config.get("dir_name"),
            use_last_experiment_directory=config.get(
                "use_last_experiment_directory", False
            ),
        )

        model_path = os.path.join(experiment_dir_path, "models", f"encoder.pkl")

    return model_path


def _load_pickle(path: str):
    """
    Loads a Python object from a pickle file.

    Args:
        path (str): The file path to the pickle file.

    Returns:
        Any: The Python object loaded from the pickle file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        pickle.UnpicklingError: If the file is not a valid pickle file.
    """
    with open(path, "rb") as f:
        obj = pickle.load(f)

    return obj


def load_yaml(path: Union[str, Path]):
    """
    Loads and parses a YAML file.

    Args:
        path (Union[str, Path]): The file path to the YAML file.

    Returns:
        Any: The data parsed from the YAML file.

    Raises:
        Exception: If the specified file does not exist.
        yaml.YAMLError: If the file contains invalid YAML.
    """
    if not os.path.isfile(path):
        raise Exception("File not found: {}".format(path))

    with open(path, "r", encoding="utf-8") as f:
        file = yaml.load(f, yaml.FullLoader)
    return file


def load_model(path: str):
    """
    Loads a machine learning model from a specified path. Supports pickle files.

    Args:
        path (str): The file path to the model.

    Returns:
        Any: The loaded machine learning model.

    Raises:
        ValueError: If the file extension is not supported for loading.
        FileNotFoundError: If the specified file does not exist.
        pickle.UnpicklingError: If the file is not a valid pickle file.
    """
    ext = Path(path).suffix
    if ext in [".pkl", ".pickle"]:
        obj = _load_pickle(path)
    else:
        raise ValueError(f"Can't load model. Unsupported file extension: {ext}")

    return obj


def get_eval_sets_from_config(config: Dict):
    """
    Generates evaluation datasets based on the provided configuration. It handles
    both local and remote data sources, applies encoding if necessary, and splits
    the data into training, validation, test, and optionally out-of-time (OOT) sets.

    Args:
        config (Dict): Configuration dictionary containing dataset paths and parameters.

    Returns:
        Dict[str, Tuple[Any, Any]]: A dictionary containing the evaluation sets
        with keys 'train', 'valid', 'test', and optionally 'OOT'.

    Raises:
        Exception: If required files are not found.
        ValueError: If there are issues with data loading or processing.
    """
    dev_data_path = config.get("dev_data_path")

    if dev_data_path is None:
        experiment_dir_path = get_experiment_dir_path(
            config["results_path"],
            experiment_dir_name=config.get("dir_name"),
            use_last_experiment_directory=config.get(
                "use_last_experiment_directory", False
            ),
        )

        eval_sets_path = os.path.join(experiment_dir_path, "data", f"eval_sets.pkl")

        if os.path.exists(eval_sets_path):
            return _load_pickle(eval_sets_path)

    else:
        encoder_path = get_encoder_path_from_config(config)
        encoder = load_model(encoder_path) if os.path.exists(encoder_path) else None

        spark = None
        temp_dir = None

        local_file_extenstions = [".csv", ".pkl", ".pickle", ".parquet"]

        if Path(dev_data_path).suffix not in local_file_extenstions:
            temp_dir = TempDirectory()
            spark = create_spark_session(spark_config=None, temp_dir=temp_dir)

        dev_data, target = get_input(
            spark=spark, data_path="dev_data_path", config=config
        )

        if encoder is not None:
            dev_data = encoder.transform(dev_data)

        splitter = DataSplitter(
            split_fractions=[0.6, 0.2, 0.2],
            shuffle=True,
            group_column=None,
            target_name=config.get("target_name"),
            stratify=True,
        )

        train_idx, valid_idx, test_idx = splitter.transform(dev_data, target)

        eval_sets = {
            "train": (dev_data.loc[train_idx], target.loc[train_idx]),
            "valid": (dev_data.loc[valid_idx], target.loc[valid_idx]),
            "test": (dev_data.loc[test_idx], target.loc[test_idx]),
        }
        # Handle the case where a Spark session might be needed

        if config.get("oot_data_path") is not None:
            oot_data_path = config["oot_data_path"]
            if (
                Path(oot_data_path).suffix not in local_file_extenstions
                and spark is None
            ):
                temp_dir = TempDirectory()
                spark = create_spark_session(spark_config=None, temp_dir=temp_dir)
            oot, oot_target = get_input(
                spark=spark, data_path="oot_data_path", config=config
            )
            if encoder is not None:
                oot = encoder.transform(oot)
            eval_sets["OOT"] = oot, oot_target

        if spark is not None:
            stop_spark_session(spark=spark, temp_dir=temp_dir)

        return eval_sets