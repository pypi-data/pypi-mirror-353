import math
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from nltk.tokenize import word_tokenize
import nlpaug.augmenter.char as nac
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.sentence as nas
import nlpaug.augmenter.spectrogram as nsp
import torch

from dreamml.utils.serialize import Serializable


class TextAugmenter(BaseEstimator, TransformerMixin):
    """
    A transformer for augmenting text data using various augmentation techniques.

    This class integrates with scikit-learn's pipeline and allows for
    augmentation of text data based on specified augmentation strategies.
    It can optionally balance classes by augmenting each class to match the
    size of the largest class.

    Args:
        augmentations (list): A list of augmentation wrapper objects.
        text_column (str): The name of the column containing text data.
        target_column (str): The name of the column containing target labels.
        start_index (int, optional): The starting index for augmented data.
            Defaults to 0.
        aug_p (float, optional): The proportion of the dataset to augment for
            each augmentation type. Defaults to 0.0.
        balance_classes (bool, optional): Whether to balance classes by augmenting
            each class to match the size of the largest class. Defaults to False.

    Attributes:
        augmentations (list): List of augmentation wrapper objects.
        text_column (str): Name of the text column.
        target_column (str): Name of the target column.
        start_index (int): Starting index for augmented data.
        aug_p (float): Proportion of data to augment.
        balance_classes (bool): Flag to balance classes.
    """

    def __init__(
        self,
        augmentations,
        text_column,
        target_column,
        start_index=0,
        aug_p=0.0,
        balance_classes=False,
    ):
        self.augmentations = augmentations
        self.text_column = text_column
        self.target_column = target_column
        self.start_index = start_index
        self.aug_p = aug_p
        self.balance_classes = balance_classes

    def fit(self, X, y=None):
        """
        Fit the transformer on the data.

        This method does not perform any fitting but is required for compatibility
        with scikit-learn pipelines.

        Args:
            X (pd.DataFrame): Input data.
            y (pd.Series, optional): Target labels. Defaults to None.

        Returns:
            TextAugmenter: The fitted transformer.
        """
        return self

    def transform(self, X):
        """
        Transform the input data by augmenting text data.

        Depending on the `balance_classes` flag, this method either augments
        the data uniformly or balances each class by augmenting it to match
        the size of the largest class.

        Args:
            X (pd.DataFrame): Input data containing text and target columns.

        Returns:
            pd.DataFrame: Augmented data as a new DataFrame.

        Raises:
            ValueError: If the input DataFrame does not contain the specified
                        text or target columns.
        """
        if self.text_column not in X.columns or self.target_column not in X.columns:
            raise ValueError(
                f"Input DataFrame must contain '{self.text_column}' and '{self.target_column}' columns."
            )

        num_samples_per_aug = math.ceil(len(X) * self.aug_p)
        augmented_data = []

        if self.balance_classes:
            class_counts = X[self.target_column].value_counts()
            max_class_size = class_counts.max()

            for class_label, count in class_counts.items():
                class_data = X[X[self.target_column] == class_label]
                num_samples_for_class = max_class_size - count
                num_samples_for_class = math.ceil(num_samples_for_class * self.aug_p)

                for aug in self.augmentations:
                    num_samples_for_class_min = min(
                        class_data.shape[0], num_samples_for_class
                    )
                    sampled_data = class_data.sample(num_samples_for_class_min)
                    for idx, row in sampled_data.iterrows():
                        original_text = row[self.text_column]
                        augmented_text = aug.augment(original_text)
                        augmented_row = row.copy()
                        augmented_row[self.text_column] = augmented_text
                        augmented_row["_group_nlp_aug_field"] = idx
                        augmented_data.append(augmented_row)
        else:
            for aug in self.augmentations:
                sampled_data = X.sample(num_samples_per_aug)
                for idx, row in sampled_data.iterrows():
                    original_text = row[self.text_column]
                    augmented_text = aug.augment(original_text)
                    augmented_row = row.copy()
                    augmented_row[self.text_column] = augmented_text
                    augmented_row["_group_nlp_aug_field"] = idx
                    augmented_data.append(augmented_row)

        augmented_df = pd.DataFrame(augmented_data)
        augmented_df.index = range(
            self.start_index + 1, self.start_index + 1 + len(augmented_df)
        )

        return augmented_df


class AugmentationWrapper(Serializable):
    """
    A wrapper class for different types of text augmentation techniques.

    This class provides a unified interface to various augmentation methods
    from the `nlpaug` library. It handles the initialization of specific
    augmenters based on the augmentation type and manages serialization.

    Args:
        aug_type (str): The type of augmentation to apply.
        **kwargs: Additional keyword arguments specific to the augmentation type.

    Attributes:
        aug_type (str): The type of augmentation.
        params (dict): Parameters for the augmentation.
        aug_stopwords (list): List of stopwords to exclude from augmentation.
    """

    def __init__(self, aug_type, **kwargs):
        self.aug_type = aug_type
        self.params = kwargs
        self.aug_stopwords = [
            "TOKEN",
            "token",
            "datetime",
            "DATETIME",
            "num_token",
            "NUM_TOKEN",
            "name_token",
            "NAME_TOKEN",
            "company_token",
            "COMPANY_TOKEN",
            "url_token",
            "URL_TOKEN",
            "email_token",
            "EMAIL_TOKEN",
            "login_token",
            "LOGIN_TOKEN",
        ]

    @staticmethod
    def split(text):
        """
        Tokenize the input text using NLTK's word_tokenize.

        Args:
            text (str): The text to tokenize.

        Returns:
            list: A list of word tokens.
        """
        return word_tokenize(str(text), language="russian")

    def _get_aug_type(self):
        """
        Initialize and return the appropriate augmenter based on the augmentation type.

        This method selects the augmenter from `nlpaug` library corresponding
        to the `aug_type`. It also ensures that stopwords are set if not provided.

        Raises:
            ValueError: If the specified augmentation type is unknown.

        Returns:
            Augmenter: An instance of the selected augmenter.
        """
        if self.aug_type == "KeyboardAug":
            if "stopwords" not in self.params:
                self.params["stopwords"] = self.aug_stopwords
            aug = nac.KeyboardAug(tokenizer=self.split, **self.params)
        elif self.aug_type == "RandomCharAug":
            if "stopwords" not in self.params:
                self.params["stopwords"] = self.aug_stopwords
            aug = nac.RandomCharAug(tokenizer=self.split, **self.params)
        elif self.aug_type == "RandomWordAug":
            if "stopwords" not in self.params:
                self.params["stopwords"] = self.aug_stopwords
            aug = naw.RandomWordAug(**self.params)
        elif self.aug_type == "SplitAug":
            if "stopwords" not in self.params:
                self.params["stopwords"] = self.aug_stopwords
            aug = naw.SplitAug(**self.params)
        elif self.aug_type == "OCR":
            if "stopwords" not in self.params:
                self.params["stopwords"] = self.aug_stopwords
            aug = nac.OcrAug(tokenizer=self.split, **self.params)
        elif self.aug_type == "SynonymAug":
            if "stopwords" not in self.params:
                self.params["stopwords"] = self.aug_stopwords
            aug = naw.SynonymAug(**self.params)
        elif self.aug_type == "BackTranslationAug":
            aug = naw.BackTranslationAug(**self.params)
        else:
            raise ValueError(f"Unknown augmentation type: {self.aug_type}")
        return aug

    def augment(self, text):
        """
        Apply the specified augmentation to the input text.

        Args:
            text (str): The text to augment.

        Returns:
            str: The augmented text.

        Raises:
            ValueError: If the augmentation process fails.
        """
        aug = self._get_aug_type()
        augmented_text = aug.augment(text)
        if isinstance(augmented_text, list):
            augmented_text = augmented_text[0]
        return augmented_text

    def serialize(self) -> dict:
        """
        Serialize the augmentation wrapper into a dictionary.

        This includes the augmentation type and its parameters.

        Returns:
            dict: A dictionary representation of the augmentation wrapper.
        """
        init_dict = {
            "aug_type": self.aug_type,
        }
        init_dict.update(self.params)

        return self._serialize(init_dict)