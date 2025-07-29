from abc import ABC
from copy import deepcopy
from typing import Tuple

import optuna
import pandas as pd
from optuna import Trial

from dreamml.logging import get_logger
from dreamml.modeling.cv import make_cv
from dreamml.modeling.metrics import BaseMetric, metrics_mapping
from dreamml.modeling.models.callbacks.callbacks import AddIntermediateMetricsCallback

_logger = get_logger(__name__)


class OptunaOptimizator(ABC):
    """
    Abstract base class for Optuna optimizers.

    This class provides a framework for optimizing machine learning models using Optuna.
    It handles parameter preparation, intermediate metric logging, and callback management.

    Attributes:
        model: The machine learning model to be optimized.
        metric: The metric used to evaluate the model's performance.
        params_bounds: A dictionary specifying the bounds for each hyperparameter.
        metric_period: The frequency of metric logging in Optuna study iterations.
        n_jobs: The number of parallel jobs for Optuna optimization.
        _logger: Logger instance for logging information and warnings.
    """

    def __init__(self, params_bounds, model, metric):
        """
        Initializes the OptunaOptimizator with parameter bounds, model, and metric.

        Args:
            params_bounds (dict): Dictionary with hyperparameter names as keys and their bounds as values.
            model: The machine learning model to be optimized.
            metric (BaseMetric): The metric used to evaluate the model's performance.
        """
        self.model = model
        self.metric = metric
        self.params_bounds = params_bounds
        self.metric_period = (
            100  # Log metric to Optuna study every 100 iterations
        )
        self.n_jobs = 1
        self._logger = model._logger or _logger

    def prepare_params(self, trial: Trial):
        """
        Prepares hyperparameters for the model based on the trial suggestions.

        Args:
            trial (Trial): An Optuna trial object containing parameter suggestions.

        Returns:
            dict: A dictionary of hyperparameters with values suggested by the trial.

        Raises:
            ValueError: If a parameter name does not have a defined distribution type.
        """
        params = deepcopy(self.model.params)
        for param_name in self.params_bounds:
            param_type = _check_param_value(param_name)

            if param_type == "integer":
                param_value_min, param_value_max = self.params_bounds[param_name]
                params[param_name] = trial.suggest_int(
                    param_name, param_value_min, param_value_max
                )
            elif param_type == "loginteger":
                param_value_min, param_value_max = self.params_bounds[param_name]
                params[param_name] = trial.suggest_int(
                    param_name, param_value_min, param_value_max, log=True
                )
            elif param_type == "discrete":
                param_value_min, param_value_max = self.params_bounds[param_name]
                params[param_name] = trial.suggest_discrete_uniform(
                    param_name, param_value_min, param_value_max, 0.1
                )
            elif param_type == "loguniform":
                param_value_min, param_value_max = self.params_bounds[param_name]
                params[param_name] = trial.suggest_loguniform(
                    param_name, param_value_min, param_value_max
                )
            elif param_type == "category":
                params[param_name] = trial.suggest_categorical(
                    param_name, self.params_bounds[param_name]
                )
            elif param_type == "float":
                param_value_min, param_value_max = self.params_bounds[param_name]
                params[param_name] = trial.suggest_float(
                    param_name,
                    param_value_min,
                    param_value_max,
                )
            else:
                self._logger.warning(
                    f"Parameter '{param_name}' is not included in the Optuna parameter list."
                )

        if self.model.model_name == "log_reg":
            if "penalty" in params:
                if params["penalty"] == "elasticnet":
                    params["l1_ratio"] = trial.suggest_uniform("l1_ratio", 0.0, 1.0)
                else:
                    params["l1_ratio"] = None

        return params

    def _intermediate_metric_availability_check(self) -> bool:
        """
        Checks the availability of intermediate metrics for logging in Optuna.

        Returns:
            bool: True if intermediate metrics are supported, False otherwise.
        """
        # Currently disabled as it doesn't improve the metric
        return False

    def _add_intermediate_values_callback(self, optuna_params: dict) -> dict:
        """
        Adds a callback for intermediate metric logging to Optuna parameters.

        Args:
            optuna_params (dict): Original Optuna optimization parameters.

        Returns:
            dict: Updated Optuna optimization parameters with the callback added.
        """
        model_name = self.model.model_name
        if model_name == "PyBoost":
            iter_param_name = "ntrees"
            n_estimators = self.model.params["ntrees"]
        else:
            iter_param_name = "n_estimators"
            n_estimators = self.model.params["n_estimators"]

        optuna_params["callbacks"] = [
            AddIntermediateMetricsCallback(iter_param_name, n_estimators)
        ]

        debug_msg = f"AddIntermediateMetricsCallback applied for {model_name}."
        self._logger.debug(debug_msg)
        return optuna_params

    def _report_intermediate_values(self, trial, callback_info_list):
        """
        Reports intermediate metric values to the Optuna trial.

        Args:
            trial: The current Optuna trial.
            callback_info_list: List of callback information containing intermediate metrics.
        """
        eval_results = []
        for iteration in callback_info_list:
            metrics_list_per_eval_set = iteration.metrics_list_per_eval_set
            eval_set_metric_list = metrics_list_per_eval_set[
                next(iter(metrics_list_per_eval_set))
            ]
            eval_metric = None
            for idx, dct in enumerate(eval_set_metric_list):
                if next(iter(dct)) in self.model.eval_metric.name:
                    eval_metric = eval_set_metric_list[idx][next(iter(dct))]
            if not eval_metric:
                eval_metric_dict = eval_set_metric_list[-1]
                eval_metric = eval_metric_dict[list(eval_metric_dict.keys())[-1]]
            eval_results.append(eval_metric)

        self.model.callback.callback_info_list = []

        for idx in range(0, len(eval_results), self.metric_period):
            trial.report(idx, eval_results[idx])

    def _logging_info(self, trial, metric):
        """
        Logs trial parameters and metric information.

        Args:
            trial: The current Optuna trial.
            metric (float): The metric value to log.
        """
        params = ""
        for k, v in trial.params.items():
            params += f"{k}: {v}\n"

        self._logger.debug(f"Trial({trial.number + 1}) params: \n{params}")
        self._logger.info(
            f"Trial({trial.number + 1}) score on VALID sample: {metric}\n"
        )


class CVOptunaOptimizationModel(OptunaOptimizator):
    """
    Optuna optimizer for cross-validated machine learning models in dreamml_base.

    This optimizer uses cross-validation to evaluate model performance during hyperparameter optimization.

    Args:
        model: An instance of a dreamml_base model with a standardized API.
        cv: Cross-validation strategy.
        metric (BaseMetric): The metric used to evaluate the model's performance.
        params_bounds (dict): Dictionary with hyperparameter names as keys and their bounds as values.
        splitter_df (pd.DataFrame): DataFrame used for splitting data in cross-validation.
        n_iter (int, optional): Number of optimization iterations. Defaults to 64.
        timeout (int, optional): Maximum time in seconds for the optimization process. Defaults to 7200.
        seed (int, optional): Random seed for reproducibility. Defaults to 27.

    Attributes:
        optimizer (optuna.study.Study): Instance of the Optuna optimizer study.
        cv: Cross-validation strategy.
        splitter_df (pd.DataFrame): DataFrame used for splitting data in cross-validation.
        train_set: Tuple containing training data and target labels.
        maximize (bool): Flag indicating whether to maximize the metric.
        n_iter (int): Number of optimization iterations.
        timeout (int): Maximum time in seconds for optimization.
        seed (int): Random seed for reproducibility.
        direction (str): Optimization direction, either "minimize" or "maximize".
    """

    def __init__(
        self,
        model,
        cv,
        metric: BaseMetric,
        params_bounds: dict,
        splitter_df: pd.DataFrame,
        n_iter: int = 64,
        timeout: int = 7200,
        seed: int = 27,
    ) -> None:
        """
        Initializes the CVOptunaOptimizationModel with model, cross-validation, metric, and optimization settings.

        Args:
            model: An instance of a dreamml_base model with a standardized API.
            cv: Cross-validation strategy.
            metric (BaseMetric): The metric used to evaluate the model's performance.
            params_bounds (dict): Dictionary with hyperparameter names as keys and their bounds as values.
            splitter_df (pd.DataFrame): DataFrame used for splitting data in cross-validation.
            n_iter (int, optional): Number of optimization iterations. Defaults to 64.
            timeout (int, optional): Maximum time in seconds for the optimization process. Defaults to 7200.
            seed (int, optional): Random seed for reproducibility. Defaults to 27.
        """
        super().__init__(params_bounds, model, metric)
        self.cv = cv
        self.splitter_df = splitter_df
        self.optimizer = None
        self.train_set = None
        self.maximize = metric.maximize
        self.n_iter = n_iter
        self.timeout = timeout
        self.seed = seed
        self.direction = "minimize"

    def objective(self, trial: Trial) -> float:
        """
        Objective function for Optuna optimization.

        This function sets the model's parameters based on the trial, performs cross-validation,
        logs the metric, and returns the cross-validation score.

        Args:
            trial (Trial): An Optuna trial object containing parameter suggestions.

        Returns:
            float: The cross-validation score for the current set of parameters.
        """
        self.model.params = self.prepare_params(trial)
        _, cv_score, _, _, _, _ = make_cv(
            estimator=self.model,
            x_train_cv=self.train_set[0],
            y_train_cv=self.train_set[1],
            cv=self.cv,
            splitter_df=self.splitter_df,
            metric=self.metric,
        )

        if self.maximize:
            cv_score = -cv_score

        self._logging_info(trial, cv_score)
        return cv_score

    def fit(self, data, target) -> None:
        """
        Trains the optimizer by running the optimization process.

        Args:
            data (pd.DataFrame): Feature matrix for training, shape = [n_samples, n_features].
            target (pd.Series): True labels for training, shape = [n_samples].

        Returns:
            dict: The best hyperparameters found during optimization.
        """
        self.train_set = (data, target)
        self.optimizer = optuna.create_study(
            sampler=optuna.samplers.TPESampler(seed=self.seed),
            direction=self.direction,
        )
        optuna_params = {
            "func": self.objective,
            "n_trials": self.n_iter,
            "timeout": self.timeout,
            "show_progress_bar": True,
            "n_jobs": self.n_jobs,
        }

        self.optimizer.optimize(**optuna_params)
        max_params = self.optimizer.best_params

        return max_params


class OptunaOptimizationModel(OptunaOptimizator):
    """
    Optuna optimizer for machine learning models in dreamml_base using Hold-Out validation.

    This optimizer evaluates model performance on a separate validation set during hyperparameter optimization.

    Args:
        model: An instance of a dreamml_base model with a standardized API.
        metric (BaseMetric): The metric used to evaluate the model's performance.
        eval_set (Tuple[pd.DataFrame, pd.Series]): Validation feature matrix and target labels.
        params_bounds (dict): Dictionary with hyperparameter names as keys and their bounds as values.
        n_iter (int, optional): Number of optimization iterations. Defaults to 30.
        timeout (int, optional): Maximum time in seconds for the optimization process. Defaults to 7200.
        seed (int, optional): Random seed for reproducibility. Defaults to 27.

    Attributes:
        optimizer (optuna.study.Study): Instance of the Optuna optimizer study.
        eval_set (Tuple[pd.DataFrame, pd.Series]): Validation feature matrix and target labels.
        maximize (bool): Flag indicating whether to maximize the metric.
        n_iter (int): Number of optimization iterations.
        timeout (int): Maximum time in seconds for optimization.
        seed (int): Random seed for reproducibility.
        direction (str): Optimization direction, either "minimize" or "maximize".
        train_set: Tuple containing training data and target labels.
    """

    def __init__(
        self,
        model,
        metric: BaseMetric,
        eval_set: Tuple[pd.DataFrame, pd.Series],
        params_bounds: dict,
        n_iter: int = 30,
        timeout: int = 7200,
        seed: int = 27,
    ) -> None:
        """
        Initializes the OptunaOptimizationModel with model, metric, evaluation set, and optimization settings.

        Args:
            model: An instance of a dreamml_base model with a standardized API.
            metric (BaseMetric): The metric used to evaluate the model's performance.
            eval_set (Tuple[pd.DataFrame, pd.Series]): Validation feature matrix and target labels.
            params_bounds (dict): Dictionary with hyperparameter names as keys and their bounds as values.
            n_iter (int, optional): Number of optimization iterations. Defaults to 30.
            timeout (int, optional): Maximum time in seconds for the optimization process. Defaults to 7200.
            seed (int, optional): Random seed for reproducibility. Defaults to 27.
        """
        super().__init__(params_bounds, model, metric)
        self.optimizer = None
        self.eval_set = eval_set
        self.maximize = metric.maximize
        self.n_iter = n_iter
        self.timeout = timeout
        self.seed = seed
        self.direction = "minimize"

    def fit(self, data, target) -> None:
        """
        Trains the optimizer by running the optimization process.

        Args:
            data (pd.DataFrame): Feature matrix for training, shape = [n_samples, n_features].
            target (pd.Series): True labels for training, shape = [n_samples].

        Raises:
            ValueError: If the intermediate metric distribution is not defined for a parameter.

        Returns:
            None
        """
        self.train_set = (data, target)
        self.optimizer = optuna.create_study(
            sampler=optuna.samplers.TPESampler(seed=self.seed),
            direction=self.direction,
        )
        optuna_params = {
            "func": self.objective,
            "n_trials": self.n_iter,
            "timeout": self.timeout,
            "show_progress_bar": True,
            "n_jobs": self.n_jobs,
        }

        if self._intermediate_metric_availability_check():
            optuna_params = self._add_intermediate_values_callback(optuna_params)

        self.optimizer.optimize(**optuna_params)
        max_params = self.optimizer.best_params
        self.model.params.update(max_params)

        if self.model.task == "topic_modeling":
            self.model.fit(self.train_set)
        elif self.model.task == "anomaly_detection":
            self.model.fit(self.train_set[0], None, None)
        else:
            self.model.fit(*self.train_set, *self.eval_set)

    def objective(self, trial: Trial) -> float:
        """
        Objective function for Optuna optimization.

        This function sets the model's parameters based on the trial, fits the model,
        evaluates it on the validation set, logs the metric, and returns the metric value.

        Args:
            trial (Trial): An Optuna trial object containing parameter suggestions.

        Returns:
            float: The evaluation metric for the current set of parameters.
        """
        self.model.params = self.prepare_params(trial)

        if self.model.task == "topic_modeling":
            self.model.fit(self.train_set)
            metric = self.metric(self.model.topic_modeling_data)

        elif self.model.task == "anomaly_detection":  # iforest
            self.model.fit(self.train_set[0], None, None)
            y_pred = self.model.transform(self.train_set[0])  # all_data
            metric = self._get_weighted_metric(
                "silhouette_score", self.train_set[0], y_pred, 0.7
            )

        else:
            self.model.fit(*self.train_set, *self.eval_set)
            y_pred = self.model.transform(self.eval_set[0])
            metric = self.metric(self.eval_set[1], y_pred)

        if self.maximize:
            metric = -metric

        if self._intermediate_metric_availability_check():
            callback_info_list = self.model.callback.callback_info_list
            self._report_intermediate_values(trial, callback_info_list)

        self._logging_info(trial, metric)
        return metric

    def _get_weighted_metric(self, metric_name: str, X, y_pred, w1: float = 0.5):
        """
        Calculates a weighted combination of two metrics.

        Args:
            metric_name (str): Name of the second metric to include.
            X: Feature matrix used for calculating the second metric.
            y_pred: Predictions or scores from the model.
            w1 (float, optional): Weight for the first metric. Defaults to 0.5.

        Raises:
            ValueError: If an unsupported metric name is provided.

        Returns:
            float: The weighted combination of the two metrics.
        """
        w2 = 1 - w1
        second_metric = metrics_mapping.get(metric_name)(
            self.model.model_name, task=self.model.task
        )

        assert second_metric.maximize == self.metric.maximize

        avg_anomaly_score = self.metric(y_pred)
        if metric_name == "silhouette_score":
            metric_dict = {"x": X, "scores": y_pred.reshape(-1, 1)}
            silhouette_score = second_metric(metric_dict)
        else:
            msg = f"Wrong metric! {metric_name}."
            raise ValueError(msg)

        weighted_metric = w1 * silhouette_score + w2 * avg_anomaly_score
        return weighted_metric


def _check_param_value(param_name):
    """
    Determines the distribution type for a given hyperparameter name.

    This function categorizes hyperparameters into types such as integer, loginteger, discrete,
    loguniform, category, or float based on predefined lists.

    Args:
        param_name (str): The name of the hyperparameter.

    Raises:
        ValueError: If the parameter name does not match any predefined distribution types.

    Returns:
        str: The distribution type of the hyperparameter.
    """
    # FIXME: The parameter distribution should be defined in one place in the config,
    #  and parameters should also be taken from one place (not from ..)
    integer_params = [
        "max_depth",
        "num_leaves",
        "subsample_for_bin",
        "min_child_weight",
        "scale_pos_weight",
        "max_bin",
        "min_data_in_bin",
        "epochs",
        "batch_size",
        "max_iter",
        "num_topics",
        "num_models",
        "iterations",
        "n_estimators",
    ]
    loginteger_params = [
        "min_child_samples",
        "min_data_in_leaf",
    ]
    discrete_params = [
        "subsample",
        "colsample_bytree",
        "colsample_bylevel",
        "colsample",
    ]
    loguniform_params = [
        "learning_rate",
        "lr",
        "gamma",
        "alpha",
        "reg_alpha",
        "reg_lambda",
        "l2_leaf_reg",
        "min_split_gain",
        "lambda_l2",
        "C",
        "eta",
        "weight_decay",
        "tol",
        "l1_ratio",
    ]
    category_params = [
        "optimizer_type",
        "scheduler_type",
        "sampler_type",
        "penalty",
        "solver",
        "grow_policy",
        "bootstrap_type",
    ]
    float_params = [
        "max_samples",
        "max_features",
        "contamination",
    ]

    if param_name in integer_params:
        return "integer"
    elif param_name in loginteger_params:
        return "loginteger"
    elif param_name in discrete_params:
        return "discrete"
    elif param_name in loguniform_params:
        return "loguniform"
    elif param_name in category_params:
        return "category"
    elif param_name in float_params:
        return "float"
    else:
        raise ValueError(
            f"No distribution defined for parameter {param_name} during optimization."
        )