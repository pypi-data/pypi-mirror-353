import os
import warnings
from pathlib import Path
from typing import Dict, Union

import hydra
import numpy as np
from hydra.utils import instantiate
from omegaconf import OmegaConf, DictConfig

from dreamml.config import Config
from dreamml.config._legacy import legacy_key_mapping
from dreamml.configs.config_checker import ConfigChecker
from dreamml.logging import get_logger, get_root_logger
from dreamml.utils.errors import ConfigurationError
from dreamml.utils.warnings import DMLWarning

_logger = get_logger(__name__)

DREAMML_PATH = Path(__file__).parent.parent


def _get_dotted_key_map(cfg, parent_key=""):
    """
    Recursively creates a mapping from dotted key paths to their corresponding values in the configuration.

    Args:
        cfg (dict or DictConfig): The configuration dictionary to process.
        parent_key (str, optional): The base key path for recursion. Defaults to "".

    Returns:
        dict: A dictionary mapping dotted key paths to their respective values.
    """
    dotted_key_to_value = {}

    for key, value in cfg.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict) or isinstance(value, DictConfig):
            # Recurse into nested structures
            dotted_key_to_value.update(_get_dotted_key_map(value, full_key))
        else:
            # Add the mapping of value to its dotted key
            dotted_key_to_value[full_key] = value

    return dotted_key_to_value


def _merge_nested_dicts(base_dict, merge_dict, full_key_path):
    """
    Merges `merge_dict` into `base_dict` in-place. Raises a KeyError if key collisions occur.

    Args:
        base_dict (dict): The dictionary to merge into.
        merge_dict (dict): The dictionary whose contents should be merged.
        full_key_path (str): The full dotted path leading to this merge, used for error reporting.

    Raises:
        KeyError: If a key collision is encountered during the merge.
    """
    for k, v in merge_dict.items():
        if k in base_dict:
            # Collision: key already exists.
            raise KeyError(
                f"Encountered duplicated key {repr(k)} while parsing {repr(full_key_path)}. "
                f"Avoid using dotted keys inside nested dictionaries."
            )
        base_dict[k] = v


def _nested_dict_from_dot_keys(flat_dict):
    """
    Converts a flat dictionary with dot-separated keys into a nested dictionary.

    Args:
        flat_dict (dict): A dictionary where keys are dot-separated strings representing nested keys.

    Returns:
        dict: A nested dictionary corresponding to the structure defined by the dot-separated keys in `flat_dict`.

    Raises:
        KeyError: If a key collision occurs where a non-dictionary value is expected to become a dictionary or if there are duplicated keys at the same level.

    Example:
        >>> flat_dict = {
        ...     'a.b.c': 1,
        ...     'a.b.d': 2,
        ...     'x': 3,
        ...     'y.z': 4
        ... }
        >>> _nested_dict_from_dot_keys(flat_dict)
        {'a': {'b': {'c': 1, 'd': 2}}, 'x': 3, 'y': {'z': 4}}
    """
    nested = {}

    for dotted_key, value in flat_dict.items():
        # Split the key into components (e.g. 'a.b.c' -> ['a', 'b', 'c'])
        key_parts = dotted_key.split(".")
        current_dict = nested

        # Traverse the hierarchy for all but the last key part
        for part in key_parts[:-1]:
            # If the part doesn't exist, create a new dict
            # If it does, ensure it's a dictionary
            if part not in current_dict:
                current_dict[part] = {}
            elif not isinstance(current_dict[part], dict):
                raise KeyError(
                    f"Encountered a scalar value where a dictionary was expected while parsing {repr(dotted_key)} "
                    f"(conflicting key: {repr(part)})."
                )
            current_dict = current_dict[part]

        # Before assigning to the final key part, ensure we handle nested dicts in value
        if isinstance(value, dict):
            # Recursively convert nested dict values that may contain dotted keys themselves
            value = _nested_dict_from_dot_keys(value)

        final_key = key_parts[-1]

        # Check if there's a key collision
        if final_key in current_dict:
            existing_value = current_dict[final_key]
            if isinstance(existing_value, dict) and isinstance(value, dict):
                # Merge dictionaries
                _merge_nested_dicts(existing_value, value, dotted_key)
            else:
                # Can't merge scalar values or different types
                raise KeyError(f"Encountered duplicated key: {repr(final_key)}")
        else:
            # Simply set the value
            current_dict[final_key] = value

    return nested


def _rename_legacy_keys(original_dict):
    """
    Renames legacy keys in the original dictionary based on a predefined key mapping.

    Args:
        original_dict (dict): The dictionary containing original keys.

    Returns:
        dict: A new dictionary with legacy keys renamed to their new counterparts.
    """
    renamed_dict = {}

    for key, value in original_dict.items():
        # Use the new key from key_mapping if it exists, otherwise keep the original key
        new_key = legacy_key_mapping.get(key, key)

        renamed_dict[new_key] = value

    return renamed_dict


class ConfigStorage(Config):
    """
    The primary class for handling configuration management and setting default parameter values.
    """

    _key_mapping: dict
    _user_config: dict
    _config: DictConfig
    _config_checker: ConfigChecker

    def __setattr__(self, key, value):
        """
        Overrides the default setattr to handle setting attributes based on key mappings.

        Args:
            key (str): The attribute name.
            value: The value to set for the attribute.
        """
        if (
            key not in ["_key_mapping", "_user_config", "_config"]
            and key in self._key_mapping
        ):
            dotted_key = self._key_mapping[key]
            d = self
            keys = dotted_key.split(".")
            if len(keys) == 1:
                super().__setattr__(key, value)
                return

            for key in keys[:-1]:
                if isinstance(d, dict):
                    # FIXME: remove after removing Extra.allow
                    d = d[key]
                else:
                    try:
                        d = getattr(d, key)
                    except AttributeError:
                        # FIXME: remove after removing Extra.allow
                        setattr(d, key, value)

            if isinstance(d, dict):
                # FIXME: remove after removing Extra.allow
                d[key] = value
            else:
                setattr(d, keys[-1], value)
        else:
            super().__setattr__(key, value)

    def __getattr__(self, key):
        """
        Overrides the default getattr to handle retrieving attributes based on key mappings.

        Args:
            key (str): The attribute name to retrieve.

        Returns:
            The value of the requested attribute.
        """
        if (
            key not in ["_key_mapping", "_user_config", "_config"]
            and key in self._key_mapping
        ):
            dotted_key = self._key_mapping[key]
            d = self
            keys = dotted_key.split(".")
            if len(keys) == 1:
                return super().__getattr__(key)

            for key in keys[:-1]:
                if isinstance(d, dict):
                    # FIXME: remove after removing Extra.allow
                    d = d[key]
                else:
                    d = getattr(d, key)

            if isinstance(d, dict):
                # FIXME: remove after removing Extra.allow
                value = d[keys[-1]]
            else:
                value = getattr(d, keys[-1])

        else:
            value = super(ConfigStorage, self).__getattr__(key)

        return value

    def __init__(
        self,
        user_config: Union[Dict, DictConfig],
        config_file_path: str = None,
        skip_checks: bool = False,
    ):
        """
        Initializes the ConfigStorage instance by loading and merging configurations.

        Args:
            user_config (Dict or DictConfig): The user-provided configuration.
            config_file_path (str, optional): Path to an additional configuration file. Defaults to None.
            skip_checks (bool, optional): Whether to skip configuration checks. Defaults to False.

        Raises:
            ConfigurationError: If the task is not specified in the user configuration.
        """
        task = self._get_task_from_user_config(user_config)
        if task is None:
            raise ConfigurationError("Task must be specified.")

        user_config_dir = user_config.get("config_dir")
        cfg_path = self._get_default_config_path(
            user_config, user_config_dir=user_config_dir
        )
        cfg = self._get_default_conifg(cfg_path, overrides=[f"+task_defaults={task}"])

        if skip_checks:
            OmegaConf.set_struct(cfg, False)

        cfg = self._merge_config_with_user_config(cfg, user_config)

        if config_file_path:
            loaded_config = self.load_config_file(config_file_path)
            cfg = OmegaConf.merge(cfg, loaded_config)

        config_checker = ConfigChecker(cfg)
        config_checker.modify_and_check_config()

        instantiated_cfg = instantiate(cfg)
        OmegaConf.set_struct(instantiated_cfg, True)

        # TODO: test readonly
        # OmegaConf.set_readonly(instantiated_cfg, True)
        super().__init__(**instantiated_cfg)
        self._key_mapping = legacy_key_mapping
        self._config_checker = config_checker
        self._user_config = user_config
        self._config = cfg

        root_logger = get_root_logger()
        root_logger.start_logging_session()

        ignore_third_party_warnings = True
        if ignore_third_party_warnings:
            warnings.filterwarnings("ignore")
            warnings.filterwarnings("default", category=DMLWarning)

    def check_data(self, data_dict):
        """
        Checks the provided data dictionary against the configuration.

        Args:
            data_dict (dict): The data dictionary to validate.
        """
        self._config_checker.check_data(data_dict)

    def get_all_params(self):
        """
        Retrieves a dictionary containing all configuration parameters and their current values.

        Returns:
            dict: A dictionary of all configuration parameters and their values.
        """
        return self.dict()

    def get_dotted_key_dict(self):
        """
        Retrieves a dictionary mapping dotted key paths to their corresponding values in the configuration.

        Returns:
            dict: A dictionary with dotted keys as keys and their respective values.
        """
        return _get_dotted_key_map(self._config)

    def save_config_file(self, path: str = "./config.yaml"):
        """
        Saves the current configuration to a YAML file at the specified path.

        Args:
            path (str, optional): The file path where the configuration will be saved. Defaults to "./config.yaml".
        """
        # FIXME: strange logic with dynamically setting labels in metric_params
        labels = self.pipeline.metric_params.get("labels")
        if labels is not None:
            if isinstance(labels, np.ndarray):
                labels = labels.tolist()
            self._config.pipeline.metric_params.labels = labels

        # FIXME: dynamically setting parameters in config
        self._config.data.splitting.custom_cv = self.data.splitting.custom_cv

        # TODO: probably we can do OmegaConf.merge(self._config, DictConfig(self.dict()))
        # TODO: to update all parameters that were set during pipeline
        # TODO: problem: losing ${} interpolations

        OmegaConf.save(self._config, path)

    @staticmethod
    def load_config_file(path: str = "./config.yaml") -> DictConfig:
        """
        Loads a configuration from a YAML file.

        Args:
            path (str, optional): The file path from which to load the configuration. Defaults to "./config.yaml".

        Returns:
            DictConfig: The loaded configuration.
        """
        loaded_data = OmegaConf.load(path)

        return loaded_data

    def save_pretrained(self, path):
        """
        Saves the current configuration as a pretrained configuration to the specified directory.

        Args:
            path (str): The directory path where the pretrained configuration will be saved.
        """
        os.makedirs(path, exist_ok=True)

        path = os.path.join(path, "config.yaml")
        self.save_config_file(path)

    @classmethod
    def from_pretrained(cls, path):
        """
        Loads a pretrained configuration from the specified directory and returns a ConfigStorage instance.

        Args:
            path (str): The directory path from which to load the pretrained configuration.

        Returns:
            ConfigStorage: An instance of ConfigStorage initialized with the pretrained configuration.
        """
        path = os.path.join(path, "config.yaml")

        cfg = cls.load_config_file(path)

        # TODO: any changes here for backward compatibility

        return cls(cfg, skip_checks=True)

    @staticmethod
    def _get_task_from_user_config(config):
        """
        Extracts the task from the user-provided configuration.

        Args:
            config (dict or DictConfig): The user configuration.

        Returns:
            str or None: The task if specified, otherwise None.
        """
        task = (
            config.get("pipeline.task")
            or config.get("pipeline", {}).get("task")
            or config.get("task")  # deprecated
        )

        return task

    @staticmethod
    def _get_module_config_dir():
        """
        Retrieves the default configuration directory for the module.

        Returns:
            str: The path to the module's configuration directory.
        """
        return str(Path(__file__).parent.parent / "config")

    @staticmethod
    def _get_default_config_path(user_config=None, user_config_dir=None):
        """
        Determines the default configuration path based on user configuration and directory.

        Args:
            user_config (dict or DictConfig, optional): The user-provided configuration. Defaults to None.
            user_config_dir (str, optional): The user-provided configuration directory. Defaults to None.

        Returns:
            str: The path to the default configuration directory.
        """
        config_path = None
        if user_config_dir is not None:
            config_path = user_config_dir
        elif user_config is not None:
            saving_path = (
                user_config.get("pipeline.saving.path")
                or user_config.get("pipeline.saving", {}).get("path")
                or user_config.get("pipeline", {}).get("saving.path")
                or user_config.get("pipeline", {}).get("saving", {}).get("path")
                or user_config.get("path")  # deprecated
            )

            if saving_path is not None:
                possible_config_path = str((Path(saving_path).parent.resolve() / "dreamml" / "config"))

                if os.path.exists(possible_config_path):
                    config_path = possible_config_path

        if config_path is None:
            config_path = ConfigStorage._get_module_config_dir()

        _logger.info(f"Using config at location: {config_path}")

        return config_path

    @staticmethod
    def _get_default_conifg(config_dir, overrides=None):
        """
        Initializes Hydra and composes the default configuration with optional overrides.

        Args:
            config_dir (str): The directory containing the configuration files.
            overrides (list, optional): A list of configuration overrides. Defaults to None.

        Returns:
            DictConfig: The composed default configuration.
        """
        with hydra.initialize_config_dir(config_dir=config_dir, version_base="1.3"):
            cfg = hydra.compose(config_name="default", overrides=overrides)

        return cfg

    @staticmethod
    def _create_omegaconf(user_config: dict):
        """
        Transforms user-provided configuration by renaming legacy keys and converting dotted keys to a nested structure.

        Args:
            user_config (dict): The user-provided flat configuration dictionary.

        Returns:
            DictConfig: The transformed nested DictConfig.
        """
        dotted_config = _rename_legacy_keys(user_config)

        nested_dict = _nested_dict_from_dot_keys(dotted_config)

        return DictConfig(nested_dict)

    @staticmethod
    def _merge_config_with_user_config(config: DictConfig, user_config):
        """
        Merges the user configuration with the default configuration.

        Args:
            config (DictConfig): The default configuration.
            user_config (dict or DictConfig): The user-provided configuration.

        Returns:
            DictConfig: The merged configuration.
        """
        if not isinstance(user_config, DictConfig):
            user_config = ConfigStorage._create_omegaconf(user_config)

        for vec_name in ["tfidf", "fasttext", "glove", "word2vec"]:
            vec_params = getattr(config.pipeline.vectorization, vec_name).params
            OmegaConf.set_struct(vec_params, False)

        # for additional params
        OmegaConf.set_struct(config.pipeline.metric_params, False)

        # for custom cv
        OmegaConf.set_struct(config.data.splitting.validation_params.cv_params, False)

        merged_cfg = OmegaConf.merge(config, user_config)

        return merged_cfg