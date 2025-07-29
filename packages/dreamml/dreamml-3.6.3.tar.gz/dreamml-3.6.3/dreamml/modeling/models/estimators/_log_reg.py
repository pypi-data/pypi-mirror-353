import logging
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

from sklearn.linear_model import LogisticRegression

from dreamml.modeling.models.estimators import BaseModel
from dreamml.features.feature_extraction._transformers import LogTargetTransformer


class LogRegModel(BaseModel):
    """Logistic Regression Model with a standardized API for dreamml_base.

    This class encapsulates a logistic regression model, providing methods for training
    and making predictions. It integrates with the dreamml_base framework and supports
    feature selection, handling categorical features, and applying target transformations.

    Attributes:
        model_name (str): Name of the model, set to "log_reg".
        params (dict): Dictionary of hyperparameters.
        task (str): Name of the task (e.g., "regression", "binary", "multiclass").
        used_features (List[str]): List of features selected based on specific metric values.
        estimator_class: Class of the model estimator.
        estimator: Trained model instance.
        categorical_features (List[str]): List of categorical features.
        fitted (bool): Indicates whether the model has been fitted.
    """

    model_name = "log_reg"

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
        log_target_transformer: Optional[LogTargetTransformer] = None,
        parallelism: int = -1,
        train_logger: Optional[logging.Logger] = None,
        **params: Any,
    ):
        """Initializes the LogRegModel with specified parameters.

        Args:
            estimator_params (Dict[str, Any]): Dictionary of hyperparameters for the estimator.
            task (str): Name of the task (e.g., "regression", "binary", "multiclass").
            used_features (List[str]): List of features selected based on specific metric values.
            categorical_features (List[str]): List of categorical features.
            metric_name (str): Name of the metric used for evaluation.
            metric_params (Dict[str, Any]): Dictionary of parameters for the metric.
            weights (Optional[Any], optional): Weights for the model. Defaults to None.
            target_with_nan_values (bool, optional): Indicates if the target contains NaN values. Defaults to False.
            log_target_transformer (Optional[LogTargetTransformer], optional): Transformer for target logging. Defaults to None.
            parallelism (int, optional): Degree of parallelism. Defaults to -1.
            train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
            **params (Any): Additional keyword parameters.
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
        self.estimator_class = self._estimators.get(self.task, LogisticRegression)

    @property
    def _estimators(self) -> Dict[str, Any]:
        """Dictionary of sklearn wrappers over Logistic Regression.

        Returns:
            Dict[str, Any]: A dictionary where the key is the task name and the value is the corresponding estimator class.
        """
        estimators = {
            "classification": LogisticRegression,
        }
        return estimators

    def _create_eval_set(
        self,
        data: pd.DataFrame,
        target: pd.Series,
        *eval_set: Tuple[pd.DataFrame, pd.Series],
        asnumpy: bool = False
    ) -> List[Tuple[pd.DataFrame, pd.Series]]:
        """Creates an evaluation set in sklearn format.

        If an evaluation set is provided, it validates and returns it. Otherwise, it uses the provided data and target.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            *eval_set (Tuple[pd.DataFrame, pd.Series]): Optional evaluation dataset.
            asnumpy (bool, optional): Whether to return the evaluation set as NumPy arrays. Defaults to False.

        Returns:
            List[Tuple[pd.DataFrame, pd.Series]]: List containing tuples of evaluation data and target.
        """
        data = self.validate_input_data(data)
        if eval_set:
            valid_data = self.validate_input_data(eval_set[0])
            return [(valid_data, eval_set[1])]

        return [(data, target)]

    def fit(self, data: pd.DataFrame, target: pd.Series, *eval_set: Tuple[pd.DataFrame, pd.Series]) -> "LogRegModel":
        """Trains the logistic regression model on the provided data and target.

        Args:
            data (pd.DataFrame): Feature matrix for training, shape [n_samples, n_features].
            target (pd.Series): Target vector for training, shape [n_samples].
            *eval_set (Tuple[pd.DataFrame, pd.Series]): Optional tuple containing evaluation data and target.

        Returns:
            LogRegModel: The trained model instance.

        Raises:
            ValueError: If the input data is invalid or fitting fails.
        """
        params = {
            key: value
            for key, value in self.params.items()
            if key
            in [
                "penalty",
                "dual",
                "tol",
                "C",
                "fit_intercept",
                "intercept_scaling",
                "class_weight",
                "random_state",
                "solver",
                "max_iter",
                "multi_class",
                "verbose",
                "warm_start",
                "n_jobs",
                "l1_ratio",
            ]
        }
        if "n_jobs" in params and params["n_jobs"] == 0:
            params["n_jobs"] = 1

        self.estimator = self.estimator_class(**params)
        data = self._fill_nan_values(data)
        self.estimator.fit(X=data, y=target)
        self.fitted = True

        return self

    def transform(self, data: pd.DataFrame) -> Any:
        """Applies the trained model to the provided data to generate predictions.

        The model must be fitted before calling this method. If the model is not fitted,
        an exception will be raised.

        Args:
            data (pd.DataFrame): Feature matrix for prediction, shape [n_samples, n_features].

        Returns:
            Any: Prediction results. Returns a probability vector for binary classification
                 or a probability matrix for multiclass classification.

        Raises:
            NotFittedError: If the model has not been fitted.
            ValueError: If the input data is invalid.
        """
        self.check_is_fitted
        data = self.validate_input_data(data)
        data = self._fill_nan_values(data)
        prediction = self.estimator.predict_proba(data)
        if self.task == "binary":
            return prediction[:, 1]
        elif self.task == "multiclass":
            return prediction

    @staticmethod
    def _get_best_iteration(estimator: Any) -> int:
        """Retrieves the best iteration from the estimator.

        Args:
            estimator (Any): The trained estimator.

        Returns:
            int: The best iteration number.
        """
        return 1

    @property
    def best_iteration(self) -> int:
        """Gets the best iteration number.

        Returns:
            int: The best iteration number, currently fixed at 1.
        """
        return 1