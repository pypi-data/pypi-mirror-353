from typing import Dict
import torch.nn as nn
from transformers import AutoModel
from peft import get_peft_model, LoraConfig


class BertModelForClassification(nn.Module):
    """BERT model tailored for classification tasks.

    This class wraps a pre-trained BERT model and adds classification layers on
    top. It supports the integration of LoRA (Low-Rank Adaptation) configurations
    for parameter-efficient fine-tuning and allows freezing of model layers to
    prevent their weights from being updated during training.

    Attributes:
        model_name (str): Path or identifier for the pre-trained BERT model.
        config (Dict): Configuration dictionary containing settings like
            'lora_config', 'freeze_layers', 'dropout_rate', and 'num_labels'.
        bert (nn.Module): The pre-trained BERT model.
        hidden_size (int): The size of the hidden layers in the BERT model.
        pre_classifier (nn.Linear): Linear layer for pre-classification processing.
        dropout (nn.Dropout): Dropout layer for regularization.
        classifier (nn.Linear): Final linear layer for classification output.
    """

    def __init__(self, model_path: str, config: Dict):
        """Initializes the BertModelForClassification instance.

        Args:
            model_path (str): Path or name of the pre-trained BERT model.
            config (Dict): Configuration dictionary for model setup.

        Raises:
            KeyError: If required keys are missing in the config dictionary.
        """
        super().__init__()
        self.model_name = model_path
        self.config = config
        self.bert = AutoModel.from_pretrained(self.model_name)
        self.hidden_size = self.bert.config.hidden_size

        if config["lora_config"]:
            lora_config = LoraConfig(config["lora_config"])
            self.bert = get_peft_model(self.bert, lora_config)

        if config["freeze_layers"]:
            for param in self.bert.parameters():
                param.requires_grad = False

        self.pre_classifier = nn.Linear(self.hidden_size, self.hidden_size)
        self.dropout = nn.Dropout(config["dropout_rate"])
        self.classifier = nn.Linear(self.hidden_size, config["num_labels"])

    def forward(self, input_ids, attention_mask):
        """Performs a forward pass through the model.

        Args:
            input_ids (torch.Tensor): Tensor of input token IDs.
            attention_mask (torch.Tensor): Tensor indicating which tokens should
                be attended to.

        Returns:
            torch.Tensor: The classification logits output by the model.
        """
        output = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        hidden_state = output[0]
        hidden_state = hidden_state[:, 0]
        hidden_state = self.pre_classifier(hidden_state)
        hidden_state = nn.ReLU()(hidden_state)
        hidden_state = self.dropout(hidden_state)
        output = self.classifier(hidden_state)
        return output

    def _count_trainable_params(self):
        """Counts the number of trainable parameters in the model.

        Returns:
            int: The total number of trainable parameters.
        """
        trainable_params = sum(
            p.numel() for p in self.parameters() if p.requires_grad
        )
        return trainable_params