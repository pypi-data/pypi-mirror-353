import numpy as np
import pandas as pd
from scipy.optimize import minimize
import optuna
import random
import logging
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from typing import Dict, Any
import multiprocessing as mp

from dreamml.logging.logger import CombinedLogger
from dreamml.logging import get_logger
from dreamml.modeling.models.estimators import BaseModel

_logger = get_logger(__name__)

import gc


class AMTSModel(BaseModel):
    model_name = "AMTS"
    """
    Alt-mode Time Series Model (AMTSModel) for forecasting using Prophet with group-wise optimization.

    This model supports parallel optimization of hyperparameters for different groups within the dataset.
    It leverages Optuna for hyperparameter tuning and allows for calibration of additional features
    such as weekends and holidays.

    Attributes:
        model_name (str): The name of the model.
        estimator_class (Prophet): The underlying estimator class used for forecasting.
        n_iterations (int): Number of iterations for hyperparameter optimization.
        split_by_group (bool): Whether to split the data by groups for modeling.
        group_column (str): The name of the column representing group identifiers.
        horizon (int): Forecasting horizon.
        time_column_frequency (Any): Frequency of the time column.
        final_fit (bool): Indicates if the final fit has been performed.
        models_by_groups (dict): Models instantiated per group.
        hyper_params_by_group (dict): Best hyperparameters per group.
        hyper_params_calib_by_groups (dict): Calibrated hyperparameters per group.
        forecast (np.array): Forecasted values.
        df_prophet_dev (pd.DataFrame): Development dataframe for Prophet.
        cross_val_initial (int): Initial window for cross-validation.
        cross_val_period (int): Period between cross-validation folds.
        cross_val_horizon (int): Horizon for cross-validation.
        mem_info (int): Memory information placeholder.
    """

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        metric_name=None,
        metric_params: Dict = None,
        **params,
    ):
        """
        Initializes the AMTSModel with estimator parameters, task, and metric configurations.

        Args:
            estimator_params (Dict[str, Any]): Dictionary of hyperparameters for the estimator.
            task (str): Name of the task (e.g., regression, binary, multi).
            metric_name (str, optional): Name of the evaluation metric.
            metric_params (Dict, optional): Parameters for the evaluation metric.
            **params: Additional parameters for the model.

        Raises:
            KeyError: If required parameters are missing in `params`.
        """
        super().__init__(
            estimator_params=estimator_params,
            task=task,
            metric_name=metric_name,
            metric_params=metric_params,
            **params,
        )
        self.estimator_class = self._estimators.get(self.task)
        self.n_iterations = self.params["n_iterations"]
        self.split_by_group = self.params["split_by_group"]
        self.group_column = self.params["group_column"]
        self.horizon = self.params["horizon"]
        self.time_column_frequency = self.params["time_column_frequency"]
        self.final_fit = False

        self.models_by_groups = dict()
        self.hyper_params_by_group = dict()
        self.hyper_params_calib_by_groups = dict()

        self.forecast = None
        self.df_prophet_dev = None
        self.cross_val_initial = 0
        self.cross_val_period = 0
        self.cross_val_horizon = 0

        self.mem_info = 0

    @property
    def _estimators(self):
        """
        Retrieves the dictionary of available estimators.

        Returns:
            Dict[str, Any]: A dictionary mapping task names to estimator classes.
        """
        estimators = {"amts": Prophet}
        return estimators

    def process_group(self, group_data):
        """
        Processes a single group by performing hyperparameter optimization and fitting the estimator.

        Args:
            group_data (tuple): A tuple containing the group name and its corresponding dataframe.

        Returns:
            tuple: A tuple containing the model name, fitted estimator, best hyperparameters,
                   and calibrated hyperparameters for the group.

        Raises:
            Exception: If the optimization or fitting process fails.
        """
        group_name, df_group = group_data

        self.df_prophet_dev = df_group[: -self.horizon]
        if self.final_fit:
            self.df_prophet_dev = df_group

        self.calculate_cross_val_params()

        study = optuna.create_study(direction="minimize")
        study.optimize(
            func=self.optuna_obj, n_trials=self.n_iterations, show_progress_bar=True
        )

        logging.getLogger("cmdstanpy").disabled = True
        self.estimator = self.estimator_class(**study.best_params)
        self.estimator.fit(self.df_prophet_dev[["ds", "y"]])

        self.forecast = np.array(
            self.estimator.predict(self.df_prophet_dev["ds"].to_frame())["yhat"]
        )
        logging.getLogger("cmdstanpy").disabled = False

        hyper_params_calib_by_groups = dict()

        if self.time_column_frequency.value == "D":
            self.optimize_hyper_params(model_name=f"model_{group_name}")
            hyper_params_calib_by_groups.update(
                self.hyper_params_calib_by_groups[f"model_{group_name}"]
            )
        gc.collect()

        return (
            f"model_{group_name}",
            self.estimator,
            study.best_params,
            hyper_params_calib_by_groups,
        )

    def parallel_optimization(self, df, group_column):
        """
        Performs parallel optimization of hyperparameters across different groups.

        Args:
            df (pd.DataFrame): The dataframe containing the training data.
            group_column (str): The column name to group the data by.

        Returns:
            tuple: Three dictionaries containing models by groups, best hyperparameters by group,
                   and calibrated hyperparameters by group.
        """
        groups = [
            (group_name, df_group) for group_name, df_group in df.groupby(group_column)
        ]
        with mp.Pool(mp.cpu_count() - 2) as pool:
            results = []
            for result in pool.imap(self.process_group, groups):
                results.append(result)
                gc.collect()

        models_by_groups = {
            model_name: estimator for model_name, estimator, _, _ in results
        }
        hyper_params_by_group = {
            model_name: best_params for model_name, _, best_params, _ in results
        }
        hyper_params_calib_by_groups = {
            model_name: calib_params for model_name, _, _, calib_params in results
        }

        return models_by_groups, hyper_params_by_group, hyper_params_calib_by_groups

    def fit_group(self, amts_data: Dict):
        """
        Trains and optimizes the model on group-wise data provided in `amts_data`.

        Args:
            amts_data (Dict): A dictionary containing training data with keys 'sample_name' and values as tuples of (X, y).

        Raises:
            KeyError: If 'train' key is missing in `amts_data`.
        """
        df = amts_data["train"][0]
        df["y"] = amts_data["train"][1]

        (
            self.models_by_groups,
            self.hyper_params_by_group,
            self.hyper_params_calib_by_groups,
        ) = self.parallel_optimization(
            df=df,
            group_column=self.group_column,
        )

        self.fitted = True

    def fit(self, amts_data: Dict, final=False):
        """
        Trains and optimizes the model on the provided `amts_data`.

        Args:
            amts_data (Dict): A dictionary containing training data with keys 'sample_name' and values as tuples of (X, y).
            final (bool, optional): Indicates whether this is the final fit. Defaults to False.

        Raises:
            KeyError: If required keys are missing in `amts_data` or `params`.
        """
        self.final_fit = final

        if self.split_by_group:
            self.fit_group(amts_data)
            return

        self.df_prophet_dev = amts_data["train"][0]
        self.df_prophet_dev["y"] = amts_data["train"][1]

        self.calculate_cross_val_params()

        study = optuna.create_study(direction="minimize")
        study.optimize(
            func=self.optuna_obj, n_trials=self.n_iterations, show_progress_bar=True
        )

        logging.getLogger("cmdstanpy").disabled = True
        self.estimator = self.estimator_class(**study.best_params)
        self.estimator.fit(self.df_prophet_dev[["ds", "y"]])
        self.forecast = np.array(
            self.estimator.predict(self.df_prophet_dev["ds"].to_frame())["yhat"]
        )
        logging.getLogger("cmdstanpy").disabled = False

        if self.time_column_frequency.value == "D":
            self.optimize_hyper_params(model_name="model_0")

        self.models_by_groups["model_0"] = self.estimator
        self.hyper_params_by_group["model_0"] = study.best_params

        self.fitted = True

    def prophet_crossval(self, params):
        """
        Performs cross-validation on the Prophet model with the given parameters.

        Args:
            params (dict): Hyperparameters for the Prophet model.

        Returns:
            float: The mean Absolute Percentage Error (MAPE) from performance metrics.

        Raises:
            Exception: If cross-validation or metric calculation fails.
        """
        logging.getLogger("cmdstanpy").disabled = True
        model = Prophet(**params)
        model.fit(self.df_prophet_dev)

        if self.split_by_group or self.parallelism == 0:
            parallel = None
        else:
            parallel = "processes"

        df_cv = cross_validation(
            model,
            initial=f"{self.cross_val_initial} days",
            period=f"{self.cross_val_period} days",
            horizon=f"{self.cross_val_horizon} days",
            parallel=parallel,
        )
        df_p = performance_metrics(df_cv)
        logging.getLogger("cmdstanpy").disabled = False
        loss = 0
        try:
            loss = df_p["mape"].mean()
        except Exception:
            pass
        return loss

    def optuna_obj(self, trial):
        """
        Objective function for Optuna to optimize Prophet hyperparameters.

        Args:
            trial (optuna.trial.Trial): A trial object for suggesting hyperparameter values.

        Returns:
            float: The loss value (MAPE) to be minimized.
        """
        params = {
            "changepoint_prior_scale": trial.suggest_loguniform(
                name="changepoint_prior_scale", low=0.01, high=10
            ),
            "seasonality_prior_scale": trial.suggest_loguniform(
                name="seasonality_prior_scale", low=0.1, high=10
            ),
            "weekly_seasonality": trial.suggest_int(
                name="weekly_seasonality", low=0, high=10
            ),
            "yearly_seasonality": trial.suggest_int(
                name="yearly_seasonality", low=0, high=20
            ),
        }

        return self.prophet_crossval(params)

    def optimize_hyper_params(self, model_name: str):
        """
        Optimizes hyperparameters for additional features such as weekends and holidays.

        Args:
            model_name (str): The identifier for the model group being calibrated.

        Raises:
            ValueError: If the optimization fails to converge.
        """
        self.hyper_params_calib_by_groups[model_name] = {
            "is_weekend": random.normalvariate(0, 1),
            "is_holiday": random.normalvariate(0, 1),
            "is_pre_holiday": random.normalvariate(0, 1),
            "is_pre_pre_holiday": random.normalvariate(0, 1),
        }

        target = np.array(self.df_prophet_dev["y"])
        forecast = self.forecast
        for name_param, w_init in self.hyper_params_calib_by_groups[model_name].items():
            b = np.array(self.df_prophet_dev[name_param])
            results = minimize(
                self.calibration_obj,
                w_init,
                args=(target, forecast, b),
                method="Nelder-Mead",
            )
            loss, opt_w = results.fun, results.x
            self.hyper_params_calib_by_groups[model_name][name_param] = opt_w

    def calibration_obj(self, w, target, forecast, b):
        """
        Objective function for calibrating additional feature weights.

        Args:
            w (float): Current weight for the feature.
            target (np.array): True target values.
            forecast (np.array): Forecasted values from the estimator.
            b (np.array): Binary feature array (e.g., is_weekend).

        Returns:
            float: The objective loss value.

        Raises:
            Exception: If the objective calculation fails.
        """
        return self.objective(target, (forecast + (w * b)))

    def calculate_cross_val_params(self):
        """
        Calculates cross-validation parameters based on the frequency of the time column.
        """
        if self.time_column_frequency.value == "H":
            self.cross_val_initial = int(int(len(self.df_prophet_dev) * 0.2) / 24)
            self.cross_val_period = int(int(len(self.df_prophet_dev) * 0.1) / 24)
            self.cross_val_horizon = int(self.horizon / 24)

        if self.time_column_frequency.value == "D":
            self.cross_val_initial = int(len(self.df_prophet_dev) * 0.2)
            self.cross_val_period = int(len(self.df_prophet_dev) * 0.1)
            self.cross_val_horizon = self.horizon

        if self.time_column_frequency.value == "W":
            self.cross_val_initial = int(len(self.df_prophet_dev) * 0.2) * 7
            self.cross_val_period = int(len(self.df_prophet_dev) * 0.1) * 7
            self.cross_val_horizon = self.horizon * 7

        if self.time_column_frequency.value == "M":
            self.cross_val_initial = int(len(self.df_prophet_dev) * 0.2) * 30
            self.cross_val_period = int(len(self.df_prophet_dev) * 0.1) * 30
            self.cross_val_horizon = self.horizon * 30

        if self.time_column_frequency.value == "Y":
            self.cross_val_initial = int(len(self.df_prophet_dev) * 0.2) * 365
            self.cross_val_period = int(len(self.df_prophet_dev) * 0.1) * 365
            self.cross_val_horizon = self.horizon * 365

    def transform(self, df_prophet: pd.DataFrame) -> np.array:
        """
        Applies the trained model to the provided dataframe and generates forecasts.

        The model must be fitted before calling this method. If `split_by_group` is enabled,
        forecasts are generated for each group separately with calibrated hyperparameters.

        Args:
            df_prophet (pd.DataFrame): DataFrame containing the features for prediction. Must include a 'ds' column.

        Returns:
            np.array or dict: Array of forecasted values if not split by group,
                              otherwise a dictionary mapping model names to their forecasts.

        Raises:
            AttributeError: If the model has not been fitted.
            KeyError: If group identifiers are missing in the forecasts.
        """
        if self.split_by_group:
            forecast_dict = dict()
            for group_name, df_group in df_prophet.groupby(self.group_column):
                forecast = np.array(
                    self.models_by_groups[f"model_{group_name}"].predict(df_group)[
                        "yhat"
                    ]
                )
                if self.time_column_frequency.value == "D":
                    forecast = (
                        forecast
                        + (
                            self.hyper_params_calib_by_groups[f"model_{group_name}"][
                                "is_weekend"
                            ]
                            * df_prophet["is_weekend"]
                        )
                        + (
                            self.hyper_params_calib_by_groups[f"model_{group_name}"][
                                "is_holiday"
                            ]
                            * df_prophet["is_holiday"]
                        )
                        + (
                            self.hyper_params_calib_by_groups[f"model_{group_name}"][
                                "is_pre_holiday"
                            ]
                            * df_prophet["is_pre_holiday"]
                        )
                        + (
                            self.hyper_params_calib_by_groups[f"model_{group_name}"][
                                "is_pre_pre_holiday"
                            ]
                            * df_prophet["is_pre_pre_holiday"]
                        )
                    )

                forecast_dict[f"model_{group_name}"] = forecast
            return forecast_dict

        else:
            forecast = np.array(
                self.models_by_groups["model_0"].predict(df_prophet)["yhat"]
            )
            if self.time_column_frequency.value == "D":
                forecast = (
                    forecast
                    + (
                        self.hyper_params_calib_by_groups["model_0"]["is_weekend"]
                        * df_prophet["is_weekend"]
                    )
                    + (
                        self.hyper_params_calib_by_groups["model_0"]["is_holiday"]
                        * df_prophet["is_holiday"]
                    )
                    + (
                        self.hyper_params_calib_by_groups["model_0"][
                            "is_pre_holiday"
                        ]
                        * df_prophet["is_pre_holiday"]
                    )
                    + (
                        self.hyper_params_calib_by_groups["model_0"][
                            "is_pre_pre_holiday"
                        ]
                        * df_prophet["is_pre_pre_holiday"]
                    )
                )
            return forecast

    def serialize(self) -> dict:
        """
        Serializes the model's state into a dictionary.

        Returns:
            dict: A dictionary containing serialized model state and additional information.
        """
        data = super().serialize()

        additional_dict = {
            "models_by_groups": self.models_by_groups,
            "hyper_params_by_group": self.hyper_params_by_group,
            "hyper_params_calib_by_groups": self.hyper_params_calib_by_groups,
            "df_prophet_dev": self.df_prophet_dev,
            "forecast": self.forecast,
            "cross_val_initial": self.cross_val_initial,
            "cross_val_period": self.cross_val_period,
            "cross_val_horizon": self.cross_val_horizon,
            "final_fit": self.final_fit,
        }

        data["additional"].update(additional_dict)

        return data

    @classmethod
    def deserialize(cls, data):
        """
        Deserializes the model's state from a dictionary.

        Args:
            data (dict): A dictionary containing the serialized model state.

        Returns:
            AMTSModel: An instance of AMTSModel with state restored.

        Raises:
            KeyError: If required keys are missing in the input dictionary.
        """
        instance = super().deserialize(data)

        instance.models_by_groups = data["additional"]["models_by_groups"]
        instance.hyper_params_by_group = data["additional"]["hyper_params_by_group"]
        instance.hyper_params_calib_by_groups = data["additional"][
            "hyper_params_calib_by_groups"
        ]
        instance.df_prophet_dev = data["additional"]["df_prophet_dev"]
        instance.forecast = data["additional"]["forecast"]
        instance.cross_val_initial = data["additional"]["cross_val_initial"]
        instance.cross_val_period = data["additional"]["cross_val_period"]
        instance.cross_val_horizon = data["additional"]["cross_val_horizon"]
        instance.final_fit = data["additional"]["final_fit"]

        return instance

    def evaluate_and_print(self, **eval_sets):
        """
        Evaluates the model's performance on provided evaluation sets and prints the results.

        For classification tasks, the GINI metric is used.
        For regression tasks, MAE, R2, and RMSE metrics are used.
        Metrics are printed to the standard output with their respective scores.

        Args:
            eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                A dictionary where keys are dataset names and values are tuples of (features, true values).

        Raises:
            KeyError: If expected keys are missing in the evaluation sets.
        """
        if not self.split_by_group:
            super().evaluate_and_print(**eval_sets)
        else:
            metrics_to_eval = {}
            if self.eval_metric.name.upper() not in metrics_to_eval:
                metrics_to_eval[self.eval_metric.name.upper()] = self.eval_metric
            if self.objective.name.upper() not in metrics_to_eval:
                metrics_to_eval[self.objective.name.upper()] = self.objective

            df = eval_sets["train"][0]
            df["y"] = eval_sets["train"][1]
            eval_sets_tmp = {"train": None, "valid": None}
            for group_name, df_group in df.groupby(self.group_column):
                eval_sets_tmp["train"] = pd.concat(
                    [eval_sets_tmp["train"], df_group[: -self.horizon]], axis=0
                )
                eval_sets_tmp["valid"] = pd.concat(
                    [eval_sets_tmp["valid"], df_group[-self.horizon :]], axis=0
                )

            for sample in eval_sets_tmp:
                data = eval_sets_tmp[sample]
                forecast_dict = self.transform(data)

                scores = {}
                for group_name, df_group in data.groupby(self.group_column):
                    y_true = df_group["y"]
                    y_pred = forecast_dict[f"model_{group_name}"]

                    for name, metric in metrics_to_eval.items():
                        try:
                            scores[name] = metric(y_true, y_pred)
                        except (ValueError, KeyError, IndexError):
                            scores[name] = np.nan

                    metrics_output = ", ".join(
                        [f"{name} = {value:.2f}" for name, value in scores.items()]
                    )
                    output_per_sample = (
                        f"{sample}-score: {group_name}--group: \t {metrics_output}"
                    )

                    logger = CombinedLogger([self._logger, _logger])
                    logger.info(output_per_sample)