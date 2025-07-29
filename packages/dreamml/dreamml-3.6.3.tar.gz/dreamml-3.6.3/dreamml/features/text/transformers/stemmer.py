import nltk
from sklearn.base import TransformerMixin, BaseEstimator


class Stemmer(TransformerMixin, BaseEstimator):
    """
    A transformer that applies stemming to Russian text using the SnowballStemmer.

    This transformer can be used in scikit-learn pipelines to preprocess text data by reducing words to their stem forms.

    Attributes:
        _stemmer (nltk.stem.SnowballStemmer): An instance of the SnowballStemmer for the Russian language.
    """

    def __init__(self):
        """
        Initializes the Stemmer with a SnowballStemmer for the Russian language.
        """
        self._stemmer = nltk.stem.SnowballStemmer("russian")

    def fit(self, X, y=None):
        """
        Fits the transformer to the data.

        Since stemming does not require fitting, this method simply returns the transformer itself.

        Args:
            X (iterable): The input data to fit. This parameter is ignored.
            y (optional): The target values. This parameter is ignored.

        Returns:
            Stemmer: Returns the transformer instance itself.
        """
        return self

    def _coder_stem(self, s):
        """
        Applies stemming to a single string.

        This method splits the input string into words, stems each word, and then joins them back into a single string.

        Args:
            s (str): The input string to stem.

        Returns:
            str: The stemmed version of the input string.
        """
        return " ".join([self._stemmer.stem(w) for w in s.split()])

    def transform(self, X):
        """
        Transforms a list of documents by applying stemming to each document.

        Args:
            X (list of str): The input documents to transform.

        Returns:
            list of str: A list of stemmed documents.
        """
        return [self._coder_stem(doc) for doc in X]