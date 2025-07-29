import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from sklearn.model_selection import train_test_split
from typing import Union, Optional, List

from dreamml.modeling.metrics import BaseMetric
from dreamml.modeling.models.estimators import BoostingBaseModel


def select_subset_features(
    features_imp: pd.DataFrame,
    remaining_features: List[str] = [],
    threshold_value: Union[float, int] = None,
    top_k: Optional[int] = None,
) -> list:
    """
    Select a subset of features based on their importance scores.

    Features are selected either by applying a threshold to their importance scores
    or by selecting the top-k features with the highest importance. Additionally, 
    certain features can be retained regardless of their importance.

    Args:
        features_imp (pd.DataFrame): 
            A DataFrame containing feature importance scores. It should have at least 
            one column with "importance" in its name and another column named "feature".
        
        remaining_features (List[str], optional): 
            A list of feature names that must be retained in the dataset 
            regardless of their importance scores. Defaults to an empty list.
        
        threshold_value (Union[float, int], optional): 
            The threshold value for feature importance. Features with importance 
            scores above this value will be retained. Defaults to None.
        
        top_k (Optional[int], optional): 
            The number of top features to select based on importance scores. 
            If specified, selects the top-k features. Defaults to None.

    Returns:
        list: 
            A list of feature names that have been selected based on the specified criteria.

    Raises:
        ValueError: 
            If neither `threshold_value` nor `top_k` is provided, or if both are invalid.
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

    needed_columns = [
        col for col in remaining_features if col not in valid_features["feature"].tolist()
    ]
    valid_features = pd.concat(
        [valid_features, features_imp[features_imp["feature"].isin(needed_columns)]],
        axis=0,
    )
    valid_features = valid_features.drop_duplicates(subset="feature", keep="first")
    return valid_features["feature"].tolist()


def calculate_permutation_feature_importance(
    estimator: BoostingBaseModel,
    metric: BaseMetric,
    data: pd.DataFrame,
    target: pd.Series,
    fraction_sample: float = 0.8,
    maximize: bool = True,
) -> pd.DataFrame:
    """
    Calculate permutation feature importance based on the change in a specified metric.

    This function evaluates the importance of each feature by measuring the impact on the 
    model's performance metric when the feature's values are randomly shuffled. A decrease 
    in the metric indicates that the feature is important, while an increase suggests that 
    the feature may not be significant for the model.

    Args:
        estimator (BoostingBaseModel): 
            A trained model that follows the sklearn API. The model should have been fitted 
            using the `fit` method prior to calling this function.
        
        metric (BaseMetric): 
            A metric function used to evaluate the model's performance. It should take 
            the true values and the predicted values as input and return a numerical score.
        
        data (pd.DataFrame): 
            A DataFrame containing the feature matrix on which the feature importance 
            is to be evaluated.
        
        target (pd.Series): 
            A Series containing the target variable corresponding to the feature matrix.
        
        fraction_sample (float, optional): 
            The fraction of observations to sample from the data for calculating feature 
            importance. Must be between 0 and 1. Defaults to 0.8.
        
        maximize (bool, optional): 
            Indicates whether the metric is to be maximized (`True`) or minimized (`False`). 
            This affects how the importance scores are calculated. Defaults to True.

    Returns:
        pd.DataFrame: 
            A DataFrame containing the features and their corresponding permutation importance 
            scores, sorted in descending order of importance.

    Raises:
        TypeError: 
            If `data` is not a pandas DataFrame.
        
        ValueError: 
            If `fraction_sample` is not within the range [0, 1], or if the sampled target 
            does not contain all necessary classes for multiclass classification.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            f"data must be pandas.core.DataFrame, but data is {type(data)}"
        )

    if fraction_sample < 0 or fraction_sample > 1:
        raise ValueError(
            f"fraction_sample must be in range [0, 1], "
            f"but fraction_sample is {fraction_sample}"
        )
    elif 0 < fraction_sample < 1:
        # FIXME: Some classes in multiclass may be missing after split
        x, _, y, _ = train_test_split(
            data, target, train_size=fraction_sample, random_state=1
        )
        if isinstance(y, pd.DataFrame):
            for column_name in y:
                if y[column_name].nunique() != 2:
                    raise ValueError(
                        "During permutation, not all classes are present in the target sample."
                    )
    else:  # fraction_sample = 0 or fraction_sample = 1
        x = data
        y = target

    baseline_prediction = estimator.transform(x)
    baseline_score = metric(y, baseline_prediction)

    x_copy = x.copy(deep=True)
    feature_importance = np.zeros(x.shape[1])
    pbar = tqdm(x.columns, desc="Calculating permutation importance")
    for num, feature in enumerate(pbar):
        pbar.set_postfix(feature=feature)

        x[feature] = np.random.permutation(x[feature])
        score = metric(y, estimator.transform(x))

        feature_importance[num] = score
        x[feature] = x_copy[feature]

    if maximize:
        feature_importance = 1 - feature_importance / baseline_score
    else:
        feature_importance = feature_importance / baseline_score - 1

    df = pd.DataFrame(
        {"feature": x.columns, "permutation_importance": feature_importance}
    )
    df = df.sort_values(by="permutation_importance", ascending=False).reset_index(drop=True)

    return df