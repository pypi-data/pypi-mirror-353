from typing import Optional

from dreamml.pipeline.fitter import FitterBase
from dreamml.stages.batch_selection.batch_selection_reverse import (
    BatchSelectionReverseModelStage,
)
from dreamml.configs.config_storage import ConfigStorage
from dreamml.stages.algo_info import AlgoInfo


class BatchSelectionReverseModelStage10(BatchSelectionReverseModelStage):
    """
    Batch stage for TOP@ feature selection and model building at step 10 down.

    Attributes:
        name (str): The name of the stage.
    """

    name = "batch10_down"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: Optional[FitterBase] = None,
        vectorization_name: str = None,
        stage_params: str = "step_10_down",
    ):
        """
        Initializes the BatchSelectionReverseModelStage10.

        Args:
            algo_info (AlgoInfo): Information about the algorithm.
            config (ConfigStorage): Configuration storage.
            fitter (Optional[FitterBase], optional): The fitter object. Defaults to None.
            vectorization_name (str, optional): Name of the vectorization. Defaults to None.
            stage_params (str, optional): Parameters for the stage. Defaults to "step_10_down".

        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
            stage_params=stage_params,
        )


class BatchSelectionReverseModelStage5(BatchSelectionReverseModelStage):
    """
    Batch stage for TOP@ feature selection and model building at step 5 down.

    Attributes:
        name (str): The name of the stage.
    """

    name = "batch5_down"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: Optional[FitterBase] = None,
        vectorization_name: str = None,
        stage_params: str = "step_5_down",
    ):
        """
        Initializes the BatchSelectionReverseModelStage5.

        Args:
            algo_info (AlgoInfo): Information about the algorithm.
            config (ConfigStorage): Configuration storage.
            fitter (Optional[FitterBase], optional): The fitter object. Defaults to None.
            vectorization_name (str, optional): Name of the vectorization. Defaults to None.
            stage_params (str, optional): Parameters for the stage. Defaults to "step_5_down".

        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
            stage_params=stage_params,
        )


class BatchSelectionReverseModelStage1(BatchSelectionReverseModelStage):
    """
    Batch stage for TOP@ feature selection and model building at step 1 down.

    Attributes:
        name (str): The name of the stage.
    """

    name = "batch1_down"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        experiment_path: str,
        fitter: Optional[FitterBase] = None,
        vectorization_name: str = None,
        stage_params: str = "step_1_down",
    ):
        """
        Initializes the BatchSelectionReverseModelStage1.

        Args:
            algo_info (AlgoInfo): Information about the algorithm.
            config (ConfigStorage): Configuration storage.
            experiment_path (str): Path to the experiment directory.
            fitter (Optional[FitterBase], optional): The fitter object. Defaults to None.
            vectorization_name (str, optional): Name of the vectorization. Defaults to None.
            stage_params (str, optional): Parameters for the stage. Defaults to "step_1_down".

        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
            stage_params=stage_params,
        )