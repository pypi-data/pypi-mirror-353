import re
from string import punctuation
from sklearn.base import TransformerMixin, BaseEstimator

punctuation.replace("_", "")


class PunctuationEraser(TransformerMixin, BaseEstimator):
    """
    Transformer that removes punctuation from text data.

    This class leverages regular expressions to substitute punctuation characters
    with spaces in the input text data, excluding the underscore character.
    """

    def __init__(self):
        """
        Initializes the PunctuationEraser with a compiled regular expression pattern.

        The pattern is designed to match all punctuation characters except the underscore.
        """
        self._punctuation = punctuation.replace("_", "")
        self._punct_re = re.compile(f"[{self._punctuation}]")

    def fit(self, X, y=None):
        """
        Fits the transformer to the data.

        Since this transformer does not learn from the data, it simply returns itself.

        Args:
            X (iterable): The input data to fit. Not used.
            y (iterable, optional): The target values. Not used.

        Returns:
            PunctuationEraser: The fitted transformer (self).
        """
        return self

    def transform(self, X):
        """
        Transforms the input data by removing punctuation.

        Each document in X is processed by substituting punctuation characters with spaces.

        Args:
            X (iterable): The input data to transform, where each element is a document.

        Returns:
            list: A list of transformed documents with punctuation removed.
        """
        return [self._punct_re.sub(" ", str(doc)) for doc in X]