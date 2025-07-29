from pathlib import Path
from tqdm.auto import tqdm
from collections import Counter
from typing import List
import pandas as pd
from nltk.corpus import stopwords
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

from dreamml.logging import get_logger
from dreamml.features.text.transformers.depersonalizer import Depersonalizer
from dreamml.features.text.transformers.digit_eraser import DigitEraser
from dreamml.features.text.transformers.punctuation_eraser import PunctuationEraser
from dreamml.features.text.transformers.word_filter import WordFilter
from dreamml.features.text.transformers.word_joiner import WordJoiner
from dreamml.features.text.transformers.word_normalizer import WordNormalizer
from dreamml.features.text.transformers.word_splitter import WordSplitter
from dreamml.features.text.transformers.word_synonyms import WordSynonyms
from dreamml.features.text.transformers.text_cleaner import TextCleaner
from dreamml.utils.loading_utils import load_yaml
from dreamml.utils.serialize import Serializable

tqdm.pandas()

_logger = get_logger(__name__)

SYNONYMS_PATH = Path(__file__).parent.parent.parent / "references/synonyms.yaml"
STANDARD_STOPWORDS_PATH = (
    Path(__file__).parent.parent.parent / "references/standard_stopwords.yaml"
)
RUSSIAN_NAMES_SURNAMES_PATH = (
    Path(__file__).parent.parent.parent / "references/russian_names_surnames_adj.yaml"
)


class CounterTransformer:
    """A transformer that counts token occurrences and filters tokens based on frequency and stopwords.

    Attributes:
        stopwords (list): Combined list of English and Russian stopwords from NLTK.
        fitted (bool): Indicator whether the transformer has been fitted.
        counts (Counter): Counter object storing token frequencies after fitting.
    """

    stopwords = stopwords.words("english") + stopwords.words("russian")

    def __init__(self):
        """Initializes the CounterTransformer.

        Sets the fitted flag to False.
        """
        self.fitted = False

    def fit(self, data: List[List[str]]):
        """Fits the transformer by counting token occurrences in the provided data.

        Args:
            data (List[List[str]]): A list of tokenized text data.

        Returns:
            None
        """
        self.counts = Counter([v for t in data for v in t])
        self.fitted = True

    def transform(self, data: List[List[str]], threshold: int = 1) -> List[List[str]]:
        """Transforms the data by filtering out tokens that occur more than the threshold and are not stopwords.

        Args:
            data (List[List[str]]): A list of tokenized text data to transform.
            threshold (int, optional): The frequency threshold for filtering tokens. Defaults to 1.

        Returns:
            List[List[str]]: The transformed data with filtered tokens.
        """
        new_tokens = []
        for sample in data:
            sample_list = []
            for token in sample:
                if (
                    threshold is not None and self.counts[token] > threshold
                ) and token not in self.stopwords:
                    sample_list.append(token)
            new_tokens.append(sample_list)
        return new_tokens


class TextFeaturesTransformer(BaseEstimator, TransformerMixin, Serializable):
    """A transformer for preprocessing and transforming text features in a dataset.

    This transformer applies a series of text preprocessing steps defined by the
    `text_preprocessing_params` and integrates them into a scikit-learn Pipeline.

    Attributes:
        text_features (list): List of text feature column names to preprocess.
        text_features_preprocessed (list): List of preprocessed text feature column names.
        text_preprocessing_params (dict): Parameters defining which preprocessing steps to apply.
        additional_stopwords (list): List of additional stopwords to filter out.
        verbose (bool): If True, the pipeline will output verbose logs.
        standard_stopwords (list): Standard stopwords loaded from a YAML file.
        file_synonyms (dict): Synonyms loaded from a YAML file.
        rus_names_dict (dict): Russian names and surnames loaded from a YAML file.
        preprocessing_pipeline (Pipeline): The constructed preprocessing pipeline.
    """

    def __init__(
        self,
        text_features,
        text_preprocessing_params,
        additional_stopwords,
        verbose=False,
    ):
        """
        Initializes the TextFeaturesTransformer.

        Args:
            text_features (list): List of text feature column names to preprocess.
            text_preprocessing_params (dict): Parameters defining which preprocessing steps to apply.
            additional_stopwords (list): List of additional stopwords to filter out.
            verbose (bool, optional): If True, the pipeline will output verbose logs. Defaults to False.
        """
        self.text_features = text_features
        self.text_features_preprocessed = []
        self.text_preprocessing_params = text_preprocessing_params
        self.additional_stopwords = additional_stopwords
        self.verbose = verbose
        # ---
        self.standard_stopwords = load_yaml(STANDARD_STOPWORDS_PATH)
        self.file_synonyms = load_yaml(SYNONYMS_PATH)
        self.rus_names_dict = load_yaml(RUSSIAN_NAMES_SURNAMES_PATH)
        # ---
        self.preprocessing_pipeline = self.create_pipeline(text_preprocessing_params)

    def fit(self, X, y=None):
        """
        Fits the transformer. As this transformer does not require fitting, it returns itself.

        Args:
            X (pd.DataFrame): Input data.
            y (optional): Target variable. Defaults to None.

        Returns:
            TextFeaturesTransformer: The fitted transformer.
        """
        return self

    def transform(self, data: pd.DataFrame):
        """
        Transforms the input DataFrame by applying the preprocessing pipeline to the specified text features.

        Args:
            data (pd.DataFrame): The input data containing text features to preprocess.

        Returns:
            pd.DataFrame: The DataFrame with preprocessed text features added.
        """
        preproc_feature_name = f"{self.text_features[0]}_preprocessed"
        data[preproc_feature_name] = data[self.text_features[0]].copy()

        if preproc_feature_name not in self.text_features_preprocessed:
            self.text_features_preprocessed.append(preproc_feature_name)

        if isinstance(self.preprocessing_pipeline, Pipeline):
            data[preproc_feature_name] = self.preprocessing_pipeline.fit_transform(
                data[preproc_feature_name]
            )

        return data

    def create_pipeline(self, params):
        """
        Creates a text preprocessing pipeline based on the provided parameters.

        Args:
            params (dict): Parameters defining which preprocessing steps to include.

        Returns:
            Pipeline or None: The constructed preprocessing pipeline or None if no steps are specified.
        """
        if params is None:
            return None

        # Check if text processing parameters are enabled
        steps = []
        if params.get("depersonalizer", False):
            steps.append(
                ("depersonalizer", Depersonalizer(rus_names_dict=self.rus_names_dict))
            )
        if params.get("text_cleaner", False):
            steps.append(("text_cleaner", TextCleaner()))
        if params.get("digit_eraser", False):
            steps.append(("digit_eraser", DigitEraser()))
        if params.get("punct_eraser", False):
            steps.append(("punct_eraser", PunctuationEraser()))

        # Process word_pipeline
        word_pipeline_params = params.get("word_pipeline", {})
        word_steps = []

        if any(word_pipeline_params.values()):  # Check if any word_pipeline steps are enabled
            # Add mandatory steps: word_splitter and word_joiner
            word_steps.append(("word_splitter", WordSplitter()))  # First step
            if word_pipeline_params.get("word_normalizer", False):
                word_steps.append(("word_normalizer", WordNormalizer()))
            if word_pipeline_params.get("word_standard_stopwords", False):
                word_steps.append(
                    (
                        "word_standard_stopwords",
                        WordFilter(stop_words=set(self.standard_stopwords)),
                    )
                )
            if word_pipeline_params.get("word_additional_stopwords", False):
                word_steps.append(
                    (
                        "word_additional_stopwords",
                        WordFilter(stop_words=set(self.additional_stopwords)),
                    )
                )
            if word_pipeline_params.get("word_synonyms", False):
                word_steps.append(
                    ("word_synonyms", WordSynonyms(synonyms=self.file_synonyms))
                )
            word_steps.append(("word_joiner", WordJoiner()))  # Last step

            # Add word_pipeline to the main Pipeline
            steps.append(("word_pipeline", Pipeline(word_steps)))

        if not steps:
            return None

        # Create the final Pipeline
        return Pipeline(steps, verbose=self.verbose)

    def serialize(self) -> dict:
        """
        Serializes the transformer into a dictionary.

        Returns:
            dict: A dictionary representation of the transformer, including initialization parameters and additional data.
        """
        init_dict = {
            "text_features": self.text_features,
            "text_preprocessing_params": self.text_preprocessing_params,
            "additional_stopwords": self.additional_stopwords,
            "verbose": self.verbose,
        }

        additional_dict = {
            "text_features_preprocessed": self.text_features_preprocessed,
        }

        return self._serialize(init_data=init_dict, additional_data=additional_dict)

    @classmethod
    def deserialize(cls, data):
        """
        Deserializes the transformer from a dictionary.

        Args:
            data (dict): The serialized transformer data.

        Returns:
            TextFeaturesTransformer: The deserialized transformer instance.
        """
        instance = cls._deserialize(data)

        instance.text_features_preprocessed = data["additional"][
            "text_features_preprocessed"
        ]

        return instance