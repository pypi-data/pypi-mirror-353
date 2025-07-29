from sklearn.base import TransformerMixin, BaseEstimator


class WordSynonyms(TransformerMixin, BaseEstimator):
    """Replaces synonyms with their corresponding base words.

    This transformer replaces words in the input data with their base words as defined
    in the provided synonyms dictionary.

    Args:
        synonyms (dict, optional): A dictionary where keys are base words and values
            are lists of synonyms. Defaults to None.
    """

    def __init__(self, synonyms: dict = None):
        """Initializes the WordSynonyms transformer.

        Args:
            synonyms (dict, optional): A dictionary mapping base words to their synonyms.
                Defaults to None.
        """
        self.synonyms = synonyms

    def fit(self, X, y=None):
        """Fits the transformer to the data.

        This transformer does not learn from the data; it simply returns itself.

        Args:
            X: The input data.
            y (optional): The target variable. Defaults to None.

        Returns:
            WordSynonyms: The fitted transformer.
        """
        return self

    def transform(self, X):
        """Transforms the input data by replacing synonyms with base words.

        Args:
            X: The input data, typically a list of lists containing words.

        Returns:
            list: The transformed data with synonyms replaced by their base words.
        """
        inverse_synonyms = {
            synonym: base_word
            for base_word, synonyms in self.synonyms.items()
            for synonym in synonyms
        }
        # Equivalent to: inverse_synonyms.get(w, w) == inverse_synonyms[w] if w in inverse_synonyms else w
        return [[inverse_synonyms.get(w, w) for w in words] for words in X]