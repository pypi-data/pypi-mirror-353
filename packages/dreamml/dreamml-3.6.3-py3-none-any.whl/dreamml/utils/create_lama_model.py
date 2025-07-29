from copy import deepcopy
from typing import Optional, Dict

import pandas as pd

from dreamml.configs.config_storage import ConfigStorage
from dreamml.logging import get_logger
from dreamml.modeling.models.estimators._lightautoml import LAMA

_logger = get_logger(__name__)


def add_lama_model(
    data: dict,
    config: ConfigStorage,
    used_features: list or None = None,
    hyper_params: dict or None = None,
    embeddngs: Optional[Dict[str, Dict[str, pd.DataFrame]]] = None,
    **params,
) -> dict:
    """
    Trains and adds a WhiteBox AutoML (LAMA) model to the models dictionary.

    This function evaluates whether to use LAMA based on the configuration.
    If enabled, it prepares the features, updates hyperparameters, and integrates
    embedding algorithms if provided. The trained LAMA model is then added to the
    models dictionary.

    Args:
        data (dict): 
            A dictionary containing datasets. The key is the dataset name, and the 
            value is a tuple with a features matrix (pd.DataFrame) and a target vector (pd.Series).
        config (ConfigStorage): 
            Configuration object containing experiment parameters.
        used_features (list, optional): 
            List of feature names to be used. Defaults to None, which uses all features from the training set.
        hyper_params (dict, optional): 
            Dictionary of hyperparameters for the LAMA model. Defaults to None, which initializes with default settings.
        embeddngs (Optional[Dict[str, Dict[str, pd.DataFrame]]], optional): 
            Dictionary of embeddings. The first key is the vectorization algorithm name, and the second key 
            corresponds to the dataset name with its associated pd.DataFrame. Defaults to None.
        **params: 
            Additional keyword arguments to update hyperparameters.

    Returns:
        dict: 
            A dictionary containing the trained models. The key is the model name, and the value is the trained LAMA model.

    Raises:
        AssertionError: 
            If the pipeline finishes without generating any models, a warning is logged. 
            Other AssertionErrors are propagated.
    """
    models = {}
    if config.pipeline.alt_mode.use_lama:
        try:
            if not used_features:
                used_features = data["train"][0].columns.to_list()
            if not hyper_params:
                hyper_params = {
                    "task": config.pipeline.task,
                    "loss_function": config.pipeline.loss_function,
                    # for compatibility with other models, actually not used
                }

            if "eval_metric" not in hyper_params:
                hyper_params["eval_metric"] = config.pipeline.eval_metric

            if "objective" not in hyper_params:
                hyper_params["objective"] = config.pipeline.loss_function

            hyper_params.update(params)

            vectorization_algos = config.pipeline.vectorization.vectorization_algos
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
                    models = _get_lama_model_dict(
                        models,
                        data_cp,
                        config,
                        hyper_params,
                        used_features_cp,
                        model_name=f"LAMA.{vectorization_name}",
                    )
            else:
                models = _get_lama_model_dict(
                    models, data, config, hyper_params, used_features
                )

        except AssertionError as e:
            if "Pipeline finished with 0 models" in str(e):
                _logger.warning("LAMA was unable to generate any models.")
            else:
                raise

    return models


def _get_lama_model_dict(
    models: dict,
    data: dict,
    config: ConfigStorage,
    hyper_params: dict,
    used_features: list,
    model_name: str = "LAMA",
) -> dict:
    """
    Trains a LAMA model and adds it to the provided models dictionary.

    This helper function initializes a LAMA model with the given parameters,
    fits it using the training and validation data, and updates the models
    dictionary with the trained model.

    Args:
        models (dict): 
            Dictionary to store trained models. The key is the model name, and the value is the model instance.
        data (dict): 
            A dictionary containing datasets. The key is the dataset name, and the value is a tuple 
            with a features matrix (pd.DataFrame) and a target vector (pd.Series).
        config (ConfigStorage): 
            Configuration object containing experiment parameters.
        hyper_params (dict): 
            Dictionary of hyperparameters for the LAMA model.
        used_features (list): 
            List of feature names to be used for training the model.
        model_name (str, optional): 
            Name to assign to the trained model in the models dictionary. Defaults to "LAMA".

    Returns:
        dict: 
            Updated models dictionary with the trained LAMA model added.
    """
    lama_model = LAMA(
        estimator_params=hyper_params,
        task=config.pipeline.task,
        used_features=used_features,
        metric_name=config.pipeline.eval_metric,
        metric_params=config.pipeline.metric_params,
        lama_time=config.pipeline.alt_mode.lama_time,
    )
    lama_model.fit(*data["train"], *data["valid"])
    models[model_name] = lama_model
    return models