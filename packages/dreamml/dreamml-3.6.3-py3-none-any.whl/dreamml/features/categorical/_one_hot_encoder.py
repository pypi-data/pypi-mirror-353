import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
import logging


class DmlOneHotEncoder:
    """
    A custom one-hot encoder that integrates with pandas DataFrames for encoding and decoding categorical features.

    Attributes:
        encoder (OneHotEncoder): The underlying sklearn OneHotEncoder used for encoding features.
    """

    def __init__(self):
        """
        Initializes the DmlOneHotEncoder with a OneHotEncoder instance.

        The OneHotEncoder is configured to return dense arrays with integer data types.
        """
        self.encoder = OneHotEncoder(sparse=False, dtype=np.integer)

    def fit(self, data: pd.DataFrame, feature: str):
        """
        Fits the OneHotEncoder to the specified feature in the provided DataFrame.

        Args:
            data (pd.DataFrame): The input DataFrame containing the feature to encode.
            feature (str): The name of the column to be one-hot encoded.

        Returns:
            DmlOneHotEncoder: Returns the instance itself to allow method chaining.

        Raises:
            ValueError: If the specified feature is not found in the DataFrame.
        """
        if feature not in data.columns:
            raise ValueError(f"Feature '{feature}' not found in the DataFrame.")
        self.encoder = self.encoder.fit(data[[feature]])
        return self

    def transform(self, data: pd.DataFrame, feature: str):
        """
        Transforms the specified feature in the DataFrame using the fitted OneHotEncoder.

        The original feature column is replaced with its one-hot encoded columns.

        Args:
            data (pd.DataFrame): The input DataFrame containing the feature to transform.
            feature (str): The name of the column to be one-hot encoded.

        Returns:
            pd.DataFrame: The transformed DataFrame with one-hot encoded columns.

        Raises:
            ValueError: If the encoder has not been fitted before calling transform.
            ValueError: If the specified feature is not found in the DataFrame.
        """
        if not hasattr(self.encoder, 'categories_'):
            raise ValueError("The encoder has not been fitted yet. Please call 'fit' before 'transform'.")
        if feature not in data.columns:
            raise ValueError(f"Feature '{feature}' not found in the DataFrame.")

        x_transformed = pd.DataFrame(
            data=self.encoder.transform(data[[feature]]),
            columns=self.encoder.get_feature_names_out(),
            index=data.index
        )
        data = pd.concat([data, x_transformed], axis=1)
        data.drop(columns=[feature], axis=1, inplace=True)

        return data

    def inverse_transform(self, data: pd.DataFrame, feature: str):
        """
        Reverts the one-hot encoded columns back to the original categorical feature.

        If not all one-hot encoded columns are present in the DataFrame, logs an informational message.

        Args:
            data (pd.DataFrame): The input DataFrame containing one-hot encoded columns.
            feature (str): The name of the original categorical feature to restore.

        Returns:
            pd.DataFrame: The DataFrame with the original categorical feature restored.

        Raises:
            ValueError: If the encoder has not been fitted before calling inverse_transform.
        """
        if not hasattr(self.encoder, 'categories_'):
            raise ValueError("The encoder has not been fitted yet. Please call 'fit' before 'inverse_transform'.")

        one_hot_columns = [
            column
            for column in self.encoder.get_feature_names_out()
            if column in data.columns
        ]
        if len(one_hot_columns) == len(self.encoder.get_feature_names_out()):
            data[feature] = self.encoder.inverse_transform(data[one_hot_columns])
            data.drop(columns=one_hot_columns, axis=1, inplace=True)
        else:
            missing_columns = list(
                set(self.encoder.get_feature_names_out()) - set(one_hot_columns)
            )
            message = f"Columns {missing_columns} are missing in the data for one_hot_encoder inverse_transform."
            logging.info(message)

        return data