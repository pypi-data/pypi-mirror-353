from typing import List
import pandas as pd
import numpy as np
from gensim.models import FastText
from nltk import word_tokenize
from numpy import hstack

from dreamml.features.feature_vectorization._base import BaseVectorization


class FastTextVectorization(BaseVectorization):
    """Vectorizes text features using the FastText model.

    This class provides functionality to fit a FastText model on text data and transform
    text features into numerical vector representations. It supports both concatenated
    text features and individual text features.

    Attributes:
        name (str): The name identifier for the vectorization method.
    """
    name = "fasttext"

    def __init__(self, text_features: List[str], **kwargs):
        """Initializes the FastTextVectorization with specified text features.

        Args:
            text_features (List[str]): A list of column names representing text features to be vectorized.
            **kwargs: Additional keyword arguments for initialization. Supports 'vectorizer_type' to specify
                      the type of vectorizer, defaulting to "fasttext" if not provided.

        """
        super().__init__(
            text_features, kwargs.pop("vectorizer_type", "fasttext"), **kwargs
        )

    def fit(self, x: pd.DataFrame, y: pd.Series):
        """Fits the FastText model on the provided dataset.

        This method concatenates the specified text features, tokenizes the text into sentences,
        and trains the FastText model. It also sets up the feature columns based on whether
        text features are concatenated or handled individually.

        Args:
            x (pd.DataFrame): The input DataFrame containing feature columns.
            y (pd.Series): The target variable series.

        Raises:
            ValueError: If text_features are not present in the input DataFrame.
        """
        concat_text_features_series = (
            x[self.text_features].astype(str).agg(" ".join, axis=1)
        )
        sentences = [
            word_tokenize(str(text), language="russian")
            for text in concat_text_features_series
        ]
        self.vectorizer = (
            FastText(sentences, **self.params).wv
            if self.vectorizer is None
            else self.vectorizer
        )

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

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        """Transforms the input DataFrame by vectorizing its text features.

        This method checks if a pretrained FastText vectorizer is loaded, then processes the text
        features either by concatenating them or handling them individually. It generates a DataFrame
        containing the vectorized representations of the text features.

        Args:
            x (pd.DataFrame): The input DataFrame containing feature columns to be transformed.

        Returns:
            pd.DataFrame: A DataFrame with FastText vectorized features as numerical columns.

        Raises:
            ValueError: If the vectorizer has not been fitted or loaded properly.
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
                fasttext_matrix = np.array(
                    [self._get_vector(text) for text in x[feature]]
                )
                embeddings_list.append(fasttext_matrix)
                columns_list.extend(columns)

        embeddings_df = pd.DataFrame(
            data=hstack(embeddings_list), columns=columns_list, index=x.index
        )
        return embeddings_df