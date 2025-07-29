from typing import List, Optional
import pandas as pd
from gensim.corpora.dictionary import Dictionary
from nltk import word_tokenize
from dreamml.features.feature_vectorization._base import BaseVectorization


class BowVectorization(BaseVectorization):
    """Bag-of-Words vectorization for text features.

    This class transforms text data into a bag-of-words (BoW) representation
    using tokenization and dictionary creation for each specified text feature.
    """

    name = "bow"

    def __init__(self, text_features: List[str], **kwargs):
        """Initializes the BowVectorization with specified text features.

        Args:
            text_features (List[str]): A list of column names representing text features to vectorize.
            **kwargs: Additional keyword arguments. Can include 'vectorizer_type' to specify the type of vectorizer.

        """
        super().__init__(text_features, kwargs.pop("vectorizer_type", "bow"), **kwargs)
        self.vectorizers = {feature: None for feature in self.text_features}

    def fit(
        self,
        x: pd.DataFrame,
        y: pd.Series,
        x_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ):
        """Fits the vectorizer using the training data.

        This method sets up the vectorizer based on the provided training data.
        It identifies and prepares the text features that will be used for vectorization.

        Args:
            x (pd.DataFrame): The training feature data.
            y (pd.Series): The training target data.
            x_val (Optional[pd.DataFrame], optional): The validation feature data. Defaults to None.
            y_val (Optional[pd.Series], optional): The validation target data. Defaults to None.

        """
        self.set_used_features()

    def transform(self, x: pd.DataFrame, _: bool = False):
        """Transforms the input data into a bag-of-words representation.

        For each specified text feature, this method tokenizes the text,
        creates a dictionary, and generates the bag-of-words corpus.

        Args:
            x (pd.DataFrame): The input feature data to transform.
            _ (bool, optional): An unused boolean parameter. Defaults to False.

        Returns:
            dict: A dictionary where each key is a text feature and the value
                  is another dictionary containing the 'dict' (gensim Dictionary)
                  and 'bow_corpus' (list of bag-of-words representations).

        Raises:
            ValueError: If a specified text feature is not found in the input DataFrame.
        """
        bow_corpus_dict = dict()
        for feature in self.text_features:
            if feature not in x.columns:
                raise ValueError(f"Feature '{feature}' not found in the input DataFrame.")
            corpus = [
                word_tokenize(str(text), language="russian") for text in x[feature]
            ]
            dictionary = Dictionary(corpus)
            bow_corpus = [dictionary.doc2bow(doc) for doc in corpus]

            bow_corpus_dict[feature] = {"dict": dictionary, "bow_corpus": bow_corpus}
        return bow_corpus_dict