import re
from sklearn.base import TransformerMixin, BaseEstimator


class WordSplitter(TransformerMixin, BaseEstimator):
    """A transformer that splits text into words and converts them to lowercase.

    This transformer uses a regular expression to find all word characters
    and converts the text to lowercase before splitting.

    Attributes:
        _chars_re (re.Pattern): Compiled regular expression pattern for matching words.
    """

    def __init__(self):
        """Initializes the WordSplitter with a specific regex pattern."""
        self._chars_re = re.compile(r"[_a-zа-яё]+")

    def fit(self, X, y=None):
        """Fits the transformer to the data.

        This transformer does not learn anything from the data, so it simply returns itself.

        Args:
            X (iterable): The input data to fit.
            y (ignored): Not used, present for API consistency by convention.

        Returns:
            WordSplitter: Returns the instance itself.
        """
        return self

    def preprocess_doc(self, doc):
        """Preprocesses a single document by splitting it into lowercase words.

        Args:
            doc (str): The document to preprocess.

        Returns:
            list: A list of lowercase words extracted from the document.
        """
        return [word for word in self._chars_re.findall(str(doc).lower())]

    def transform(self, X):
        """Transforms a collection of documents by preprocessing each one.

        Args:
            X (iterable): An iterable of documents to transform.

        Returns:
            list: A list where each element is a list of lowercase words from the corresponding document.
        """
        return [self.preprocess_doc(doc) for doc in X]