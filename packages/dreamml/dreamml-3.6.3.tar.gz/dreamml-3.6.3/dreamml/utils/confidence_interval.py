from collections.abc import Callable

import numpy as np
import pandas as pd
from scipy import stats
from typing import Union, Optional

from dreamml.modeling.metrics import BaseMetric


def create_bootstrap_index(
    df: pd.DataFrame,
    bootstrap_samples: int = 200,
    random_seed: Optional[int] = None,
    task: str = "binary",
    target: Optional[Union[pd.Series, np.array]] = None,
) -> np.array:
    """
    Creates a matrix of indices for objects included in the bootstrap samples.

    Args:
        df (pd.DataFrame): Feature matrix used to create bootstrap samples.
        bootstrap_samples (int, optional): Number of bootstrap samples to generate. Defaults to 200.
        random_seed (Optional[int], optional): Seed for the random number generator. Defaults to None.
        task (str, optional): Type of task. Defaults to "binary".
        target (Optional[Union[pd.Series, np.array]], optional): Target variable. Required if task is "multilabel". Defaults to None.

    Returns:
        np.array: A matrix containing the indices of bootstrap samples.

    Raises:
        ValueError: If task is "multilabel" and target is not provided.
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    if task == "multilabel":
        if target is None:
            raise ValueError(
                "Target is required for bootstrap sampling as all classes have to be presented in samples."
            )
        bootstrap_index = np.empty((bootstrap_samples, 0), dtype=int)
        target = target.reset_index(drop=True)

        # Ensure that each class is represented in the samples
        for target_class, cnt in target.value_counts().to_frame().iterrows():
            cnt = int(cnt)
            bootstrap_index = np.append(
                bootstrap_index,
                np.random.choice(
                    target[target == target_class].index, size=(bootstrap_samples, cnt)
                ),
                axis=-1,
            )
        return bootstrap_index
    else:
        bootstrap_index = np.random.randint(
            0, df.shape[0], size=(bootstrap_samples, df.shape[0])
        )
        return bootstrap_index


def create_bootstrap_scores(
    x: pd.DataFrame,
    y: pd.Series,
    y_pred: pd.Series,
    metric: Callable,
    bootstrap_samples: int = 200,
    random_seed: int = 27,
    task: Optional[str] = None,
) -> np.array:
    """
    Computes the quality metric for each bootstrap sample.

    Args:
        x (pd.DataFrame): Feature matrix used to create bootstrap samples.
        y (pd.Series): Target variable.
        y_pred (pd.Series): Model predictions.
        metric (Callable): Function to compute the quality metric.
        bootstrap_samples (int, optional): Number of bootstrap samples to generate. Defaults to 200.
        random_seed (int, optional): Seed for the random number generator. Defaults to 27.
        task (Optional[str], optional): Type of task. Defaults to None.

    Returns:
        np.array: An array containing bootstrap metric scores.
    """
    x = x.reset_index(drop=True)
    y = y.reset_index(drop=True) if isinstance(y, pd.DataFrame) else y

    if task not in (
        "multiclass",
        "multilabel",
    ):  # In this case, predictions are np.array([n_samples, n_classes])
        y_pred = pd.Series(y_pred)

    y_pred = (
        y_pred.reset_index(drop=True) if isinstance(y_pred, pd.DataFrame) else y_pred
    )

    bootstrap_scores = []
    bootstrap_index = create_bootstrap_index(
        x, bootstrap_samples, random_seed, task=task, target=y
    )

    y_pred = y_pred.values if isinstance(y_pred, (pd.Series, pd.DataFrame)) else y_pred
    y = y.values if isinstance(y, (pd.Series, pd.DataFrame)) else y

    for sample_idx in bootstrap_index:
        y_true_bootstrap, y_pred_bootstrap = y[sample_idx], y_pred[sample_idx]
        try:
            bootstrap_scores.append(metric(y_true_bootstrap, y_pred_bootstrap))
        except Exception:
            continue

    return np.array(bootstrap_scores)


def calculate_conf_interval(x: np.array, alpha: float = 0.05):
    """
    Calculates the confidence interval for the mean of the provided sample.

    Args:
        x (np.array): Sample data used to compute the confidence interval.
        alpha (float, optional): Significance level for the confidence interval. Defaults to 0.05.

    Returns:
        Tuple[float, float]: The lower and upper bounds of the confidence interval.
    """
    x_mean = np.mean(x)
    q_value = stats.t.ppf(1 - alpha / 2, x.shape[0])

    std_error = q_value * np.sqrt(x_mean) / np.sqrt(x.shape[0])

    return x_mean - std_error, x_mean + std_error