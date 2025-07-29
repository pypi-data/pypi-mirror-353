import pandas as pd
from typing import List, Optional
from dreamml.data._dataset import DataSet


def optimizer_selector(
    data_storage: DataSet,
    used_features: List = None,
    vectorization_name: Optional[str] = None,
) -> str:
    """
    Selects the optimization method based on the size of the training and validation datasets.

    Args:
        data_storage (DataSet): An instance of the data storage class.
        used_features (List, optional): A list of features to be used. Defaults to None.
        vectorization_name (Optional[str], optional): The name of the vectorization algorithm. Defaults to None.

    Returns:
        str: The chosen optimization method.
             - "local": Uses a pipeline based on splitting the training set into train/valid/test.
             - "distributed": Uses a pipeline based on cross-validation.

    Raises:
        KeyError: If the expected keys are not found in the dataset.
        AttributeError: If the dataset does not have the required attributes or methods.
        TypeError: If the provided arguments are of incorrect types.
    """
    data = data_storage.get_eval_set(
        used_features, vectorization_name=vectorization_name
    )
    train_size = data.get("train", pd.DataFrame())[0].memory_usage(deep=True).sum()
    train_size = round(train_size / 1024 / 1024, 2)
    valid_size = data.get("valid", pd.DataFrame())[0].memory_usage(deep=True).sum()
    valid_size = round(valid_size / 1024 / 1024, 2)

    total_size = train_size + valid_size
    if total_size > 1024:
        return "local"
    else:
        return "distributed"