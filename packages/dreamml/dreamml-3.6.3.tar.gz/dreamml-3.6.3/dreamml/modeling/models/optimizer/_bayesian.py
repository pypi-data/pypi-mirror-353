"""
Module implementing Bayesian Optimization for ML models with a standardized API for dreamml_base.

Available classes:
- BayesianOptimizator: Implements the Bayesian Optimization algorithm.
- BayesianOptimizationModel: Bayesian optimization tailored for dreamml_base models.
- CVBayesianOptimizationModel: Cross-validated Bayesian optimization for dreamml_base models.
"""

from typing import Tuple

import pandas as pd
from bayes_opt import BayesianOptimization

from dreamml.logging import get_logger
from dreamml.modeling.models.estimators import BoostingBaseModel
from dreamml.modeling.cv import make_cv
from dreamml.modeling.metrics import BaseMetric

_logger = get_logger(__name__)


class BayesianOptimizator:
    """Implements the Bayesian Optimization algorithm for hyperparameter tuning.

    Attributes:
        model (BoostingBaseModel): The model to be optimized.
        params_bounds (dict): Bounds for the hyperparameters.
        _logger (Logger): Logger instance for logging information.
    """

    def __init__(self, params_bounds: dict, model: BoostingBaseModel) -> None:
        """
        Initializes the BayesianOptimizator with parameter bounds and the model.

        Args:
            params_bounds (dict): A dictionary where keys are parameter names and values are tuples of (min, max).
            model (BoostingBaseModel): The machine learning model to be optimized.
        """
        self.model = model
        self.params_bounds = params_bounds
        self._logger = model._logger or _logger

    @staticmethod
    def check_param_value(params: dict) -> dict:
        """Validates and adjusts hyperparameter values.

        Ensures that certain hyperparameters are integers. If a hyperparameter that requires
        an integer value is provided as a float or another type, it is converted to an integer.

        Args:
            params (dict): Dictionary of hyperparameters with their values.

        Returns:
            dict: Validated and possibly adjusted dictionary of hyperparameters.
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
        return params


class BayesianOptimizationModel(BayesianOptimizator):
    """Bayesian Optimization for ML models within the dreamml_base framework.

    This class optimizes hyperparameters of a BoostingBaseModel using Bayesian Optimization.

    Attributes:
        metric (BaseMetric): Metric used to evaluate model performance.
        optimizer (BayesianOptimization): Instance of the Bayesian optimizer.
        train_set (Tuple[pd.DataFrame, pd.Series]): Training data and targets.
        maximize (bool): Flag indicating whether to maximize or minimize the metric.
        eval_set (Tuple[pd.DataFrame, pd.Series]): Evaluation data and targets.
        init_points (int): Number of initial random evaluations.
        n_iter (int): Total number of optimization iterations.
        seed (int): Random seed for reproducibility.
    """

    def __init__(
        self,
        model: BoostingBaseModel,
        metric: BaseMetric,
        eval_set: Tuple[pd.DataFrame, pd.Series],
        params_bounds: dict,
        maximize: bool = True,
        n_iter: int = 30,
        seed: int = 27,
    ) -> None:
        """
        Initializes the BayesianOptimizationModel with necessary parameters.

        Args:
            model (BoostingBaseModel): The model to be optimized.
            metric (BaseMetric): The metric used to evaluate model performance.
            eval_set (Tuple[pd.DataFrame, pd.Series]): Evaluation dataset (features and targets).
            params_bounds (dict): Bounds for the hyperparameters.
            maximize (bool, optional): Whether to maximize the metric. Defaults to True.
            n_iter (int, optional): Number of optimization iterations. Defaults to 30.
            seed (int, optional): Random seed for reproducibility. Defaults to 27.
        """
        super().__init__(params_bounds, model)
        self.metric = metric
        self.optimizer = None
        self.train_set = None
        self.maximize = maximize
        self.eval_set = eval_set
        self.init_points = int(n_iter * 0.2)
        self.n_iter = n_iter
        self.seed = seed

    def objective(self, **fit_params) -> float:
        """Objective function for Bayesian Optimization.

        Updates the model with the provided hyperparameters, fits it on the training set,
        evaluates it on the evaluation set, and returns the metric value.

        Args:
            **fit_params: Arbitrary keyword arguments for model hyperparameters.

        Returns:
            float: The evaluated metric value. Returns negative metric if minimizing.
        """
        valid_params = self.check_param_value(fit_params)
        params = self.model.params
        params.update(valid_params)

        self.model.params = params
        self.model.fit(*self.train_set, *self.eval_set)
        y_pred = self.model.transform(self.eval_set[0])
        self._logger.info("=" * 78)
        if self.maximize:
            return self.metric(self.eval_set[1], y_pred)
        else:
            return -self.metric(self.eval_set[1], y_pred)

    def fit(self, data: pd.DataFrame, target: pd.Series) -> None:
        """Fits the Bayesian optimizer to the provided data.

        Initializes the optimizer, performs the optimization process, and updates the model
        with the best-found hyperparameters.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): True target values for training.

        Raises:
            ValueError: If the provided data and target have incompatible shapes.
        """
        self.train_set = (data, target)
        self.optimizer = BayesianOptimization(
            self.objective, self.params_bounds, random_state=self.seed
        )
        self.optimizer.maximize(
            init_points=self.init_points, n_iter=self.n_iter, alpha=1e-6, acq="ucb", xi=0.0
        )
        max_params = self.optimizer.max["params"]
        max_params = self.check_param_value(max_params)
        self.model.params.update(max_params)
        self.model.fit(*self.train_set, *self.eval_set)


class CVBayesianOptimizationModel(BayesianOptimizator):
    """Cross-Validated Bayesian Optimization for ML models within the dreamml_base framework.

    This class performs Bayesian Optimization with cross-validation to optimize
    the hyperparameters of a BoostingBaseModel.

    Attributes:
        cv: Cross-validation strategy.
        splitter_df (pd.DataFrame): DataFrame for splitting the dataset.
        metric (BaseMetric): Metric used to evaluate model performance.
        optimizer (BayesianOptimization): Instance of the Bayesian optimizer.
        train_set (Tuple[pd.DataFrame, pd.Series]): Training data and targets.
        maximize (bool): Flag indicating whether to maximize or minimize the metric.
        init_points (int): Number of initial random evaluations.
        n_iter (int): Total number of optimization iterations.
        timeout (int): Maximum time allowed for optimization in seconds.
        seed (int): Random seed for reproducibility.
    """

    def __init__(
        self,
        model: BoostingBaseModel,
        cv,
        metric: BaseMetric,
        params_bounds: dict,
        splitter_df: pd.DataFrame,
        maximize: bool = True,
        n_iter: int = 30,
        timeout: int = 7200,
        seed: int = 27,
    ) -> None:
        """
        Initializes the CVBayesianOptimizationModel with necessary parameters.

        Args:
            model (BoostingBaseModel): The model to be optimized.
            cv: Cross-validation strategy.
            metric (BaseMetric): The metric used to evaluate model performance.
            params_bounds (dict): Bounds for the hyperparameters.
            splitter_df (pd.DataFrame): DataFrame used for splitting the dataset.
            maximize (bool, optional): Whether to maximize the metric. Defaults to True.
            n_iter (int, optional): Number of optimization iterations. Defaults to 30.
            timeout (int, optional): Timeout for the optimization process in seconds. Defaults to 7200.
            seed (int, optional): Random seed for reproducibility. Defaults to 27.
        """
        super().__init__(params_bounds, model)
        self.cv = cv
        self.splitter_df = splitter_df
        self.metric = metric
        self.optimizer = None
        self.train_set = None
        self.maximize = maximize
        self.init_points = int(n_iter * 0.2)
        self.n_iter = n_iter
        self.timeout = timeout
        self.seed = seed

    def objective(self, **fit_params) -> float:
        """Objective function for Bayesian Optimization with cross-validation.

        Updates the model with the provided hyperparameters, performs cross-validation,
        and returns the cross-validated metric value.

        Args:
            **fit_params: Arbitrary keyword arguments for model hyperparameters.

        Returns:
            float: The cross-validated metric value. Returns negative metric if minimizing.
        """
        valid_params = self.check_param_value(fit_params)
        params = self.model.params
        params.update(valid_params)

        self.model.params = params
        _, cv_score, _, _, _, _ = make_cv(
            estimator=self.model,
            x_train_cv=self.train_set[0],
            y_train_cv=self.train_set[1],
            cv=self.cv,
            splitter_df=self.splitter_df,
            metric=self.metric,
        )
        self._logger.info("=" * 111)

        if self.maximize:
            return cv_score
        return -cv_score

    def fit(self, data: pd.DataFrame, target: pd.Series) -> dict:
        """Fits the Bayesian optimizer with cross-validation to the provided data.

        Initializes the optimizer, performs the optimization process, and returns
        the best-found hyperparameters.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): True target values for training.

        Returns:
            dict: The best-found hyperparameters after optimization.

        Raises:
            TimeoutError: If the optimization process exceeds the specified timeout.
        """
        self.train_set = (data, target)
        self.optimizer = BayesianOptimization(
            self.objective, self.params_bounds, random_state=self.seed
        )
        self.optimizer.maximize(
            init_points=self.init_points, n_iter=self.n_iter, alpha=1e-6, acq="ucb", xi=0.0
        )
        max_params = self.optimizer.max["params"]
        max_params = self.check_param_value(max_params)

        return max_params