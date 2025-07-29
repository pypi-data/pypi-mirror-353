from typing import List
from scipy.sparse import hstack
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from dreamml.features.feature_vectorization._base import BaseVectorization


class TfidfVectorization(BaseVectorization):
    """
    A vectorization class that transforms text features into TF-IDF feature vectors.

    This class utilizes scikit-learn's `TfidfVectorizer` to convert textual data
    into numerical feature vectors based on the Term Frequency-Inverse Document
    Frequency (TF-IDF) scheme. It supports both concatenated text features and
    individual text feature processing.

    Attributes:
        name (str): The name identifier for the vectorization method.
        vectorizers (dict): A dictionary of `TfidfVectorizer` instances for each text feature.
        feature_columns (dict): A dictionary mapping each text feature to its corresponding feature column names.
    """
    name = "tfidf"

    def __init__(self, text_features: List[str], **kwargs):
        """
        Initializes the TfidfVectorization instance with specified text features and parameters.

        Args:
            text_features (List[str]): A list of column names in the DataFrame that contain textual data.
            **kwargs: Additional keyword arguments for configuring the vectorization process.
                - vectorizer_type (str, optional): The type of vectorizer to use. Defaults to "tfidf".
                - vector_size (int, optional): The size of the vector. This parameter is removed from `self.params`.

        Raises:
            KeyError: If `vector_size` is not present in the provided `kwargs`.
        """
        super().__init__(
            text_features, kwargs.pop("vectorizer_type", "tfidf"), **kwargs
        )
        self.params.pop("vector_size")
        if self.concat_text_features:
            self.vectorizers = {"text": TfidfVectorizer(**self.params)}
        else:
            self.vectorizers = {
                feature: TfidfVectorizer(**self.params)
                for feature in self.text_features
            }

    def fit(self, x: pd.DataFrame, y: pd.Series):
        """
        Fits the TF-IDF vectorizers to the provided DataFrame.

        Depending on the configuration, it either concatenates all text features
        into a single series and fits a single `TfidfVectorizer`, or fits individual
        `TfidfVectorizer` instances for each text feature.

        Args:
            x (pd.DataFrame): The input DataFrame containing the text features to be vectorized.
            y (pd.Series): The target variable. Not utilized in this method but included for compatibility.

        Raises:
            ValueError: If the input DataFrame does not contain the specified text features.
        """
        if self.concat_text_features:
            concat_text_features_series = (
                x[self.text_features].astype(str).agg(" ".join, axis=1)
            )
            vectorizer = self.vectorizers["text"]
            vectorizer.fit(concat_text_features_series)
            self.feature_columns["text"] = [
                self._remove_preprocessed_prefix(f"{self.name}_{idx}")
                for idx in range(vectorizer.get_feature_names_out().size)
            ]
        else:
            for feature in self.text_features:
                self.vectorizers[feature].fit(x[feature])
                self.feature_columns[feature] = [
                    self._remove_preprocessed_prefix(f"{self.name}_{feature}_{idx}")
                    for idx in range(
                        self.vectorizers[feature].get_feature_names_out().size
                    )
                ]
        self.set_used_features()

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms the input DataFrame's text features into TF-IDF feature vectors.

        This method generates TF-IDF embeddings for the specified text features
        and returns a DataFrame containing the resulting numerical vectors.

        Args:
            x (pd.DataFrame): The input DataFrame containing the text features to be transformed.

        Returns:
            pd.DataFrame: A DataFrame where each text feature has been transformed into its corresponding TF-IDF vectors.

        Raises:
            KeyError: If the input DataFrame does not contain the specified text features.
        """
        embeddings_list = []
        columns_list = []

        if self.concat_text_features:
            concat_text_features_series = (
                x[self.text_features].astype(str).agg(" ".join, axis=1)
            )
            vectorizer = self.vectorizers["text"]
            columns_list = self.feature_columns["text"]
            embeddings_list = [vectorizer.transform(concat_text_features_series)]
        else:
            for feature in self.text_features:
                vectorizer = self.vectorizers[feature]
                columns = self.feature_columns[feature]
                tfidf_matrix = vectorizer.transform(x[feature])
                embeddings_list.append(tfidf_matrix)
                columns_list.extend(columns)

        embeddings_df = pd.DataFrame(
            data=hstack(embeddings_list).toarray(), columns=columns_list, index=x.index
        )
        return embeddings_df

    def _serialize(
        self,
        init_data=None,
        additional_data=None,
    ) -> dict:
        """
        Serializes the current state of the TfidfVectorization instance.

        This method prepares the vectorization instance's data for storage or transmission,
        including the configuration and trained vectorizers.

        Args:
            init_data (dict, optional): Initial data for serialization. Defaults to None.
            additional_data (dict, optional): Additional data to include in the serialization. Defaults to None.

        Returns:
            dict: A dictionary containing the serialized state of the instance, including vectorizers.

        Raises:
            KeyError: If `additional_data` is not provided.
        """
        additional_data["vectorizers"] = self.vectorizers

        return super()._serialize(init_data, additional_data)

    @classmethod
    def deserialize(cls, data: dict):
        """
        Deserializes the provided data to create a new TfidfVectorization instance.

        This class method reconstructs a `TfidfVectorization` instance from serialized data,
        restoring its configuration and vectorizers.

        Args:
            data (dict): The serialized data containing the configuration and vectorizers.

        Returns:
            TfidfVectorization: A new instance of `TfidfVectorization` initialized with the provided data.

        Raises:
            KeyError: If the necessary keys are not present in the `data` dictionary.
            TypeError: If the data types of the serialized components are incorrect.
        """
        instance = super().deserialize(data)

        instance.vectorizers = data["additional"]["vectorizers"]

        return instance