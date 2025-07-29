from typing import List, Any, Optional

from pydantic import Extra, Field, model_validator

from dreamml.config._base_config import BaseConfig
from dreamml.config.data import DataConfig
from dreamml.config.models import ModelsConfig
from dreamml.config.pipeline import PipelineConfig
from dreamml.config.stages import StagesConfig
from dreamml.config.validation import ValidationConfig


class Config(BaseConfig, extra=Extra.forbid):
    """
    Configuration class that aggregates various configuration components for the dreamml_base framework.

    Attributes:
        data (DataConfig): Configuration related to data processing.
        models (ModelsConfig): Configuration for machine learning models.
        pipeline (PipelineConfig): Configuration for the machine learning pipeline.
        stages (StagesConfig): Configuration for different stages in the pipeline.
        validation (ValidationConfig): Configuration for data validation processes.
        service_fields (List[Any]): List of service-specific fields, default is an empty list.
        config_dir (Optional[str]): Directory path where configuration files are located.
    """

    data: DataConfig
    models: ModelsConfig
    pipeline: PipelineConfig
    stages: StagesConfig
    validation: ValidationConfig
    service_fields: List = Field([], alias="_service_fields")
    config_dir: Optional[str] = None

    @model_validator(mode="after")
    def _check_pyboost_device(self):
        """
        Validates that if 'pyboost' is included in the pipeline's model list, the device is set to 'cuda'.

        Raises:
            ValueError: If 'pyboost' is in the model list but the device is not set to 'cuda'.
        
        Returns:
            Config: The validated configuration instance.
        """
        if "pyboost" in self.pipeline.model_list and self.pipeline.device != "cuda":
            raise ValueError(
                "PyBoost supports only GPU mode. "
                "Please remove PyBoost from pipeline.model_list or change device type to GPU."
            )

        return self

    @model_validator(mode="after")
    def _check_forbidden_grouping(self):
        """
        Ensures that 'linear_reg' estimator is not used with 'group_column' in 'amts' tasks.

        Raises:
            ValueError: If 'linear_reg' is in the model list and grouping by group column is enabled for 'amts' task.
        
        Returns:
            Config: The validated configuration instance.
        """
        if (
            self.pipeline.task == "amts"
            and "linear_reg" in self.pipeline.model_list
            and self.data.splitting.split_by_group
        ):
            raise ValueError(
                "'linear_reg' estimator with 'group_column' in 'amts' task is not supported."
            )

        return self

    @model_validator(mode="after")
    def _check_target_name_provided(self):
        """
        Validates the presence and type of 'target_name' based on the pipeline task.

        Raises:
            ValueError: 
                - If 'target_name' is not specified for tasks that require it.
                - If 'target_name' is not a string for tasks other than 'multilabel' and 'multiregression'.
                - If 'target_name' is not a list of strings for 'multilabel' and 'multiregression' tasks.
        
        Returns:
            Config: The validated configuration instance.
        """
        if self.data.columns.target_name is None:
            if self.pipeline.task not in [
                "topic_modeling",
                "phrase_retrieval",
                "anomaly_detection",
            ]:
                raise ValueError(
                    f"`target_name` must be specified for {self.pipeline.task} task."
                )
        elif not isinstance(
            self.data.columns.target_name, str
        ) and self.pipeline.task not in ["multilabel", "multiregression"]:
            raise ValueError(
                f"'target_name' must be 'str' for {self.pipeline.task} task "
                f"but received `{type(self.data.columns.target_name )}`."
            )
        elif not isinstance(
            self.data.columns.target_name, list
        ) and self.pipeline.task in ["multilabel", "multiregression"]:
            raise ValueError(
                f"'target_name' must be a list of strings for {self.pipeline.task} task "
                f"but received `{type(self.data.columns.target_name )}`."
            )

        return self