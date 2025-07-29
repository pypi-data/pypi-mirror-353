import re
from sklearn.base import TransformerMixin, BaseEstimator


class DigitEraser(TransformerMixin, BaseEstimator):
    """Transformer that removes numeric values from text documents.

    This transformer scans each document and replaces all numeric digits with a space.

    Attributes:
        _digit_re (Pattern): Compiled regular expression to match one or more digits.
    """

    def __init__(self):
        """Initializes the DigitEraser with a compiled regular expression for digits."""
        self._digit_re = re.compile(r"\d+")

    def fit(self, X, y=None):
        """Fits the transformer on the data.

        Since DigitEraser does not learn from the data, this method simply returns the instance itself.

        Args:
            X (iterable): The input data to fit. Ignored in this transformer.
            y (iterable, optional): The target values. Ignored in this transformer.

        Returns:
            DigitEraser: The fitted transformer.
        """
        return self

    def transform(self, X):
        """Transforms the data by removing all numeric digits from each document.

        Args:
            X (iterable): An iterable of documents (strings) to be transformed.

        Returns:
            list: A list of transformed documents with numeric digits removed.

        Raises:
            TypeError: If an element in X cannot be converted to a string.
        """
        return [self._digit_re.sub(" ", str(doc)) for doc in X]