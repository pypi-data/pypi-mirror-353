from typing import List, Optional, Dict, Any, Tuple, Union
import random
import pandas as pd
import numpy as np
import logging

import torch
from torch.utils.data import DataLoader
from transformers import DataCollatorWithPadding

from dreamml.modeling.models.estimators import BaseModel
from dreamml.modeling.models.estimators.bert_for_sequence_classification._dataset import (
    TextDataset,
)
from dreamml.modeling.models.estimators.bert_for_sequence_classification._bert_utils import (
    load_tokenizer,
    get_sampler,
)
from dreamml.modeling.models.estimators.bert_for_sequence_classification._model import (
    BertModelForClassification,
)
from dreamml.modeling.models.estimators.bert_for_sequence_classification._trainer import (
    Trainer,
)


seed = 27
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)


class BertModel(BaseModel):
    """
    BertModel is a specialized model for vectorization and optimization stages using BERT architecture.

    Args:
        estimator_params (Dict[str, Any]): Parameters specific to the estimator.
        task (str): The task type (e.g., binary, multilabel, multiclass).
        used_features (List[str]): List of feature names used in the model.
        categorical_features (List[str]): List of categorical feature names.
        metric_name: Name of the metric used for evaluation.
        metric_params: Parameters for the metric.
        parallelism (int, optional): Degree of parallelism. Defaults to -1.
        train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
        text_features (optional): Features that contain text data. Defaults to None.
        augmentation_params (Tuple[list, float], optional): Parameters for data augmentation. Defaults to None.
        **params: Additional keyword arguments.
    
    Attributes:
        tokenizer: Tokenizer loaded based on the provided model path and maximum length.
        model: Initialized BERT model for classification.
        trainer: Trainer instance for handling the training process.
        training_graph: Graph representing the training process.
        dataloader_num_workers (int): Number of workers for data loading.
    """

    model_name = "bert"

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str],
        categorical_features: List[str],
        metric_name,
        metric_params,
        parallelism: int = -1,
        train_logger: Optional[logging.Logger] = None,
        text_features=None,
        augmentation_params: Tuple[list, float] = None,
        **params,
    ):
        """
        Initializes the BertModel with the given parameters.

        Args:
            estimator_params (Dict[str, Any]): Parameters specific to the estimator.
            task (str): The task type (e.g., binary, multilabel, multiclass).
            used_features (List[str]): List of feature names used in the model.
            categorical_features (List[str]): List of categorical feature names.
            metric_name: Name of the metric used for evaluation.
            metric_params: Parameters for the metric.
            parallelism (int, optional): Degree of parallelism. Defaults to -1.
            train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
            text_features (optional): Features that contain text data. Defaults to None.
            augmentation_params (Tuple[list, float], optional): Parameters for data augmentation. Defaults to None.
            **params: Additional keyword arguments.
        """
        super().__init__(
            estimator_params,
            task,
            used_features,
            categorical_features,
            metric_name,
            metric_params,
            parallelism=parallelism,
            train_logger=train_logger,
            text_features=text_features,
            augmentation_params=augmentation_params,
            **params,
        )
        self.tokenizer = load_tokenizer(
            self.params["model_path"], self.params["max_length"]
        )
        self.model = self._init_bert_model()
        self.trainer = None
        self.training_graph = None
        self.dataloader_num_workers = 0
        self._logger.info(f"Bert params: {self.params}")

    def _init_bert_model(self):
        """
        Initializes the BERT model for classification with the specified configuration.

        Returns:
            BertModelForClassification: An instance of the BERT classification model.

        Raises:
            KeyError: If required parameters are missing from self.params or self.metric_params.
        """
        model_config = {
            "num_labels": len(self.metric_params["labels"]),
            "dropout_rate": self.params["dropout_rate"],
            "lora_config": self.params["lora_config"],
            "freeze_layers": self.params["freeze_layers"],
        }
        model = BertModelForClassification(
            model_path=self.params["model_path"],
            config=model_config,
        )
        num_trainable_params = model._count_trainable_params()
        self._logger.info(f"Num trainable params: {num_trainable_params}")
        return model

    def fit(self, data, target, *eval_set):
        """
        Trains the BERT model using the provided data and target.

        Args:
            data: Training data.
            target: Target labels for training.
            *eval_set: Optional evaluation dataset and its corresponding targets.

        Raises:
            ValueError: If eval_set does not contain exactly two elements (validation data and target).
        """
        valid_data, valid_target = eval_set

        train_dataloader = self._create_dataloader(
            data=data,
            target=target,
            sampler_type=self.params["sampler_type"],
            augmenters=self.text_augmentations,
            aug_p=self.aug_p,
        )
        valid_dataloader = self._create_dataloader(
            data=valid_data,
            target=valid_target,
            sampler_type="sequential",
        )

        trainer_config = {
            "task": self.task,
            "objective": self.params["objective"],
            "learning_rate": self.params["learning_rate"],
            "epochs": self.params["epochs"],
            "batch_size": self.params["batch_size"],
            "weight_decay": self.params["weight_decay"],
            "total_steps": len(train_dataloader),
            "early_stopping_patience": self.params["early_stopping_patience"],
            "optimizer_type": self.params["optimizer_type"],
            "scheduler_type": self.params["scheduler_type"],
            "clip_grad_norm": self.params["clip_grad_norm"],
            "gradient_accumulation_steps": self.params["gradient_accumulation_steps"],
            "device": self.params["device"],
            "seed": seed,
            "_logger": self._logger,
            "save_best_only": self.params["save_best_only"],
            "save_model_path": self.params["save_model_path"],
            "load_best_model_at_end": self.params.get("load_best_model_at_end", True),
        }
        self.trainer = Trainer(trainer_config)
        self.trainer.fit(self.model, train_dataloader, valid_dataloader)
        self.trainer.plot_training_history()

        if trainer_config["load_best_model_at_end"]:
            self.trainer = Trainer.load(trainer_config["save_model_path"])
            self._logger.info(f"Loaded Trainer object with the best epoch.")

    @torch.no_grad()
    def transform(self, data: pd.DataFrame):
        """
        Transforms the input data by generating predictions using the trained model.

        Args:
            data (pd.DataFrame): Input data to transform.

        Returns:
            Union[np.ndarray, None]: Predicted probabilities for each class or None if the task type is unsupported.

        Raises:
            AttributeError: If the trainer has not been initialized.
        """
        dataloader = self._create_dataloader(
            data=data,
            target=None,
            sampler_type="sequential",
        )
        predictions = self.trainer.predict_proba(dataloader)

        if self.task == "binary":
            return predictions[:, 1]
        elif self.task in ("multilabel", "multiclass"):
            return predictions
        else:
            return

    def _create_dataloader(
        self,
        data: pd.DataFrame,
        target: Optional[pd.Series] = None,
        sampler_type="sequential",
        augmenters: Optional[list] = None,
        aug_p: float = 0.2,
    ):
        """
        Creates a DataLoader for the given data and target.

        Args:
            data (pd.DataFrame): Input data.
            target (Optional[pd.Series], optional): Target labels. Defaults to None.
            sampler_type (str, optional): Type of sampler to use. Defaults to "sequential".
            augmenters (Optional[list], optional): List of data augmenters. Defaults to None.
            aug_p (float, optional): Probability of applying augmentation. Defaults to 0.2.

        Returns:
            DataLoader: PyTorch DataLoader for the dataset.

        Raises:
            KeyError: If text_features are not found in the data.
        """
        data: pd.Series = data[self.text_features].astype(str).agg(" ".join, axis=1)
        dataset = TextDataset(
            texts=data.tolist(),
            labels=None if target is None else target.tolist(),
            tokenizer=self.tokenizer,
            max_length=self.params["max_length"],
            augmenters=augmenters,
            aug_p=aug_p,
        )
        sampler = get_sampler(dataset, sampler_type)
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        dataloader = DataLoader(
            dataset,
            batch_size=self.params["batch_size"],
            sampler=sampler,
            collate_fn=data_collator,
            # num_workers=self.dataloader_num_workers,
        )
        return dataloader