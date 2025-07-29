import numpy as np
import pandas as pd


def filter_outliers(data: pd.DataFrame, target: pd.Series, config: dict):
    """
    Calculates and removes outliers from the data.

    Args:
        data (pd.DataFrame): Feature matrix.
        target (pd.Series): Target variable vector.
        config (dict): Configuration settings for the experiment.

    Returns:
        Tuple[pd.DataFrame, pd.Series]: A tuple where the first element is the transformed feature matrix and the second element is the transformed target variable vector.

    Raises:
        KeyError: If required percentile keys are missing in the config.
        TypeError: If the input types are not as expected.
    """
    min_perc = np.percentile(target, q=config.get("min_percentile", 1))
    max_perc = np.percentile(target, q=config.get("max_percentile", 99))
    filter_outliers_by_perc(data, target, min_perc, max_perc)


def filter_outliers_in_eval_set(eval_sets, config):
    """
    Removes outliers from evaluation sets. Outliers are removed from the 'train' and 'valid' sets. If a 'test' set is present, an additional 'test2' set without outliers is created, while the original 'test' set remains unchanged. Outliers are not removed from the 'OOT' set if it exists.

    Args:
        eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): A dictionary where the key is the name of the dataset and the value is a tuple containing the feature matrix and target vector.
        config (dict): Configuration settings for the experiment.

    Returns:
        Dict[str, Tuple[pd.DataFrame, pd.Series]]: The transformed dictionary with outliers removed from applicable datasets.

    Raises:
        KeyError: If required keys are missing in the eval_sets.
        TypeError: If the input types are not as expected.
    """
    eval_sets["train"] = filter_outliers(*eval_sets["train"], config=config)
    eval_sets["valid"] = filter_outliers(*eval_sets["valid"], config=config)

    if "test" in eval_sets:
        eval_sets["test2"] = filter_outliers(*eval_sets["test"], config=config)
    return eval_sets


def filter_outliers_by_perc(data, target, min_perc, max_perc):
    """
    Filters out outliers from the data based on specified percentile thresholds.

    Args:
        data (pd.DataFrame): Feature matrix.
        target (pd.Series): Target variable vector.
        min_perc (float): Minimum percentile threshold.
        max_perc (float): Maximum percentile threshold.

    Returns:
        Tuple[pd.DataFrame, pd.Series]: A tuple containing the filtered feature matrix and target vector.

    Raises:
        ValueError: If min_perc is greater than max_perc.
        TypeError: If the input types are not as expected.
    """
    target_mask = (target >= min_perc) & (target <= max_perc)

    data = data.loc[target_mask]
    # data = data.reset_index(drop=True)

    target = target.loc[target_mask]
    # target = target.reset_index(drop=True)

    return data, target


def filter_outliers_by_train_valid(eval_sets, conc_df, config):
    """
    Removes outliers from the evaluation sets. Outliers are removed from the 'train' and 'valid' sets. If a 'test' set is present, an additional 'test2' set without outliers is created, while the original 'test' set remains unchanged. Outliers are not removed from the 'OOT' set if it exists.

    Args:
        eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): A dictionary where the key is the name of the dataset and the value is a tuple containing the feature matrix and target vector.
        conc_df (Tuple[pd.DataFrame, pd.Series]): A tuple containing the concatenated feature matrix and target vector.
        config (dict): Configuration settings for the experiment, typically containing 'min_percentile' and 'max_percentile' keys from ConfigStorage.

    Returns:
        Dict[str, Tuple[pd.DataFrame, pd.Series]]: The transformed dictionary with outliers removed from applicable datasets.

    Raises:
        KeyError: If required keys are missing in the eval_sets or config.
        TypeError: If the input types are not as expected.
    """
    target = conc_df[1]
    min_perc, max_perc = get_min_max_perc(config, target)
    eval_sets["train"] = filter_outliers_by_perc(
        *eval_sets["train"], min_perc, max_perc
    )
    eval_sets["valid"] = filter_outliers_by_perc(
        *eval_sets["valid"], min_perc, max_perc
    )

    if "test" in eval_sets:
        target = eval_sets["test"][1]
        min_perc, max_perc = get_min_max_perc(config, target)

        eval_sets["test2"] = filter_outliers_by_perc(
            *eval_sets["test"], min_perc, max_perc
        )
    return eval_sets


def get_min_max_perc(config, target):
    """
    Computes the minimum and maximum percentile values for the target variable based on the configuration.

    Args:
        config (dict): Configuration settings containing 'min_percentile' and 'max_percentile' keys.
        target (pd.Series): Target variable vector.

    Returns:
        Tuple[float, float]: A tuple containing the minimum and maximum percentile values.

    Raises:
        KeyError: If 'min_percentile' or 'max_percentile' keys are missing in the config.
        TypeError: If the input types are not as expected.
    """
    min_perc = np.percentile(target, q=config.get("min_percentile"))
    max_perc = np.percentile(target, q=config.get("max_percentile"))
    return min_perc, max_perc