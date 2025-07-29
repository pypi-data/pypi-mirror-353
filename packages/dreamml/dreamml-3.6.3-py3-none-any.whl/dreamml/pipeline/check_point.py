import pickle
import os
from typing import Dict

from dreamml.logging import get_logger
from dreamml.stages.stage import BaseStage

_logger = get_logger(__name__)


class CheckPoint:
    """Handles checkpointing of experiment stages and pipeline parameters.

    This class provides methods to save and load individual stages of an experiment
    as well as the associated pipeline parameters. It ensures that stages can be
    persisted and retrieved efficiently, facilitating experiment reproducibility
    and continuity.
    """

    def __init__(self, experiment_path: str):
        """Initializes the CheckPoint with the specified experiment path.

        Args:
            experiment_path (str): The file system path where the experiment
                checkpoints will be stored.
        """
        self.experiment_path = experiment_path
        self.checkpoint_path = os.path.join(experiment_path, "cpts")

    def save_stage(self, stage_name: str, stage: BaseStage, pipeline_params: Dict):
        """Saves a stage and pipeline parameters to the checkpoint directory.

        This method serializes the given stage using pickle and stores it in the
        checkpoint directory under a filename derived from the stage name. If the
        stage contains a vectorizer with a loaded model, the model is removed to
        conserve space before saving. The pipeline parameters are also serialized
        and saved separately.

        Args:
            stage_name (str): The name of the stage to be saved.
            stage (BaseStage): The stage instance to serialize and save.
            pipeline_params (Dict): A dictionary of pipeline parameters to serialize and save.

        Raises:
            IOError: If there is an error writing to the filesystem.
            pickle.PickleError: If serialization fails.
        """
        stage_path = os.path.join(self.checkpoint_path, f"{stage_name}.stage")

        if hasattr(stage, "vectorizer") and stage.vectorizer is not None:
            if (
                hasattr(stage.vectorizer, "model_path")
                and stage.vectorizer.model_path is not None
            ):
                stage.vectorizer.vectorizer = None  # Remove the model to save space
                log_msg = f"Removed loaded model from vectorizer {stage.vectorizer.name} to conserve space."
                _logger.debug(log_msg)

        with open(stage_path, "wb") as file:
            pickle.dump(stage, file)

        pipeline_params_path = os.path.join(self.checkpoint_path, f"pipeline_params")
        with open(pipeline_params_path, "wb") as file:
            pickle.dump(pipeline_params, file)

    def load_stage(self, stage_name: str):
        """Loads a stage from the checkpoint directory.

        This method deserializes the stage associated with the given stage name
        from the checkpoint directory.

        Args:
            stage_name (str): The name of the stage to be loaded.

        Returns:
            BaseStage: The deserialized stage instance.

        Raises:
            FileNotFoundError: If the specified stage file does not exist.
            IOError: If there is an error reading the file.
            pickle.PickleError: If deserialization fails.
        """
        stage_path = os.path.join(self.checkpoint_path, f"{stage_name}.stage")
        with open(stage_path, "rb") as file:
            stage = pickle.load(file)
        _logger.info(f"{stage_name} successfully loaded from {stage_path}")

        return stage

    def load_pipeline_params(self):
        """Loads pipeline parameters from the checkpoint directory.

        This method deserializes the pipeline parameters stored in the checkpoint directory.

        Returns:
            Dict: A dictionary containing the pipeline parameters.

        Raises:
            FileNotFoundError: If the pipeline parameters file does not exist.
            IOError: If there is an error reading the file.
            pickle.PickleError: If deserialization fails.
        """
        pipeline_params_path = os.path.join(self.checkpoint_path, "pipeline_params")
        with open(pipeline_params_path, "rb") as file:
            pipeline_params = pickle.load(file)

        return pipeline_params