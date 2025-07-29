from pathlib import Path
from typing import Dict

import omegaconf
from omegaconf import DictConfig
import torch

from dreamml.logging import get_logger

_logger = get_logger(__name__)


class ConfigChecker:
    """A class to modify and validate configuration settings.

    This class provides methods to adjust configuration parameters
    and ensure they meet the required criteria for the pipeline execution.
    """

    def __init__(
        self,
        config: DictConfig,
    ):
        """Initializes the ConfigChecker with the given configuration.

        Args:
            config (DictConfig): The configuration object to be checked and modified.
        """
        self.config = config

    def modify_and_check_config(self):
        """Modifies and validates the configuration.

        This method sequentially updates various configuration parameters
        and ensures that the configuration is suitable for the pipeline.

        Returns:
            DictConfig: The modified and validated configuration.

        Raises:
            ValueError: If the device specified is 'cuda' but CUDA is not available.
        """
        self.set_subtask()
        self.set_absolute_path()
        self.set_parallelism_to_num_targets()
        self.set_auto_device()
        self.modify_cuda_unsupported_params()

        return self.config

    def set_subtask(self):
        """Sets the subtask in the pipeline configuration based on vectorization algorithms and text features.

        If both vectorization algorithms and text features are present, sets the subtask to 'nlp'.
        Otherwise, sets it to 'tabular'.
        """
        if (
            len(self.config.pipeline.vectorization.vectorization_algos) > 0
            and len(self.config.data.columns.text_features) > 0
        ):
            self.config.pipeline.subtask = "nlp"
        else:
            self.config.pipeline.subtask = "tabular"

    def set_absolute_path(self):
        """Converts the saving path in the pipeline configuration to an absolute path."""
        path = self.config.pipeline.saving.path
        self.config.pipeline.saving.path = str(Path(path).resolve())

    def set_parallelism_to_num_targets(self):
        """Sets the pipeline's parallelism based on the number of target variables.

        If the target name is a list and the task is 'multilabel',
        sets the parallelism to the number of targets.
        """
        target_name = self.config.data.columns.target_name
        task = self.config.pipeline.task

        if isinstance(target_name, list) and task == "multilabel":
            self.config.pipeline.parallelism = len(target_name)

    def set_auto_device(self):
        """Automatically sets the device for the pipeline based on CUDA availability.

        If the device is set to 'auto', it selects 'cuda' if available, else 'cpu'.
        Raises an error if 'cuda' is selected but CUDA is not available.

        Raises:
            ValueError: If the device is set to 'cuda' but CUDA is not available.
        """
        cuda_is_available = torch.cuda.is_available()
        if self.config.pipeline.device == "auto":
            self.config.pipeline.device = "cuda" if cuda_is_available else "cpu"

        if self.config.pipeline.device == "cuda" and not cuda_is_available:
            raise ValueError("GPU is not available. Please select another device.")

    def modify_cuda_unsupported_params(self):
        """Modifies configuration parameters that are unsupported by CUDA.

        Specifically, removes the 'colsample_bylevel' parameter from CatBoost optimization bounds
        if the pipeline task is set to 'cuda'.
        """
        if self.config.pipeline.task == "cuda":
            # Parameter does not work on GPU
            with omegaconf.open_dict(self.config):
                del self.config.models.catboost.optimization_bounds.colsample_bylevel

    def check_data(self, data: Dict):
        """Checks the integrity of the provided data.

        Validates the target column in the data based on the task specified in the configuration.

        Args:
            data (Dict): The data to be checked.

        Raises:
            ValueError: If there are NaN values in the target column for certain tasks.
            ValueError: If the target column has an unsupported data type for binary tasks.
        """
        self._data_check_target(data)

    def _data_check_target(self, data):
        """Validates the target column in the data based on the configured task.

        For non-multilabel and non-multiregression tasks, it ensures that there are no NaN
        values in the target column. For binary tasks, it checks that the target column
        is not of float type.

        Args:
            data (Dict): The data to be validated.

        Raises:
            ValueError: If NaN values are detected in the target column for certain tasks.
            ValueError: If the target column has a float data type for binary tasks.
        """
        task = self.config.pipeline.task
        target_name = self.config.data.columns.target_name

        if task == "timeseries":
            target_name = "target"

        if target_name is None:
            return

        for sample, df in data.items():
            if task not in ["multilabel", "multiregression"]:
                if df[target_name].isna().sum() != 0:
                    raise ValueError(
                        f"Detected NaN values in target column `{target_name}` "
                        f"which is explicitly forbidden for '{task}' task."
                    )

            if task in ["binary"]:
                target_dtype = df[target_name].dtype
                if target_dtype == "float":
                    raise ValueError(
                        f"`{target_dtype}` type for target column ({target_name}) is not supported for '{task}' task."
                    )