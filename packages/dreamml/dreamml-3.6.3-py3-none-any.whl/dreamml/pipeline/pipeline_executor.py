import pandas as pd


def choose_pipeline(data: dict) -> str:
    """
    Determines the validation method based on the size of the training dataset.

    Args:
        data (dict): A dictionary containing datasets. 
                     The key is the dataset name, and the value is a tuple consisting of 
                     a feature matrix (pd.DataFrame) and a target variable vector (pd.Series).

    Returns:
        str: The validation method to use.
             - "cv" indicates a cross-validation-based pipeline.
             - "hold-out" indicates a pipeline based on splitting the training data into train/valid/test.
    """
    train_len = data.get("train", pd.DataFrame())[0].shape[0]
    valid_len = data.get("valid", pd.DataFrame())[0].shape[0]

    total_len = train_len + valid_len
    if total_len < 250000:
        return "cv"
    else:
        return "hold-out"