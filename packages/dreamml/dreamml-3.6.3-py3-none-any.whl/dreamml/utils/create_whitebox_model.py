from copy import deepcopy
from typing import Tuple, Dict, Optional

import pandas as pd

from dreamml.modeling.models.estimators._lama_v_1_3 import WBAutoML
from dreamml.configs.config_storage import ConfigStorage

wb_params = {
    "interpreted_model": True,
    "monotonic": False,
    "max_bin_count": 5,
    "select_type": None,
    "pearson_th": 0.9,
    "metric_th": None,
    "vif_th": 5.0,
    "imp_th": 0.001,
    "th_const": 0.005,
    "force_single_split": False,
    "th_nan": 0.005,
    "th_cat": 0.005,
    "th_mark": 0.005,
    "woe_diff_th": 0.01,
    "min_bin_size": 0.01,
    "min_bin_mults": (2, 4),
    "min_gains_to_split": (0.0, 0.5, 1.0),
    "metric_tol": 1e-4,
    "cat_alpha": 1,
    "cat_merge_to": "to_woe_0",
    "nan_merge_to": "to_woe_0",
    "mark_merge_to": "to_woe_0",
    "oof_woe": False,
    "n_folds": 6,
    "n_jobs": 10,
    "l1_grid_size": 20,
    "l1_exp_scale": 4,
    "imp_type": "feature_imp",
    "regularized_refit": False,
    "p_val": 0.05,
    "debug": False,
    "verbose": 2,
}


def add_whitebox_model(
    data: dict,
    config: ConfigStorage,
    used_features: list or None = None,
    hyper_params: dict or None = None,
    embeddngs: Optional[Dict[str, Dict[str, pd.DataFrame]]] = None,
) -> dict:
    """
    Trains and adds a WhiteBox AutoML model to the models dictionary.

    Args:
        data (dict):
            A dictionary containing data. The key is the dataset name, and the value is a tuple with
            a feature matrix (pd.DataFrame) and a target variable vector (pd.Series).
        config (ConfigStorage):
            A configuration object with experiment parameters.
        used_features (list or None, optional):
            A list of features to be used for training. Defaults to None.
        hyper_params (dict or None, optional):
            A dictionary of model hyperparameters. Defaults to None.
        embeddngs (Optional[Dict[str, Dict[str, pd.DataFrame]]], optional):
            A dictionary of embeddings. Defaults to None.

    Returns:
        dict:
            A dictionary containing the trained models.

    Raises:
        KeyError:
            If required keys are missing in the data or config.
        Exception:
            If an error occurs during model training.
    """
    if config.pipeline.alt_mode.use_whitebox_automl:
        wb_models = {}

        if not used_features:
            used_features = data["train"][0].columns.to_list()
        if not hyper_params:
            hyper_params = wb_params

        if "eval_metric" not in hyper_params:
            hyper_params["eval_metric"] = config.pipeline.eval_metric

        if "objective" not in hyper_params:
            hyper_params["objective"] = config.pipeline.loss_function

        vectorization_algos = config.get("vectorization_algos", [])
        if len(vectorization_algos) > 0 and embeddngs is not None:
            for vectorization_name in vectorization_algos:
                embeddings_df = embeddngs[vectorization_name]
                data_cp = data.copy()
                used_features_cp = deepcopy(used_features)
                for sample_name, sample in data_cp.items():
                    X_sample = pd.concat(
                        [sample[0], embeddings_df[sample_name]],
                        axis=1,
                        ignore_index=False,
                    )
                    data_cp[sample_name] = (X_sample, sample[1])
                    used_features_cp = [
                        col
                        for col in data_cp["train"][0].columns
                        if col not in config.data.columns.text_features
                    ]
                wb_model = _get_wb_model(
                    data_cp,
                    config,
                    hyper_params,
                    used_features_cp,
                    model_name=f"WBAutoML.{vectorization_name}",
                )
                wb_models.update(wb_model)
        else:
            wb_model = _get_wb_model(data, config, hyper_params, used_features)
            wb_models.update(wb_model)
        return wb_models

    return {}


def _get_wb_model(
    data: dict,
    config: ConfigStorage,
    hyper_params: dict,
    used_features: list,
    model_name: str = "WBAutoML",
) -> dict:
    """
    Creates and fits a WhiteBox AutoML model.

    Args:
        data (dict):
            A dictionary containing data. The key is the dataset name, and the value is a tuple with
            a feature matrix (pd.DataFrame) and a target variable vector (pd.Series).
        config (ConfigStorage):
            A configuration object with experiment parameters.
        hyper_params (dict):
            A dictionary of model hyperparameters.
        used_features (list):
            A list of features to be used for training.
        model_name (str, optional):
            The name of the model. Defaults to "WBAutoML".

    Returns:
        dict:
            A dictionary containing the trained WhiteBox AutoML model with the specified model name.

    Raises:
        Exception:
            If an error occurs during model initialization or training.
    """
    wb_model = WBAutoML(
        estimator_params=hyper_params,
        task=config.pipeline.task,
        used_features=used_features,
        metric_name=config.pipeline.eval_metric,
        metric_params=config.pipeline.metric_params,
    )
    wb_model.fit(*data["train"], *data["valid"])
    return {model_name: wb_model}