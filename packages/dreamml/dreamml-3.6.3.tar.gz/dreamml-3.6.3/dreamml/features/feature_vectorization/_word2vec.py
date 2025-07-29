from typing import List
import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from nltk import word_tokenize
from numpy import hstack

from dreamml.features.feature_vectorization._base import BaseVectorization


class Word2VecVectorization(BaseVectorization):
    """Vectorizes text features using the Word2Vec model.

    This class transforms text data into numerical vectors by training a Word2Vec model
    on the provided text features. It can handle multiple text columns and concatenate
    them if required.

    Attributes:
        name (str): The name identifier for this vectorization method.
    """

    name = "word2vec"

    def __init__(self, text_features: List[str], **kwargs):
        """Initializes the Word2VecVectorization instance.

        Args:
            text_features (List[str]): A list of column names containing text data to be vectorized.
            **kwargs: Additional keyword arguments for configuring the vectorization.
                - vectorizer_type (str, optional): The type of vectorizer to use. Defaults to "word2vec".

        Raises:
            ValueError: If text_features is empty or not provided.
        """
        super().__init__(
            text_features, kwargs.pop("vectorizer_type", "word2vec"), **kwargs
        )

    def fit(self, x: pd.DataFrame, y: pd.Series):
        """Fits the Word2Vec model on the provided data.

        This method trains the Word2Vec model using the concatenated text from the specified
        text features. It processes the text, tokenizes it, and builds the vocabulary.

        Args:
            x (pd.DataFrame): The input DataFrame containing the text features.
            y (pd.Series): The target series (unused in this method).

        Raises:
            TypeError: If the input DataFrame does not contain the specified text features.
            ValueError: If the Word2Vec model fails to train on the provided data.
        """
        concat_text_features_series = (
            x[self.text_features].astype(str).agg(" ".join, axis=1)
        )
        sentences = [
            word_tokenize(str(text), language="russian")
            for text in concat_text_features_series
        ]
        self.vectorizer = (
            Word2Vec(sentences, **self.params).wv
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
        """Transforms the input DataFrame into word vectors.

        This method converts the text data in the specified features into numerical vectors
        using the trained Word2Vec model. The vectors are concatenated if multiple text
        features are provided.

        Args:
            x (pd.DataFrame): The input DataFrame containing the text features to transform.

        Returns:
            pd.DataFrame: A DataFrame containing the word vectors for each input example.

        Raises:
            AttributeError: If the Word2Vec model has not been fitted or loaded.
            ValueError: If the input DataFrame does not contain the required text features.
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
                word2vec_matrix = np.array(
                    [self._get_vector(text) for text in x[feature]]
                )
                embeddings_list.append(word2vec_matrix)
                columns_list.extend(columns)

        embeddings_df = pd.DataFrame(
            data=hstack(embeddings_list), columns=columns_list, index=x.index
        )
        return embeddings_df