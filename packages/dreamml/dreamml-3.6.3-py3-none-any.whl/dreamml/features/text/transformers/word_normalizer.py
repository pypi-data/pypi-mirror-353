from functools import lru_cache
import pymorphy2
from sklearn.base import TransformerMixin, BaseEstimator


class WordNormalizer(TransformerMixin, BaseEstimator):
    """Normalizes words to their base (normal) forms.

    This transformer processes a collection of documents by converting each word
    to its normal form using the pymorphy2 morphological analyzer. It caches
    the results of normalization to improve performance for repeated words.
    """

    def __init__(self):
        """Initializes the WordNormalizer with a pymorphy2 MorphAnalyzer.

        Sets up the morphological analyzer used for normalizing words.
        """
        self._parser = pymorphy2.MorphAnalyzer()

    def fit(self, X, y=None):
        """Fits the transformer to the data.

        Since this transformer does not learn from the data, this method
        simply returns the instance itself.

        Args:
            X (Iterable): The input data to fit. Typically ignored.
            y (Iterable, optional): The target values. Defaults to None.

        Returns:
            WordNormalizer: The fitted transformer.
        """
        return self

    @lru_cache(maxsize=10000)
    def _normal_form(self, word):
        """Converts a word to its normal form.

        Uses the morphological analyzer to parse the word and extract its
        normal form.

        Args:
            word (str): The word to normalize.

        Returns:
            str: The normal form of the word.

        Raises:
            IndexError: If the word cannot be parsed and no normal form is found.
        """
        return self._parser.parse(word)[0].normal_form

    def _preprocess_words(self, doc):
        """Processes a document by normalizing all its words.

        Iterates over each word in the document and converts it to its normal form.

        Args:
            doc (Iterable[str]): A single document represented as a list of words.

        Returns:
            list[str]: A list of normalized words.
        """
        return [self._normal_form(word) for word in doc]

    def transform(self, X):
        """Transforms a collection of documents by normalizing their words.

        Applies the normalization process to each document in the input collection.

        Args:
            X (Iterable[Iterable[str]]): A collection of documents, each represented
                as a list of words.

        Returns:
            list[list[str]]: A list of documents with all words normalized.
        """
        return [self._preprocess_words(doc) for doc in X]