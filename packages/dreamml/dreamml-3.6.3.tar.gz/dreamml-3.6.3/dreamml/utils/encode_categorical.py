from copy import deepcopy
import pandas as pd

from dreamml.features.categorical.categorical_encoder import (
    CategoricalFeaturesTransformer,
)
from dreamml.configs.config_storage import ConfigStorage


def encode_categorical(
    config: ConfigStorage,
    dev_data: pd.DataFrame,
    oot_data: pd.DataFrame,
    indexes: tuple,
):
    """
    Encodes categorical features in the provided datasets using a CategoricalFeaturesTransformer.

    This function initializes a transformer with the specified configuration, fits it on the development data,
    and then transforms both the development and out-of-time (OOT) datasets.

    Args:
        config (ConfigStorage): The configuration storage object containing data and pipeline configurations.
        dev_data (pd.DataFrame): The development dataset to be transformed.
        oot_data (pd.DataFrame): The out-of-time dataset to be transformed. Can be None.
        indexes (tuple): A tuple containing indices for train and validation splits.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, CategoricalFeaturesTransformer]:
            - Transformed development dataset.
            - Transformed out-of-time dataset (if oot_data is not None).
            - The fitted CategoricalFeaturesTransformer instance.

    Raises:
        ValueError: If the configuration is missing required categorical or text feature information.
        TypeError: If the input datasets are not pandas DataFrame instances.
        Exception: If the transformer fails to fit or transform the data.
    """
    train_idx, valid_idx = indexes[0], indexes[1]
    train_valid = dev_data.loc[train_idx]
    train_valid = train_valid.append(dev_data.loc[valid_idx])

    encoder_conf = {
        "categorical_features": deepcopy(config.data.columns.categorical_features),
        "text_features": deepcopy(config.data.columns.text_features),
        "target_name": config.data.columns.target_name,
        "time_column": config.data.columns.time_column,
        "task": config.pipeline.task,
    }

    transformer = CategoricalFeaturesTransformer(encoder_conf)
    _ = transformer.fit(dev_data)

    dev_data = transformer.transform(dev_data)
    if oot_data is not None:
        oot_data = transformer.transform(oot_data)

    return dev_data, oot_data, transformer