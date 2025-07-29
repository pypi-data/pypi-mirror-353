# -*- coding: utf-8 -*-

import argparse
import torch
import torch.nn as nn
import numpy as np

from transformers import AutoTokenizer, AutoModelForTokenClassification

# Прогнозируемые знаки препинания
PUNK_MAPPING = {".": "PERIOD", ",": "COMMA", "?": "QUESTION"}

# Прогнозируемый регистр LOWER - нижний регистр, UPPER - верхний регистр для первого символа,
# UPPER_TOTAL - верхний регистр для всех символов
LABELS_CASE = ["LOWER", "UPPER", "UPPER_TOTAL"]
# Добавим в пунктуацию метку O означающий отсутсвие пунктуации
LABELS_PUNC = ["O"] + list(PUNK_MAPPING.values())

# Сформируем метки на основе комбинаций регистра и пунктуации
LABELS_list = []
for case in LABELS_CASE:
    for punc in LABELS_PUNC:
        LABELS_list.append(f"{case}_{punc}")
LABELS = {label: i + 1 for i, label in enumerate(LABELS_list)}
LABELS["O"] = -100
INVERSE_LABELS = {i: label for label, i in LABELS.items()}

LABEL_TO_PUNC_LABEL = {
    label: label.split("_")[-1] for label in LABELS.keys() if label != "O"
}
LABEL_TO_CASE_LABEL = {
    label: "_".join(label.split("_")[:-1]) for label in LABELS.keys() if label != "O"
}


def token_to_label(token, label):
    """
    Converts a token and its label into a punctuated token based on the label.

    Args:
        token (str): The input token.
        label (str or int): The label indicating punctuation and casing. Can be a string label or its corresponding integer.

    Returns:
        str: The token with appropriate punctuation and casing applied.

    Raises:
        None
    """
    if type(label) == int:
        label = INVERSE_LABELS[label]
    if label == "LOWER_O":
        return token
    if label == "LOWER_PERIOD":
        return token + "."
    if label == "LOWER_COMMA":
        return token + ","
    if label == "LOWER_QUESTION":
        return token + "?"
    if label == "UPPER_O":
        return token.capitalize()
    if label == "UPPER_PERIOD":
        return token.capitalize() + "."
    if label == "UPPER_COMMA":
        return token.capitalize() + ","
    if label == "UPPER_QUESTION":
        return token.capitalize() + "?"
    if label == "UPPER_TOTAL_O":
        return token.upper()
    if label == "UPPER_TOTAL_PERIOD":
        return token.upper() + "."
    if label == "UPPER_TOTAL_COMMA":
        return token.upper() + ","
    if label == "UPPER_TOTAL_QUESTION":
        return token.upper() + "?"
    if label == "O":
        return token


def decode_label(label, classes="all"):
    """
    Decodes an integer label into its corresponding string representation.

    Args:
        label (int): The integer label to decode.
        classes (str, optional): Specifies the type of label to decode. 
                                 Options are "all" (default), "punc" for punctuation, or "case" for casing.

    Returns:
        str: The decoded label based on the specified class.

    Raises:
        KeyError: If the label does not exist in the inverse label mapping.
    """
    if classes == "punc":
        return LABEL_TO_PUNC_LABEL[INVERSE_LABELS[label]]
    if classes == "case":
        return LABEL_TO_CASE_LABEL[INVERSE_LABELS[label]]
    else:
        return INVERSE_LABELS[label]


MODEL_REPO = "kontur-ai/sbert_punc_case_ru"


class SbertPuncCase(nn.Module):
    """
    A neural network model for restoring punctuation and case in text using SBERT.

    This model utilizes a pretrained SBERT tokenizer and token classification model to predict punctuation and casing for each token in the input text.

    Attributes:
        tokenizer (AutoTokenizer): The tokenizer used for preprocessing input text.
        model (AutoModelForTokenClassification): The pretrained token classification model.
    """

    def __init__(self):
        """
        Initializes the SbertPuncCase model by loading the tokenizer and the pretrained token classification model.
        """
        super().__init__()

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_REPO, strip_accents=False)
        self.model = AutoModelForTokenClassification.from_pretrained(MODEL_REPO)
        self.model.eval()

    def forward(self, input_ids, attention_mask):
        """
        Performs a forward pass through the token classification model.

        Args:
            input_ids (torch.Tensor): Tensor of input token IDs.
            attention_mask (torch.Tensor): Tensor indicating which tokens should be attended to.

        Returns:
            transformers.modeling_outputs.TokenClassificationOutput: The output of the token classification model.

        Raises:
            None
        """
        return self.model(input_ids=input_ids, attention_mask=attention_mask)

    def punctuate(self, text):
        """
        Restores punctuation and casing in the input text.

        Processes the input text by tokenizing, predicting punctuation and casing labels, and reconstructing the punctuated text.

        Args:
            text (str): The input text to restore punctuation and case.

        Returns:
            str: The restored text with appropriate punctuation and casing.

        Raises:
            None
        """
        text = text.strip().lower()

        # Разобьем предложение на слова
        words = text.split()

        tokenizer_output = self.tokenizer(words, is_split_into_words=True)

        if len(tokenizer_output.input_ids) > 512:
            return " ".join(
                [
                    self.punctuate(" ".join(text_part))
                    for text_part in np.array_split(words, 2)
                ]
            )

        predictions = (
            self(
                torch.tensor([tokenizer_output.input_ids], device=self.model.device),
                torch.tensor(
                    [tokenizer_output.attention_mask], device=self.model.device
                ),
            )
            .logits.cpu()
            .data.numpy()
        )
        predictions = np.argmax(predictions, axis=2)

        # decode punctuation and casing
        splitted_text = []
        word_ids = tokenizer_output.word_ids()
        for i, word in enumerate(words):
            label_pos = word_ids.index(i)
            label_id = predictions[0][label_pos]
            label = decode_label(label_id)
            splitted_text.append(token_to_label(word, label))
        capitalized_text = " ".join(splitted_text)
        return capitalized_text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Punctuation and case restoration model sbert_punc_case_ru"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="text to restore",
        default="sbert punc case расставляет точки запятые и знаки вопроса вам нравится",
    )
    parser.add_argument(
        "-d",
        "--device",
        type=str,
        help="run model on cpu or gpu",
        choices=["cpu", "cuda"],
        default="cpu",
    )
    args = parser.parse_args()
    print(f"Source text:   {args.input}\n")
    sbertpunc = SbertPuncCase().to(args.device)
    punctuated_text = sbertpunc.punctuate(args.input)
    print(f"Restored text: {punctuated_text}")