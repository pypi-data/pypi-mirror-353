import os
from tqdm.auto import tqdm
import numpy as np
import torch
from sklearn.metrics import log_loss, f1_score


class EarlyStoppingEpochCallback:
    """Callback for early stopping of training based on epochs.

    Monitors the validation loss and stops training if there is no improvement
    after a specified number of epochs.

    Attributes:
        patience (int): Number of epochs with no improvement after which training will be stopped.
        min_delta (float): Minimum change in the monitored quantity to qualify as an improvement.
        counter (int): Counter for epochs with no improvement.
        best_loss (float or None): Best observed validation loss.
        early_stop (bool): Flag indicating whether to stop training early.
    """

    def __init__(self, patience=2, min_delta=0.001):
        """Initializes the EarlyStoppingEpochCallback.

        Args:
            patience (int, optional): Number of epochs with no improvement after which training will be stopped. Defaults to 2.
            min_delta (float, optional): Minimum change in the monitored quantity to qualify as an improvement. Defaults to 0.001.
        """
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False

    def __call__(self, val_loss):
        """Checks whether training should be stopped early based on validation loss.

        Args:
            val_loss (float): Current epoch's validation loss.

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


class EarlyStoppingBatchCallback:
    """Callback for early stopping of training based on batches.

    Monitors the validation loss after each batch and stops training if there is no improvement
    after a specified fraction of batches or a minimum number of batches.

    Attributes:
        patience_fraction (float): Fraction of batches with no improvement after which training will be stopped.
        min_delta (float): Minimum change in the monitored quantity to qualify as an improvement.
        min_patience (int): Minimum number of batches to wait before stopping.
        patience (int or None): Adaptive patience based on the number of batches.
        best_loss (float or None): Best observed loss.
        counter (int): Counter for batches with no improvement.
        early_stop (bool): Flag indicating whether to stop training early.
    """

    def __init__(self, patience_fraction=0.1, min_delta=0, min_patience=300):
        """Initializes the EarlyStoppingBatchCallback.

        Args:
            patience_fraction (float, optional): Fraction of batches with no improvement after which training will be stopped. Defaults to 0.1.
            min_delta (float, optional): Minimum change in the monitored quantity to qualify as an improvement. Defaults to 0.
            min_patience (int, optional): Minimum number of batches to wait before stopping. Defaults to 300.
        """
        self.patience_fraction = patience_fraction
        self.min_delta = min_delta
        self.min_patience = min_patience
        self.patience = None  # Will be set dynamically
        self.best_loss = None
        self.counter = 0
        self.early_stop = False

    def _set_adaptive_patience(self, num_batches):
        """Sets adaptive patience based on the total number of batches.

        Args:
            num_batches (int): Total number of batches in an epoch.
        """
        self.patience = max(
            self.min_patience, int(num_batches * self.patience_fraction)
        )

    def __call__(self, current_loss, num_batches=None):
        """Checks whether training should be stopped early based on current loss.

        Args:
            current_loss (float): Current batch's loss.
            num_batches (int, optional): Total number of batches in an epoch. Used for adaptive patience. Defaults to None.

        Returns:
            bool: True if training should be stopped early, False otherwise.
        """
        if self.patience is None and num_batches is not None:
            self._set_adaptive_patience(num_batches)

        if self.best_loss is None:
            self.best_loss = current_loss
        elif current_loss < self.best_loss - self.min_delta:
            self.best_loss = current_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True

        return self.early_stop


class ProgressBarCallback:
    """Callback for displaying training and validation progress.

    Utilizes a progress bar to show the progress of epochs and batches during training or validation phases.
    """

    def __init__(self, total_epochs, total_batches, phase="Training"):
        """Initializes the ProgressBarCallback.

        Args:
            total_epochs (int): Total number of epochs.
            total_batches (int): Total number of batches per epoch.
            phase (str, optional): Phase of training ("Training" or "Validation"). Defaults to "Training".
        """
        self.total_epochs = total_epochs
        self.total_batches = total_batches
        self.phase = phase
        self.progress_bar = None

    def start(self, epoch):
        """Starts the progress bar for the specified epoch.

        Args:
            epoch (int): Current epoch number.
        """
        self.progress_bar = tqdm(total=self.total_batches, position=0, leave=True)
        self.progress_bar.set_description(
            f"Phase: {self.phase} | Epoch: {epoch}/{self.total_epochs}"
        )

    def update(self, avg_loss=None):
        """Updates the progress bar by one batch.

        Optionally updates the progress bar with the average loss.

        Args:
            avg_loss (float, optional): Average loss to display. Defaults to None.
        """
        self.progress_bar.update(1)
        if avg_loss is not None:
            self.progress_bar.set_postfix({"avg_loss": f"{avg_loss:.4f}"})

    def close(self):
        """Closes the progress bar."""
        self.progress_bar.close()


class GradientClippingCallback:
    """Callback for gradient clipping to prevent gradient explosion.

    Applies gradient clipping with a specified maximum norm to the model's parameters.
    """

    def __init__(self, max_norm: float):
        """Initializes the GradientClippingCallback.

        Args:
            max_norm (float): Maximum norm for the gradients. Gradients with a norm larger than this will be clipped.
        """
        self.max_norm = max_norm

    def __call__(self, model):
        """Applies gradient clipping to the model's parameters.

        Args:
            model: The model whose gradients will be clipped.
        """
        torch.nn.utils.clip_grad_norm_(model.parameters(), self.max_norm)


class CustomMetricCallback:
    """Callback for calculating and logging custom metrics.

    Collects predictions and true labels during validation and computes metrics such as log loss.
    """

    def __init__(self):
        """Initializes the CustomMetricCallback."""
        self.valid_predictions = []
        self.valid_labels = []

    def add(self, predictions, labels):
        """Adds predictions and true labels for metric calculation.

        Args:
            predictions (array-like): Predicted probabilities or scores.
            labels (array-like): True labels.
        """
        self.valid_predictions.extend(predictions)
        self.valid_labels.extend(labels)

    def compute(self):
        """Computes the log loss based on the collected predictions and labels.

        Returns:
            float: Computed log loss.
        """
        valid_pred_proba = self.valid_predictions
        valid_preds = np.argmax(self.valid_predictions, axis=1)
        logloss = log_loss(self.valid_labels, valid_pred_proba)
        return logloss

    def reset(self):
        """Resets the collected predictions and labels."""
        self.valid_predictions = []
        self.valid_labels = []


class ModelCheckpointCallback:
    """Callback for saving the model when a monitored metric improves.

    Saves the model checkpoint to a specified filepath when the monitored metric achieves a better score.
    """

    def __init__(
        self,
        filepath: str = "./checkpoints/best_model.pth",
        monitor: str = "val_loss",
        mode: str = "min",
    ):
        """Initializes the ModelCheckpointCallback.

        Args:
            filepath (str, optional): Filepath to save the model checkpoint. Defaults to "./checkpoints/best_model.pth".
            monitor (str, optional): Metric to monitor for improvement. Defaults to "val_loss".
            mode (str, optional): Direction of improvement ("min" for lower is better, "max" for higher is better). Defaults to "min".
        """
        self.filepath = filepath
        self.monitor = monitor
        self.mode = mode
        self.best_score = float("inf") if mode == "min" else float("-inf")

    def __call__(self, model, score):
        """Checks if the current score is better than the best score and saves the model if it is.

        Args:
            model: The model to be saved.
            score (float): The current score of the monitored metric.
        """
        if (self.mode == "min" and score < self.best_score) or (
            self.mode == "max" and score > self.best_score
        ):
            self.best_score = score
            self.save_model(model)

    def save_model(self, model):
        """Saves the current model to the specified filepath.

        Args:
            model: The model to be saved.
        """
        self._check_filepath()
        torch.save(model.state_dict(), self.filepath)

    def _check_filepath(self):
        """Ensures that the directory for the filepath exists; creates it if it does not."""
        directory = os.path.dirname(self.filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)