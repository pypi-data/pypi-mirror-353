import random
import torch
from torch.utils.data import Dataset


class TextDatasetAugsOnTheFly(Dataset):
    """A dataset class for text data with on-the-fly augmentations.

    This dataset applies text augmentations dynamically during data retrieval.

    Attributes:
        texts (list): List of text samples.
        labels (list, optional): List of corresponding labels.
        tokenizer: Tokenizer for encoding text.
        max_length (int, optional): Maximum length of tokenized sequences.
        augmenters (list, optional): List of augmentation wrappers.
        aug_p (float, optional): Probability of applying augmentation to each text.
    """

    def __init__(
        self,
        texts,
        labels=None,
        tokenizer=None,
        max_length=None,
        augmenters=None,
        aug_p=0.2,
    ):
        """Initializes the TextDatasetAugsOnTheFly.

        Args:
            texts (list): List of text samples.
            labels (list, optional): List of corresponding labels. Defaults to None.
            tokenizer: Tokenizer for encoding text. Defaults to None.
            max_length (int, optional): Maximum length of tokenized sequences. Defaults to None.
            augmenters (list, optional): List of augmentation wrappers. Defaults to None.
            aug_p (float, optional): Probability of applying augmentation to each text. Defaults to 0.2.
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.augmenters = augmenters or []
        self.aug_p = aug_p

    def __len__(self):
        """Returns the total number of samples in the dataset.

        Returns:
            int: Number of text samples.
        """
        return len(self.texts)

    def __getitem__(self, idx):
        """Retrieves a single data sample.

        Applies augmentation with a probability `aug_p` and tokenizes the text.

        Args:
            idx (int): Index of the sample to retrieve.

        Returns:
            dict: A dictionary containing `input_ids`, `attention_mask`, and optionally `labels`.

        Raises:
            IndexError: If the index is out of range.
            AttributeError: If tokenizer is not provided.
        """
        text = self.texts[idx]

        if self.augmenters and random.random() < self.aug_p:
            augmenter = random.choice(self.augmenters)
            text = augmenter.augment(text)
            if isinstance(text, list):
                text = text[0]

        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        item = {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
        }

        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)

        return item


class TextDataset(Dataset):
    """A dataset class for text data with optional preprocessing and augmentation.

    This dataset pre-generates augmented texts and tokenizes all samples during initialization.

    Attributes:
        texts (list): List of text samples.
        labels (list, optional): List of corresponding labels.
        tokenizer: Tokenizer for encoding text.
        max_length (int, optional): Maximum length of tokenized sequences.
        augmenters (list, optional): List of augmentation wrappers.
        aug_p (float, optional): Probability of applying augmentation to each text.
        tokenized_texts (list): List of tokenized text samples.
    """

    def __init__(
        self,
        texts,
        labels=None,
        tokenizer=None,
        max_length=None,
        augmenters=None,
        aug_p=0.2,
    ):
        """Initializes the TextDataset.

        Args:
            texts (list): List of text samples.
            labels (list, optional): List of corresponding labels. Defaults to None.
            tokenizer: Tokenizer for encoding text. Defaults to None.
            max_length (int, optional): Maximum length of tokenized sequences. Defaults to None.
            augmenters (list, optional): List of augmentation wrappers from the nlpaug library. Defaults to None.
            aug_p (float, optional): Probability of applying augmentation to each text. Defaults to 0.2.

        Raises:
            AttributeError: If tokenizer is not provided.
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.augmenters = augmenters or []
        self.aug_p = aug_p

        if self.augmenters:
            # Generate original and augmented texts
            self.texts, self.labels = self._generate_augmented_texts(
                self.texts, self.labels
            )

        # Pre-tokenize the entire dataset
        self.tokenized_texts = self._tokenize_texts(self.texts)

    def _apply_augmentations(self, text):
        """Applies all augmenters to the given text if any are specified.

        Args:
            text (str): The text to augment.

        Returns:
            list: A list containing the original and augmented texts.
        """
        augmented_texts = [text]
        if self.augmenters:
            for aug in self.augmenters:
                augmented_texts.append(aug.augment(text))
        return augmented_texts

    def _generate_augmented_texts(self, texts, labels):
        """Generates a list of texts and labels, including original and augmented samples.

        Args:
            texts (list): Original list of text samples.
            labels (list): Original list of labels.

        Returns:
            tuple: A tuple containing the new list of texts and the corresponding labels.
        """
        all_texts = []
        all_labels = []
        for text, label in zip(texts, labels):
            if random.random() < self.aug_p:
                augmented_texts = self._apply_augmentations(text)
                all_texts.extend(augmented_texts)
                all_labels.extend([label] * len(augmented_texts))
            else:
                # Add text and label without augmentation
                all_texts.append(text)
                all_labels.append(label)
        return all_texts, all_labels

    def _tokenize_texts(self, texts):
        """Tokenizes all texts in the dataset.

        Args:
            texts (list): List of text samples to tokenize.

        Returns:
            list: A list of dictionaries containing `input_ids` and `attention_mask` for each sample.

        Raises:
            AttributeError: If tokenizer is not provided.
        """
        tokenized_texts = []
        for text in texts:
            encoding = self.tokenizer.encode_plus(
                text,
                add_special_tokens=True,
                max_length=self.max_length,
                padding="max_length",
                truncation=True,
                return_attention_mask=True,
                return_tensors="pt",
            )
            tokenized_texts.append(
                {
                    "input_ids": encoding["input_ids"].squeeze(0),
                    "attention_mask": encoding["attention_mask"].squeeze(0),
                }
            )
        return tokenized_texts

    def __len__(self):
        """Returns the total number of samples in the dataset.

        Returns:
            int: Number of text samples.
        """
        return len(self.texts)

    def __getitem__(self, idx):
        """Retrieves a single tokenized data sample.

        Args:
            idx (int): Index of the sample to retrieve.

        Returns:
            dict: A dictionary containing `input_ids`, `attention_mask`, and optionally `labels`.

        Raises:
            IndexError: If the index is out of range.
        """
        tokenized_data = self.tokenized_texts[idx]

        item = {
            "input_ids": tokenized_data["input_ids"],
            "attention_mask": tokenized_data["attention_mask"],
        }

        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)

        return item