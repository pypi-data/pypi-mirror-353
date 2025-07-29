from typing import Dict

import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import f1_score, precision_score, recall_score
from torch import softmax
from torch.optim.lr_scheduler import ReduceLROnPlateau
from numpy import asarray
import torch

from dreamml.modeling.models.estimators.bert_for_sequence_classification._bert_utils import (
    get_optimizer,
    get_scheduler,
    get_loss_function,
)
from dreamml.modeling.models.callbacks.bert_callbacks import ProgressBarCallback
from dreamml.modeling.models.estimators.bert_for_sequence_classification._model import (
    BertModelForClassification,
)


class Trainer:
    """Trainer class for training and evaluating BERT models for sequence classification.

    This class handles the training loop, validation, prediction, and model saving/loading
    for BERT-based sequence classification tasks.
    """

    def __init__(self, config: Dict):
        """Initialize the Trainer with the given configuration.

        Args:
            config (Dict): Configuration dictionary containing training parameters such as
                task, objective, learning_rate, epochs, batch_size, weight_decay,
                total_steps, early_stopping_patience, optimizer_type, scheduler_type,
                clip_grad_norm, gradient_accumulation_steps, device, seed, _logger,
                save_best_only, and save_model_path.
        """
        self.config = config
        self.task = config["task"]
        self.objective = config["objective"]
        self.learning_rate = config["learning_rate"]
        self.n_epochs = config["epochs"]
        self.batch_size = config["batch_size"]
        self.weight_decay = config["weight_decay"]
        self.total_steps = config["total_steps"]
        self.early_stopping_patience = config["early_stopping_patience"]
        self.optimizer_type = config["optimizer_type"]
        self.scheduler_type = config["scheduler_type"]
        self.clip_grad_norm = config["clip_grad_norm"]
        self.gradient_accumulation_steps = config["gradient_accumulation_steps"]
        self.device = config["device"]
        self.seed = config["seed"]
        self._logger = config["_logger"]
        self.save_best_only = config["save_best_only"]
        self.save_model_path = config["save_model_path"]

        # ---
        self.loss_fn = get_loss_function(config["objective"])
        self.early_stopping_counter = 0
        self.best_val_loss = float("inf")
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.history = None

    def fit(self, model, train_dataloader, val_dataloader):
        """Train the model using the provided training and validation dataloaders.

        Args:
            model: The model to be trained.
            train_dataloader: DataLoader for the training data.
            val_dataloader: DataLoader for the validation data.

        Returns:
            The trained model set to evaluation mode.
        """
        self.model = model.to(self.device)

        self.optimizer = get_optimizer(
            self.model,
            self.learning_rate,
            self.optimizer_type,
            self.weight_decay,
        )
        self.scheduler = get_scheduler(
            self.optimizer,
            self.scheduler_type,
            self.optimizer_type,
            self.total_steps,
        )
        self.history = {
            "train_loss": [],
            "val_loss": [],
            "val_acc": [],
            "val_f1": [],
            "val_precision": [],
            "val_recall": [],
        }
        train_progress = ProgressBarCallback(
            self.n_epochs, len(train_dataloader), "Training"
        )
        valid_progress = ProgressBarCallback(
            self.n_epochs, len(val_dataloader), "Validation"
        )

        for epoch in range(self.n_epochs):
            self._logger.info(f"Epoch: {epoch + 1} / {self.n_epochs}")
            train_progress.start(epoch + 1)
            valid_progress.start(epoch + 1)

            train_info = self.train_epoch(train_dataloader, train_progress)
            val_info = self.val_epoch(val_dataloader, valid_progress)

            self.history["train_loss"].extend([train_info["loss"]])
            self.history["val_loss"].extend([val_info["loss"]])
            self.history["val_acc"].extend([val_info["acc"]])
            self.history["val_f1"].extend([val_info["f1"]])
            self.history["val_precision"].extend([val_info["precision"]])
            self.history["val_recall"].extend([val_info["recall"]])

            if self.save_best_only and val_info["loss"] < self.best_val_loss:
                self.save(self.save_model_path)

            if isinstance(self.scheduler, ReduceLROnPlateau):
                self.scheduler.step(val_info["loss"])
            else:
                self.scheduler.step()

            if val_info["loss"] < self.best_val_loss:
                self.best_val_loss = val_info["loss"]
                self.early_stopping_counter = 0
            else:
                self.early_stopping_counter += 1

            train_progress.close()
            valid_progress.close()

            self._logging_info()
            if self.early_stopping_counter >= self.early_stopping_patience:
                print(f"Early stopping triggered at epoch {epoch + 1}")
                break

        return self.model.eval()

    def train_epoch(self, train_dataloader, train_progress):
        """Perform one epoch of training.

        Args:
            train_dataloader: DataLoader for the training data.
            train_progress: ProgressBarCallback instance for tracking training progress.

        Returns:
            A dictionary containing the average training loss for the epoch.
        """
        self.model.train()
        losses = []

        for step, batch in enumerate(train_dataloader):
            ids = batch["input_ids"].to(self.device, dtype=torch.long)
            mask = batch["attention_mask"].to(self.device, dtype=torch.long)
            targets = batch["labels"].to(self.device, dtype=torch.long)

            outputs = self.model(ids, mask)
            loss = self.loss_fn(outputs, targets)
            loss = loss / self.gradient_accumulation_steps

            loss.backward()

            if (step + 1) % self.gradient_accumulation_steps == 0:
                if self.clip_grad_norm:
                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(), self.clip_grad_norm
                    )
                self.optimizer.step()
                self.optimizer.zero_grad()

            loss_val = loss.item() * self.gradient_accumulation_steps
            losses.append(loss_val)
            train_progress.update(sum(losses) / len(losses))

        avg_train_loss = sum(losses) / len(losses)
        return {"loss": avg_train_loss}

    @torch.no_grad()
    def val_epoch(self, val_dataloader, valid_progress):
        """Perform one epoch of validation.

        Args:
            val_dataloader: DataLoader for the validation data.
            valid_progress: ProgressBarCallback instance for tracking validation progress.

        Returns:
            A dictionary containing validation metrics including accuracy, loss, F1 score,
            precision, and recall.
        """
        self.model.eval()
        all_logits = []
        all_labels = []

        for batch in val_dataloader:
            ids = batch["input_ids"].to(self.device, dtype=torch.long)
            mask = batch["attention_mask"].to(self.device, dtype=torch.long)
            targets = batch["labels"].to(self.device, dtype=torch.long)
            outputs = self.model(ids, mask)
            batch_loss = self.loss_fn(outputs, targets).item()
            all_logits.append(outputs)
            all_labels.append(targets)
            valid_progress.update(batch_loss)

        all_labels = torch.cat(all_labels).to(self.device)
        all_logits = torch.cat(all_logits).to(self.device)
        loss = self.loss_fn(all_logits, all_labels).item()
        acc = (all_logits.argmax(1) == all_labels).float().mean().item()

        # Additional metrics
        preds = all_logits.argmax(1).cpu().numpy()
        labels = all_labels.cpu().numpy()

        if self.config["task"] == "binary":
            f1 = f1_score(labels, preds)
            precision = precision_score(labels, preds)
            recall = recall_score(labels, preds)
        else:
            f1 = f1_score(labels, preds, average="macro")
            precision = precision_score(labels, preds, average="macro")
            recall = recall_score(labels, preds, average="macro")

        return {
            "acc": acc,
            "loss": loss,
            "f1": f1,
            "precision": precision,
            "recall": recall,
        }

    @torch.no_grad()
    def predict(self, test_dataloader):
        """Generate predictions for the test data.

        Args:
            test_dataloader: DataLoader for the test data.

        Returns:
            A NumPy array of predicted class labels.

        Raises:
            RuntimeError: If the model has not been trained yet.
        """
        if not self.model:
            raise RuntimeError("You should train the model first.")
        self.model.eval()
        predictions = []

        for batch in test_dataloader:
            ids = batch["input_ids"].to(self.device, dtype=torch.long)
            mask = batch["attention_mask"].to(self.device, dtype=torch.long)
            outputs = self.model(ids, mask)
            predictions.extend(outputs.argmax(1).tolist())
        return asarray(predictions)

    @torch.no_grad()
    def predict_proba(self, test_dataloader):
        """Generate probability estimates for the test data.

        Args:
            test_dataloader: DataLoader for the test data.

        Returns:
            A NumPy array of probability scores for each class.

        Raises:
            RuntimeError: If the model has not been trained yet.
        """
        if not self.model:
            raise RuntimeError("You should train the model first.")
        self.model.eval()
        transform_progress = ProgressBarCallback(1, len(test_dataloader), "Transform")
        transform_progress.start(1)

        probabilities_list = []

        for batch in test_dataloader:
            ids = batch["input_ids"].to(self.device, dtype=torch.long)
            mask = batch["attention_mask"].to(self.device, dtype=torch.long)
            logits = self.model(ids, mask)
            probabilities = softmax(logits, dim=1).cpu().numpy()
            probabilities_list.append(probabilities)
        predictions = np.concatenate(probabilities_list, axis=0)
        transform_progress.close()
        return predictions

    def save(self, path: str):
        """Save the trained model and trainer configuration to the specified path.

        Args:
            path (str): The file path where the model checkpoint will be saved.

        Raises:
            RuntimeError: If the model has not been trained yet.
        """
        if self.model is None:
            raise RuntimeError("You should train the model first")

        checkpoint = {
            "config": self.model.config,
            "trainer_config": self.config,
            "model_name": self.model.model_name,
            "model_state_dict": self.model.state_dict(),
        }
        torch.save(checkpoint, path)

    @classmethod
    def load(cls, path: str):
        """Load a trained model and trainer configuration from the specified path.

        Args:
            path (str): The file path from where to load the model checkpoint.

        Returns:
            An instance of Trainer with the loaded model and configuration.

        Raises:
            RuntimeError: If any of the required keys are missing in the checkpoint.
        """
        ckpt = torch.load(path)
        keys = ["config", "trainer_config", "model_state_dict"]
        for key in keys:
            if key not in ckpt:
                raise RuntimeError(f"Missing key {key} in checkpoint")
        new_model = BertModelForClassification(ckpt["model_name"], ckpt["config"])
        new_model.load_state_dict(ckpt["model_state_dict"])
        new_trainer = cls(ckpt["trainer_config"])
        new_trainer.model = new_model
        new_trainer.model.to(new_trainer.device)
        return new_trainer

    def plot_training_history(self):
        """Plot the training and validation loss and F1 score over epochs.

        Returns:
            A matplotlib.pyplot object containing the training history plots.
        """
        train_loss = self.history.get("train_loss", [])
        val_loss = self.history.get("val_loss", [])
        val_f1 = self.history.get("val_f1", [])

        epochs = range(1, len(val_loss) + 1)

        # Loss plot
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plt.plot(
            epochs, train_loss, label="Train Loss", color="blue", marker="o", alpha=0.7
        )
        plt.plot(epochs, val_loss, label="Validation Loss", color="orange", marker="o")
        plt.title("Loss over Epochs", fontsize=16)
        plt.xlabel("Epochs", fontsize=14)
        plt.ylabel("Loss", fontsize=14)
        plt.legend()
        plt.grid(alpha=0.3)

        # F1 score plot
        plt.subplot(1, 2, 2)
        plt.plot(epochs, val_f1, label="Validation F1", color="green", marker="o")
        plt.title("F1 over Epochs", fontsize=16)
        plt.xlabel("Epochs", fontsize=14)
        plt.ylabel("F1", fontsize=14)
        plt.legend()
        plt.grid(alpha=0.3)

        plt.tight_layout()

        return plt

    def _logging_info(self):
        """Log the latest training history information."""
        for key, info_list in self.history.items():
            self._logger.info(f"{key}: {info_list[-1]}")