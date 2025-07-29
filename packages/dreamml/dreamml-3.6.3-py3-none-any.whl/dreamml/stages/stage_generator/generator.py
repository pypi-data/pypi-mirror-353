from copy import deepcopy
from pathlib import Path
from typing import Sequence, Dict, Optional, Type

from dreamml.data._dataset import DataSet
from dreamml.logging import get_logger
from dreamml.modeling.cv import BaseCrossValidator
from dreamml.stages.algo_info import AlgoInfo
from dreamml.stages.stage_generator.registry import stages_registry, estimators_registry
from dreamml.configs.config_storage import ConfigStorage
from dreamml.pipeline.fitter.utils import get_fitter

_logger = get_logger(__name__)


class StageGenerator:
    """
    Pipeline generator class responsible for constructing pipeline stages based on user configurations.

    This class fills stages with user-defined configurations, sequences actions for each model,
    retrieves available stages from a registry with standard parameters, and updates them with
    user-specific configurations.
    """

    def __init__(
        self,
        config: ConfigStorage,
        experiment_path: str,
        custom_cv: Optional[Type[BaseCrossValidator]] = None,
    ):
        """
        Initializes the StageGenerator with configuration, experiment path, and an optional custom cross-validator.

        Args:
            config (ConfigStorage): Configuration storage containing pipeline and model settings.
            experiment_path (str): Path to the experiment directory.
            custom_cv (Optional[Type[BaseCrossValidator]]): Custom cross-validator class, if any.

        """
        self.config = config
        self.experiment_path = experiment_path
        self.custom_cv = custom_cv

    def _get_stage_list(self, data_storage: DataSet) -> Sequence:
        """
        Creates a list of stage objects for the pipeline.

        This method generates stages by iterating over vectorization algorithms and models,
        checking for conflicts, and initializing each stage with the appropriate configuration
        and fitter.

        Args:
            data_storage (DataSet): The dataset containing features and other relevant data.

        Returns:
            Sequence: An iterable list of stage objects to be executed in the pipeline.
        """
        stages = []
        stage_idx = 0

        vectorization_algos = self.config.pipeline.vectorization.vectorization_algos
        model_list = self.config.pipeline.model_list
        stage_list = self.config.pipeline.stage_list

        if len(vectorization_algos) == 0:
            vectorization_algos = [None]

        current_vectorization_name = None
        for vectorization_name in vectorization_algos:
            for algo in model_list:
                stage_list_cp = stage_list.copy()

                if (
                    "vectorization" in stage_list_cp
                    and vectorization_name == current_vectorization_name
                ):
                    stage_list_cp.remove("vectorization")
                else:
                    current_vectorization_name = vectorization_name

                for stg in stage_list_cp:
                    algo = "bert" if vectorization_name == "bert" else algo
                    if self.check_conflict(algo, stg):
                        continue
                    estimator_class = estimators_registry.get(algo)
                    algo_info = AlgoInfo(
                        estimator_class,
                        deepcopy(getattr(self.config.models, algo).params),
                        [],
                        [],
                        (
                            self.config.data.augmentation.text_augmentations,
                            self.config.data.augmentation.aug_p,
                        ),
                        deepcopy(getattr(self.config.models, algo).optimization_bounds),
                    )
                    fitter = get_fitter(
                        self.config,
                        data_size=len(data_storage),
                        custom_cv=self.custom_cv,
                        vectorization_name=vectorization_name,
                        algo=algo,
                    )
                    algo_info.cat_features.extend(data_storage.cat_features)
                    algo_info.text_features.extend(
                        data_storage.text_features_preprocessed
                    )

                    stage = stages_registry.get(stg)(
                        algo_info=algo_info,
                        config=self.config,
                        fitter=fitter,
                        vectorization_name=vectorization_name,
                    )
                    stage.experiment_path = self.experiment_path

                    stage_identifier = f"{stage_idx}_{stage.name}"
                    stage.id = stage_identifier

                    log_path = (
                        Path(f"{self.experiment_path}")
                        / "logs"
                        / f"{stage_identifier}.log"
                    )
                    stage.init_logger(log_file=log_path)

                    stages.append(stage)
                    stage_idx += 1

        _logger.debug(
            f"Created stages list:\n"
            + "\n".join(
                [
                    f"{idx+1} {stage.name} {stage.algo_info.algo_class.model_name}"
                    for idx, stage in enumerate(stages)
                ]
            )
        )

        return stages

    def get_pipeline_params(self, data_storage: DataSet) -> Dict:
        """
        Generates pipeline parameters by creating a list of stages and indexing them.

        Args:
            data_storage (DataSet): The dataset containing features and other relevant data.

        Returns:
            Dict: A dictionary mapping stage IDs to their corresponding stage objects and indices.
        """
        stage_list = self._get_stage_list(data_storage)

        pipeline_params = dict()
        for i, stage in enumerate(stage_list):
            pipeline_params[stage.id] = {
                "stage": stage,
                "stage_idx": i,
            }

        return pipeline_params

    def check_conflict(self, algo, stage):
        """
        Checks for conflicts between the specified algorithm and stage.

        This method determines if a given algorithm is incompatible with a particular stage
        based on predefined rules and the current pipeline configuration.

        Args:
            algo (str): The name of the machine learning algorithm.
            stage (str): The name of the stage in the pipeline.

        Returns:
            bool: True if there is a conflict between the algorithm and stage, False otherwise.

        """
        if algo == "linear_reg" and stage in (
            "dtree",
            "corr",
            "permutation",
            "opt",
            "batch5",
            "batch5_down",
            "batch10",
            "batch10_down",
        ):
            return True
        elif algo == "log_reg" and stage in (
            "batch5",
            "batch5_down",
            "batch10",
            "batch10_down",
        ):
            return True
        elif algo == "bert" and stage not in ("vectorization", "opt"):
            return True
        elif self.config.pipeline.task == "multilabel" and stage in (
            "batch5",
            "batch5_down",
            "batch10",
            "batch10_down",
        ):
            if self.config.pipeline.task_specific.multilabel.target_with_nan_values:
                return True  # OneVsRestWrapper is used, which lacks TreeExplainer
            elif (
                not self.config.pipeline.task_specific.multilabel.target_with_nan_values
                and algo == "lightgbm"
            ):
                return True  # Only lightgbm uses OneVsRestWrapper, which lacks TreeExplainer
            else:
                return False
        elif algo in ["ae", "vae"] and stage not in ["base"]:
            return True
        elif algo in ["iforest"] and stage not in ["base", "opt"]:
            return True
        else:
            return False