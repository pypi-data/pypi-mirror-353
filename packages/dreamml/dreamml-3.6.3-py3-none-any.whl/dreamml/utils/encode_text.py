import pandas as pd
import numpy as np
from dreamml.configs.config_storage import ConfigStorage
from dreamml.features.text.augmentation import TextAugmenter
from dreamml.logging import get_logger
from dreamml.features.text._base import TextFeaturesTransformer


_logger = get_logger(__name__)


def encode_text(config: ConfigStorage, dev_data, oot_data, indexes):
    """
    Encodes textual data using the specified text features transformer and applies augmentations if configured.

    This function initializes a `TextFeaturesTransformer` with the provided configuration, fits it on the development data,
    and transforms both development and out-of-time (OOT) datasets. If text augmentations are specified in the configuration
    and the vectorization algorithm does not include "bert", it applies text augmentations to the datasets.

    Args:
        config (ConfigStorage): The configuration storage containing text feature settings and augmentation parameters.
        dev_data (pd.DataFrame or pd.Series): The development dataset containing textual data to be transformed.
        oot_data (pd.DataFrame or pd.Series): The out-of-time dataset containing textual data to be transformed. Can be `None`.
        indexes (tuple of list of pd.Index): A tuple containing lists of pandas Index objects for data splitting.

    Returns:
        Tuple[
            pd.DataFrame or pd.Series,
            pd.DataFrame or pd.Series,
            tuple of list of pd.Index,
            list[str],
            TextFeaturesTransformer
        ]: A tuple containing the transformed development data, transformed out-of-time data,
        updated indexes, list of preprocessed text feature names, and the fitted `TextFeaturesTransformer`.

    Raises:
        ValueError: If the configuration parameters are invalid or missing required fields.
        RuntimeError: If the text transformation or augmentation processes fail.
    """
    # Text preprocessing
    transformer = TextFeaturesTransformer(
        text_features=config.text_features,
        text_preprocessing_params=config.pipeline.text_preprocessing_params,
        additional_stopwords=config.data.augmentation.additional_stopwords,
        verbose=True,
    )
    transformer.fit(dev_data)
    dev_data = transformer.transform(dev_data)

    if oot_data is not None:
        oot_data = transformer.transform(oot_data)

    text_features_preprocessed = transformer.text_features_preprocessed

    if len(config.text_augmentations) > 0 and "bert" not in config.vectorization_algos:
        dev_data, oot_data, indexes = apply_augmentations(
            config, dev_data, oot_data, indexes, text_features_preprocessed
        )

    return dev_data, oot_data, indexes, text_features_preprocessed, transformer


def apply_augmentations(
    config: ConfigStorage, dev_data, oot_data, indexes, text_features_preprocessed
):
    """
    Applies text augmentations to the development and out-of-time datasets based on the provided configuration.

    This function adds a service field to both development and out-of-time datasets for grouping purposes.
    It initializes a `TextAugmenter` with the specified augmentation settings, fits it on the training portion of the
    development data, and transforms the training data to include augmented samples. The augmented data is then
    concatenated back to the development dataset, and indexes are updated accordingly. Logging is performed to
    provide insights into the augmentation process.

    Args:
        config (ConfigStorage): The configuration storage containing augmentation settings and column mappings.
        dev_data (pd.DataFrame or pd.Series): The development dataset to be augmented.
        oot_data (pd.DataFrame or pd.Series): The out-of-time dataset to be augmented. Can be `None`.
        indexes (tuple of list of pd.Index): A tuple containing lists of pandas Index objects for data splitting.
        text_features_preprocessed (list[str]): List of preprocessed text feature column names.

    Returns:
        Tuple[pd.DataFrame or pd.Series, pd.DataFrame or pd.Series, tuple of list of pd.Index]]:
            A tuple containing the augmented development data, augmented out-of-time data, and updated indexes.

    Raises:
        ValueError: If the augmentation parameters are invalid or missing required fields.
        RuntimeError: If the augmentation process fails.
    """
    # Add service field for grouping
    dev_data["_group_nlp_aug_field"] = dev_data.index.tolist()
    if oot_data is not None:
        oot_data["_group_nlp_aug_field"] = oot_data.index.tolist()

    target_name = config.data.columns.target_name
    max_index = max([max(i.values) for i in indexes])
    indexes_list = list(indexes)

    aug_balancer = TextAugmenter(
        augmentations=config.data.augmentation.text_augmentations,
        text_column=text_features_preprocessed[0],
        target_column=target_name,
        start_index=max_index,
        aug_p=config.data.augmentation.aug_p,
        balance_classes=config.data.augmentation.aug_balance_classes,
    )
    train_data = dev_data.iloc[indexes[0]]
    aug_balancer.fit(train_data)
    augmented_data = aug_balancer.transform(train_data)

    # Save augmentations in the original text feature column
    augmented_data[config.data.columns.text_features[0]] = augmented_data[
        text_features_preprocessed[0]
    ]

    dev_data = pd.concat([dev_data, augmented_data], axis=0)
    indexes_list[0] = indexes_list[0].append(augmented_data.index)
    indexes = tuple(indexes_list)

    # Logging
    diff = dev_data.iloc[indexes[0]].shape[0] - train_data.shape[0]
    ratio = dev_data.iloc[indexes[0]].shape[0] / train_data.shape[0]
    unique_before, counts_before = np.unique(
        train_data[target_name].values, return_counts=True
    )
    unique_after, counts_after = np.unique(
        dev_data.iloc[indexes[0]][target_name].values, return_counts=True
    )

    _logger.debug(f"train shape before: {train_data.shape}")
    _logger.debug(f"train shape after: {dev_data.iloc[indexes[0]].shape}")
    _logger.debug(f"diff: {diff} | ratio: {round(ratio * 100, 2)}%")
    _logger.debug(f"train_data classes unique, counts: {unique_before, counts_before}")
    _logger.debug(f"train_data classes unique, counts: {unique_after, counts_after}")

    return dev_data, oot_data, indexes