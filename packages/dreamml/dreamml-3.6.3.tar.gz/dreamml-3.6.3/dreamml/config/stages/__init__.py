from typing import Literal, Union, Optional

from dreamml.config._base_config import BaseConfig


class OptimizationConfig(BaseConfig):
    optimizer: Literal["auto", "distributed", "local", "optuna", "bayesian"]
    optimizer_timeout: int
    n_iterations: Union[int, Literal["auto"]]
    n_iterations_used: Optional[int] = None


class StagesConfig(BaseConfig):
    optimization: OptimizationConfig
