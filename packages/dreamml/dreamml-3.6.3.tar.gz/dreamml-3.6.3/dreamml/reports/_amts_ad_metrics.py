import numpy as np
import pandas as pd
from typing import Optional, Dict
from scipy.stats import pearsonr, spearmanr

from dreamml.logging import get_logger
from dreamml.modeling.metrics.metrics_mapping import metrics_mapping
from dreamml.modeling.models.estimators import BoostingBaseModel
from dreamml.modeling.models.estimators import BaseModel
from dreamml.reports.metrics_calculation import BaseMetricsCalculator

_logger = get_logger(__name__)


class CalculateAMTSADMetrics(BaseMetricsCalculator):
    """Calculate AMTSAD metrics for provided models and evaluation datasets.

    This class inherits from BaseMetricsCalculator and is responsible for computing
    various evaluation metrics for binary classification models. It supports multiple
    models, handles predictions, and computes metrics such as MAE, RMSE, MAPE, R²,
    Pearson correlation, and Spearman rank correlation.

    Attributes:
        models (Dict[str, BaseModel]): Dictionary of models to evaluate.
        group_column: Column name used for grouping the data.
        split_by_group: Flag indicating whether to split metrics calculation by group.
        predictions_ (Dict[str, np.ndarray]): Dictionary to store model predictions.
        predictions_loss_ (Dict[str, np.ndarray]): Dictionary to store prediction losses.
        predictions_mark_ (Dict[str, np.ndarray]): Dictionary to store prediction marks.
        metrics (Dict[str, Callable]): Dictionary of metrics to calculate.
        target_ (Dict[str, np.ndarray]): Dictionary to store target values.
    """

    def __init__(
        self,
        models: Dict[str, BaseModel],
        group_column,
        split_by_group,
        predictions: Optional[Dict] = None,
        vectorizers: Optional[Dict] = None,
    ) -> None:
        """Initialize CalculateAMTSADMetrics with models and configuration.

        Args:
            models (Dict[str, BaseModel]): Dictionary of models to evaluate.
            group_column: Column name used for grouping the data.
            split_by_group: Flag indicating whether to split metrics calculation by group.
            predictions (Optional[Dict], optional): Precomputed predictions. Defaults to None.
            vectorizers (Optional[Dict], optional): Vectorizer objects for preprocessing. Defaults to None.

        Raises:
            RuntimeError: If no instances of `BoostingBaseModel` are found in the models.
        """
        super().__init__(models, predictions=predictions, vectorizers=vectorizers)
        self.models = models
        self.target_ = {}
        self.predictions_ = {}
        self.predictions_loss_ = {}
        self.predictions_mark_ = {}
        self.metrics = self._get_metrics_to_calculate()
        self.group_column = group_column
        self.split_by_group = split_by_group

    def _get_metrics_to_calculate(self):
        """Retrieve the set of metrics to calculate based on the first BoostingBaseModel.

        Iterates through the provided models to find an instance of `BoostingBaseModel`.
        Initializes default metrics and appends additional metrics if not already present.

        Returns:
            Dict[str, Callable]: A dictionary mapping metric names to their corresponding functions.

        Raises:
            RuntimeError: If no instances of `BoostingBaseModel` are found in the models.
        """
        first_model = None
        for first_model in self.models.values():
            if isinstance(first_model, BoostingBaseModel):
                break
        if first_model is None:
            raise RuntimeError(
                "No instances of `BoostingBaseModel` found in `prepared_model_dict`"
            )

        metrics = {
            first_model.objective.name: first_model.objective,
            first_model.eval_metric.name: first_model.eval_metric,
        }

        for name in ["mae", "rmse", "mape", "r2"]:
            if name not in metrics:
                metrics[name] = metrics_mapping[name]()

        metrics["pearsonr"] = pearsonr
        metrics["spearmanr"] = spearmanr

        return metrics

    def create_all_predictions(self, **eval_set):
        """Generate predictions for all models using the provided evaluation datasets.

        Applies each model in `self.models` to the corresponding evaluation dataset.
        Stores the predictions, prediction losses, and prediction marks in respective
        dictionaries.

        Args:
            **eval_set: Arbitrary keyword arguments representing evaluation datasets.
                       Expected to include 'nbeats_inference_data'.
        """
        for model in self.models:
            data = eval_set["nbeats_inference_data"]

            pred_dict = self.models[model].transform(data)
            for segment_name, pred_by_segment in pred_dict.items():
                self.predictions_[f"{model}_{segment_name}"] = pred_by_segment

            pred_loss_dict = self.models[model].transform(data, return_ad_loss=True)
            for segment_name, pred_loss_by_segment in pred_loss_dict.items():
                self.predictions_loss_[f"{model}_{segment_name}"] = pred_loss_by_segment

            pred_mark_dict = self.models[model].transform(data, return_ad_mark=True)
            for segment_name, pred_mark_by_segment in pred_mark_dict.items():
                self.predictions_mark_[f"{model}_{segment_name}"] = pred_mark_by_segment

    def calculate_metrics(self, model_name, model_group, **kwargs):
        """Calculate evaluation metrics for a specific model and group.

        Computes the predefined metrics by comparing the model's predictions against
        the true target values. Handles different metric types and manages exceptions
        during metric computation.

        Args:
            model_name (str): Name of the model from `self.models`.
            model_group (str): The group associated with the model.
            **kwargs: Arbitrary keyword arguments, expected to include 'nbeats_inference_data'.

        Returns:
            List[float]: A list containing the model name followed by the calculated metric scores.
                         Metrics are rounded to two decimal places where applicable.
        """
        try:
            metrics_score = [model_name]
        except TypeError:
            metrics_score = [model_name]

        data = kwargs["nbeats_inference_data"]
        y = data["y"].reshape(-1)
        for metric_name, metric in self.metrics.items():
            for segment_name, pred in self.predictions_.items():
                self.target_[model_group] = y
                if segment_name != model_group:
                    continue
                try:
                    score = metric(y, pred)
                except (ValueError, TypeError, KeyError) as e:
                    print(f"{e}")
                    score = np.nan
                if isinstance(score, tuple):
                    metrics_score.append(round(100 * score[0], 2))
                elif isinstance(score, (int, float, np.float32, np.float64)):
                    if metric_name in [
                        "r2",
                    ]:
                        metrics_score.append(round(100 * score, 2))
                    else:
                        metrics_score.append(round(score, 2))
                else:
                    metrics_score.append(0)

        return metrics_score

    def transform(self, **eval_sets):
        """Compute binary classification metrics for each model and evaluation set.

        Iterates through all models and evaluation datasets to calculate the required
        metrics. Organizes the results into a pandas DataFrame for easy interpretation.

        Args:
            **eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                Dictionary where the key is the name of the evaluation set, and the value
                is a tuple containing the feature matrix and the true target vector.

        Returns:
            pd.DataFrame: A DataFrame containing the calculated metric values for each model
                          and evaluation set.
        """
        scores = {}
        self.create_all_predictions(**eval_sets)

        for model in self.models:
            if model == "nbeats_revin":
                for segment_name, pred_by_segment in self.predictions_.items():
                    scores[f"{segment_name}"] = self.calculate_metrics(
                        model, segment_name, **eval_sets
                    )
            elif model == "LinearReg":
                scores[f"{model}_model_0"] = self.calculate_metrics(
                    model, "model_0", **eval_sets
                )
            else:
                for model_group in self.models[model].models_by_groups:
                    scores[f"{model}_{model_group}"] = self.calculate_metrics(
                        model, model_group, **eval_sets
                    )
        return self._to_frame(scores, **eval_sets)

    def _to_frame(self, scores: dict, **eval_sets) -> pd.DataFrame:
        """Convert the metrics scores dictionary to a pandas DataFrame.

        Formats the scores dictionary into a DataFrame, renames the columns to include
        metric names and evaluation set identifiers, and fills missing values with zeros.
        Additionally, adds a column with model details.

        Args:
            scores (Dict[str, List[float]]): 
                Dictionary where the key is the model name and the value is a list of metric scores.
            **eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                Dictionary where the key is the name of the evaluation set, and the value
                is a tuple containing the feature matrix and the true target vector.

        Returns:
            pd.DataFrame: A formatted DataFrame containing metric scores with appropriate column names.
        """
        scores = pd.DataFrame(scores)
        scores = scores.T.reset_index()
        scores_name = ["Model Name", "# Features"]

        for metric in self.metrics:
            scores_name.append(f"{metric} test")

        if self.calculate_metrics_ratio:
            scores_name.append(f"{metric} delta train vs test")
            scores_name.append(f"{metric} delta train vs test, %")

            if "OOT" in eval_sets:
                scores_name.append(f"{metric} delta train vs OOT")
                scores_name.append(f"{metric} delta train vs OOT, %")

        scores.columns = scores_name
        scores = scores.fillna(0)

        scores["Model Details"] = [
            f"Link to train sheet {model}" for model in scores["Model Name"]
        ]
        return scores