from copy import deepcopy
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from dreamml.utils.serialize import Serializable


class DmlLabelEncoder(Serializable):
    """
    DmlLabelEncoder is a label encoding utility that transforms categorical features into numerical values
    using sklearn's LabelEncoder. It supports fitting to data, transforming data, inverse transforming,
    and serialization/deserialization.

    Attributes:
        encoder (LabelEncoder): The underlying sklearn LabelEncoder instance.
    """

    def __init__(self):
        """
        Initializes the DmlLabelEncoder with a new instance of LabelEncoder.
        """
        self.encoder = LabelEncoder()

    def fit(self, data: pd.DataFrame, feature: str):
        """
        Fits the LabelEncoder to the specified feature in the given DataFrame.

        Args:
            data (pd.DataFrame): The DataFrame containing the feature to encode.
            feature (str): The name of the feature/column to encode.

        Returns:
            DmlLabelEncoder: The fitted encoder instance.
        """
        self.encoder = self.encoder.fit(data[feature])
        return self

    def transform(self, data: pd.DataFrame, feature: str):
        """
        Transforms the specified feature in the given DataFrame using the fitted LabelEncoder.

        Args:
            data (pd.DataFrame): The DataFrame containing the feature to transform.
            feature (str): The name of the feature/column to transform.

        Returns:
            pd.DataFrame: A new DataFrame with the transformed feature.
        """
        x_transformed = deepcopy(data)
        x_transformed[feature] = self.encoder.transform(x_transformed[feature])
        return x_transformed

    def inverse_transform(self, data: pd.DataFrame, feature: str):
        """
        Inversely transforms the specified feature in the given DataFrame using the fitted LabelEncoder.

        Args:
            data (pd.DataFrame): The DataFrame containing the feature to inverse transform.
            feature (str): The name of the feature/column to inverse transform.

        Returns:
            pd.DataFrame: A new DataFrame with the inverse transformed feature.
        """
        x_transformed = deepcopy(data)
        if feature in x_transformed.columns:
            x_transformed[feature] = self.encoder.inverse_transform(
                x_transformed[feature]
            )
        return x_transformed

    def serialize(self) -> dict:
        """
        Serializes the DmlLabelEncoder instance into a dictionary.

        Returns:
            dict: A dictionary containing the serialized encoder data.
        """
        return self._serialize(additional_data={"encoder": self.encoder})

    @classmethod
    def deserialize(cls, data):
        """
        Deserializes the given data into a DmlLabelEncoder instance.

        Args:
            data (dict): The serialized data dictionary.

        Returns:
            DmlLabelEncoder: A new instance of DmlLabelEncoder with the loaded encoder.
        """
        instance = cls._deserialize(data)

        instance.encoder = data["additional"]["encoder"]

        return instance