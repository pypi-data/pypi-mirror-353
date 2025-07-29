from nlpaug.augmenter.word import WordAugmenter

from typing import List, Dict
import random


class SynonymsWordAug(WordAugmenter):
    """A word augmenter that substitutes words with their synonyms.

    This augmenter replaces words in the input text with their synonyms, supporting multiple languages
    and allowing custom synonym dictionaries.

    Args:
        name (str, optional): Name of the augmenter. Defaults to "SynonymsWordAug".
        aug_min (int, optional): Minimum number of words to augment. Defaults to 1.
        aug_max (int, optional): Maximum number of words to augment. Defaults to None.
        aug_p (float, optional): Probability of augmenting each word. Defaults to 0.3.
        stopwords (List[str], optional): List of stopwords that should not be augmented. Defaults to None.
        tokenizer (Callable, optional): Tokenizer function to split input text into tokens. Defaults to None.
        reverse_tokenizer (Callable, optional): Function to reverse the tokenization process. Defaults to None.
        device (str, optional): Device to perform augmentation on. Defaults to "cpu".
        verbose (int, optional): Verbosity level. Defaults to 0.
        stopwords_regex (str, optional): Regular expression to identify stopwords. Defaults to None.
        custom_synonyms (Dict[str, List[str]], optional): Dictionary of custom synonyms for substitution.
            Defaults to an empty dictionary.

    Attributes:
        custom_synonyms (Dict[str, List[str]]): Custom synonyms for word substitution.
    """

    def __init__(
        self,
        name="SynonymsWordAug",
        aug_min=1,
        aug_max=None,
        aug_p=0.3,
        stopwords=None,
        tokenizer=None,
        reverse_tokenizer=None,
        device="cpu",
        verbose=0,
        stopwords_regex=None,
        custom_synonyms: Dict[str, List[str]] = dict(),
    ):
        super(SynonymsWordAug, self).__init__(
            action="substitute",
            name=name,
            aug_min=aug_min,
            aug_max=aug_max,
            aug_p=aug_p,
            stopwords=stopwords,
            tokenizer=tokenizer,
            reverse_tokenizer=reverse_tokenizer,
            device=device,
            verbose=0,
            stopwords_regex=stopwords_regex,
        )

        self.custom_synonyms: Dict[str, List[str]] = custom_synonyms

    def _detect_language(self, word: str) -> str:
        """Detects the language of a given word based on its characters.

        Args:
            word (str): The word whose language needs to be detected.

        Returns:
            str: The detected language code ("en" for English, "ru" for Russian).
        """
        english_letters = set("abcdefghijklmnopqrstuvwxyz")
        russian_letters = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")

        is_en = any(letter in english_letters for letter in word.lower())
        is_ru = any(letter in russian_letters for letter in word.lower())

        if is_en and not is_ru:
            return "en"
        elif is_ru and not is_en:
            return "ru"
        else:
            return "ru"

    def _transform(self, token: str) -> str:
        """Transforms a token by substituting it with a random synonym.

        Args:
            token (str): The word to be substituted.

        Returns:
            str: A synonym of the token if available; otherwise, the original token.
        """
        synonyms: list = []
        synonyms.extend(self.custom_synonyms.get(token, []))
        if not synonyms:
            return token

        return random.choice(synonyms)

    def substitute(self, data: str) -> str:
        """Substitutes words in the input data with their synonyms.

        Args:
            data (str): The input text to be augmented.

        Returns:
            str: The augmented text with substituted synonyms.

        Raises:
            ValueError: If the tokenizer is not defined.
        """
        tokens = self.tokenizer(data)
        results = tokens.copy()

        aug_indexes = self._get_random_aug_idxes(tokens)
        if aug_indexes is None:
            return data
        aug_indexes.sort(reverse=True)

        for aug_idx in aug_indexes:
            new_word = self._transform(results[aug_idx])
            results[aug_idx] = new_word

        return self.reverse_tokenizer(results)