from natasha import NamesExtractor, MorphVocab
from sklearn.base import TransformerMixin, BaseEstimator
from tqdm import tqdm


class NameEraser(TransformerMixin, BaseEstimator):
    """Transformer that removes named entities from text data.

    This transformer utilizes Natasha's NamesExtractor to identify and erase
    named entities from each document in the input data.

    Attributes:
        _names_extractor (NamesExtractor): An instance of NamesExtractor for extracting names.
    """

    def __init__(self):
        """Initializes the NameEraser with a NamesExtractor.

        Initializes the NamesExtractor using MorphVocab for morphological vocabulary.
        """
        self._names_extractor = NamesExtractor(MorphVocab())

    def fit(self, X, y=None):
        """Fits the transformer to the data.

        This method does not perform any fitting and simply returns the transformer itself.

        Args:
            X (iterable): Input data to fit. Ignored.
            y (iterable, optional): Target values. Ignored. Defaults to None.

        Returns:
            NameEraser: Returns the instance itself.
        """
        return self

    @staticmethod
    def _replace_str_index(text, start, stop, char=" "):
        """Replaces a substring in the text with a specified character.

        This method replaces the substring of `text` from index `start` to `stop`
        with the `char` character repeated for the length of the substring.

        Args:
            text (str): The original text.
            start (int): The starting index of the substring to replace.
            stop (int): The ending index of the substring to replace.
            char (str, optional): The character to replace with. Defaults to " ".

        Returns:
            str: The text with the specified substring replaced.

        Raises:
            ValueError: If `start` or `stop` indices are out of bounds.
        """
        return f"{text[:start]}{char * (stop - start)}{text[stop:]}"

    def _erase_name(self, doc):
        """Erases named entities from a single document.

        Identifies named entities within the document and replaces them with spaces.

        Args:
            doc (str): The document from which to erase named entities.

        Returns:
            str: The document with named entities erased.

        Raises:
            AttributeError: If the NamesExtractor fails to process the document.
        """
        matches = self._names_extractor(str(doc))
        for m in matches:
            doc = NameEraser._replace_str_index(doc, m.start, m.stop)
        return doc

    def transform(self, X):
        """Transforms the input data by erasing named entities from each document.

        Applies the `_erase_name` method to each document in the input data,
        displaying a progress bar during the transformation.

        Args:
            X (iterable): An iterable of documents (strings) to be transformed.

        Returns:
            list: A list of transformed documents with named entities erased.

        Raises:
            TypeError: If `X` is not iterable.
            AttributeError: If any document in `X` is not a string.
        """
        return [self._erase_name(doc) for doc in tqdm(X, "Name eraser")]