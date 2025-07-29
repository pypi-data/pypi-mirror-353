from typing import Optional

from dreamml.pipeline.fitter import FitterBase
from dreamml.stages.batch_selection.batch_selection_model_stage import (
    BatchSelectionModelStage,
)
from dreamml.configs.config_storage import ConfigStorage
from dreamml.stages.algo_info import AlgoInfo


class BatchSelectionModelStage10(BatchSelectionModelStage):
    """Batch TOP@ feature selection stage and model building for batch10.

    This stage handles the selection of top features and the construction of models
    specific to the "batch10" configuration.

    Attributes:
        name (str): The name identifier for this batch stage.
    """

    name = "batch10"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: Optional[FitterBase] = None,
        stage_params: str = "step_10",
        vectorization_name: str = None,
    ):
        """Initializes the BatchSelectionModelStage10.

        Args:
            algo_info (AlgoInfo): Information about the algorithm to be used.
            config (ConfigStorage): Configuration storage containing necessary settings.
            fitter (Optional[FitterBase], optional): An optional fitter instance. Defaults to None.
            stage_params (str, optional): Parameters specific to this stage. Defaults to "step_10".
            vectorization_name (str, optional): Name of the vectorization technique. Defaults to None.
        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
            stage_params=stage_params,
        )


class BatchSelectionModelStage5(BatchSelectionModelStage):
    """Batch TOP@ feature selection stage and model building for batch5.

    This stage manages the selection of top features and the development of models
    tailored to the "batch5" configuration.

    Attributes:
        name (str): The name identifier for this batch stage.
    """

    name = "batch5"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: Optional[FitterBase] = None,
        stage_params: str = "step_5",
        vectorization_name: str = None,
    ):
        """Initializes the BatchSelectionModelStage5.

        Args:
            algo_info (AlgoInfo): Information about the algorithm to be used.
            config (ConfigStorage): Configuration storage containing necessary settings.
            fitter (Optional[FitterBase], optional): An optional fitter instance. Defaults to None.
            stage_params (str, optional): Parameters specific to this stage. Defaults to "step_5".
            vectorization_name (str, optional): Name of the vectorization technique. Defaults to None.
        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
            stage_params=stage_params,
        )