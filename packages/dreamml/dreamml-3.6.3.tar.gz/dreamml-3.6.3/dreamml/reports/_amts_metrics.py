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


class CalculateAMTSMetrics(BaseMetricsCalculator):
    """Calculator for AMTS metrics using provided models and evaluation datasets.

    This class extends BaseMetricsCalculator to compute various metrics
    for the given models across different evaluation datasets, optionally
    splitting results by group.

    Attributes:
        models (Dict[str, BaseModel]): Dictionary of models to evaluate.
        group_column (Any): Column name used for grouping in split_by_group.
        split_by_group (bool): Flag indicating whether to split metrics by group.
        predictions_ (Dict[str, Any]): Dictionary to store predictions from models.
        metrics (Dict[str, Callable]): Dictionary mapping metric names to metric functions.
    """

    def __init__(
        self,
        models: Dict[str, BaseModel],
        group_column,
        split_by_group,
        predictions: Optional[Dict] = None,
        vectorizers: Optional[Dict] = None,
    ) -> None:
        """Initializes the CalculateAMTSMetrics instance.

        Args:
            models (Dict[str, BaseModel]): Dictionary of models to evaluate.
            group_column (Any): Column name used for grouping in split_by_group.
            split_by_group (bool): Flag indicating whether to split metrics by group.
            predictions (Optional[Dict], optional): Initial predictions dictionary. Defaults to None.
            vectorizers (Optional[Dict], optional): Dictionary of vectorizers if any. Defaults to None.
        
        Raises:
            RuntimeError: If no instances of BoostingBaseModel are found in models.
        """
        super().__init__(models, predictions=predictions, vectorizers=vectorizers)
        self.models = models
        self.predictions_ = {}
        self.metrics = self._get_metrics_to_calculate()
        self.group_column = group_column
        self.split_by_group = split_by_group

    def _get_metrics_to_calculate(self):
        """Retrieves the metrics to calculate based on the models.

        Iterates through the provided models to find the first instance of BoostingBaseModel
        and uses its objective and evaluation metric as part of the metrics to compute.
        Additionally adds standard metrics like MAE, RMSE, MAPE, R2, Pearsonr, and Spearmanr.

        Returns:
            Dict[str, Callable]: A dictionary mapping metric names to their corresponding functions.

        Raises:
            RuntimeError: If no instances of BoostingBaseModel are found in models.
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
        """Generates predictions for all models using the provided evaluation datasets.

        Applies each model in self.models to the corresponding datasets in eval_set.
        Handles special cases for 'nbeats_revin' and 'LinearReg' models and supports
        splitting predictions by group if required.

        Args:
            **eval_set: Arbitrary keyword arguments representing evaluation datasets.
                Each key corresponds to a dataset name, and each value is the dataset itself.
        
        Raises:
            None
        """
        for model in self.models:

            if model == "nbeats_revin":
                data = eval_set["nbeats_train_data"]
                data["X"] = data.pop("X_test")
                data["ids"] = data.pop("ids_test")
                pred_dict = self.models[model].transform(data)
                for segment_name, pred_by_segment in pred_dict.items():
                    self.predictions_[f"{model}_{segment_name}"] = pred_by_segment
            elif model == "LinearReg":
                sample_pred = {}
                for sample in eval_set:
                    data, _ = eval_set[sample]
                    data = data.sort_index()
                    pred = self.create_prediction(self.models[model], data)
                    sample_pred[sample] = pred
                self.predictions_[f"{model}_model_0"] = sample_pred
            else:
                for model_group in self.models[model].models_by_groups:

                    sample_pred = {}

                    for sample in eval_set["amts_train_data"]:
                        data, _ = eval_set["amts_train_data"][sample]
                        data = data.sort_index()
                        pred = self.create_prediction(self.models[model], data)

                        if self.split_by_group:
                            sample_pred[sample] = pred[model_group]
                        else:
                            sample_pred[sample] = pred

                    self.predictions_[f"{model}_{model_group}"] = sample_pred

    def calculate_metrics(self, model_name, model_group, **kwargs):
        """Calculates metrics for a specific model and group.

        Computes specified metrics by comparing true targets with predictions for
        a given model and group. Handles different model types such as 'nbeats_revin',
        'AMTS', and 'linear_reg'.

        Args:
            model_name (str): Name of the model from self.models.
            model_group (str): Specific group within the model if applicable.
            **kwargs: Additional keyword arguments containing evaluation datasets.
                Expected to include datasets like 'nbeats_train_data' or 'amts_train_data'.

        Returns:
            list: A list containing the model name followed by the computed metric scores.
        
        Raises:
            None
        """
        try:
            metrics_score = [model_name]
        except TypeError:
            metrics_score = [model_name]

        if model_name == "nbeats_revin":
            data = kwargs["nbeats_train_data"]
            y = data["y_test"]
            for metric_name, metric in self.metrics.items():
                for target, (segment_name, pred) in zip(y, self.predictions_.items()):
                    if segment_name != model_group:
                        continue
                    try:
                        score = metric(target, pred)
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

        elif model_name in ["AMTS", "linear_reg"]:
            for metric_name, metric in self.metrics.items():
                for sample in kwargs["amts_train_data"]:
                    df, target = kwargs["amts_train_data"][sample]

                    if self.split_by_group:
                        df["y"] = target
                        for group_name, df_group in df.groupby(self.group_column):
                            if f"model_{group_name}" == model_group:
                                target = np.array(df_group["y"])
                            pred = self.predictions_[f"{model_name}_{model_group}"][
                                sample
                            ]
                    else:
                        pred = self.predictions_[f"{model_name}_{model_group}"][sample]
                    try:
                        score = metric(target, pred)
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
        """Calculates classification metrics for each model and evaluation set.

        Processes all models in self.models and each dataset in eval_sets to compute
        the relevant metrics. Aggregates the results into a pandas DataFrame.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.
                Each key corresponds to a dataset name, and each value is the dataset itself.
        
        Returns:
            pandas.DataFrame: A DataFrame containing the computed metric values for each model.
        
        Raises:
            None
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
        """Converts the scores dictionary into a formatted pandas DataFrame.

        Transforms the scores dictionary, which maps model names to metric scores,
        into a pandas DataFrame with appropriate column names. Handles naming conventions
        based on the presence of 'AMTS' or 'linear_reg' models and fills missing values with zeros.

        Args:
            scores (dict): Dictionary mapping model names to lists of metric scores.
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.
                Each key corresponds to a dataset name, and each value is the dataset itself.

        Returns:
            pandas.DataFrame: A DataFrame containing the formatted metric scores.
        
        Raises:
            None
        """
        scores = pd.DataFrame(scores)
        scores = scores.T.reset_index()
        scores_name = ["Model Name", "# Features"]

        for metric in self.metrics:
            if "AMTS" in self.models or "linear_reg" in self.models:
                for sample in eval_sets["amts_train_data"]:
                    scores_name.append(f"{metric} {sample}")
            else:
                scores_name.append(f"{metric} test")

        if self.calculate_metrics_ratio:
            scores_name.append(f"{metric} delta train vs test")
            scores_name.append(f"{metric} delta train vs test, %")

        scores.columns = scores_name
        scores = scores.fillna(0)

        scores["Model Details"] = [
            f"Link to train sheet {model}" for model in scores["Model Name"]
        ]
        return scores