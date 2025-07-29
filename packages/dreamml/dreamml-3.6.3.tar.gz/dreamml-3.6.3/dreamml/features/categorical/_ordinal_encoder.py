import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder


class DmlOrdinalEncoder:
    """
    A custom ordinal encoder for encoding categorical features in a DataFrame.

    Attributes:
        encoder (OrdinalEncoder): The underlying sklearn OrdinalEncoder instance.
    """

    def __init__(self):
        """
        Initializes the DmlOrdinalEncoder with an OrdinalEncoder.

        The OrdinalEncoder is initialized to use integer data types for encoded values.
        """
        self.encoder = OrdinalEncoder(dtype=np.integer)

    def fit(self, data: pd.DataFrame, feature: str):
        """
        Fits the ordinal encoder to a specific feature in the DataFrame.

        Args:
            data (pd.DataFrame): The DataFrame containing the feature to encode.
            feature (str): The name of the feature/column to fit the encoder on.

        Returns:
            DmlOrdinalEncoder: The fitted encoder instance.

        Raises:
            ValueError: If the specified feature is not in the DataFrame.
        """
        if feature not in data.columns:
            raise ValueError(f"Feature '{feature}' not found in DataFrame columns.")
        self.encoder = OrdinalEncoder().fit(data[[feature]])
        return self

    def transform(self, data: pd.DataFrame, feature: str):
        """
        Transforms the specified feature in the DataFrame using the fitted encoder.

        Args:
            data (pd.DataFrame): The DataFrame containing the feature to transform.
            feature (str): The name of the feature/column to transform.

        Returns:
            pd.DataFrame: The DataFrame with the transformed feature.

        Raises:
            NotFittedError: If the encoder has not been fitted yet.
            ValueError: If the specified feature is not in the DataFrame.
        """
        if not hasattr(self.encoder, 'categories_'):
            raise NotFittedError("This DmlOrdinalEncoder instance is not fitted yet. Call 'fit' first.")
        if feature not in data.columns:
            raise ValueError(f"Feature '{feature}' not found in DataFrame columns.")
        data[feature] = self.encoder.transform(data[[feature]])
        data[feature] = data[feature].astype(np.integer)
        return data

    def inverse_transform(self, data: pd.DataFrame, feature: str):
        """
        Inversely transforms the encoded feature back to its original categorical values.

        Args:
            data (pd.DataFrame): The DataFrame containing the encoded feature.
            feature (str): The name of the feature/column to inverse transform.

        Returns:
            pd.DataFrame: The DataFrame with the feature inverse transformed.

        Raises:
            NotFittedError: If the encoder has not been fitted yet.
            ValueError: If the specified feature is not in the DataFrame.
        """
        if not hasattr(self.encoder, 'categories_'):
            raise NotFittedError("This DmlOrdinalEncoder instance is not fitted yet. Call 'fit' first.")
        if feature in data.columns:
            data[feature] = self.encoder.inverse_transform(data[[feature]])
        return data