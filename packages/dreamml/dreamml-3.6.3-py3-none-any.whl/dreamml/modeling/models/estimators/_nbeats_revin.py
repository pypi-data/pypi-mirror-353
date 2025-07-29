import numpy as np
from typing import Dict, Any
import torch
from torch import nn
from torch.nn.functional import mse_loss, l1_loss

from dreamml.logging import get_logger
from dreamml.modeling.models.estimators import BaseModel
from dreamml.modeling.models.estimators._nbeats import NBeatsNet
from dreamml.modeling.models.estimators._revin import RevIN

from sklearn.metrics import mean_absolute_percentage_error

_logger = get_logger(__name__)


class NBEATS_REVIN_Model(BaseModel, nn.Module):
    """
    NBEATS_REVIN_Model provides a standardized API for dreamml_base, integrating N-BEATS with RevIN normalization.

    This model is designed for time series forecasting and anomaly detection tasks. It leverages the N-BEATS
    architecture enhanced with RevIN normalization layers to improve forecasting accuracy and robustness.

    Attributes:
        model_name (str): The name of the model.
        estimator_class (BaseModel): The class of the underlying estimator.
        split_by_group (bool): Indicates whether to split data by groups.
        estimator (callable): The trained estimator instance.
        horizon (int): The forecasting horizon.
        nb_blocks_per_stack (int): Number of blocks per stack in the N-BEATS model.
        hidden_layer_units (int): Number of units in the hidden layers.
        backcast_length (int): Length of the input sequence for backcasting.
        sequence (int): Length of the sequence for anomaly detection.
        batch_size (int): Batch size for training.
        n_epochs (int): Number of training epochs.
        start_learning_rate (float): Initial learning rate.
        th_ad (float): Threshold for anomaly detection.
        revin_layer (RevIN): RevIN normalization layer.
        loss (callable): Loss function for training.
        optimiser (torch.optim.Optimizer): Optimizer for training.
        scheduler (torch.optim.lr_scheduler): Learning rate scheduler.
        train_global_loss (list): History of training loss.
        test_global_loss (list): History of validation loss.
        fitted (bool): Indicates whether the model has been fitted.
    """

    model_name = "nbeats_revin"

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        metric_name=None,
        metric_params: Dict = None,
        **params,
    ):
        """
        Initializes the NBEATS_REVIN_Model with the provided parameters.

        Args:
            estimator_params (Dict[str, Any]): Dictionary of hyperparameters for the estimator.
            task (str): The name of the task to be solved.
            metric_name (str, optional): The name of the evaluation metric.
            metric_params (Dict, optional): Parameters for the evaluation metric.
            **params: Additional optional parameters.

        """
        nn.Module.__init__(self)
        BaseModel.__init__(
            self,
            estimator_params=estimator_params,
            task=task,
            metric_name=metric_name,
            metric_params=metric_params,
            **params,
        )
        self.estimator_class = self._estimators.get(self.task)
        self.split_by_group = self.params["split_by_group"]

        # model params
        self.device = self.params["device"]
        self.horizon = self.params["horizon"]
        self.nb_blocks_per_stack = self.params["nb_blocks_per_stack"]
        self.hidden_layer_units = self.params["hidden_layer_units"]
        self.backcast_length = self.params["backcast_length"]
        self.sequence = self.params["sequence"]

        # fit params
        self.batch_size = self.params["batch_size"]
        self.n_epochs = self.params["n_epochs"]
        self.start_learning_rate = self.params["learning_rate"]

        self.th_ad = self.params["th_ad"]

        self.revin_layer = RevIN(1)
        self.loss = None
        self.optimiser = None
        self.scheduler = None
        self.train_global_loss = None
        self.test_global_loss = None
        self.fitted = False

    @property
    def _estimators(self) -> Dict:
        """
        Retrieves a dictionary of estimators based on the task.

        Returns:
            Dict: A dictionary where keys are task names and values are the corresponding estimator classes.
        """
        estimators = {
            "amts": NBeatsNet,
            "amts_ad": NBeatsNet,
        }
        return estimators

    def get_model_params(self) -> Dict:
        """
        Creates parameters for initializing the N-BEATS model.

        Returns:
            Dict: A dictionary of parameters for the N-BEATS model initialization.
        """
        return {
            "device": self.device,
            "stack_types": (NBeatsNet.TREND_BLOCK, NBeatsNet.SEASONALITY_BLOCK),
            "nb_blocks_per_stack": self.nb_blocks_per_stack,
            "forecast_length": self.horizon,
            "backcast_length": self.backcast_length,
            "thetas_dim": (4, 8),
            "share_weights_in_stack": False,
            "hidden_layer_units": self.hidden_layer_units,
            "nb_harmonics": None,
        }

    def get_model_params_ad(self) -> Dict:
        """
        Creates parameters for initializing the N-BEATS model for Anomaly Detection.

        Returns:
            Dict: A dictionary of parameters for the N-BEATS model initialization tailored for anomaly detection.
        """
        return {
            "device": self.device,
            "stack_types": (NBeatsNet.TREND_BLOCK, NBeatsNet.SEASONALITY_BLOCK),
            "nb_blocks_per_stack": self.nb_blocks_per_stack,
            "forecast_length": self.sequence,
            "backcast_length": self.sequence,
            "thetas_dim": (4, 8),
            "share_weights_in_stack": False,
            "hidden_layer_units": self.hidden_layer_units,
            "nb_harmonics": None,
        }

    def get_model_fit_params(self, data) -> Dict:
        """
        Creates parameters for training the model.

        Args:
            data: Training data containing 'X_train', 'y_train', and 'ids_train'.

        Returns:
            Dict: A dictionary of parameters required for fitting the model.
        """
        return {
            "x_train": data["X_train"],
            "y_train": data["y_train"],
            "ids_train": data["ids_train"],
            "loss": "mse",
            "lr": self.start_learning_rate,
            "batch_size": self.batch_size,
            "n_epochs": self.n_epochs,
            "validation_data": [data["X_test"], data["y_test"], data["ids_test"]],
        }

    def get_model_final_fit_params(self, data) -> Dict:
        """
        Creates parameters for the final training of the model.

        Args:
            data: Final training data containing 'X' and 'y'.

        Returns:
            Dict: A dictionary of parameters required for the final fitting of the model.
        """
        return {
            "x_train": data["X"],
            "y_train": data["y"],
            "ids_train": data["ids"],
            "loss": "mse",
            "lr": self.start_learning_rate,
            "batch_size": self.batch_size,
            "n_epochs": self.n_epochs,
            "validation_data": None,
        }

    def get_model_fit_params_ad(self, data) -> Dict:
        """
        Creates parameters for training the model specifically for Anomaly Detection.

        Args:
            data: Training data containing 'X' and 'y'.

        Returns:
            Dict: A dictionary of parameters required for fitting the model for anomaly detection.
        """
        return {
            "x_train": data["X"],
            "y_train": data["y"],
            "ids_train": data["ids"],
            "loss": "mse",
            "lr": self.start_learning_rate,
            "batch_size": self.batch_size,
            "n_epochs": self.n_epochs,
            "validation_data": None,
        }

    def data_generator(self, x, y, ids, size):
        """
        Generates batches of data for model training.

        Args:
            x (np.array): Input features.
            y (np.array): Target values.
            ids (np.array): Identifiers for the samples.
            size (int): Batch size.

        Yields:
            Tuple[np.array, np.array, np.array]: A batch of (x, y, ids).
        """
        assert len(x) == len(y) == len(ids)
        batches = []
        for ii in range(0, len(x), size):
            x_batch = x[ii : ii + size]
            y_batch = y[ii : ii + size]
            id_batch = ids[ii : ii + size]
            batches.append((x_batch, y_batch, id_batch))
        for batch in batches:
            yield batch

    def squeeze_last_dim(self, tensor):
        """
        Removes the last dimension of a tensor if it is of size 1.

        Args:
            tensor (torch.Tensor): The input tensor.

        Returns:
            torch.Tensor: The tensor with the last dimension squeezed if applicable.
        """
        if len(tensor.shape) == 3 and tensor.shape[-1] == 1:
            return tensor[..., 0]
        return tensor

    def compile(self, loss, lr):
        """
        Configures the loss function, optimizer, and learning rate scheduler for training.

        Args:
            loss (str): The type of loss function to use ('mse' or 'mae').
            lr (float): The learning rate.

        Raises:
            ValueError: If an unsupported loss type is provided.
        """
        if loss == "mse":
            self.loss = mse_loss
        elif loss == "mae":
            self.loss = l1_loss
        else:
            raise ValueError(f"Unsupported loss type: {loss}")

        self.optimiser = torch.optim.AdamW(params=self.parameters(), lr=lr)
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimiser, mode="min", factor=0.5, patience=20
        )

    def forward(self, x_in, ids):
        """
        Defines the forward pass of the model.

        Args:
            x_in (torch.Tensor): Input tensor.
            ids (np.array): Array of sample identifiers.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Tuple containing the backcast and forecast tensors.
        """
        ids_tensor = torch.tensor(ids).float().view(ids.shape[0], 1)
        ids_tensor = ids_tensor.to(self.device)
        x = self.revin_layer(x_in, "norm")
        b, x_out = self.estimator(x, ids_tensor)
        out = self.revin_layer(x_out, "denorm")
        return b, out

    def _fit(
        self,
        x_train,
        y_train,
        ids_train,
        loss,
        lr,
        batch_size,
        n_epochs,
        validation_data=None,
    ):
        """
        Trains the model on the provided training data.

        Args:
            x_train (np.array): Training input features.
            y_train (np.array): Training target values.
            ids_train (np.array): Training sample identifiers.
            loss (str): Loss function to use ('mse' or 'mae').
            lr (float): Learning rate.
            batch_size (int): Size of each training batch.
            n_epochs (int): Number of training epochs.
            validation_data (Tuple[np.array, np.array, np.array], optional): Validation data.

        Raises:
            AssertionError: If the lengths of x_train, y_train, and ids_train do not match.
        """
        self.compile(loss, lr)

        self.train_global_loss = []
        self.test_global_loss = []

        for epoch in range(n_epochs):
            self.train()
            train_loss = []
            for x_train_batch, y_train_batch, id_batch in self.data_generator(
                x_train, y_train, ids_train, batch_size
            ):
                self.optimiser.zero_grad()
                _, forecast = self(
                    torch.tensor(x_train_batch, dtype=torch.float, device=self.device),
                    id_batch,
                )
                loss_value = self.loss(
                    forecast,
                    torch.tensor(y_train_batch, dtype=torch.float, device=self.device),
                )
                train_loss.append(loss_value.item())
                loss_value.backward()
                self.optimiser.step()
            train_loss = np.mean(train_loss)
            self.train_global_loss.append(train_loss)

            test_loss = -1
            if validation_data is not None:
                x_test, y_test, ids_test = validation_data
                self.eval()
                _, forecast = self(
                    torch.tensor(x_test, dtype=torch.float).to(self.device), ids_test
                )
                test_loss = self.loss(
                    forecast,
                    self.squeeze_last_dim(
                        torch.tensor(y_test, dtype=torch.float).to(self.device)
                    ),
                ).item()

                self.test_global_loss.append(test_loss)

            if validation_data is not None:
                self.scheduler.step(test_loss)
            else:
                self.scheduler.step(train_loss)

            if epoch % 10 == 0:
                print(f"Epoch {str(epoch + 1).zfill(len(str(n_epochs)))}/{n_epochs}")
                print(
                    f"[==============================] - "
                    f"loss: {train_loss:.4f} - val_loss: {test_loss:.4f} "
                    f"lr: {self.scheduler._last_lr[0]}"
                )

    def fit(self, data: Dict, final=False):
        """
        Wrapper function to train the model.

        Args:
            data (Dict): Dictionary containing training data.
            final (bool, optional): Indicator for final model training.

        Raises:
            KeyError: If the task is not supported.
        """
        if self.task == "amts":
            model_params = self.get_model_params()
            if final:
                fit_params = self.get_model_final_fit_params(data)
            else:
                fit_params = self.get_model_fit_params(data)
        elif self.task == "amts_ad":
            model_params = self.get_model_params_ad()
            fit_params = self.get_model_fit_params_ad(data)
        else:
            raise KeyError(f"Unsupported task: {self.task}")

        self.estimator = self.estimator_class(**model_params)
        self._fit(**fit_params)

        self.fitted = True

    def predict(self, x, ids, return_ad_loss=False):
        """
        Generates predictions from the model.

        Args:
            x (np.array): Input features, shape (batch_size, sequence_length).
            ids (np.array): Sample identifiers, shape (batch_size,).
            return_ad_loss (bool, optional): If True, returns anomaly detection loss.

        Returns:
            np.array: Forecasted values or anomaly detection losses.

        Raises:
            RuntimeError: If the model has not been fitted.
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before prediction.")

        self.eval()
        with torch.no_grad():
            b, f = self(torch.tensor(x, dtype=torch.float).to(self.device), ids)
            if return_ad_loss:
                loss_list = []
                x = x.reshape(-1)
                f = f.reshape(-1)
                for _x, _f in zip(x, f):
                    loss = self.loss(
                        _f, torch.tensor(_x, dtype=torch.float, device=self.device)
                    )
                    loss = loss.detach().cpu().numpy().item()
                    loss_list.append(loss)
                return np.array(loss_list)
            b, f = b.detach().cpu().numpy(), f.detach().cpu().numpy()
            return f.reshape(-1)

    def change_forecast_ad(self, forecast):
        """
        Converts forecasted losses into binary anomaly marks based on a threshold.

        Args:
            forecast (np.array): Array of loss values.

        Returns:
            np.array: Binary array indicating anomalies (1) or normal (0).
        """
        forecast_ad = []
        for i in forecast:
            if i > self.th_ad:
                forecast_ad.append(1)
            else:
                forecast_ad.append(0)
        forecast_ad = np.array(forecast_ad)
        return forecast_ad

    def transform(
        self, data: Dict, return_ad_mark=False, return_ad_loss=False
    ) -> Dict[str, np.array]:
        """
        Applies the trained model to the provided data.

        The model must be fitted before calling this method. If not, an exception is raised.

        Args:
            data (Dict): Dictionary containing input data with keys like 'X' and 'ids'.
            return_ad_mark (bool, optional): Whether to return anomaly detection marks.
            return_ad_loss (bool, optional): Whether to return anomaly detection losses.

        Returns:
            Dict[str, np.array]: Dictionary mapping segment names to their forecasts or anomaly detections.

        Raises:
            RuntimeError: If the model has not been fitted.
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before transformation.")

        forecast_dict = {}

        if self.split_by_group:
            for x, ids in zip(data["X"], data["ids"]):
                x = x.reshape(1, -1)
                ids = np.array([ids])
                forecast = self.predict(x=x, ids=ids, return_ad_loss=return_ad_loss)
                if return_ad_mark:
                    forecast = (
                        self.change_forecast_ad(forecast)
                        if self.task == "amts_ad"
                        else forecast
                    )
                forecast_dict[f"segment_{ids[0]}"] = forecast
        else:
            forecast = self.predict(
                x=data["X"], ids=data["ids"], return_ad_loss=return_ad_loss
            )
            if return_ad_mark:
                forecast = (
                    self.change_forecast_ad(forecast)
                    if self.task == "amts_ad"
                    else forecast
                )
            forecast_dict[f"segment_{data['ids'][0]}"] = forecast

        return forecast_dict

    def evaluate_and_print(self, data: Dict):
        """
        Evaluates the model on the provided test data and prints the Mean Absolute Percentage Error (MAPE).

        Args:
            data (Dict): Dictionary containing test data with keys 'X_test', 'y_test', and 'ids_test'.

        Raises:
            KeyError: If required keys are missing in the data dictionary.
        """
        if "y_test" not in data or "X_test" not in data or "ids_test" not in data:
            raise KeyError("Data must contain 'X_test', 'y_test', and 'ids_test' keys.")

        y = data["y_test"]
        data["X"] = data.pop("X_test")
        data["ids"] = data.pop("ids_test")

        forecast_dict = self.transform(data)
        for segment_y, (segment_name, forecast) in zip(y, forecast_dict.items()):
            loss = mean_absolute_percentage_error(segment_y, forecast)
            print(f"segment: {segment_name}, loss mape: {loss}")