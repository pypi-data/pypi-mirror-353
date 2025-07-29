from typing import Optional, Tuple, Dict
import numpy as np
import pandas as pd
import math

from sklearn.metrics import confusion_matrix

from dreamml.configs.config_storage import ConfigStorage
from dreamml.reports.kds import report
from sklearn.preprocessing import LabelBinarizer

from dreamml.modeling.metrics.metrics_mapping import metrics_mapping
from dreamml.logging import get_logger
from dreamml.reports.metrics_calculation import BaseMetricsCalculator
from dreamml.modeling.models.estimators import BaseModel
from dreamml.utils.confidence_interval import (
    create_bootstrap_scores,
    calculate_conf_interval,
)

_logger = get_logger(__name__)


class CalculateDataStatistics:
    """
    Calculates statistical summaries for datasets and features.

    This class provides methods to compute:
        - Statistics for each dataset (e.g., train, valid):
            Number of observations, number of target events, and the proportion of target events.
        - Feature statistics:
            Target variable name, number of categorical features, and number of continuous features.
        - Detailed statistics for each feature:
            Variable name, number of non-missing values, minimum, mean, maximum values, and percentiles (25th, 50th, 75th).

    Attributes:
        transformer (Optional): Transformer for categorical features.
        features (pd.Series): Series containing all feature names.
        config (ConfigStorage): Configuration storage object.
        task (str): Type of the task (e.g., "binary", "multiclass", "multilabel").
        business (bool): Flag indicating whether to include business-specific statistics.
    """

    def __init__(
        self,
        transformer: Optional,
        features: pd.Series,
        config: ConfigStorage,
        task: str,
        business: bool = False,
    ) -> None:
        """
        Initializes the CalculateDataStatistics class.

        Args:
            transformer (Optional): Transformer for categorical features.
            features (pd.Series): Series containing all feature names.
            config (ConfigStorage): Configuration storage object.
            task (str): Type of the task (e.g., "binary", "multiclass", "multilabel").
            business (bool, optional): Flag indicating whether to include business-specific statistics. Defaults to False.
        """
        self.features = features
        self.transformer = transformer
        self.config = config
        self.task = task
        self.business = business

    def _calculate_samples_stats(self, **eval_sets) -> pd.DataFrame:
        """
        Calculates statistics for each evaluation dataset.

        Computes the number of observations, number of target events, and the event rate for each dataset.

        Args:
            **eval_sets: Dict[str, Tuple[pd.DataFrame, pd.Series]]
                A dictionary where keys are dataset names (e.g., "train", "valid") and values are tuples
                containing the feature matrix and target vector.

        Returns:
            pd.DataFrame: DataFrame containing the calculated statistics for each dataset.

        Raises:
            ValueError: If the task type is not one of "binary", "multiclass", or "multilabel".
        """
        if self.task == "binary":
            result = {}
            for data_name in eval_sets:
                data, target = eval_sets[data_name]

                if self.business:
                    time_column = self.config.data.columns.time_column
                    if time_column is not None:
                        start_date = data[time_column].min()
                        end_date = data[time_column].max()
                    else:
                        start_date = "NA"
                        end_date = "NA"

                    stats = [
                        start_date,
                        end_date,
                        len(data),
                        len(data) - np.sum(target),
                        np.sum(target),
                        np.mean(target),
                    ]

                    if "All_sample" not in result:
                        result["All_sample"] = ["NA", "NA", 0, 0, 0, 0]
                        if time_column is not None:
                            result["All_sample"][0] = start_date
                            result["All_sample"][1] = end_date

                    if time_column is not None:
                        result["All_sample"][0] = min(
                            start_date, result["All_sample"][0]
                        )
                        result["All_sample"][1] = max(end_date, result["All_sample"][1])
                    result["All_sample"][2] += stats[2]
                    result["All_sample"][3] += stats[3]
                    result["All_sample"][4] += stats[4]
                    result["All_sample"][5] = (
                        result["All_sample"][4] / result["All_sample"][2]
                    )
                else:
                    stats = [len(data), np.sum(target), np.mean(target)]

                result[data_name] = stats

            result = pd.DataFrame(result).T.reset_index()

            if self.business:
                columns = [
                    "Dataset",
                    "Start_date",
                    "End_date",
                    "Observations",
                    '"0"',
                    '"1"',
                    "Event-Rate",
                ]
            else:
                columns = ["Dataset", "# Observations", "# Events", "# Event Rate"]

            result.columns = columns

            if self.business and self.config.data.columns.time_column is not None:
                result["Start_date"] = result["Start_date"].dt.strftime("%d.%m.%y")
                result["End_date"] = result["End_date"].dt.strftime("%d.%m.%y")

            return result.fillna(0)

        elif self.task in ("multiclass", "multilabel"):
            if self.task == "multiclass":
                labels = self.config.pipeline.metric_params["labels"]
                arange_labels = np.arange(len(labels))
                labels_dict = dict(zip(arange_labels, labels))
                label_binarizer = LabelBinarizer().fit(arange_labels)
                eval_set_cols = labels
            else:
                eval_set_cols = eval_sets["train"][1].columns.tolist()

            columns = ["Dataset", "# Observations"]
            columns.extend([f"# Events {class_name}" for class_name in eval_set_cols])
            columns.extend(
                [f"# Event Rate {class_name}" for class_name in eval_set_cols]
            )

            result = {}
            for data_name in eval_sets:
                data, target = eval_sets[data_name]
                if self.config.pipeline.task == "multiclass":
                    labels_in_sample = arange_labels

                    target = pd.DataFrame(
                        data=label_binarizer.transform(target), columns=labels_in_sample
                    )

                events = np.sum(target).tolist()
                event_rate = np.mean(target).tolist()
                result[data_name] = [len(data)] + events + event_rate

            result = pd.DataFrame(result).T.reset_index()
            assert len(columns) == result.shape[1]
            result.columns = columns
            return result.fillna(0)

        else:
            raise ValueError(
                f'Task must be one of ["binary", "multiclass", "multilabel"], but got {self.task}'
            )

    def _calculate_variables_stats(self, **eval_sets) -> pd.DataFrame:
        """
        Calculates statistical summaries for each feature across datasets.

        Computes the number of non-missing values, mean, standard deviation,
        minimum, 25th percentile, median, 75th percentile, and maximum for each feature.

        Args:
            **eval_sets: Dict[str, Tuple[pd.DataFrame, pd.Series]]
                A dictionary where keys are dataset names (e.g., "train", "valid") and values are tuples
                containing the feature matrix and target vector.

        Returns:
            pd.DataFrame: DataFrame containing the calculated statistics for each feature.
        """
        sample_name = next(iter(eval_sets))
        data, _ = eval_sets[sample_name]

        result = data.describe().T.reset_index()

        if len(result.columns) == 5:  # Only text features in the dataset
            result.columns = ["Variable Name", "Count", "Unique", "Top", "Freq"]
        else:
            result.columns = [
                "Variable Name",
                "Number of Filled Values",
                "AVG Value",
                "STD Value",
                "MIN Value",
                "25% Percentile Value",
                "50% Percentile Value",
                "75% Percentile Value",
                "MAX Value",
            ]

        return result.fillna(0)

    def _calculate_variables_types_stats(self) -> pd.DataFrame:
        """
        Calculates statistics based on feature types.

        Computes the number of categorical variables, the number of continuous variables,
        and the name of the target variable.

        Returns:
            pd.DataFrame: DataFrame containing the feature type statistics.

        Raises:
            ValueError: If the task type is not one of "binary", "multiclass", or "multilabel".
        """
        target_name = self.config.data.columns.target_name
        drop_features = self.config.data.columns.drop_features

        if self.task in ["multiclass", "multilabel"]:
            target_names = (
                [target_name] if not isinstance(target_name, list) else target_name
            )
            stats = pd.DataFrame(
                {"Target Variable": [tn for tn in target_names]}
            )
            stats["# Categorical"] = len(self.transformer.cat_features)
            stats["# Continuous"] = (
                self.features.shape[0]
                - len(self.transformer.cat_features)
                - len(drop_features)
            )
            return stats.fillna(0)

        elif self.task == "binary":
            stats = pd.DataFrame(
                {
                    "Target Variable": [target_name],
                    "# Categorical": [len(self.transformer.cat_features)],
                    "# Continuous": [
                        self.features.shape[0]
                        - len(self.transformer.cat_features)
                        - len(drop_features)
                    ],
                }
            )
            return stats.fillna(0)

        else:
            raise ValueError('Task must be one of ["binary", "multiclass", "multilabel"]')

    def transform(
        self, **eval_sets
    ) -> Tuple[Optional[pd.DataFrame], pd.DataFrame, pd.DataFrame]:
        """
        Generates a comprehensive data statistics report.

        Combines sample statistics, feature type statistics, and detailed feature statistics.

        Args:
            **eval_sets: Dict[str, Tuple[pd.DataFrame, pd.Series]]
                A dictionary where keys are dataset names (e.g., "train", "valid") and values are tuples
                containing the feature matrix and target vector.

        Returns:
            Tuple[Optional[pd.DataFrame], pd.DataFrame, pd.DataFrame]:
                A tuple containing:
                    - Sample statistics DataFrame
                    - Feature types statistics DataFrame
                    - Detailed feature statistics DataFrame
        """
        result = (
            self._calculate_samples_stats(**eval_sets),
            self._calculate_variables_types_stats(),
            self._calculate_variables_stats(**eval_sets),
        )
        return result


class CalculateClassificationMetrics(BaseMetricsCalculator):
    """
    Calculates classification metrics for binary classification tasks, including GINI and metric ratios.

    This class computes metrics such as GINI and the relative difference in quality metrics.
    It also determines the best models based on these metrics.

    Attributes:
        metric_name (str): Name of the metric to calculate.
        bootstrap_samples (int): Number of bootstrap samples for confidence intervals.
        p_value (float): Significance level for confidence intervals.
        metric_params (dict): Parameters for the metric calculation.
        task (str): Type of the task (e.g., "binary", "multiclass", "multilabel").
        target_with_nan_values (bool): Indicates if the target contains NaN values (specific to multilabel).
        vectorizers (Optional[Dict]): Dictionary of vectorizers used in the models.
    """

    def __init__(
        self,
        models: Dict[str, BaseModel],
        bootstrap_samples: int = 200,
        p_value: float = 0.05,
        config: ConfigStorage = None,
        metric_name: str = "gini",
        task: str = "binary",
        predictions: Optional[Dict] = None,
        vectorizers: Optional[Dict] = None,
    ) -> None:
        """
        Initializes the CalculateClassificationMetrics class.

        Args:
            models (Dict[str, BaseModel]): Dictionary of models where keys are model names and values are model instances.
            bootstrap_samples (int, optional): Number of bootstrap samples for confidence intervals. Defaults to 200.
            p_value (float, optional): Significance level for confidence intervals. Defaults to 0.05.
            config (ConfigStorage, optional): Configuration storage object. Defaults to None.
            metric_name (str, optional): Name of the metric to calculate. Defaults to "gini".
            task (str, optional): Type of the task (e.g., "binary", "multiclass", "multilabel"). Defaults to "binary".
            predictions (Optional[Dict], optional): Dictionary of model predictions on evaluation sets. Defaults to None.
            vectorizers (Optional[Dict], optional): Dictionary of vectorizers used in the models. Defaults to None.
        """
        self.metric_name = metric_name
        self.bootstrap_samples = bootstrap_samples
        self.p_value = p_value
        self.metric_params = config.pipeline.metric_params
        self.task = task
        self.target_with_nan_values = (
            config.pipeline.task_specific.multilabel.target_with_nan_values
        )
        self.vectorizers = vectorizers

        super().__init__(models, predictions, vectorizers, calculate_metrics_ratio=True)

    def _get_metrics_to_calculate(self):
        """
        Determines which metrics to calculate based on the task type.

        Returns:
            Dict[str, Any]: Dictionary mapping metric names to their corresponding metric classes.
        """
        if self.task == "multiclass":
            metric_class = metrics_mapping[self.metric_name](
                task=self.task, labels=self.metric_params["labels"]
            )
        elif self.task == "multilabel":
            metric_class = metrics_mapping[self.metric_name](
                task=self.task, target_with_nan_values=self.target_with_nan_values
            )
        else:
            metric_class = metrics_mapping[self.metric_name](
                task=self.task,
            )
        return {self.metric_name: metric_class}

    def get_best_models(self, stats_df: pd.DataFrame, **eval_sets) -> dict:
        """
        Identifies the best models based on the Gini metric on test and OOT datasets.

        Args:
            stats_df (pd.DataFrame): DataFrame containing model names, metrics, and the number of features.
            **eval_sets: Dict[str, Tuple[pd.DataFrame, pd.Series]]
                A dictionary where keys are dataset names (e.g., "test", "OOT") and values are tuples
                containing the feature matrix and target vector.

        Returns:
            dict: Dictionary containing the best model names, their indices, and confidence intervals for "test" and "oot" datasets.
        """
        stats_df = stats_df.reset_index(drop=True)

        metric_name = self.metric_name
        metric = metrics_mapping[self.metric_name](task=self.task, **self.metric_params)

        metric_column = metric_name + " test"

        best_score = (
            stats_df[metric_column].max()
            if metric.maximize
            else stats_df[metric_column].min()
        )

        test_best_score_model_name = stats_df[stats_df[metric_column] == best_score][
            "Model Name"
        ].to_list()[0]

        test_scores = create_bootstrap_scores(
            x=eval_sets["test"][0],
            y=eval_sets["test"][1],
            y_pred=self.predictions_[test_best_score_model_name]["test"],
            metric=metric,
            bootstrap_samples=self.bootstrap_samples,
            task=self.task,
            random_seed=27,
        )
        test_conf_interval = calculate_conf_interval(test_scores, alpha=self.p_value)

        min_num_of_features_test = stats_df[
            (stats_df[metric_name + " test"] >= test_conf_interval[0])
            & (stats_df[metric_name + " test"] <= test_conf_interval[1])
        ]["# Features"].min()
        if not (
            min_num_of_features_test > 0
        ):  # For grouped metrics: select the best model
            min_num_of_features_test = stats_df[
                stats_df["Model Name"] == test_best_score_model_name
            ]["# Features"].max()
            _logger.info(
                "The best model on test ("
                + metric_name
                + ") was selected based on the metric performance on test rather than the confidence interval (see report)."
            )

        # If the dataset is small, the confidence interval may not be well-estimated -- reduce p_value to 0.01
        if math.isnan(min_num_of_features_test):
            while self.p_value > 0.01 and math.isnan(min_num_of_features_test):
                self.p_value = np.round(self.p_value / 2, 2)
                test_conf_interval = calculate_conf_interval(
                    test_scores, alpha=self.p_value
                )

                min_num_of_features_test = stats_df[
                    (stats_df[metric_name + " test"] >= test_conf_interval[0])
                    & (stats_df[metric_name + " test"] <= test_conf_interval[1])
                ]["# Features"].min()

        min_df_test = stats_df[stats_df["# Features"] == min_num_of_features_test]
        if metric_name == "logloss":
            best_model_name_test = min_df_test[
                min_df_test[metric_name + " test"]
                == min_df_test[metric_name + " test"].min()
            ]["Model Name"].to_list()[0]
        else:
            best_model_name_test = min_df_test[
                min_df_test[metric_name + " test"]
                == min_df_test[metric_name + " test"].max()
            ]["Model Name"].to_list()[0]

        best_idx_test = stats_df[
            stats_df["Model Name"] == best_model_name_test
        ].index[0]

        best_results = {
            "test": {
                "name": best_model_name_test,
                "index": best_idx_test,
                "ci": test_conf_interval,
            }
        }
        if "OOT" in eval_sets.keys():
            if metric_name == "logloss":
                oot_best_score_model_name = stats_df[
                    stats_df[metric_name + " OOT"]
                    == stats_df[metric_name + " OOT"].min()
                ]["Model Name"].to_list()[0]
            else:
                oot_best_score_model_name = stats_df[
                    stats_df[metric_name + " OOT"]
                    == stats_df[metric_name + " OOT"].max()
                ]["Model Name"].to_list()[0]

            oot_scores = create_bootstrap_scores(
                x=eval_sets["OOT"][0],
                y=eval_sets["OOT"][1],
                y_pred=self.predictions_[test_best_score_model_name]["OOT"],
                metric=metric,
                bootstrap_samples=self.bootstrap_samples,
                task=self.task,
                random_seed=27,
            )
            oot_conf_interval = calculate_conf_interval(oot_scores, alpha=self.p_value)

            min_num_of_features_oot = stats_df[
                (stats_df[metric_name + " OOT"] >= oot_conf_interval[0])
                & (stats_df[metric_name + " OOT"] <= oot_conf_interval[0])
            ]["# Features"].min()
            if not (
                min_num_of_features_oot > 0
            ):  # For grouped metrics: select the best model
                min_num_of_features_oot = stats_df[
                    stats_df["Model Name"] == oot_best_score_model_name
                ]["# Features"].max()
                _logger.info(
                    "The best model on OOT ("
                    + metric_name
                    + ") was selected based on the metric performance on OOT rather than the confidence interval (see report)."
                )
            min_df_oot = stats_df[stats_df["# Features"] == min_num_of_features_oot]
            if metric_name == "logloss":
                best_model_name_oot = min_df_oot[
                    min_df_oot[metric_name + " OOT"]
                    == min_df_oot[metric_name + " OOT"].min()
                ]["Model Name"].to_list()[0]
            else:
                best_model_name_oot = min_df_oot[
                    min_df_oot[metric_name + " OOT"]
                    == min_df_oot[metric_name + " OOT"].max()
                ]["Model Name"].to_list()[0]

            best_idx_oot = stats_df[
                stats_df["Model Name"] == best_model_name_oot
            ].index[0]
            best_results["oot"] = {
                "name": best_model_name_oot,
                "index": best_idx_oot,
                "ci": oot_conf_interval,
            }
        return best_results


class CalculateDetailedMetrics:
    """
    Calculates detailed metrics for binary classification tasks.

    This class computes metrics for each bin of the model's predicted probabilities.
    For each bin, the following metrics are calculated:
        - Minimum, mean, and maximum probability.
        - Event rate within the bin.
        - Number of observations, target events, and non-target events.
        - Cumulative target and non-target events.
        - False Positive Rate (FPR) and True Positive Rate (TPR).
        - GINI coefficient.
        - ROC-AUC score, its standard error, and a 95% confidence interval.

    Attributes:
        n_bins (int): Number of bins to divide the predicted probabilities.
        metric_name (str): Name of the primary metric to calculate.
        metric_params (dict): Parameters for metric calculations.
        task (str): Type of the task (e.g., "binary", "multiclass", "multilabel").
    """

    def __init__(
        self,
        n_bins: int = 20,
        metric_name: str = "gini",
        metric_params: dict = None,
        task: str = "binary",
    ):
        """
        Initializes the CalculateDetailedMetrics class.

        Args:
            n_bins (int, optional): Number of bins to divide the predicted probabilities. Defaults to 20.
            metric_name (str, optional): Name of the primary metric to calculate. Defaults to "gini".
            metric_params (dict, optional): Parameters for metric calculations. Defaults to None.
            task (str, optional): Type of the task (e.g., "binary", "multiclass", "multilabel"). Defaults to "binary".
        """
        self.n_bins = n_bins
        self.metric_name = metric_name
        self.metric_params = metric_params
        self.task = task

    @staticmethod
    def calculate_conf_interval(
        y_true, y_pred, scores: pd.DataFrame, metric_name, metric_params, task: str
    ) -> pd.DataFrame:
        """
        Calculates the confidence interval and standard error for ROC AUC.

        Args:
            y_true: Ground truth target values.
            y_pred: Predicted probabilities.
            scores (pd.DataFrame): DataFrame with basic metrics calculated per bin.
            metric_name (str): Name of the primary metric.
            metric_params (dict): Parameters for metric calculations.
            task (str): Type of the task.

        Returns:
            pd.DataFrame: DataFrame updated with confidence intervals and standard errors.

        Raises:
            KeyError: If the required columns are missing in the DataFrame.
        """
        num_row = scores.shape[0]
        task_ = "binary" if task == "multilabel" else task

        if task in ["multilabel", "binary"]:
            data = pd.DataFrame({"y_pred": y_pred, "y_true": y_true})
            data = (
                data.dropna(subset=["y_true"])
                if data["y_true"].isna().sum() > 0
                else data
            )
            y_true, y_pred = data["y_true"], data["y_pred"]

        auc = 100 * metrics_mapping.get("roc_auc")(task=task_, **metric_params)(
            y_true, y_pred
        )
        gini = 2 * auc - 100
        metric = 100 * metrics_mapping.get(metric_name)(task=task_, **metric_params)(
            y_true, y_pred
        )

        std_error = 1.96 * np.sqrt(auc * (100 - auc) / y_true.shape[0])
        std_metric = 1.96 * np.sqrt(auc * np.abs(100 - metric) / y_true.shape[0])

        scores.loc[num_row, metric_name] = metric
        scores.loc[num_row, metric_name + " Std Err"] = std_metric
        scores.loc[num_row, metric_name + " 95% LCL"] = metric - std_metric
        scores.loc[num_row, metric_name + " 95% UCL"] = metric + std_metric
        scores.loc[num_row, "GINI"] = gini
        scores.loc[num_row, "AUC"] = auc
        scores.loc[num_row, "AUC Std Err"] = std_error
        scores.loc[num_row, "AUC 95% LCL"] = auc - std_error
        scores.loc[num_row, "AUC 95% UCL"] = auc + std_error

        return np.round(scores, 4)

    @staticmethod
    def calculate_total_stats(scores: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates overall statistics for the entire dataset.

        Computes the total number of observations, target events, non-target events,
        and the overall event rate.

        Args:
            scores (pd.DataFrame): DataFrame with metrics calculated per bin.

        Returns:
            pd.DataFrame: DataFrame updated with total statistics.
        """
        num_row = scores.shape[0] - 1
        scores.loc[num_row, "decile"] = "Total"
        scores.loc[num_row, "#obs"] = scores["#obs"].sum()
        scores.loc[num_row, "#event"] = scores["#event"].sum()
        scores.loc[num_row, "#nonevent"] = scores["#nonevent"].sum()
        scores.loc[num_row, "eventrate"] = scores["#event"].sum() / scores["#obs"].sum()
        return scores

    def calculate_base_bins_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates basic metrics for each bin.

        Args:
            data (pd.DataFrame): DataFrame containing 'y_pred', 'y_true', and 'bin' columns.

        Returns:
            pd.DataFrame: DataFrame with metrics calculated for each bin.

        Raises:
            ValueError: If there is an issue with metric calculations.
        """
        data_gp = data.groupby(["bin"])
        scores = data_gp.agg(
            {"y_pred": ["min", "mean", "max"], "y_true": ["mean", "count", "sum"]}
        )
        scores.columns = [
            "prob_min",
            "prob_mean",
            "prob_max",
            "eventrate",
            "#obs",
            "#event",
        ]
        scores = scores.reset_index()
        scores["bin"] = np.arange(1, scores.shape[0] + 1)
        scores = scores.sort_values(by="bin", ascending=False)

        scores["#nonevent"] = scores["#obs"] - scores["#event"]
        scores["cum # ev"] = scores["#event"].cumsum()
        scores["cum # nonev"] = scores["#nonevent"].cumsum()
        scores = scores.reset_index(drop=True)

        try:
            fpr, tpr = self.roc_auc_metrics(data)
            tpr = np.round(100 * tpr, 4)
            fpr = np.round(100 * fpr, 4)
            scores["1 - Specificity"] = fpr[: len(scores)][::-1]
            scores["Sensitivity"] = tpr[: len(scores)][::-1]
            return scores
        except ValueError:
            return scores

    def roc_auc_metrics(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates False Positive Rate (FPR) and True Positive Rate (TPR) for each bin.

        Args:
            data (pd.DataFrame): DataFrame containing 'y_pred', 'y_true', and 'bin' columns.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Arrays of TPR and FPR for each bin.

        Raises:
            ValueError: If there is an issue with confusion matrix calculations.
        """
        sensitivity_score = np.zeros(self.n_bins)
        specificity_score = np.zeros(self.n_bins)
        unique_bins = data["bin"].value_counts()
        sorted_bins = unique_bins.sort_index().index

        for num, bin_ in enumerate(sorted_bins):
            mask = data["bin"] == bin_
            threshold = data.loc[mask, "y_pred"].min()
            y_pred_labels = np.where(data["y_pred"] >= threshold, 1, 0)
            tn, fp, fn, tp = confusion_matrix(data.y_true, y_pred_labels).ravel()
            sensitivity_score[num] = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity_score[num] = fp / (fp + tn) if (fp + tn) > 0 else 0

        return sensitivity_score, specificity_score

    def _transform(self, y_true, y_pred):
        """
        Transforms the true and predicted values to calculate metrics.

        Args:
            y_true: Ground truth target values.
            y_pred: Predicted probabilities.

        Returns:
            pd.DataFrame or list: DataFrame with detailed metrics per bin or list of DataFrames for multilabel tasks.
        """
        scores = (
            report(y_true, y_pred, n_bins=self.n_bins)
            if self.task != "multiclass"
            else pd.DataFrame()
        )
        scores = self.calculate_conf_interval(
            y_true, y_pred, scores, self.metric_name, self.metric_params, task=self.task
        )
        scores = (
            self.calculate_total_stats(scores) if self.task != "multiclass" else scores
        )
        return scores.fillna(".")

    def transform(self, y_true, y_pred):
        """
        Calculates detailed metrics for each bin.

        Args:
            y_true (array-like): True target values.
            y_pred (array-like): Predicted probabilities.

        Returns:
            pd.DataFrame or list: DataFrame with detailed metrics per bin or list of tuples for multilabel tasks.

        Raises:
            ValueError: If the task type is not supported.
        """
        if self.task in ["binary", "multiclass"]:
            return self._transform(y_true, y_pred)

        elif self.task == "multilabel":
            classes = y_true.columns.tolist()
            prediction_columns = [f"{i}_pred" for i in classes]
            y_pred = pd.DataFrame(y_pred, columns=prediction_columns)
            y_true.reset_index(drop=True, inplace=True)
            y_pred.reset_index(drop=True, inplace=True)
            dataset = pd.concat([y_true, y_pred], axis=1, ignore_index=False)
            scores = []
            for idx in range(len(classes)):
                _y_true = dataset[classes[idx]].values
                _y_pred = dataset[prediction_columns[idx]].values
                scores.append((classes[idx], self._transform(_y_true, _y_pred)))
            return scores

        else:
            raise ValueError(
                'Supports only "multilabel", "multiclass" and "binary" tasks.'
            )