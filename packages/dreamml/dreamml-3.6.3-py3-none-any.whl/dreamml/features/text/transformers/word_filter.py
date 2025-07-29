from sklearn.base import TransformerMixin, BaseEstimator


class WordFilter(TransformerMixin, BaseEstimator):
    """
    Filters out specified stop words from input data.

    Args:
        stop_words (set): A set of words to be removed from the input data.
    """

    def __init__(self, stop_words: set):
        self.stop_words = stop_words

    def fit(self, X, y=None):
        """
        Fits the transformer to the data.

        This method does not perform any operation and simply returns the instance itself.

        Args:
            X: The input data to fit, typically a list of word lists.
            y: Ignored. Present for API consistency by convention.

        Returns:
            self: The fitted transformer instance.
        """
        return self

    def transform(self, X):
        """
        Transforms the input data by removing stop words.

        Args:
            X: The input data to transform, typically a list of word lists.

        Returns:
            list: A list of word lists with stop words removed.
        """
        return [[w for w in words if w not in self.stop_words] for words in X]