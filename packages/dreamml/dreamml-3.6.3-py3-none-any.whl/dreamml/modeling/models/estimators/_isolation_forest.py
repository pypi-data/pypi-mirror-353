from typing import Tuple, Dict, Any, List, Optional
import logging
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from dreamml.modeling.models.estimators import BoostingBaseModel


class IForestModel(BoostingBaseModel):
    """Isolation Forest model with a standardized API for dreamml_base.

    This model is used for anomaly detection tasks and supports feature normalization.

    Attributes:
        model_name (str): Name of the algorithm ("iforest").
        params (Dict[str, Any]): Dictionary of hyperparameters.
        task (str): Name of the task (e.g., "anomaly_detection").
        used_features (List[str]): List of features selected based on specific metric values.
        estimator_class (Type[IsolationForest]): The class of the estimator.
        estimator (Optional[IsolationForest]): Instance of the trained model.
        categorical_features (List[str]): List of categorical features.
        verbose (int): Verbosity level.
        normalization_flag (bool): Flag to indicate if normalization should be applied.
        scaler (Optional[Pipeline]): Pipeline for data normalization.
        fitted (bool): Indicates whether the model has been trained.
    """

    model_name = "iforest"

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str],
        categorical_features: List[str],
        metric_name: str,
        metric_params: Dict[str, Any],
        weights: Optional[Any] = None,
        target_with_nan_values: bool = False,
        log_target_transformer: Optional[Any] = None,
        parallelism: int = -1,
        train_logger: Optional[logging.Logger] = None,
        **params,
    ):
        """Initializes the IForestModel with the provided parameters.

        Args:
            estimator_params (Dict[str, Any]): Dictionary of hyperparameters for the estimator.
            task (str): Name of the task (e.g., "anomaly_detection").
            used_features (List[str]): List of features selected based on specific metric values.
            categorical_features (List[str]): List of categorical features.
            metric_name (str): Name of the metric to evaluate.
            metric_params (Dict[str, Any]): Parameters for the metric.
            weights (Optional[Any], optional): Sample weights. Defaults to None.
            target_with_nan_values (bool, optional): Indicates if the target has NaN values. Defaults to False.
            log_target_transformer (Optional[Any], optional): Transformer for logging target. Defaults to None.
            parallelism (int, optional): Degree of parallelism. Defaults to -1.
            train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
            **params: Additional keyword arguments.
        """
        super().__init__(
            estimator_params,
            task,
            used_features,
            categorical_features,
            metric_name,
            metric_params,
            weights=weights,
            target_with_nan_values=target_with_nan_values,
            log_target_transformer=log_target_transformer,
            parallelism=parallelism,
            train_logger=train_logger,
            **params,
        )
        self.estimator_class = self._estimators.get(self.task)
        self.verbose = self.params.pop("verbose", 0)
        self.normalization_flag = self.params.pop("normalization_flag", False)
        self.scaler = self._norm_scaler_pipeline()

    @property
    def _estimators(self) -> Dict[str, Any]:
        """Retrieves the appropriate estimator class based on the task.

        Returns:
            Dict[str, Any]: A dictionary mapping task names to estimator classes.
        """
        estimators = {
            "anomaly_detection": IsolationForest,
        }
        return estimators

    def _norm_scaler_pipeline(self) -> Optional[Pipeline]:
        """Creates a normalization pipeline if normalization_flag is set.

        The pipeline includes StandardScaler followed by MinMaxScaler.

        Returns:
            Optional[Pipeline]: The normalization pipeline or None if normalization is not required.
        """
        if self.normalization_flag:
            return Pipeline(
                [("scaler_1", StandardScaler()), ("scaler_2", MinMaxScaler())]
            )

        self._logger.debug(f"normalization_flag: {self.normalization_flag}")
        return None

    def _pre_fit(self, data: pd.DataFrame, *eval_set: Tuple[pd.DataFrame, Optional[Any]]) -> pd.DataFrame:
        """Prepares the data before fitting the model.

        Validates the input data and sets up evaluation metrics if required.

        Args:
            data (pd.DataFrame): The training data.
            *eval_set (Tuple[pd.DataFrame, Optional[Any]]): Evaluation datasets.

        Returns:
            pd.DataFrame: The validated training data.
        """
        if self.eval_metric.is_resetting_indexes_required:
            self.eval_metric.set_indexes(train=data.index, valid=eval_set[0].index)

        data = self.validate_input_data(data)

        return data

    def fit(self, data: pd.DataFrame, target: Optional[Any], *eval_set: Tuple[pd.DataFrame, Optional[Any]]) -> None:
        """Trains the Isolation Forest model on the provided data.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (Optional[Any]): Target variable (should be None for anomaly detection).
            *eval_set (Tuple[pd.DataFrame, Optional[Any]]): Tuple containing validation data. The first element
                is the feature matrix, and the second element is None.

        Raises:
            ValueError: If the target is not None, since anomaly detection does not use target values.
        """
        data = self._pre_fit(data, *eval_set)

        if self.scaler is not None:
            self.scaler.fit(data.values)
            data = self.scaler.transform(data.values)

        params = {
            key: value
            for key, value in self.params.items()
            if key not in ["normalization_flag", "eval_metric", "objective"]
        }

        self.estimator = self.estimator_class(**params)
        self.estimator.fit(X=data, y=None)
        self.fitted = True

    def transform(self, data: pd.DataFrame) -> List[float]:
        """Applies the trained model to the provided data to generate anomaly scores.

        The model must be trained before calling this method.

        Args:
            data (pd.DataFrame): Feature matrix for prediction.

        Returns:
            List[float]: Anomaly scores for each sample in the data.

        Raises:
            ValueError: If the task is not supported or if the model has not been fitted.
        """
        data = self.validate_input_data(data)
        if self.scaler is not None:
            data = self.scaler.transform(data.values)

        if self.task == "anomaly_detection":
            prediction = self.estimator.decision_function(data)
        else:
            raise ValueError(f"Wrong task! {self.task}")
        return prediction.tolist()

    @staticmethod
    def _get_best_iteration(estimator) -> int:
        """Retrieves the best iteration of the estimator.

        Args:
            estimator: The trained estimator.

        Returns:
            int: The best iteration number.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError("The _get_best_iteration method is not implemented.")