from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

import optuna
import xgboost.callback
from colorama import Fore

from dreamml.logging import get_logger
from dreamml.utils.styling import ANSIColoringMixin

_logger = get_logger(__name__)


@dataclass
class ModelCallbackInfo(ANSIColoringMixin):
    """
    Stores information about a single iteration of model training, including metrics for training and evaluation sets.

    Attributes:
        iter (int): The current iteration number.
        train_metrics_list (List[Dict[str, float]]): A list of dictionaries containing training metrics.
            Example:
                [{'mae': 55.9128}, {'mae2': 30.0003}]
        metrics_list_per_eval_set (Dict[str, List[Dict[str, float]]]): A dictionary where each key is an evaluation set name
            and the value is a list of dictionaries containing metrics for that evaluation set.
            Example:
                {
                    'validation_1': [{'mae': 55.9128}],
                    'validation_2': [{'mae': 54.0003}, {'rmse': 100.0003}],
                }
        use_colors (bool, optional): Flag to determine if colors should be used in the output. Defaults to False.
        tail_str (str): A string appended at the end of each line. Defaults to "|  ".
        left_padding (str): The padding added to the beginning of each line. Defaults to four spaces.
        set_alignment_length (int): The alignment length for set names. Defaults to 18.
        metric_alignment_length (int): The alignment length for metric names and values. Defaults to 25.
        metric_round (int): The number of decimal places to round metric values. Defaults to 4.
    """

    iter: int
    train_metrics_list: List[Dict[str, float]]
    metrics_list_per_eval_set: Dict[str, List[Dict[str, float]]]
    use_colors: bool = False
    tail_str: str = "|  "
    left_padding: str = " " * 4
    set_alignment_length: int = 18
    metric_alignment_length: int = 25
    metric_round: int = 4

    def __str__(self) -> str:
        """
        Returns a formatted string representation of the callback information.

        Returns:
            str: A string that includes iteration number, training metrics, and evaluation set metrics with optional coloring.
        """
        train_set_name = "train set:"
        possibly_colored_train_set_name = self._add_ansi_color(
            train_set_name, Fore.GREEN
        )
        train_set_str = f"{self.left_padding}{possibly_colored_train_set_name:<{self.set_alignment_length}}{self.tail_str}"

        for train_metric in self.train_metrics_list:
            train_set_str += self._format_metric(train_metric, Fore.GREEN)

        eval_set_str = ""
        for eval_set_key in self.metrics_list_per_eval_set.keys():
            eval_set_name = f"{eval_set_key}:"
            possibly_colored_eval_set_name = self._add_ansi_color(
                eval_set_name, Fore.YELLOW
            )

            eval_set_str += f"{self.left_padding}{possibly_colored_eval_set_name:<{self.set_alignment_length}}{self.tail_str}"

            for eval_set_metric in self.metrics_list_per_eval_set[eval_set_key]:
                eval_set_str += self._format_metric(eval_set_metric, Fore.YELLOW)

            eval_set_str += "\n"

        iteration_str = f"iter {self.iter}:"
        output = f"{iteration_str}\n{train_set_str}\n{eval_set_str}"

        return output.rstrip()

    def _format_metric(self, metric: Dict[str, float], color: Optional[str]) -> str:
        """
        Formats a single metric with optional coloring.

        Args:
            metric (Dict[str, float]): A dictionary containing a single metric name and its value.
                Example: {"mae": 55.9128}
            color (Optional[str]): The color code to apply to the metric name. If None, no color is applied.

        Returns:
            str: A formatted string of the metric name and value with alignment and coloring.
        """
        metric_name = list(metric.keys())[0]
        possibly_colored_metric_name = self._add_ansi_color(metric_name, color)

        metric_value = metric[metric_name]

        metric_name_and_value_str = (
            f"{possibly_colored_metric_name} {metric_value:.{self.metric_round}f}"
        )

        s = f"{metric_name_and_value_str:<{self.metric_alignment_length}}{self.tail_str}"

        return s


@dataclass
class ModelCallbackInfoList:
    """
    Manages a list of ModelCallbackInfo instances.

    Attributes:
        callback_list (List[ModelCallbackInfo]): A list containing ModelCallbackInfo objects.
    """

    callback_list: List[ModelCallbackInfo]

    def __getitem__(self, index: int) -> ModelCallbackInfo:
        """
        Retrieves a ModelCallbackInfo instance by its index.

        Args:
            index (int): The index of the callback information to retrieve.

        Returns:
            ModelCallbackInfo: The callback information at the specified index.
        """
        return self.callback_list[index]

    def append(self, callback_info: ModelCallbackInfo) -> None:
        """
        Appends a new ModelCallbackInfo instance to the callback list.

        Args:
            callback_info (ModelCallbackInfo): The callback information to append.
        """
        self.callback_list.append(callback_info)

    def __repr__(self) -> str:
        """
        Returns the official string representation of the callback list.

        Returns:
            str: A newline-separated string of the repr of each callback in the list.
        """
        return "\n".join([repr(callback) for callback in self.callback_list])

    def __str__(self) -> str:
        """
        Returns the informal string representation of the callback list.

        Returns:
            str: A newline-separated string of the str of each callback in the list.
        """
        return "\n".join([str(callback) for callback in self.callback_list])


class ModelLoggingCallback:
    """
    Base class for logging callbacks in model training.

    Attributes:
        callback_info_list (ModelCallbackInfoList): A list to store callback information.
        _logger (Optional[logging.Logger]): The logger used for logging callback information.
    """

    def __init__(self, train_logger: Optional[logging.Logger] = None):
        """
        Initializes the ModelLoggingCallback with an optional logger.

        Args:
            train_logger (Optional[logging.Logger], optional): A logger instance for training logs. Defaults to None.
        """
        super().__init__()
        self.callback_info_list = ModelCallbackInfoList([])
        self._logger = train_logger

    def _log(self, callback_info: ModelCallbackInfo) -> None:
        """
        Logs the callback information using the assigned logger.

        Args:
            callback_info (ModelCallbackInfo): The callback information to log.
        """
        logger = self._logger or _logger
        logger.info(callback_info)


class XGBoostLoggingCallback(xgboost.callback.TrainingCallback, ModelLoggingCallback):
    """Logging callback for XGBoost models."""

    def __init__(self, train_logger: Optional[logging.Logger] = None):
        """
        Initializes the XGBoostLoggingCallback with an optional logger.

        Args:
            train_logger (Optional[logging.Logger], optional): A logger instance for training logs. Defaults to None.
        """
        super().__init__()
        ModelLoggingCallback.__init__(self, train_logger=train_logger)

    def after_iteration(self, model, epoch: int, evals_log: Dict[str, Dict[str, List[float]]]) -> bool:
        """
        Callback function executed after each iteration of XGBoost training.

        Args:
            model: The trained XGBoost model.
            epoch (int): The current iteration number.
            evals_log (Dict[str, Dict[str, List[float]]]): A dictionary containing evaluation metrics for each dataset.

        Raises:
            None

        Returns:
            bool: Always returns False to indicate that training should not be terminated.
        """
        callback_info = ModelCallbackInfo(epoch, [], {})

        for eval_set_name in evals_log:
            for metric_name, metric_values in evals_log[eval_set_name].items():
                metric_value = metric_values[-1]
                if eval_set_name == "validation_0":
                    callback_info.train_metrics_list.append({metric_name: metric_value})
                else:
                    if eval_set_name not in callback_info.metrics_list_per_eval_set:
                        callback_info.metrics_list_per_eval_set[eval_set_name] = [
                            {metric_name: metric_value}
                        ]
                    else:
                        callback_info.metrics_list_per_eval_set[eval_set_name].append(
                            {metric_name: metric_value}
                        )

        self.callback_info_list.append(callback_info)
        self._log(callback_info)

        return False


class LightGBMLoggingCallback(ModelLoggingCallback):
    """Logging callback for LightGBM models."""

    def __call__(self, evr):
        """
        Callback function executed during each evaluation in LightGBM training.

        Args:
            evr: An object containing evaluation results, including iteration number and evaluation metrics.

        Raises:
            None

        Returns:
            None
        """
        callback_info = ModelCallbackInfo(evr.iteration, [], {})

        for eval_tuple in evr.evaluation_result_list:
            eval_set_name = eval_tuple[0]
            metric_name = eval_tuple[1]
            metric_value = eval_tuple[2]

            if eval_set_name == "valid_0":
                callback_info.train_metrics_list.append({metric_name: metric_value})
            elif "valid" in eval_set_name:
                if eval_set_name not in callback_info.metrics_list_per_eval_set:
                    callback_info.metrics_list_per_eval_set[eval_set_name] = [
                        {metric_name: metric_value}
                    ]
                else:
                    callback_info.metrics_list_per_eval_set[eval_set_name].append(
                        {metric_name: metric_value}
                    )

        self.callback_info_list.append(callback_info)
        self._log(callback_info)


class CatBoostLoggingCallback(ModelLoggingCallback):
    """Logging callback for CatBoost models."""

    def after_iteration(self, evr) -> bool:
        """
        Callback function executed after each iteration of CatBoost training.

        Args:
            evr: An object containing evaluation results, including iteration number and metrics.

        Raises:
            None

        Returns:
            bool: Always returns True to indicate that training should continue.
        """
        callback_info = ModelCallbackInfo(evr.iteration, [], {})

        for eval_set_name in evr.metrics:
            if eval_set_name == "learn":
                # it's the same as validation_0 in current implementation
                continue

            elif eval_set_name == "validation_0":
                iteration_metrics_per_eval_set = {}
                for metric_name, metric_value in evr.metrics[eval_set_name].items():
                    iteration_metrics_per_eval_set[metric_name.lower()] = metric_value[-1]

                callback_info.train_metrics_list.append(iteration_metrics_per_eval_set)

            else:
                if eval_set_name not in callback_info.metrics_list_per_eval_set:
                    callback_info.metrics_list_per_eval_set[eval_set_name] = []

                iteration_metrics_per_eval_set = {}
                for metric_name, metric_value in evr.metrics[eval_set_name].items():
                    iteration_metrics_per_eval_set[metric_name.lower()] = metric_value[-1]

                callback_info.metrics_list_per_eval_set[eval_set_name].append(
                    iteration_metrics_per_eval_set
                )

        self.callback_info_list.append(callback_info)
        self._log(callback_info)

        return True


class PyBoostLoggingCallback(ModelLoggingCallback):
    """Logging callback for PyBoost models."""

    _sets_list = ["train", "valid"]

    def before_train(self, evr) -> None:
        """
        Actions to be made before each training starts.

        Args:
            evr (dict): Event-related information before training starts.

        Returns:
            None
        """
        return

    def before_iteration(self, evr) -> None:
        """
        Actions to be made before each iteration starts.

        Args:
            evr (dict): Event-related information before the iteration starts.

        Returns:
            None
        """
        return

    def after_iteration(self, evr: Dict) -> bool:
        """
        Actions to be made after each iteration finishes.

        Args:
            evr (Dict): Event-related information after the iteration finishes, containing iteration number and scores.

        Returns:
            bool: Returns False to indicate that training should continue.
        """
        num_iter = evr["num_iter"]
        callback_info = ModelCallbackInfo(num_iter, [], {})

        metric_class = evr["model"].metric
        metric_name = (
            metric_class.name
            if hasattr(metric_class, "name")
            else (
                metric_class.alias
                if hasattr(metric_class, "alias")
                else metric_class.__class__.__name__
            )
        )
        if num_iter > 0:
            scores = dict(zip(self._sets_list, evr["iter_score"]))
            callback_info.train_metrics_list.append({metric_name: scores["train"]})
            if "valid" not in callback_info.metrics_list_per_eval_set:
                callback_info.metrics_list_per_eval_set["valid"] = [
                    {metric_name: scores["valid"]}
                ]
            else:
                callback_info.metrics_list_per_eval_set["valid"].append(
                    {metric_name: scores["valid"]}
                )

        self.callback_info_list.append(callback_info)
        self._log(callback_info)

        return False

    def after_train(self, evr) -> None:
        """
        Actions to be made after training finishes.

        Args:
            evr (dict): Event-related information after training finishes.

        Returns:
            None
        """
        return


class AddIntermediateMetricsCallback:
    """
    Callback to add intermediate metrics to an Optuna study during optimization.

    Attributes:
        iter_param_name (str): The name of the iteration parameter to update in trial parameters.
        max_iters (int): The maximum number of iterations allowed.
    """

    def __init__(self, iter_param_name: str, max_iters: int):
        """
        Initializes the AddIntermediateMetricsCallback.

        Args:
            iter_param_name (str): The name of the iteration parameter to update in trial parameters.
            max_iters (int): The maximum number of iterations allowed.
        """
        self.iter_param_name = iter_param_name
        self.max_iters = max_iters

    def __call__(
        self,
        study: optuna.study.Study,
        trial: optuna.trial.FrozenTrial,
    ) -> None:
        """
        Adds intermediate metrics to the Optuna study based on the trial's intermediate values.

        Args:
            study (optuna.study.Study): The Optuna study object to which trials are added.
            trial (optuna.trial.FrozenTrial): The current trial containing parameters and intermediate values.

        Raises:
            None

        Returns:
            None
        """
        trial_params = trial.params
        trial_distributions = trial.distributions

        # Check to ensure we do not exceed max_iters
        for iteration, value in trial.intermediate_values.items():
            if iteration <= self.max_iters and iteration != 0:
                trial_params.update({self.iter_param_name: iteration})
                trial_distributions.update(
                    {
                        self.iter_param_name: optuna.distributions.IntDistribution(
                            0, self.max_iters
                        )
                    }
                )
                intermediate_trial = optuna.trial.create_trial(
                    params=trial_params, distributions=trial_distributions, value=value
                )
                study.add_trial(intermediate_trial)