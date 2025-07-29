import os
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
from copy import deepcopy
import pandas as pd
import numpy as np
from nltk.tokenize import sent_tokenize
import torch
from sentence_transformers import SentenceTransformer
from dreamml.utils import sbertpunccase as sbert_punct
from dreamml.configs.config_storage import ConfigStorage
from dreamml.data._transformer import DataTransformer
from dreamml.logging import get_logger

tqdm.pandas(desc="Preprocessing")

BAD_PHRASES_PATH = Path(__file__).parent.parent / "references/bad_phrases_clean.csv"

_logger = get_logger(__name__)


class PhraseRetrieval:
    """
    A class to retrieve and process phrases from datasets, identify bad phrases,
    and manage their embeddings and scores.

    Attributes:
        config (Dict): Configuration parameters.
        device (str): Device to run the model on.
        e5_model (SentenceTransformer): Sentence transformer model for embeddings.
        punct_model (SbertPuncCase or None): Model to restore punctuation.
        data (pd.DataFrame): Dataframe containing dialog data.
        bad_phrases (List[str]): List of bad phrases.
        result_df (pd.DataFrame): Dataframe containing retrieval results.
    """

    def __init__(self, config: Dict):
        """
        Initializes the PhraseRetrieval instance with the given configuration.

        Args:
            config (Dict): A dictionary containing configuration parameters.

        Raises:
            KeyError: If 'e5_model_path' is not found in the configuration.
        """
        self.config = config
        self.device = self.config.get(
            "device", "cuda:0" if torch.cuda.is_available() else "cpu"
        )
        self.e5_model = SentenceTransformer(
            self.config["e5_model_path"], device=self.device
        )

        if self.config.get("punct_model_repo"):
            sbert_punct.MODEL_REPO = self.config["punct_model_repo"]
            self.punct_model = sbert_punct.SbertPuncCase().to(self.device)
        else:
            self.punct_model = None

    def load_datasets(self):
        """
        Loads datasets from the filesystem or Hadoop based on the configuration.

        This method retrieves dialog data and bad phrases, storing them in
        self.data and self.bad_phrases respectively.

        Raises:
            KeyError: If required keys are missing in the configuration.
            FileNotFoundError: If the specified data paths do not exist.
            Exception: For any other issues during data loading.
        """
        task = self.config.get("task", "phrase_retrieval")
        dialog_id_col = self.config.get("dialog_id_col", "dialog_id")
        text_col = self.config.get("text_col", "PraseText")
        phrase_col = self.config.get("phrase_col", "Фраза")

        dialog_path = self.config["dialog_path"]
        bad_phrases_path = self.config.get("bad_phrases_path", None)

        if bad_phrases_path is None:
            bad_phrases_path = str(BAD_PHRASES_PATH)

        config = {
            "pipeline.task": task,
            "data.dev_path": dialog_path,
            "data.oot_path": bad_phrases_path,
        }
        config_storage = ConfigStorage(config)
        transformer = DataTransformer(config_storage)
        data_dict = transformer._get_data()

        self.data = data_dict["dev"][[dialog_id_col, text_col]]
        self.data.columns = ["dialog_id", "text"]
        self.bad_phrases = data_dict["oot"][phrase_col].tolist()

    def restore_punctuation(self):
        """
        Restores punctuation in the text data if a punctuation model is specified.

        Applies the punctuation model to the 'text' column and stores the
        result in a new 'punct_text' column. If no punctuation model is
        specified, 'punct_text' is identical to 'text'.

        Raises:
            AttributeError: If the punctuation model is improperly configured.
            Exception: For any other issues during punctuation restoration.
        """
        if self.punct_model:
            self.data["punct_text"] = self.data["text"].progress_apply(
                lambda x: self.punct_model.punctuate(x)
            )
        else:
            self.data["punct_text"] = self.data[
                "text"
            ]  # If punctuation model is not specified, use original text

    def text_to_sentences_df(self, min_length) -> pd.DataFrame:
        """
        Splits text into sentences and merges short sentences.

        Converts the 'punct_text' column into individual sentences, ensuring each
        sentence meets the minimum length requirement by merging shorter sentences.

        Args:
            min_length (int): The minimum length of sentences after merging.

        Returns:
            pd.DataFrame: A dataframe with 'dialog_id' and 'sentence' columns.

        Raises:
            ValueError: If min_length is not a positive integer.
            Exception: For any issues during sentence tokenization or merging.
        """
        sent_tokenize_lang = self.config.get("sent_tokenize_lang", "russian")
        all_sents = (
            self.data["punct_text"]
            .progress_apply(
                lambda x: [s for s in sent_tokenize(x, language=sent_tokenize_lang)]
            )
            .to_list()
        )
        all_sents = [
            self.merge_short_sentences(dialog_sents, min_length)
            for dialog_sents in all_sents
        ]

        lengths = [len(sents) for sents in all_sents]
        d_ids = [
            d_id for (d_id, l) in zip(self.data["dialog_id"], lengths) for i in range(l)
        ]

        all_sents = [sent for sents in all_sents for sent in sents]  # Flatten
        return pd.DataFrame({"dialog_id": d_ids, "sentence": all_sents})

    @staticmethod
    def merge_short_sentences(sentences: List[str], min_length: int) -> List[str]:
        """
        Merges short sentences to ensure each sentence meets the minimum length.

        Iterates through the list of sentences, combining consecutive sentences
        until the combined length is at least min_length.

        Args:
            sentences (List[str]): A list of sentences to be merged.
            min_length (int): The minimum length required for each merged sentence.

        Returns:
            List[str]: A list of sentences where each sentence meets the minimum length.

        Raises:
            ValueError: If min_length is not a positive integer.
        """
        merged_sents = []
        i = 0

        while i < len(sentences):
            s = sentences[i]
            if len(s) >= min_length:
                merged_sents.append(s)
                i += 1
                continue
            while len(s) < min_length and i < len(sentences) - 1:
                s += " " + sentences[i + 1]
                i += 1
            merged_sents.append(s)
            i += 1
        return merged_sents

    def get_query_embs(self, phrases: List[str], batch_size: int = 64) -> np.ndarray:
        """
        Generates embeddings for a list of phrases.

        Utilizes the sentence transformer model to encode phrases into
        their corresponding embedding vectors.

        Args:
            phrases (List[str]): A list of phrases to encode.
            batch_size (int, optional): The number of phrases to encode per batch.
                Defaults to 64.

        Returns:
            np.ndarray: An array of embedding vectors for the provided phrases.

        Raises:
            ValueError: If phrases list is empty.
            Exception: For any issues during the encoding process.
        """
        return self.e5_model.encode(
            ["query: " + s for s in phrases], batch_size=batch_size
        )

    def get_scores(
        self, all_sents: List[str], ph_embs: np.ndarray, batch_size: int = 512
    ) -> np.ndarray:
        """
        Calculates cosine similarities between sentences and phrase embeddings.

        Encodes all sentences and computes the cosine similarity scores between
        each sentence and each phrase embedding.

        Args:
            all_sents (List[str]): A list of sentences to compare.
            ph_embs (np.ndarray): An array of phrase embeddings.
            batch_size (int, optional): The number of sentences to encode per batch.
                Defaults to 512.

        Returns:
            np.ndarray: A matrix of cosine similarity scores.

        Raises:
            ValueError: If inputs are of incompatible dimensions.
            Exception: For any issues during the encoding or computation process.
        """
        return (
            self.e5_model.encode(
                ["query: " + s for s in all_sents], batch_size=batch_size
            )
            @ ph_embs.T
        )

    def phrases_retrieve(
        self, sents_df: pd.DataFrame, scores: pd.DataFrame, threshold: float = 0.9
    ) -> pd.DataFrame:
        """
        Retrieves sentences that are similar to any of the bad phrases.

        Filters sentences based on the provided threshold and associates them
        with the corresponding bad phrases.

        Args:
            sents_df (pd.DataFrame): Dataframe containing 'dialog_id' and 'sentence'.
            scores (pd.DataFrame): Dataframe containing similarity scores with phrases.
            threshold (float, optional): The minimum similarity score to consider a match.
                Defaults to 0.9.

        Returns:
            pd.DataFrame: A dataframe with matched sentences, their scores, and the phrases.

        Raises:
            ValueError: If threshold is not between 0 and 1.
            Exception: For any issues during the retrieval process.
        """
        result_df = pd.DataFrame()
        for phrase in tqdm(self.bad_phrases, desc="Phrase"):
            top_scores = scores.loc[scores[phrase] > threshold, phrase]
            tmp = sents_df.loc[top_scores.index]
            tmp["score"] = top_scores
            tmp["phrase"] = phrase
            result_df = pd.concat([result_df, tmp])
        return result_df

    def fit(self):
        """
        Executes the data loading and punctuation restoration steps.

        This method prepares the data by loading the datasets and restoring
        punctuation if a punctuation model is specified.

        Raises:
            Exception: If any step during fitting fails.
        """
        self.load_datasets()
        self.restore_punctuation()

    def transform(
        self,
        threshold: float = None,
        min_length: int = None,
        batch_size_phrases: int = None,
        batch_size_dialogs: int = None,
    ) -> pd.DataFrame:
        """
        Transforms text data into embeddings and identifies matches with bad phrases.

        Performs sentence tokenization, embedding generation, similarity scoring,
        and retrieval of sentences matching bad phrases.

        Args:
            threshold (float, optional): The similarity threshold for matching phrases.
                Defaults to the value in config or 0.9.
            min_length (int, optional): The minimum sentence length after merging.
                Defaults to the value in config or 20.
            batch_size_phrases (int, optional): Batch size for encoding phrases.
                Defaults to the value in config or 512.
            batch_size_dialogs (int, optional): Batch size for encoding dialog sentences.
                Defaults to the value in config or 64.

        Returns:
            pd.DataFrame: A dataframe containing sentences that match bad phrases.

        Raises:
            ValueError: If any of the parameters are invalid.
            Exception: For any issues during the transformation process.
        """
        threshold = (
            self.config.get("threshold", 0.9) if threshold is None else threshold
        )
        min_length = (
            self.config.get("min_length", 20) if min_length is None else min_length
        )
        batch_size_phrases = (
            self.config.get("batch_size_phrases", 512)
            if batch_size_phrases is None
            else batch_size_phrases
        )
        batch_size_dialogs = (
            self.config.get("batch_size_dialogs", 64)
            if batch_size_dialogs is None
            else batch_size_dialogs
        )

        all_sents_df = self.text_to_sentences_df(min_length=min_length)
        phrases_embs = self.get_query_embs(
            self.bad_phrases, batch_size=batch_size_phrases
        )

        # Compute cosine similarity scores
        scores = pd.DataFrame(
            self.get_scores(
                all_sents_df["sentence"].tolist(),
                phrases_embs,
                batch_size=batch_size_dialogs,
            )
        )
        scores.columns = self.bad_phrases

        # Retrieve sentences containing bad phrases
        self.result_df = self.phrases_retrieve(
            all_sents_df, scores, threshold=threshold
        )

        params = {
            "threshold": threshold,
            "min_length": min_length,
            "batch_size_phrases": batch_size_phrases,
            "batch_size_dialogs": batch_size_dialogs,
        }

        _logger.debug(f"Phrase Retrieval config: {self.config}")
        _logger.debug(f"Transform params: {params}")

        return self.result_df

    def get_top_dialogs(self, top_n: int = 10, unique=True) -> pd.DataFrame:
        """
        Retrieves the top N dialogs based on similarity scores.

        Sorts the result dataframe by score in descending order and selects
        the top N dialogs. If unique is True, ensures that each dialog_id
        is unique in the result.

        Args:
            top_n (int, optional): The number of top dialogs to retrieve. Defaults to 10.
            unique (bool, optional): Whether to ensure unique dialog_ids in the result.
                Defaults to True.

        Returns:
            pd.DataFrame: A dataframe containing the top N dialogs based on scores.

        Raises:
            ValueError: If top_n is not a positive integer.
            Exception: For any issues during the retrieval process.
        """
        result_df = deepcopy(self.result_df)

        result_df.sort_values(by="score", ascending=False, inplace=True)
        result_df.reset_index(drop=True, inplace=True)

        if unique:
            result_df.drop_duplicates(subset=["dialog_id"], keep="first", inplace=True)
            top_unique_dialogs = result_df["dialog_id"].head(top_n)
            result_df = result_df[result_df["dialog_id"].isin(top_unique_dialogs)]
        else:
            result_df = result_df.head(n=top_n)

        return result_df