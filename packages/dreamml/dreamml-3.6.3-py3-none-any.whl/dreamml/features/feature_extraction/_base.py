def drop_features(config, eval_sets):
    """
    Removes specified features from each dataset in eval_sets.

    This function removes features listed under the "drop_features" and "target_name"
    keys in the configuration dictionary from each dataset in eval_sets. Additionally,
    it handles never used features and time columns based on the configuration.

    Args:
        config (dict): Configuration dictionary containing keys such as "drop_features",
            "target_name", "multitarget", "time_column", "oot_data_path", and
            "never_used_features".
        eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
            Dictionary of datasets for which features need to be dropped. The key is the
            dataset name (e.g., "train", "valid") and the value is a tuple containing
            the feature matrix (data) and the target vector (target).

    Returns:
        Tuple[Dict[str, Tuple[pandas.DataFrame, pandas.Series]], pandas.DataFrame]:
            A tuple containing:
                - The transformed eval_sets with specified features removed.
                - A pandas DataFrame with features that were marked as "drop_features".

    Raises:
        KeyError: If expected keys are missing in the config dictionary.
        TypeError: If eval_sets is not in the expected format.
    """
    
    dropped_features = set(
        config.get("drop_features") if config.get("drop_features") is not None else []
    )

    target_names = config.get("target_name")

    if isinstance(target_names, list):
        garbage_features = set(target_names) if target_names else set()
    else:
        garbage_features = [target_names] if target_names else []
        garbage_features = set(garbage_features)
        garbage_features |= set(config.get("multitarget", set()))

    if config.get("time_column") and not config.get("oot_data_path"):
        dropped_features.add(config.get("time_column"))
    never_used_features = config.get("never_used_features", [])

    dropped_data = {}
    for sample in eval_sets:
        data, target = eval_sets[sample]
        dropped_data[sample] = data[dropped_features]
        data = data.drop(garbage_features | dropped_features, axis=1)

        extra_features_to_drop = list(set(data.columns) & set(never_used_features))

        if extra_features_to_drop:
            dropped_data[sample] = dropped_data[sample].join(
                data[extra_features_to_drop]
            )
            data = data.drop(extra_features_to_drop, axis=1)

        eval_sets[sample] = (data, target)

    return eval_sets, dropped_data