from typing import Dict, List, Any, Union
import random
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.pipeline import Pipeline
from torch.utils.data import DataLoader
import torch
import torch.nn as nn

from dreamml.modeling.models.callbacks.bert_callbacks import (
    ProgressBarCallback,
    EarlyStoppingEpochCallback,
)
from dreamml.modeling.models.estimators import BaseModel
from dreamml.modeling.models.estimators.bert_for_sequence_classification._bert_utils import (
    get_loss_function,
    get_optimizer,
    get_scheduler,
    get_sampler,
    _count_trainable_parameters,
)

seed = 27
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)


class AutoEncoderBaseModel(BaseModel, nn.Module):
    """
    Base class for AutoEncoder models integrating with BaseModel and PyTorch's nn.Module.

    This class provides common functionalities for AutoEncoder models, including
    normalization, scaling, training, validation, and transformation processes.
    """

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str],
        metric_name,
        metric_params,
        **params,
    ):
        """
        Initializes the AutoEncoderBaseModel with the given parameters.

        Args:
            estimator_params (Dict[str, Any]): Parameters for the estimator.
            task (str): The task type.
            used_features (List[str]): List of feature names used in the model.
            metric_name: Name of the metric to be used.
            metric_params: Parameters for the metric.
            **params: Additional parameters.

        Raises:
            KeyError: If required parameters are missing in `params`.
        """
        nn.Module.__init__(self)
        BaseModel.__init__(
            self,
            estimator_params=estimator_params,
            task=task,
            used_features=used_features,
            metric_name=metric_name,
            metric_params=metric_params,
            **params,
        )

        self.normalization_flag: bool = self.params["normalization_flag"]
        self.scaler = self._norm_scaler_pipeline()

        # model_params
        self.learning_rate = self.params["learning_rate"]
        self.epochs = self.params["epochs"]
        self.batch_size = self.params["batch_size"]
        self.loss_fn = get_loss_function(self.params["objective"])
        self.latent_dim = self.params["latent_dim"]

        # ___
        self.estimator_class = None
        self.model = None
        self.input_dim = None
        self.optimizer = None
        self.scheduler = None

        # ___
        self.log_verbose = 500
        self.callback_info = {}
        self.num_trainable_params = 0

    def _norm_scaler_pipeline(self):
        """
        Creates a normalization and scaling pipeline if normalization is enabled.

        Returns:
            Pipeline or None: The scaler pipeline if normalization is enabled, else None.
        """
        if self.normalization_flag:
            return Pipeline(
                [("scaler_1", StandardScaler()), ("scaler_2", MinMaxScaler())]
            )

        self._logger.debug(f"normalization_flag: {self.normalization_flag}")
        return None

    def fit(self, X_train, _, *valid_set):
        """
        Fits the AutoEncoder model to the training data.

        Args:
            X_train: Training data features.
            _: Placeholder for compatibility.
            *valid_set: Validation data as a tuple (X_valid, _).

        Raises:
            Exception: If the model fails to train.
        """
        X_valid, _ = valid_set

        if self.scaler is not None:
            self.scaler.fit(X_train.values)
            X_train = self.scaler.transform(X_train.values)
            X_valid = self.scaler.transform(X_valid.values)

        train_loader = self._get_sample_loader(
            X_train, self.params["batch_size"], "random", self.params["device"]
        )
        valid_loader = self._get_sample_loader(
            X_valid, self.params["batch_size"], "sequential", self.params["device"]
        )

        self.input_dim = X_train.shape[1]
        self.model = self.estimator_class(self.input_dim, self.latent_dim).to(
            self.params["device"]
        )
        self.num_trainable_params = _count_trainable_parameters(self.model)
        self._logger.info(
            f"num_trainable_params {self.model_name}: {self.num_trainable_params}"
        )

        self.optimizer = get_optimizer(
            self.model,
            self.params["learning_rate"],
            self.params["optimizer_type"],
            self.params["weight_decay"],
        )
        self.scheduler = get_scheduler(
            self.optimizer,
            self.params["scheduler_type"],
            self.params["optimizer_type"],
            len(train_loader) * self.params["epochs"],
        )

        # train model
        self._train_model(train_loader, valid_loader)

    def _train_model(self, train_loader, valid_loader):
        """
        Trains the AutoEncoder model using the provided training and validation loaders.

        Args:
            train_loader (DataLoader): DataLoader for training data.
            valid_loader (DataLoader): DataLoader for validation data.

        Raises:
            Exception: If training fails unexpectedly.
        """
        num_epochs = self.params["epochs"]

        # Callbacks
        early_stopping_epoch = EarlyStoppingEpochCallback(patience=5, min_delta=0.0001)
        train_progress = ProgressBarCallback(num_epochs, len(train_loader), "Training")
        valid_progress = ProgressBarCallback(
            num_epochs, len(valid_loader), "Validation"
        )
        gradient_clipping = None

        for epoch in range(1, num_epochs + 1):
            self._logger.info(f"Epoch: {epoch} / {self.params['epochs']}")
            train_progress.start(epoch)
            valid_progress.start(epoch)

            train_loss = self._training_phase(
                train_loader, train_progress, gradient_clipping
            )
            valid_loss = self._validation_phase(valid_loader, valid_progress)

            # Calculate average losses per epoch
            avg_train_loss = train_loss / len(train_loader)
            avg_valid_loss = valid_loss / len(valid_loader)

            # Close progress bars
            train_progress.close()
            valid_progress.close()

            # Logs
            avg_losses_msg = f"Epoch {epoch} average loss: Train: {avg_train_loss} | Valid: {avg_valid_loss}"
            self._logger.info(avg_losses_msg)
            self.callback_info[epoch] = {
                "train": avg_train_loss,
                "valid": avg_valid_loss,
            }

            if early_stopping_epoch.early_stop:
                self._logger.info(f"Epoch {epoch} | Early stopping epoch")
                break

    def _training_phase(self, train_loader, train_progress, gradient_clipping) -> float:
        """
        Executes the training phase for one epoch.

        Args:
            train_loader (DataLoader): DataLoader for training data.
            train_progress (ProgressBarCallback): Progress bar for training.
            gradient_clipping: Function for gradient clipping.

        Returns:
            float: Total training loss for the epoch.
        """
        self.model.train()
        train_loss = 0

        for idx, batch in enumerate(train_loader):
            self.optimizer.zero_grad()

            inputs, _ = batch
            inputs = inputs.to(self.params["device"])

            if self.model_name == "ae":
                outputs = self.model(inputs)
                loss = self.loss_fn(outputs, inputs)
            else:  # "vae"
                outputs, z_mean, z_log_var = self.model(inputs)
                loss = self._vae_loss(self.loss_fn, outputs, inputs, z_mean, z_log_var)

            loss.backward()

            self.optimizer.step()
            (
                self.scheduler.step()
                if self.params["scheduler_type"] != "reduce_on_plateau"
                else None
            )

            if gradient_clipping is not None:
                gradient_clipping(self.model)  # Apply gradient clipping

            train_loss += loss.item()
            avg_loss = train_loss / (idx + 1)
            train_progress.update(avg_loss)

            if idx % self.log_verbose == 0 or idx == len(train_loader):
                self._logger.info(f"Batch: {idx} / {len(train_loader)} | Loss: {loss}")

        return train_loss

    @torch.no_grad()
    def _validation_phase(self, valid_loader, valid_progress):
        """
        Executes the validation phase for one epoch.

        Args:
            valid_loader (DataLoader): DataLoader for validation data.
            valid_progress (ProgressBarCallback): Progress bar for validation.

        Returns:
            float: Total validation loss for the epoch.
        """
        self.model.eval()
        valid_loss = 0

        for idx, batch in enumerate(valid_loader):
            inputs, _ = batch
            inputs = inputs.to(self.params["device"])

            if self.model_name == "ae":
                outputs = self.model(inputs)
                loss = self.loss_fn(outputs, inputs)
            else:  # "vae"
                outputs, z_mean, z_log_var = self.model(inputs)
                loss = self._vae_loss(self.loss_fn, outputs, inputs, z_mean, z_log_var)

            (
                self.scheduler.step(loss)
                if self.params["scheduler_type"] == "reduce_on_plateau"
                else None
            )

            valid_loss += loss.item()
            avg_loss = valid_loss / (idx + 1)
            valid_progress.update(avg_loss)

        return valid_loss

    @torch.no_grad()
    def transform(self, data: pd.DataFrame, return_output: bool = False) -> np.array:
        """
        Transforms the input data using the trained AutoEncoder model.

        Args:
            data (pd.DataFrame): Input DataFrame to be transformed.
            return_output (bool, optional): If True, returns the model's output.
                If False, returns the reconstruction error for each observation. Defaults to False.

        Returns:
            np.array: Transformed data or reconstruction errors.

        Raises:
            RuntimeError: If the model is not trained.
        """
        if self.scaler is not None:
            data = self.scaler.transform(data.values)

        self.model.to(self.params["device"])
        self.model.eval()
        loss_fn = get_loss_function(self.params["objective"], reduction="none")
        sample_loader = self._get_sample_loader(
            data, self.params["batch_size"], "sequential", self.params["device"]
        )
        transform_progress = ProgressBarCallback(1, len(sample_loader), "Transform")
        transform_progress.start(1)

        sample_loss = []
        output = []

        for idx, batch in enumerate(sample_loader):
            inputs, _ = batch
            inputs = inputs.to(self.params["device"])

            if self.model_name == "ae":
                outputs = self.model(inputs)
                loss = loss_fn(outputs.squeeze(), inputs)
            else:  # "vae"
                outputs, z_mean, z_log_var = self.model(inputs)
                loss = self._vae_loss(
                    loss_fn, outputs.squeeze(), inputs, z_mean, z_log_var
                )

            # Calculate loss for each observation in the batch
            loss_app = list(torch.mean(loss, axis=1).cpu().numpy())

            sample_loss.extend(loss_app)
            output.append(outputs.cpu().numpy())
            avg_loss = np.mean(sample_loss) / (idx + 1)
            transform_progress.update(avg_loss)
        transform_progress.close()

        if return_output:
            output = np.vstack(output)
            if self.scaler is not None:
                output = self.scaler.inverse_transform(output)
            return output
        return np.array(sample_loss)

    @staticmethod
    def _vae_loss(loss_fn, output, input, z_mean, z_log_var):
        """
        Computes the VAE loss combining reconstruction loss and KL divergence.

        Args:
            loss_fn: Loss function for reconstruction.
            output: Reconstructed output from the decoder.
            input: Original input data.
            z_mean: Mean of the latent distribution.
            z_log_var: Log variance of the latent distribution.

        Returns:
            torch.Tensor: Combined loss.
        """
        loss = loss_fn(output, input)
        kl_loss = -0.5 * torch.sum(1 + z_log_var - z_mean.pow(2) - z_log_var.exp())
        return loss + kl_loss

    def _get_sample_loader(
        self, data: pd.DataFrame, batch_size: int, sampler_type: str, device: str
    ):
        """
        Creates a DataLoader for the given data.

        Args:
            data (pd.DataFrame): Data to load.
            batch_size (int): Number of samples per batch.
            sampler_type (str): Type of sampler ('random', 'sequential', etc.).
            device (str): Device to load data onto.

        Returns:
            DataLoader: DataLoader for the dataset.
        """
        data = data.values if isinstance(data, pd.DataFrame) else data
        dataset = UnsupervisedDataset(data, device=device)
        sampler = get_sampler(dataset, sampler_type)
        loader = DataLoader(dataset, batch_size=batch_size, sampler=sampler)
        return loader

    @staticmethod
    def _calculate_threshold(losses: List[Union[int, float]]):
        """
        Calculates the threshold for anomaly detection based on losses.

        Args:
            losses (List[Union[int, float]]): List of loss values.

        Returns:
            float: Calculated threshold.
        """
        threshold = np.mean(losses) + (np.std(losses))
        return threshold


class UnsupervisedDataset(torch.utils.data.Dataset):
    """
    Dataset class for unsupervised learning tasks.

    This dataset returns input data and optionally output data for autoencoders.
    """

    def __init__(self, x: np.ndarray, device: str, output=True):
        """
        Initializes the UnsupervisedDataset.

        Args:
            x (np.ndarray): Input data array.
            device (str): Device to load tensors onto.
            output (bool, optional): Whether to return output data. Defaults to True.
        """
        self.x = x
        self.device = device
        self.output = output

    def __len__(self):
        """
        Returns the total number of samples in the dataset.

        Returns:
            int: Number of samples.
        """
        return len(self.x)

    def __getitem__(self, index):
        """
        Retrieves a single sample from the dataset.

        Args:
            index (int): Index of the sample to retrieve.

        Returns:
            tuple or torch.Tensor: Tuple of (input, output) if output is True, else input tensor.
        """
        item = torch.tensor(self.x[index], dtype=torch.float32).to(self.device)
        if self.output:
            return item, item
        else:
            return item


class VAEModel(AutoEncoderBaseModel):
    """
    Variational AutoEncoder (VAE) model.

    Inherits from AutoEncoderBaseModel and sets the estimator class to VAENet.
    """

    model_name = "vae"

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str],
        metric_name,
        metric_params,
        **params,
    ):
        """
        Initializes the VAEModel.

        Args:
            estimator_params (Dict[str, Any]): Parameters for the estimator.
            task (str): The task type.
            used_features (List[str]): List of feature names used in the model.
            metric_name: Name of the metric to be used.
            metric_params: Parameters for the metric.
            **params: Additional parameters.
        """
        super().__init__(
            estimator_params=estimator_params,
            task=task,
            used_features=used_features,
            metric_name=metric_name,
            metric_params=metric_params,
            **params,
        )
        self.estimator_class = VAENet


class AEModel(AutoEncoderBaseModel):
    """
    AutoEncoder (AE) model.

    Inherits from AutoEncoderBaseModel and sets the estimator class to AENet.
    """

    model_name = "ae"

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str],
        metric_name,
        metric_params,
        **params,
    ):
        """
        Initializes the AEModel.

        Args:
            estimator_params (Dict[str, Any]): Parameters for the estimator.
            task (str): The task type.
            used_features (List[str]): List of feature names used in the model.
            metric_name: Name of the metric to be used.
            metric_params: Parameters for the metric.
            **params: Additional parameters.
        """
        super().__init__(
            estimator_params=estimator_params,
            task=task,
            used_features=used_features,
            metric_name=metric_name,
            metric_params=metric_params,
            **params,
        )
        self.estimator_class = AENet


class VAENet(nn.Module):
    """
    Architecture of the Variational Autoencoder (VAE).

    This network consists of an encoder that maps input data to a latent space
    and a decoder that reconstructs the data from the latent representation.
    """

    def __init__(self, input_dim: int, latent_dim: int):
        """
        Initializes the VAENet architecture.

        Args:
            input_dim (int): Dimension of the input data.
            latent_dim (int): Dimension of the latent space.
        """
        super(VAENet, self).__init__()

        self.fc1 = nn.Linear(input_dim, 512)
        self.norm1 = nn.BatchNorm1d(512)
        self.fc2 = nn.Linear(512, 256)
        self.norm2 = nn.BatchNorm1d(256)
        self.fc3 = nn.Linear(256, 128)
        self.norm3 = nn.BatchNorm1d(128)

        self.fc_z_mean = nn.Linear(128, latent_dim)  # for z_mean
        self.fc_z_log_var = nn.Linear(128, latent_dim)  # for z_log_var

        self.fc4 = nn.Linear(latent_dim, 128)
        self.norm4 = nn.BatchNorm1d(128)
        self.fc5 = nn.Linear(128, 256)
        self.norm5 = nn.BatchNorm1d(256)
        self.fc6 = nn.Linear(256, 512)
        self.norm6 = nn.BatchNorm1d(512)
        self.fc7 = nn.Linear(512, input_dim)

    def encode(self, x):
        """
        Encodes the input data into mean and log variance of the latent distribution.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            tuple: Tuple containing z_mean and z_log_var tensors.
        """
        h1 = torch.relu(self.norm1(self.fc1(x)))
        h2 = torch.relu(self.norm2(self.fc2(h1)))
        h3 = torch.relu(self.norm3(self.fc3(h2)))

        z_mean = self.fc_z_mean(h3)
        z_log_var = self.fc_z_log_var(h3)
        return z_mean, z_log_var

    def reparameterize(self, z_mean, z_log_var):
        """
        Reparameterization trick to sample from the latent distribution.

        Args:
            z_mean (torch.Tensor): Mean of the latent distribution.
            z_log_var (torch.Tensor): Log variance of the latent distribution.

        Returns:
            torch.Tensor: Sampled latent vector.
        """
        std = torch.exp(0.5 * z_log_var)
        eps = torch.randn_like(std)
        return z_mean + eps * std

    def decode(self, z):
        """
        Decodes the latent vector back to the input space.

        Args:
            z (torch.Tensor): Latent vector.

        Returns:
            torch.Tensor: Reconstructed input tensor.
        """
        h4 = torch.relu(self.norm4(self.fc4(z)))
        h5 = torch.relu(self.norm5(self.fc5(h4)))
        h6 = torch.relu(self.norm6(self.fc6(h5)))
        return torch.sigmoid(self.fc7(h6))

    def forward(self, x):
        """
        Forward pass through the VAE network.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            tuple: Tuple containing reconstructed output, z_mean, and z_log_var.
        """
        z_mean, z_log_var = self.encode(x)
        z = self.reparameterize(z_mean, z_log_var)
        return self.decode(z), z_mean, z_log_var


class AENet(nn.Module):
    """
    Architecture of the AutoEncoder (AE).

    This network consists of an encoder that maps input data to a latent space
    and a decoder that reconstructs the data from the latent representation.
    """

    model_name = "ae"

    def __init__(self, input_size, latent_dim):
        """
        Initializes the AENet architecture.

        Args:
            input_size (int): Dimension of the input data.
            latent_dim (int): Dimension of the latent space.
        """
        super(AENet, self).__init__()
        # parameters
        self.input_size = input_size
        self.intermediate_size = 128
        self.latent_dim = latent_dim

        self.relu = torch.nn.ReLU()

        # encoder
        self.fc1 = torch.nn.Linear(self.input_size, self.intermediate_size)
        self.norm1 = nn.BatchNorm1d(self.intermediate_size)
        self.fc2 = torch.nn.Linear(self.intermediate_size, self.latent_dim)
        self.norm2 = nn.BatchNorm1d(self.latent_dim)

        # decoder
        self.fc3 = torch.nn.Linear(self.latent_dim, self.intermediate_size)
        self.norm3 = nn.BatchNorm1d(self.intermediate_size)
        self.fc4 = torch.nn.Linear(self.intermediate_size, self.input_size)

    def forward(self, x):
        """
        Forward pass through the AutoEncoder network.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Reconstructed input tensor.
        """
        hidden = self.norm1(self.fc1(x))
        hidden = self.relu(hidden)

        code = self.norm2(self.fc2(hidden))
        code = self.relu(code)

        hidden = self.norm3(self.fc3(code))
        hidden = self.relu(hidden)

        output = self.fc4(hidden)

        return output