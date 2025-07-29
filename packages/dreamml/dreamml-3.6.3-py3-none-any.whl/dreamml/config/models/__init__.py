from typing import Literal

from dreamml.config._base_config import BaseConfig


class ModelConfig(BaseConfig):
    params: dict
    optimization_bounds: dict = {}


AvailableEstimtors = Literal[
    "xgboost",
    "lightgbm",
    "catboost",
    "pyboost",
    "boostaroota",
    "prophet",
    "nbeats_revin",
    "linear_reg",
    "log_reg",
    "lda",
    "ensembelda",
    "bertopic",
    "bert",
    "ae",
    "vae",
    "iforest",
]


class ModelsConfig(BaseConfig):
    n_estimators: int
    xgboost: ModelConfig
    lightgbm: ModelConfig
    catboost: ModelConfig
    pyboost: ModelConfig
    boostaroota: ModelConfig
    prophet: ModelConfig
    nbeats_revin: ModelConfig
    linear_reg: ModelConfig
    log_reg: ModelConfig
    lda: ModelConfig
    ensembelda: ModelConfig
    bertopic: ModelConfig
    bert: ModelConfig
    ae: ModelConfig
    vae: ModelConfig
    iforest: ModelConfig
