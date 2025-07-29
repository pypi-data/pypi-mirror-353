from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
import pandas as pd
import numpy as np
import gensim
import fasttext
from nltk import word_tokenize
from gensim.models import FastText, KeyedVectors
from navec import Navec
from dreamml.logging import get_logger
from dreamml.utils.serialize import Serializable

_logger = get_logger(__name__)


class BaseVectorization(ABC, Serializable):
    """Abstract base class for text feature vectorization.

    This class provides a framework for vectorizing text features using various vectorizer types.
    It handles loading pre-trained models or training new vectorizers based on the provided parameters.

    Args:
        text_features (List[str]): List of column names containing text data to be vectorized.
        vectorizer_type (str): Type of vectorizer to use (e.g., 'tfidf', 'bow', 'word2vec', 'fasttext', 'glove').
        **kwargs: Additional keyword arguments for configuring the vectorizer.
            - concat_text_features (bool, optional): Whether to concatenate text features. Defaults to True.
            - model_path (str, optional): Path to a pre-trained vectorizer model.
            - binary_model (bool, optional): Indicates if the pre-trained model is in binary format. Defaults to False.
            - vector_size (int, optional): Size of the word vectors. Required for certain vectorizer types.

    Raises:
        ValueError: If `vector_size` is not provided for vectorizer types that require it.
    """

    def __init__(self, text_features: List[str], vectorizer_type: str, **kwargs):
        self.text_features = text_features
        self.vectorizer_type = vectorizer_type
        self.params = self._prepare_params(kwargs)
        self.concat_text_features = kwargs.get("concat_text_features", True)
        self.model_path = kwargs.get("model_path")
        self.binary_model: bool = kwargs.get("binary_model", False)
        self.vector_size = kwargs.get("vector_size", None)
        self.feature_columns = {}
        self.used_features = []
        self.vectorizer = None

        if self.vector_size is None and self.vectorizer_type not in ("tfidf", "bow"):
            raise ValueError(f"<vector_size> parameter not found.")

        if vectorizer_type in [
            "fasttext",
            "word2vec",
        ] and gensim.__version__.startswith("3.8"):
            # Compatibility with gensim==3.8.x
            kwargs["size"] = kwargs.pop("vector_size")

        # Load pre-trained model or train a new vectorizer:
        # 1. If user specifies a model path, load the pre-trained model:
        #    - tfidf: Do not load a model, train a new vectorizer
        #    - Word2Vec, Fasttext, Glove: Require model_path and vector_size
        # 2. If no model path is specified, train a new vectorizer:
        #    - tfidf: Always train | Requires max_features
        #    - Word2Vec, Fasttext: Require vector_size
        #    - Glove: Do not train, require model_path

        if self.model_path is not None and self.vectorizer_type not in ["tfidf", "bow"]:
            self._load_model()

    def _load_model(self):
        """Loads a pre-trained vectorizer model based on the specified type and path.

        This method utilizes the `VectorizerModelLoader` to load the appropriate pre-trained model.

        Raises:
            ValueError: If the model type is unsupported or the model cannot be loaded.
        """
        model_loader = VectorizerModelLoader(
            self.vectorizer_type,
            self.model_path,
            self.binary_model,
        )
        self.vectorizer = model_loader.load_model()
        _logger.debug(f"Loaded pretrained vectorizer from '{self.model_path}'.")

    def _prepare_params(self, params_dict: dict):
        """Prepares the parameters by filtering out irrelevant keys.

        Args:
            params_dict (dict): Dictionary of input parameters.

        Returns:
            dict: Filtered dictionary containing relevant parameters.
        """
        params = {
            key: value
            for key, value in params_dict.items()
            if key
            not in ["concat_text_features", "model_path", "binary_model", "n_jobs"]
        }
        return params

    @abstractmethod
    def fit(self, x: pd.DataFrame, y: pd.Series):
        """Fits the vectorizer to the data.

        This abstract method should be overridden by subclasses to implement the fitting logic.

        Args:
            x (pd.DataFrame): Input features.
            y (pd.Series): Target variable.

        Raises:
            NotImplementedError: If the method is not overridden by a subclass.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    @abstractmethod
    def transform(self, x: pd.DataFrame):
        """Transforms the input data into vectorized features.

        This abstract method should be overridden by subclasses to implement the transformation logic.

        Args:
            x (pd.DataFrame): Input features to transform.

        Raises:
            NotImplementedError: If the method is not overridden by a subclass.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def _get_vector(self, text):
        """Computes the mean vector for a given text input.

        This method tokenizes the text, retrieves vectors for known words, and computes their mean.
        If no words are found in the vectorizer, it returns a zero vector.

        Args:
            text (str): The text input to vectorize.

        Returns:
            np.ndarray: The mean vector of the text. Returns a zero vector if no words are found.
        """
        words = word_tokenize(str(text), language="russian")
        vectors = [self.vectorizer[word] for word in words if word in self.vectorizer]
        if vectors:
            return np.mean(vectors, axis=0)
        else:
            return np.zeros(self.vector_size)

    def set_used_features(self):
        """Aggregates and sets the list of used feature names based on feature columns."""
        for _, feature_list in self.feature_columns.items():
            self.used_features.extend(feature_list)

    @staticmethod
    def _remove_preprocessed_prefix(feature_name: str, prefix: str = "_preprocessed"):
        """Removes a specified prefix from a feature name if present.

        Args:
            feature_name (str): The original feature name.
            prefix (str, optional): The prefix to remove. Defaults to "_preprocessed".

        Returns:
            str: The feature name without the specified prefix.
        """
        return (
            feature_name.replace(prefix, "") if prefix in feature_name else feature_name
        )

    def _check_pretrained_loaded_vectorizer(self):
        """Ensures that a pre-trained vectorizer is loaded if a model path is provided.

        If the vectorizer is not already loaded and a model path is specified, this method loads the vectorizer.
        """
        if self.vectorizer is None and self.model_path is not None:
            self._load_model()

    def serialize(self) -> dict:
        """Serializes the vectorizer's state into a dictionary.

        This includes initialization parameters and additional attributes required for serialization.

        Returns:
            dict: A dictionary containing the serialized state of the vectorizer.
        """
        init_dict = {
            "text_features": self.text_features,
            "vectorizer_type": self.vectorizer_type,
            "concat_text_features": self.concat_text_features,
            "model_path": self.model_path,
            "binary_model": self.binary_model,
            "vector_size": self.vector_size,
        }
        init_dict.update(self.params)

        additional_dict = {
            "used_features": self.used_features,
            "feature_columns": self.feature_columns,
            "vectorizer": self.vectorizer,
        }

        return self._serialize(init_data=init_dict, additional_data=additional_dict)

    @classmethod
    def deserialize(cls, data):
        """Deserializes the vectorizer's state from a dictionary.

        Args:
            data (dict): The serialized state of the vectorizer.

        Returns:
            BaseVectorization: An instance of the vectorizer with the deserialized state.
        """
        instance = cls._deserialize(data)

        instance.used_features = data["additional"]["used_features"]
        instance.feature_columns = data["additional"]["feature_columns"]
        instance.vectorizer = data["additional"]["vectorizer"]

        return instance


class VectorizerModelLoader:
    """Universal class for loading pre-trained vectorizer models.

    This class supports loading various types of vectorizer models such as Word2Vec, GloVe, FastText, and others.

    Args:
        model_type (str): Type of the model ('word2vec', 'glove', 'fasttext', 'gensim', etc.).
        model_path (str): Path to the model file.
        binary (bool, optional): Indicates if the model is in binary format. Applicable for Word2Vec and FastText. Defaults to False.

    Raises:
        ValueError: If the provided `model_type` is unsupported.
    """

    def __init__(self, model_type, model_path, binary=False):
        self.model_type = model_type.lower()
        self.model_path = model_path
        self.binary = binary

    def load_model(self):
        """Loads the pre-trained vectorizer model based on its type and file extension.

        Supports models like Navec, GloVe, Word2Vec, FastText, and Gensim Word2Vec.

        Returns:
            Any: The loaded vectorizer model object.

        Raises:
            ValueError: If the `model_type` is unsupported.
        """
        file_extension = Path(self.model_path).suffix

        if (
            "navec" in self.model_path and file_extension == ".tar"
        ):  # Glove navec rus model
            model = Navec.load(self.model_path)
        elif self.model_type == "glove":
            model = self._load_glove_model(self.model_path)
        elif self.model_type == "word2vec":
            model = gensim.models.KeyedVectors.load_word2vec_format(
                self.model_path, binary=self.binary
            )
        elif self.model_type == "fasttext":
            if file_extension == ".model":
                try:
                    model = FastText.load(self.model_path)
                except Exception:
                    model = KeyedVectors.load(self.model_path)
            else:
                model = fasttext.load_model(self.model_path)
        elif self.model_type == "gensim":
            model = gensim.models.Word2Vec.load(self.model_path)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        return model

    def _load_glove_model(self, glove_file_path):
        """Loads a GloVe model from a text file and converts it to Gensim KeyedVectors.

        Args:
            glove_file_path (str): Path to the GloVe text file.

        Returns:
            KeyedVectors: Gensim KeyedVectors containing the GloVe embeddings.
        """
        glove_model = {}
        with open(glove_file_path, "r", encoding="utf-8") as f:
            for line in f:
                split_line = line.split()
                word = split_line[0]
                embedding = np.array([float(val) for val in split_line[1:]])
                glove_model[word] = embedding

        # Convert to Gensim format
        word_vectors = gensim.models.KeyedVectors(vector_size=len(embedding))
        word_vectors.add_vectors(list(glove_model.keys()), list(glove_model.values()))
        return word_vectors