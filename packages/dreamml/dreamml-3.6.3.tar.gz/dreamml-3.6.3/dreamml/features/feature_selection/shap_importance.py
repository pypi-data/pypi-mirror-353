import shap
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split

from dreamml.logging import get_logger
from dreamml.modeling.models.estimators import PyBoostModel

_logger = get_logger(__name__)


def _calculate_shap_values(estimator, data: pd.DataFrame, **params) -> list:
    """
    Calculate SHAP values for a given model instance.

    This function computes the SHAP values for the provided estimator and dataset.
    It handles different types of explainers based on the estimator's class and manages
    exceptions that may occur during the computation.

    Args:
        estimator: An instance of a model that supports the sklearn API.
            The model is expected to be trained, i.e., the fit method must have been called.
        data (pd.DataFrame): The feature matrix used to calculate SHAP values.
        **params: Additional parameters for calculating feature importance.

    Returns:
        list: A list of SHAP values. If the SHAP values are not a list, the function
            returns the SHAP values directly.

    Raises:
        TypeError: If the data provided is not a pandas DataFrame.
        ValueError: If there is an issue with the parameters or data.
        Exception: For any other unexpected errors during SHAP value computation.
    """
    if isinstance(estimator, PyBoostModel):
        explainer = shap.PermutationExplainer(
            estimator, masker=shap.maskers._tabular.Tabular(data)
        )
    else:
        explainer = shap.TreeExplainer(estimator.estimator)

    # Booster parameters are not saved in pickle, so they are empty upon loading
    if estimator.model_name == "LightGBM":
        estimator.estimator._Booster.params = estimator.params

    try:
        if isinstance(explainer, shap.PermutationExplainer):
            shap_values = explainer.shap_values(
                X=data[estimator.used_features], npermutations=5, **params
            )
        else:
            shap_values = explainer.shap_values(
                X=data[estimator.used_features], **params
            )
    except ValueError as ve:
        _logger.exception(f"ValueError encountered: {ve}. Converting data to DMatrix.")
        data = xgb.DMatrix(data[estimator.used_features])
        shap_values = explainer.shap_values(X=data)
    except Exception as e:
        _logger.exception(
            f"Unexpected error while getting SHAP values: {e}. "
            "Attempting to set 'check_additivity' parameter to `False`."
        )
        if isinstance(explainer, shap.PermutationExplainer):
            shap_values = explainer.shap_values(
                X=data[estimator.used_features], npermutations=5, **params
            )
        else:
            shap_values = explainer.shap_values(
                X=data[estimator.used_features], check_additivity=False, **params
            )

    if isinstance(shap_values, list):
        return shap_values[0]
    return shap_values


def calculate_shap_feature_importance(
    estimator, data: pd.DataFrame, fraction_sample: float = 1.0, random_seed: int = 27
) -> pd.DataFrame:
    """
    Calculate and sort feature importance based on SHAP values.

    This function computes the SHAP values for a subset of the data (defined by
    fraction_sample) and returns a DataFrame containing the features sorted by their
    importance.

    Args:
        estimator: An instance of a model that supports the sklearn API.
            The model is expected to be trained, i.e., the fit method must have been called.
        data (pd.DataFrame): The feature matrix used to calculate SHAP values.
        fraction_sample (float, optional): The fraction of observations from the data
            to use for evaluating feature importance. Defaults to 1.0.
        random_seed (int): The seed for random number generation to ensure reproducibility.

    Returns:
        pd.DataFrame: A DataFrame containing features and their corresponding
            importance scores, sorted in descending order of importance.

    Raises:
        TypeError: If the provided data is not a pandas DataFrame.
        ValueError: If fraction_sample is not within the range [0, 1].
    """
    np.random.seed(random_seed)
    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            f"data must be pandas.core.DataFrame, "
            f"but data is {type(data)}"
        )

    if fraction_sample < 0 or fraction_sample > 1:
        raise ValueError(
            f"fraction_sample must be in range [0, 1], "
            f"but fraction_sample is {fraction_sample}"
        )
    elif 0 < fraction_sample < 1:
        x, _ = train_test_split(
            data, train_size=fraction_sample, random_state=random_seed
        )
    else:  # fraction_sample = 0 or fraction_sample = 1
        x = data

    shap_values = _calculate_shap_values(estimator=estimator, data=x)
    importance = pd.DataFrame(
        {
            "feature": estimator.used_features,
            "importance": np.abs(shap_values.mean(axis=0)),
        }
    )
    importance = importance.sort_values(by="importance", ascending=False)
    importance = importance.reset_index(drop=True)

    return importance