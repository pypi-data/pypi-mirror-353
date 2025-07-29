from sklearn.base import TransformerMixin, BaseEstimator


class WordJoiner(TransformerMixin, BaseEstimator):
    """
    Transformer that joins lists of words into concatenated strings.

    This transformer takes an iterable of documents, where each document is
    represented as a list of words, and joins the words in each document
    into a single string separated by spaces.
    """

    def fit(self, X, y=None):
        """
        Fit the WordJoiner transformer on the data.

        This method does not perform any fitting but is implemented to comply
        with scikit-learn's Transformer interface.

        Args:
            X (Iterable): The input data to fit. Each element should be an
                iterable of words.
            y (optional): Ignored. This parameter exists only for
                compatibility with scikit-learn's Transformer interface.

        Returns:
            self: Returns the instance itself.
        """
        return self

    def transform(self, X):
        """
        Transform the input data by joining words in each document into a single string.

        Args:
            X (Iterable[Iterable[str]]): An iterable where each element is an
                iterable of words representing a document.

        Returns:
            List[str]: A list of strings where each string is a document with
                words joined by spaces.
        """
        return [" ".join(doc) for doc in X]