import pandas as pd
from sklearn.base import TransformerMixin, BaseEstimator
import re


class TextCleaner(TransformerMixin, BaseEstimator):
    """TextCleaner is a scikit-learn transformer for cleaning text data.

    It performs the following operations:
        1. Converts text to lowercase.
        2. Replaces dates, URLs, and other patterns.
        3. Cleans text by removing unwanted characters.
        4. Removes extra whitespace.

    Attributes:
        _date_re (re.Pattern): Compiled regular expression to match dates.
        _url_re (re.Pattern): Compiled regular expression to match URLs.
        _us_re (re.Pattern): Compiled regular expression to match 'us' followed by four digits.
        _multiple_spaces_re (re.Pattern): Compiled regular expression to match multiple whitespace characters.
    """

    def __init__(self):
        """Initializes the TextCleaner with compiled regular expressions for text cleaning.

        Attributes:
            _date_re (re.Pattern): Compiled regular expression to match dates.
            _url_re (re.Pattern): Compiled regular expression to match URLs.
            _us_re (re.Pattern): Compiled regular expression to match 'us' followed by four digits.
            _multiple_spaces_re (re.Pattern): Compiled regular expression to match multiple whitespace characters.
        """
        self._date_re = re.compile(
            "[0-9]{1,4}[\\\.\-:_,\/][0-9]{1,2}[\\\.\-:_,\/][0-9]{1,4}"
        )
        self._url_re = re.compile("https?://\S+")
        self._us_re = re.compile(r"us[0-9]{4}")
        self._multiple_spaces_re = re.compile(r"[\s]{2,}")
        pass

    def fit(self, X, y=None):
        """Fits the TextCleaner transformer.

        As this transformer does not learn from data, it simply returns itself.

        Args:
            X (array-like): Input data to fit.
            y (array-like, optional): Target values. Defaults to None.

        Returns:
            TextCleaner: Returns self.
        """
        return self

    def transform(self, X):
        """Transforms the input data by cleaning the text.

        The transformation includes:
            - Converting text to lowercase.
            - Replacing dates with the string "datetime".
            - Removing URLs.
            - Replacing specific patterns with spaces.
            - Replacing 'ё' with 'e'.
            - Replacing newline characters with spaces.
            - Removing the word "решение".
            - Removing punctuation.
            - Removing extra whitespace.
            - Stripping leading and trailing spaces.

        Args:
            X (array-like or pandas.Series): Input data to transform.

        Returns:
            pandas.Series: Transformed text data.
        """
        if isinstance(X, list):
            X = pd.Series(X)
        text = X.copy()
        text = text.str.lower()
        text = text.replace(self._date_re, "datetime", regex=True)
        text = text.replace(self._url_re, "", regex=True)
        text = text.replace(self._us_re, " ", regex=True)
        text = text.str.replace("ё", "e")
        text = text.str.replace("\n", " ")
        text = text.replace("решение", " ", regex=True)
        text = text.replace(r"[^\w\s\d]", " ", regex=True)  # Punctuation
        text = text.replace(self._multiple_spaces_re, " ", regex=True)  # Extra spaces
        text = text.str.strip()
        return text