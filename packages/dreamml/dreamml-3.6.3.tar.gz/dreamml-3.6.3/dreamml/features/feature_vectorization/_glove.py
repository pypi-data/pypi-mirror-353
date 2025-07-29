from typing import List
import pandas as pd
import numpy as np
from numpy import hstack

from dreamml.features.feature_vectorization._base import BaseVectorization


class GloveVectorization(BaseVectorization):
    """Performs GloVe vectorization on specified text features.

    This class transforms textual data into numerical vectors using pre-trained GloVe embeddings.
    It supports both concatenated text features and individual text features vectorization.

    Attributes:
        name (str): The name of the vectorization method, set to "glove".
    """

    name = "glove"

    def __init__(self, text_features: List[str], **kwargs):
        """Initializes the GloveVectorization instance.

        Args:
            text_features (List[str]): A list of column names containing text data to be vectorized.
            **kwargs: Additional keyword arguments. Can include 'vectorizer_type' and other parameters.

        Raises:
            ValueError: If 'model_path' is not provided in the keyword arguments.
        """
        super().__init__(
            text_features, kwargs.pop("vectorizer_type", "glove"), **kwargs
        )
        if self.model_path is None:
            msg = f"Required parameters for glove: model_path"
            raise ValueError(msg)

    def fit(self, x: pd.DataFrame, y: pd.Series):
        """Fits the vectorizer to the data.

        Prepares the feature columns based on whether text features are concatenated or treated individually.

        Args:
            x (pd.DataFrame): The input DataFrame containing text features.
            y (pd.Series): The target variable (not used in this method).

        Returns:
            None
        """
        if self.concat_text_features:
            self.feature_columns["text"] = [
                self._remove_preprocessed_prefix(f"{self.name}_{idx}")
                for idx in range(self.vector_size)
            ]
        else:
            for feature in self.text_features:
                self.feature_columns[feature] = [
                    self._remove_preprocessed_prefix(f"{self.name}_{feature}_{idx}")
                    for idx in range(self.vector_size)
                ]
        self.set_used_features()

    def transform(self, x: pd.DataFrame):
        """Transforms the input DataFrame into a DataFrame of GloVe embeddings.

        Converts the specified text features into their corresponding GloVe vector representations.

        Args:
            x (pd.DataFrame): The input DataFrame containing text features to be transformed.

        Returns:
            pd.DataFrame: A DataFrame containing the GloVe embeddings for the input text features.

        Raises:
            Exception: If the pretrained GloVe vectorizer is not loaded.
        """
        self._check_pretrained_loaded_vectorizer()

        embeddings_list = []
        columns_list = []

        if self.concat_text_features:
            concat_text_features_series = (
                x[self.text_features].astype(str).agg(" ".join, axis=1)
            )
            columns_list = self.feature_columns["text"]
            embeddings_list = [
                np.array(
                    [self._get_vector(text) for text in concat_text_features_series]
                )
            ]
        else:
            for feature in self.text_features:
                columns = self.feature_columns[feature]
                glove_matrix = np.array([self._get_vector(text) for text in x[feature]])
                embeddings_list.append(glove_matrix)
                columns_list.extend(columns)

        embeddings_df = pd.DataFrame(
            data=hstack(embeddings_list), columns=columns_list, index=x.index
        )
        return embeddings_df