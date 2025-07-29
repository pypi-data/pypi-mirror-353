import pandas as pd
from typing import Union, Optional, List


def select_subset_features(
    features_imp: pd.DataFrame,
    remaining_features: List[str] = [],
    threshold_value: Union[float, int] = None,
    top_k: Optional[int] = None,
) -> list:
    """
    Select a subset of features based on their importance scores.

    Features are selected either by applying a threshold to their importance scores
    or by selecting the top-k features with the highest importance scores. Additionally,
    any features specified in `remaining_features` are guaranteed to be included in the
    final subset.

    Args:
        features_imp (pd.DataFrame): A DataFrame containing feature importance scores.
            Expected to have at least two columns, one of which includes "importance" in its name
            and another containing the feature names.
        remaining_features (List[str], optional): A list of feature names that must be retained
            in the final subset regardless of their importance scores. Defaults to an empty list.
        threshold_value (Union[float, int], optional): The threshold for feature importance.
            Features with importance scores above this value will be selected. Defaults to None.
        top_k (Optional[int], optional): The number of top features to select based on importance scores.
            If specified, the top-k features are selected. Defaults to None.

    Returns:
        list: A list of selected feature names.

    Raises:
        ValueError: If neither `threshold_value` nor `top_k` is provided.
    """
    col_name = [col for col in features_imp.columns if "importance" in col][0]
    if top_k:
        valid_features = features_imp.head(n=top_k)
    elif threshold_value:
        valid_features = features_imp[features_imp[col_name] > threshold_value]
    else:
        message = (
            "Incorrect params. Set the params: threshold_value / top_k."
            f" Current params: threshold_value = {threshold_value}, "
            f"top_k = {top_k}."
        )
        raise ValueError(message)

    needed_columns = [col for col in remaining_features if col not in valid_features["feature"].tolist()]
    valid_features = pd.concat(
        [valid_features, features_imp[features_imp["feature"].isin(needed_columns)]],
        axis=0,
    )
    valid_features = valid_features[~valid_features["feature"].duplicated(keep="first")]
    return valid_features["feature"].tolist()


def select_subset_features_reverse(
    features_imp: pd.DataFrame,
    remaining_features: List[str] = [],
    bot_k: Optional[int] = None,
) -> list:
    """
    Select a subset of features by excluding the bottom-k features based on their importance scores.

    This function removes the least important features, retaining all others. Additionally,
    any features specified in `remaining_features` are guaranteed to be included in the
    final subset.

    Args:
        features_imp (pd.DataFrame): A DataFrame containing feature importance scores.
            Expected to have at least two columns: one for feature names and one for importance scores.
        remaining_features (List[str], optional): A list of feature names that must be retained
            in the final subset regardless of their importance scores. Defaults to an empty list.
        bot_k (Optional[int], optional): The number of least important features to exclude.
            If specified, the bottom-k features are excluded from the selection. Defaults to None.

    Returns:
        list: A list of selected feature names.

    Raises:
        ValueError: If `bot_k` is not provided.
    """
    if bot_k:
        valid_features = features_imp.iloc[:-bot_k]
    else:
        message = "Incorrect params. Set the params: bot_k." f" Current bot_k = {bot_k}."
        raise ValueError(message)

    needed_columns = [
        col for col in remaining_features if col not in valid_features["feature-name"].tolist()
    ]
    valid_features = pd.concat(
        [
            valid_features,
            features_imp[features_imp["feature-name"].isin(needed_columns)],
        ],
        axis=0,
    )
    valid_features = valid_features[
        ~valid_features["feature-name"].duplicated(keep="first")
    ]
    return valid_features["feature-name"].tolist()