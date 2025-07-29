from typing import Optional

import torch
from torch import nn
from torch.optim import AdamW, Adam, SGD, RMSprop
from torch.optim.lr_scheduler import (
    ExponentialLR,
    StepLR,
    ReduceLROnPlateau,
    OneCycleLR,
    CyclicLR,
    CosineAnnealingLR,
)
from torch.utils.data import (
    RandomSampler,
    SequentialSampler,
    SubsetRandomSampler,
    WeightedRandomSampler,
)
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup,
)

from dreamml.utils.make_weights_for_balanced_classes import (
    make_weights_for_balanced_classes,
)


# Service functions for transformers.AutoModelForSequenceClassification
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def load_tokenizer(model_name_or_path: str, max_len: int):
    """Load a tokenizer from a pre-trained model or a specified path.

    Args:
        model_name_or_path (str): The name of the pre-trained model or the path to the tokenizer directory.
        max_len (int): The maximum length for tokenization. Sequences longer than this will be truncated, and shorter ones will be padded.

    Returns:
        AutoTokenizer: The loaded tokenizer instance.

    Raises:
        ValueError: If the tokenizer cannot be loaded from the specified path or model name.
    """
    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path,
        truncation=True,
        padding="max_length",
        max_length=max_len,
    )
    return tokenizer


def load_model(
    model_name_or_path: str, num_labels: int, output_hidden_states: bool = True
):
    """Load a pre-trained model for sequence classification.

    Args:
        model_name_or_path (str): The name of the pre-trained model or the path to the model directory.
        num_labels (int): The number of labels for the classification task.
        output_hidden_states (bool, optional): Whether to output hidden states. Defaults to True.

    Returns:
        AutoModelForSequenceClassification: The loaded model instance.

    Raises:
        ValueError: If the model cannot be loaded from the specified path or model name.
    """
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name_or_path,
        num_labels=num_labels,
        output_hidden_states=output_hidden_states,
    )
    return model


def unfreeze_model_layers(model, unfreeze_layers: str = "all"):
    """Unfreeze specific layers of the model for training.

    Args:
        model: The model whose layers are to be unfrozen.
        unfreeze_layers (str, optional): Specifies which layers to unfreeze. Options are:
            - "all": Unfreeze all layers.
            - "classifier": Unfreeze only the classifier layers.
            - "classifier_and_pooler": Unfreeze classifier and pooler layers.
            - "last_X": Unfreeze the last X encoder layers (e.g., "last_2").
            Defaults to "all".

    Returns:
        The model with the specified layers unfrozen.

    Raises:
        ValueError: If the specified unfreeze_layers option is invalid.
    """
    if unfreeze_layers == "classifier":
        for name, param in model.bert.named_parameters():
            if "classifier" in name:
                param.requires_grad = True
            else:
                param.requires_grad = False

    if unfreeze_layers == "classifier_and_pooler":
        for name, param in model.bert.named_parameters():
            if "classifier" in name or "pooler" in name:
                param.requires_grad = True
            else:
                param.requires_grad = False

    elif unfreeze_layers.startswith("last_"):
        try:
            n_layers = int(unfreeze_layers.split("_")[1])
        except (IndexError, ValueError):
            raise ValueError(
                f"Invalid format for unfreeze_layers: {unfreeze_layers}. Expected format 'last_X' where X is an integer."
            )
        for name, param in model.bert.named_parameters():
            if "classifier" in name or "pooler" in name:
                param.requires_grad = True

            elif "encoder.layer" in name:
                layer_num = int(name.split(".")[3])
                if layer_num >= 12 - n_layers:
                    param.requires_grad = True
                param.requires_grad = False
            else:
                param.requires_grad = False

    elif unfreeze_layers == "all":
        for param in model.bert.parameters():
            param.requires_grad = True

    else:
        raise ValueError(f"Invalid unfreeze_layers option: {unfreeze_layers}")

    return model


def get_loss_function(loss_type: str, reduction: Optional[str] = None):
    """Retrieve the loss function based on the specified type.

    Args:
        loss_type (str): The type of loss function. Options include:
            - "logloss"
            - "cross-entropy"
            - "mse"
            - "mae"
            - "bce"
        reduction (Optional[str], optional): Specifies the reduction to apply to the output. Defaults to None.

    Returns:
        nn.Module: The corresponding loss function.

    Raises:
        ValueError: If the specified loss_type is unknown or unsupported.
    """
    if loss_type == "logloss":
        return nn.CrossEntropyLoss()
    elif loss_type == "cross-entropy":
        return nn.CrossEntropyLoss()
    elif loss_type == "mse":
        if reduction:
            return nn.MSELoss(reduction=reduction)
        return nn.MSELoss()
    elif loss_type == "mae":
        if reduction:
            return nn.L1Loss(reduction=reduction)
        return nn.L1Loss()
    elif loss_type == "bce":
        return nn.BCELoss()
    else:
        raise ValueError(f"Unknown loss function type: {loss_type}")


def get_optimizer(model, learning_rate, optimizer_type: str, weight_decay: float):
    """Retrieve the optimizer based on the specified type.

    Args:
        model: The model parameters to optimize.
        learning_rate: The learning rate for the optimizer.
        optimizer_type (str): The type of optimizer. Options include:
            - "adamw"
            - "adam"
            - "sgd"
            - "rmsprop"
        weight_decay (float): The weight decay (L2 penalty) coefficient.

    Returns:
        torch.optim.Optimizer: The corresponding optimizer instance.

    Raises:
        ValueError: If the specified optimizer_type is unknown or unsupported.
    """
    if optimizer_type == "adamw":
        return AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    elif optimizer_type == "adam":
        return Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    elif optimizer_type == "sgd":
        return SGD(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    elif optimizer_type == "rmsprop":
        return RMSprop(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    else:
        raise ValueError(f"Unknown optimizer type: {optimizer_type}")


def get_scheduler(
    optimizer, scheduler_type: str, optimizer_type: str, total_steps: int
):
    """Retrieve the learning rate scheduler based on the specified type.

    Args:
        optimizer (torch.optim.Optimizer): The optimizer for which to schedule the learning rate.
        scheduler_type (str): The type of scheduler. Options include:
            - "linear"
            - "exponential"
            - "step"
            - "reduce_on_plateau"
            - "one_cycle_lr"
            - "cyclic_lr"
            - "cosine"
        optimizer_type (str): The type of optimizer being used. Needed for certain scheduler configurations.
        total_steps (int): The total number of training steps.

    Returns:
        torch.optim.lr_scheduler._LRScheduler: The corresponding scheduler instance.

    Raises:
        ValueError: If the specified scheduler_type is unknown or unsupported.
    """
    """
    https://www.kaggle.com/code/isbhargav/guide-to-pytorch-learning-rate-scheduling
    """
    if scheduler_type == "linear":
        return get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=0, num_training_steps=total_steps
        )
    elif scheduler_type == "exponential":
        return ExponentialLR(optimizer, gamma=0.9)
    elif scheduler_type == "step":
        return StepLR(optimizer, step_size=2000, gamma=0.1)
    elif scheduler_type == "reduce_on_plateau":
        return ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2)
    elif scheduler_type == "one_cycle_lr":
        return OneCycleLR(optimizer, max_lr=1e-3, total_steps=total_steps)
    elif scheduler_type == "cyclic_lr":
        if optimizer_type in ["adamw", "adam"]:
            return CyclicLR(
                optimizer,
                base_lr=1e-6,
                max_lr=1e-3,
                step_size_up=2000,
                cycle_momentum=False,
            )
        return CyclicLR(optimizer, base_lr=1e-6, max_lr=1e-3, step_size_up=2000)
    elif scheduler_type == "cosine":
        return CosineAnnealingLR(optimizer, T_max=total_steps, eta_min=0)
    else:
        raise ValueError(f"Unknown scheduler type: {scheduler_type}")


def get_sampler(dataset, sampler_type: str):
    """Retrieve the data sampler based on the specified type.

    Args:
        dataset: The dataset from which to sample.
        sampler_type (str): The type of sampler. Options include:
            - "random"
            - "sequential"
            - "subset_random"
            - "weighted_random"

    Returns:
        torch.utils.data.Sampler: The corresponding sampler instance.

    Raises:
        ValueError: If the specified sampler_type is unknown or unsupported.
    """
    if sampler_type == "random":
        return RandomSampler(dataset)
    elif sampler_type == "sequential":
        return SequentialSampler(dataset)
    elif sampler_type == "subset_random":
        indices = list(range(len(dataset)))
        return SubsetRandomSampler(indices)
    elif sampler_type == "weighted_random":
        weights = make_weights_for_balanced_classes(
            dataset.labels, len(set(dataset.labels))
        )
        weights = torch.DoubleTensor(weights)
        return WeightedRandomSampler(weights, len(weights))
    else:
        raise ValueError(f"Unknown sampler type: {sampler_type}")


class EarlyStopping:
    """Early stops the training if validation loss doesn't improve after a given patience.

    Attributes:
        patience (int): How long to wait after last time validation loss improved.
        min_delta (float): Minimum change in the monitored quantity to qualify as an improvement.
        counter (int): Counts the number of epochs with no improvement.
        best_loss (float or None): Best recorded validation loss.
        early_stop (bool): Flag indicating whether to stop early.
    """

    def __init__(self, patience=2, min_delta=0.001):
        """Initialize the EarlyStopping instance.

        Args:
            patience (int, optional): Number of epochs to wait after last improvement. Defaults to 2.
            min_delta (float, optional): Minimum change to qualify as an improvement. Defaults to 0.001.
        """
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False

    def __call__(self, val_loss):
        """Call method to update early stopping status based on validation loss.

        Args:
            val_loss (float): The current epoch's validation loss.
        """
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True


def _count_trainable_parameters(model) -> int:
    """Count the number of trainable parameters in the model.

    Args:
        model: The model for which to count trainable parameters.

    Returns:
        int: The total number of trainable parameters.
    """
    num_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return num_params