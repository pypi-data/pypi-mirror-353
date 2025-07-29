import abc
from typing import Tuple, Callable
from copy import deepcopy
from abc import ABC
import numpy as np
import pandas as pd
from hyperopt import SparkTrials, STATUS_OK
from hyperopt import fmin, tpe

from dreamml.logging import get_logger
from dreamml.modeling.cv import make_cv
from dreamml.modeling.metrics import BaseMetric
from dreamml.modeling.models.estimators import BaseModel

_logger = get_logger(__name__)


class DistributedOptimizer(ABC):
    """
    Abstract base class for distributed hyperparameter optimizers.

    Args:
        model (BaseModel): The machine learning model to optimize.
        params_bounds (dict): Dictionary defining the bounds for each hyperparameter.
            Keys are hyperparameter names and values are tuples of (min, max).
        metric (BaseMetric): The metric to evaluate model performance.
        n_iter (int, optional): Number of optimization iterations. Defaults to 30.
        timeout (int, optional): Maximum time (in seconds) allowed for optimization. Defaults to 7200.
        seed (int, optional): Random seed for reproducibility. Defaults to 27.
        parallelism (int, optional): Number of parallel trials. Defaults to 5.

    Attributes:
        model (BaseModel): The machine learning model to optimize.
        optimizer (Any): The optimizer instance (initialized as None).
        metric (BaseMetric): The metric to evaluate model performance.
        maximize (bool): Flag indicating whether to maximize the metric.
        params_bounds (dict): Bounds for hyperparameters.
        init_points (int): Number of initial random evaluations.
        n_iter (int): Total number of optimization iterations.
        timeout (int): Maximum time allowed for optimization.
        seed (int): Random seed for reproducibility.
        X (pd.DataFrame): Feature matrix for training.
        y (pd.Series): Target vector for training.
        parallelism (int): Number of parallel trials.
        _logger (Logger): Logger instance for logging information.
    """

    def __init__(
        self,
        model: BaseModel,
        params_bounds: dict,
        metric: BaseMetric,
        n_iter: int = 30,
        timeout: int = 7200,
        seed: int = 27,
        parallelism: int = 5,
    ) -> None:
        self.model = model
        self.optimizer = None
        self.metric = metric
        self.maximize = self.metric.maximize
        self.params_bounds = params_bounds
        self.init_points = int(n_iter * 0.2)
        self.n_iter = n_iter
        self.timeout = timeout
        self.seed = seed
        self.X = None
        self.y = None
        self.parallelism = parallelism
        self._logger = model._logger or _logger

    def check_param_value(self, params: dict) -> dict:
        """
        Validates and adjusts hyperparameter values to ensure they are within acceptable ranges.

        Some hyperparameters are expected to be integers. This method converts them to integers
        if necessary. Additionally, it adjusts learning rate parameters to avoid zero values.

        Args:
            params (dict): Dictionary of hyperparameters where keys are parameter names
                and values are their corresponding values.

        Returns:
            dict: A validated and potentially modified dictionary of hyperparameters.

        Raises:
            None
        """
        check_params = [
            "max_depth",
            "num_leaves",
            "min_data_in_leaf",
            "min_child_samples",
            "subsample_for_bin",
            "n_estimators",
        ]
        for name in check_params:
            if params.get(name, None) is not None:
                params[name] = int(params[name])

        eps = 1e-5
        for lr_param in ["learning_rate", "lr"]:
            if lr_param in params and params[lr_param] == 0:
                params[lr_param] += eps
                self._logger.debug(
                    f"Hyperopt {lr_param} | {params[lr_param] - eps} -> {params[lr_param]}"
                )
        return params

    @abc.abstractmethod
    def fit(self, data: pd.DataFrame, target: pd.Series, eval_sets: dict = None):
        """
        Abstract method to train the optimizer with the provided data.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            eval_sets (dict, optional): Evaluation datasets for validation. Defaults to None.

        Returns:
            None

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        pass


class DistributedOptimizationModel(DistributedOptimizer):
    """
    Distributed hyperparameter optimizer using Hyperopt for dreamml_base models.

    This class leverages Hyperopt to perform distributed optimization of machine learning
    model hyperparameters based on a predefined parameter space and evaluation metric.

    Args:
        model (BaseModel): Instance of the model with a standardized API for DS-Template.
        params_bounds (dict): Dictionary defining the bounds for each hyperparameter.
            Keys are hyperparameter names and values are tuples of (min, max).
        metric (BaseMetric): The metric to evaluate model performance.
        n_iter (int, optional): Number of optimization iterations. Defaults to 30.
        timeout (int, optional): Maximum time (in seconds) allowed for optimization. Defaults to 7200.
        seed (int, optional): Random seed for reproducibility. Defaults to 27.
        parallelism (int, optional): Number of parallel trials. Defaults to 5.

    Attributes:
        init_points (int): Number of initial random evaluations (20% of n_iter).
        optimizer (Any): Optimizer instance (currently not initialized).
    """

    def _objective(self, eval_sets: dict) -> Callable[[dict], dict]:
        """
        Closure function to create an objective function for HyperOpt optimization.

        This function defines how each set of hyperparameters is evaluated using the validation set.

        Args:
            eval_sets (dict): Dictionary with keys as dataset names and values as tuples containing
                feature matrices and target vectors.

        Returns:
            Callable[[dict], dict]: A function that HyperOpt will minimize/maximize.
        """

        def objective_split(params: dict) -> dict:
            """
            Objective function for HyperOpt to evaluate model performance.

            This function trains the model with the given hyperparameters and evaluates it
            on the validation set.

            Args:
                params (dict): Dictionary of hyperparameters to optimize.

            Returns:
                dict: Dictionary containing the loss (to minimize) and the status.

            Raises:
                None
            """
            valid_params = self.check_param_value(params)

            estimator = deepcopy(self.model)
            estimator.params.update(valid_params)
            estimator.fit(self.X, self.y, *eval_sets["valid"])
            y_pred = estimator.transform(eval_sets["valid"][0])

            score = self.metric(eval_sets["valid"][1], y_pred)
            self._logger.info("=" * 120)
            return {"loss": -score if self.maximize else score, "status": STATUS_OK}

        return objective_split

    def fit(
        self, data: pd.DataFrame, target: pd.Series, eval_sets: dict = None
    ) -> None:
        """
        Trains the optimizer using the provided data and evaluates hyperparameters.

        This method runs the HyperOpt optimization process to find the best set of hyperparameters
        within the defined parameter bounds.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            eval_sets (dict, optional): Evaluation datasets for validation. Defaults to None.

        Returns:
            None

        Raises:
            None
        """
        self._logger.info("*" * 127)
        self._logger.info("Start fitting optimizer")
        self._logger.info("*" * 127)
        self.X, self.y = data, target
        algo, spark_trials = tpe.suggest, SparkTrials(parallelism=self.parallelism)
        objective = self._objective(eval_sets=eval_sets)

        best_hyperparams = fmin(
            fn=objective,
            space=self.params_bounds,
            trials=spark_trials,
            algo=algo,
            max_evals=self.n_iter,
            rstate=np.random.default_rng(self.seed),
        )
        best_hyperparams = self.check_param_value(best_hyperparams)
        self.model.params.update(best_hyperparams)
        self.model.fit(self.X, self.y, *eval_sets["valid"])
        self.model.evaluate_and_print(**eval_sets)
        self._logger.info("*" * 127)


class DistributedOptimizationCVModel(DistributedOptimizer):
    """
    Distributed hyperparameter optimizer using Hyperopt with cross-validation for dreamml_base models.

    This class extends the DistributedOptimizer to incorporate cross-validation during the
    hyperparameter optimization process, providing a more robust evaluation of model performance.

    Args:
        model (BaseModel): Instance of the model with a standardized API for DS-Template.
        params_bounds (dict): Dictionary defining the bounds for each hyperparameter.
            Keys are hyperparameter names and values are tuples of (min, max).
        metric (BaseMetric): The metric to evaluate model performance.
        cv (Any): Cross-validation strategy.
        splitter_df (pd.DataFrame): DataFrame used for splitting data in cross-validation.
        n_iter (int, optional): Number of optimization iterations. Defaults to 30.
        timeout (int, optional): Maximum time (in seconds) allowed for optimization. Defaults to 7200.
        seed (int, optional): Random seed for reproducibility. Defaults to 27.
        parallelism (int, optional): Number of parallel trials. Defaults to 5.

    Attributes:
        cv (Any): Cross-validation strategy.
        splitter_df (pd.DataFrame): DataFrame used for splitting data in cross-validation.
        mean_score (float): Mean score achieved during cross-validation.
    """

    def __init__(
        self,
        model,
        params_bounds: dict,
        metric: BaseMetric,
        cv,
        splitter_df: pd.DataFrame,
        n_iter: int = 30,
        timeout: int = 7200,
        seed: int = 27,
        parallelism: int = 5,
    ) -> None:
        super(DistributedOptimizationCVModel, self).__init__(
            model,
            params_bounds,
            metric=metric,
            n_iter=n_iter,
            timeout=timeout,
            seed=seed,
            parallelism=parallelism,
        )
        self.cv = cv
        self.splitter_df = splitter_df
        self.mean_score = None

    def _objective(self) -> Callable[[dict], dict]:
        """
        Creates an objective function for HyperOpt optimization with cross-validation.

        This function defines how each set of hyperparameters is evaluated using cross-validation.

        Returns:
            Callable[[dict], dict]: A function that HyperOpt will minimize/maximize.
        """

        def objective_cv(params) -> dict:
            """
            Objective function for HyperOpt to evaluate model performance using cross-validation.

            This function trains the model with the given hyperparameters and evaluates it
            using cross-validation.

            Args:
                params (dict): Dictionary of hyperparameters to optimize.

            Returns:
                dict: Dictionary containing the loss (to minimize) and the status.

            Raises:
                None
            """
            valid_params = self.check_param_value(params)

            estimator = deepcopy(self.model)
            estimator.params.update(valid_params)

            _, score, _, _, _, _ = make_cv(
                estimator=estimator,
                x_train_cv=self.X,
                y_train_cv=self.y,
                cv=self.cv,
                splitter_df=self.splitter_df,
                metric=self.metric,
            )
            return {"loss": -score if self.maximize else score, "status": STATUS_OK}

        return objective_cv

    def fit(
        self, data: pd.DataFrame, target: pd.Series, eval_sets: dict = None
    ) -> dict:
        """
        Trains the optimizer using the provided data and evaluates hyperparameters with cross-validation.

        This method runs the HyperOpt optimization process with cross-validation to find the best
        set of hyperparameters within the defined parameter bounds.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            eval_sets (dict, optional): Evaluation datasets for validation. Defaults to None.

        Returns:
            dict: The best hyperparameters found during optimization.

        Raises:
            None
        """
        self._logger.info("*" * 127 + "\nStart fitting optimizer\n" + "*" * 127)
        self.X, self.y = data, target
        algo, spark_trials = tpe.suggest, SparkTrials(parallelism=self.parallelism)
        objective = self._objective()

        best_hyperparams = fmin(
            fn=objective,
            space=self.params_bounds,
            trials=spark_trials,
            algo=algo,
            max_evals=self.n_iter,
            timeout=self.timeout,
            rstate=np.random.default_rng(self.seed),
        )
        best_hyperparams = self.check_param_value(best_hyperparams)
        self.model.params.update(best_hyperparams)

        estimators, score, _, _, _, _ = make_cv(
            estimator=self.model,
            x_train_cv=self.X,
            y_train_cv=self.y,
            cv=self.cv,
            splitter_df=self.splitter_df,
            metric=self.metric,
        )
        self.mean_score = score
        self._logger.info("*" * 127)
        return best_hyperparams