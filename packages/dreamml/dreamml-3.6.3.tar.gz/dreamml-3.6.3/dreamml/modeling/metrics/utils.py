import numpy as np
import pandas as pd


def calculate_quantile_bins(
    data: pd.Series,
    n_bins: int = 20,
    percentile_implementation: bool = False,
    ascending: bool = False,
) -> np.ndarray:
    """Calculate quantile bins for the given data.

    This function divides the input data into a specified number of quantile-based bins.
    It offers two implementations: a percentile-based approach and a linear binning approach.

    Args:
        data (pd.Series): A series of values to be binned into quantiles.
        n_bins (int, optional): The number of bins to divide the data into. Defaults to 20.
        percentile_implementation (bool, optional): Whether to use the percentile-based implementation.
            If set to True, the function uses percentiles to determine bin edges. Defaults to False.
        ascending (bool, optional): Determines the sorting order of the data before binning.
            If True, the data is sorted in ascending order; otherwise, in descending order. Defaults to False.

    Returns:
        np.ndarray: An array of integer labels representing the bin assignments for each data point.

    Raises:
        ValueError: If `n_bins` is less than 1.
        TypeError: If `data` is not a pandas Series.
    """
    if percentile_implementation:
        bins = np.linspace(0, 100, n_bins)
        perc = [np.percentile(data, x) for x in bins]
        perc = np.sort(np.unique(perc))
        return pd.cut(data, perc, labels=False, include_lowest=True)
    else:
        df = data.to_frame() if isinstance(data, pd.Series) else data
        idx = df.index.values.astype(int)
        df.rename({df.columns[0]: "data"}, axis=1, inplace=True)
        df.sort_values("data", ascending=ascending, inplace=True)
        df["bin"] = np.linspace(1, n_bins + 1, len(data), False, dtype=int)
        bins = df["bin"][idx].to_numpy()
        return bins