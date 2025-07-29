import numpy as np
import pandas as pd


def find_categorical_features(data: pd.DataFrame, config: dict) -> np.array:
    """
    Identifies categorical features within a dataset based on data types and configuration settings.

    This function examines the provided DataFrame to find columns with data types 'object' or 'category'.
    It excludes any columns specified in the configuration under 'drop_features'. Additionally, it ensures
    that the target column is included or excluded from categorical features based on the task type.

    Args:
        data (pd.DataFrame): The feature matrix containing the dataset.
        config (dict): A configuration dictionary that includes settings such as task type,
                       target column name, and lists of predefined categorical and text features.

    Returns:
        np.array: A numpy array containing the unique list of identified categorical feature names.

    Raises:
        ValueError: If the target column is included in categorical features for non-multiclass tasks,
                    indicating that the target must be of type int or float.
    """
    task = config["task"]
    target_name = config["target_name"]

    categorical_features = config.get("categorical_features", [])
    text_cols = config.get("text_features", [])

    object_cols = data.dtypes[data.dtypes == "object"].index.tolist()
    category_cols = data.dtypes[data.dtypes == "category"].index.tolist()

    for feature in object_cols + category_cols:
        if feature not in categorical_features + text_cols:
            categorical_features.append(feature)

    if task == "multiclass" and target_name not in categorical_features:
        categorical_features.append(target_name)

    elif task != "multiclass" and target_name in categorical_features:
        msg = f"For a {task} task, the target must be in int or float format, but got: {data[target_name].dtype}."
        raise ValueError(msg)

    return np.unique(categorical_features).tolist()