from typing import Dict, Optional

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import mean_absolute_error, r2_score

from dreamml.configs.config_storage import ConfigStorage
from dreamml.logging import get_logger
from dreamml.modeling.metrics.metrics_mapping import metrics_mapping
from dreamml.modeling.metrics.utils import calculate_quantile_bins
from dreamml.modeling.models.estimators import BoostingBaseModel, BaseModel
from dreamml.reports.metrics_calculation import BaseMetricsCalculator


_logger = get_logger(__name__)


class CalculateDataStatistics:
    """
    Calculates statistics for datasets, including sample-specific and variable-specific metrics.

    This class provides functionalities to compute:
        - Statistics for each dataset (e.g., train, valid):
            - Number of observations
            - Number of target events
            - Proportion of target events
        - Variable statistics:
            - Target variable name
            - Number of categorical features
            - Number of continuous features
        - Detailed variable statistics:
            - Variable name
            - Number of filled values
            - Minimum, mean, and maximum values
            - 25th, 50th, and 75th percentiles

    Args:
        encoder: Transformer for encoding categorical features.
        log_transformer: Transformer for transforming the target variable.
        corr_importance: DataFrame containing univariate analysis of variables.
        config: Configuration dictionary for the experiment.

    Attributes:
        transformer (CategoricalFeaturesTransformer): Transformer for categorical features.
        gini (pd.DataFrame): DataFrame containing variable analysis based on the Gini metric.
        log_transformer: Transformer for the target variable.
        categorical (list): List of categorical feature names.
        config (ConfigStorage): Configuration storage object.
    """

    def __init__(
        self, encoder, log_transformer, corr_importance, config: ConfigStorage
    ) -> None:
        self.gini = corr_importance
        self.transformer = encoder
        self.log_transformer = log_transformer
        self.categorical = self.transformer.cat_features
        self.config = config

    def _preprocessing_data(self, **eval_sets) -> list:
        """
        Indicates the removal of outliers based on the target variable.

        Args:
            **eval_sets: Arbitrary keyword arguments representing different datasets.

        Returns:
            List[str]: Messages indicating outlier removal for each dataset or "-" if not applicable.
        """
        msg = "Outliers removed based on target variable ({} and {} percentiles).".format(
            self.config.pipeline.preprocessing.min_percentile,
            self.config.pipeline.preprocessing.max_percentile,
        )
        values = [
            msg if sample in ["train", "valid", "test2"] else "-"
            for sample in eval_sets
        ]
        return values

    def _calculate_samples_stats(
        self, log_scale: bool, prefix: str = "", **eval_sets
    ) -> pd.DataFrame:
        """
        Calculates statistics for each dataset and the target vector.

        Computes the number of observations, mean, standard deviation, minimum,
        25th percentile, median, 75th percentile, and maximum of the target variable.

        Args:
            log_scale (bool): Indicates whether the target is in logarithmic scale.
            prefix (str, optional): Prefix for the statistics labels. Defaults to "".
            **eval_sets: Arbitrary keyword arguments representing different datasets.

        Returns:
            pd.DataFrame: DataFrame containing the calculated statistics.
        """
        result = {}
        for data_name in eval_sets:
            data, target = eval_sets[data_name]

            if log_scale:
                target = self.log_transformer.inverse_transform(target)

            result[data_name] = [
                len(data),
                np.mean(target),
                np.std(target),
                np.min(target),
                np.percentile(target, 25),
                np.percentile(target, 50),
                np.percentile(target, 75),
                np.max(target),
                "-",
            ]
        result = pd.DataFrame(result).T.reset_index()
        result.columns = [
            "Dataset",
            "# Observations",
            f"{prefix}Target AVG Value",
            f"{prefix}Target STD Value",
            f"{prefix}Target MIN Value",
            f"{prefix}Target 25% Percentile",
            f"{prefix}Target 50% Percentile",
            f"{prefix}Target 75% Percentile",
            f"{prefix}Target MAX Value",
            "Preprocessing",
        ]
        result["Preprocessing"] = self._preprocessing_data(**eval_sets)
        return result.fillna(0)

    def _calculate_variables_stats(self, **eval_sets) -> pd.DataFrame:
        """
        Calculates statistics for each variable.

        Computes the number of filled values, mean, standard deviation,
        minimum, 25th percentile, median, 75th percentile, and maximum
        for each feature.

        Args:
            **eval_sets: Arbitrary keyword arguments representing different datasets.

        Returns:
            pd.DataFrame: DataFrame containing the calculated variable statistics.
        """
        sample_name = next(iter(eval_sets))
        data, _ = eval_sets[sample_name]

        result = data.describe().T.reset_index()
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
        if self.categorical:
            mask = result["Variable Name"].isin(self.categorical)
            features = [
                "AVG Value",
                "STD Value",
                "MIN Value",
                "25% Percentile Value",
                "50% Percentile Value",
                "75% Percentile Value",
                "MAX Value",
            ]
            result.loc[mask, features] = "."

        return result.fillna(0)

    def _calculate_variables_types_stats(self) -> pd.DataFrame:
        """
        Calculates statistics based on variable types.

        Computes the number of categorical and continuous variables,
        and includes the name of the target variable.

        Returns:
            pd.DataFrame: DataFrame containing the variable type statistics.
        """
        target_name = self.config.data.columns.target_name
        log_target = self.config.pipeline.preprocessing.log_target
        target_name = f"log({target_name})" if log_target else target_name

        stats = pd.DataFrame(
            {
                "Target Variable": [target_name],
                "Loss Function": self.config.pipeline.loss_function,
                "Eval Metric": self.config.pipeline.eval_metric,
                "# Categorical Features": [len(self.transformer.cat_features)],
            }
        )
        if self.gini is not None:
            stats["# Continuous Features"] = [self.gini.shape[0]]

        return stats.fillna(0)

    def transform(self, **eval_sets) -> tuple:
        """
        Builds a report containing data statistics.

        Depending on whether the target has been log-transformed,
        calculates statistics for both transformed and original scales.

        Args:
            **eval_sets: Arbitrary keyword arguments representing different datasets.

        Returns:
            tuple: A tuple containing DataFrames with sample statistics,
                   variable types statistics, and variable statistics.
        """
        if self.log_transformer.fitted:
            res = (
                self._calculate_samples_stats(log_scale=True, prefix="", **eval_sets),
                self._calculate_samples_stats(
                    log_scale=False, prefix="log-", **eval_sets
                ),
            )
            result = (
                *res,
                self._calculate_variables_types_stats(),
                self._calculate_variables_stats(**eval_sets),
            )
        else:
            result = (
                self._calculate_samples_stats(log_scale=False, **eval_sets),
                self._calculate_variables_types_stats(),
                self._calculate_variables_stats(**eval_sets),
            )
        return result


class CalculateRegressionMetrics(BaseMetricsCalculator):
    """
    Calculates regression metrics including MAE, RMSE, and R².

    This class computes various regression metrics for given models and predictions.

    Args:
        models (Dict[str, BaseModel]): Dictionary where keys are model names and values are model instances.
        log_transformer (Optional): Transformer for the target variable. Defaults to None.
        predictions (Optional[Dict]): Dictionary of predictions. Defaults to None.
        vectorizers (Optional[Dict]): Dictionary of vectorizers. Defaults to None.

    Raises:
        RuntimeError: If no instances of `BoostingBaseModel` are found in the provided models.
    """

    def __init__(
        self,
        models: Dict[str, BaseModel],
        log_transformer: Optional = None,
        predictions: Optional[Dict] = None,
        vectorizers: Optional[Dict] = None,
    ) -> None:
        self.log_transformer = log_transformer

        def transform_target(target):
            if self.log_transformer is not None and self.log_transformer.fitted:
                target = self.log_transformer.inverse_transform(target)
            return target

        super().__init__(
            models,
            predictions,
            vectorizers,
            calculate_metrics_ratio=False,
            transform_target=transform_target,
        )

    def _get_metrics_to_calculate(self) -> Dict[str, callable]:
        """
        Retrieves the metrics to be calculated based on the first boosting model.

        Returns:
            Dict[str, callable]: Dictionary mapping metric names to their corresponding functions.

        Raises:
            RuntimeError: If no instances of `BoostingBaseModel` are found.
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

        # Additional metrics
        for name in ["mae", "rmse", "mape", "r2"]:
            if name not in metrics:
                metrics[name] = metrics_mapping[name]()

        if first_model.task != "multiregression":
            metrics["pearsonr"] = lambda x, y: pearsonr(x, y)[0]
            metrics["spearmanr"] = lambda x, y: spearmanr(x, y)[0]

        return metrics

    def create_prediction(self, model: BaseModel, data: pd.DataFrame) -> np.array:
        """
        Generates predictions from a model and applies inverse transformation if needed.

        Args:
            model (BaseModel): The model to generate predictions from.
            data (pd.DataFrame): The input data for prediction.

        Returns:
            np.array: The predicted values, possibly inverse transformed.
        """
        pred = super().create_prediction(model, data)

        if self.log_transformer is not None and self.log_transformer.fitted:
            pred = self.log_transformer.inverse_transform(pred)

        return pred


class CalculateDetailedMetrics:
    """
    Calculates detailed regression metrics across quantile bins of predictions.

    This class computes various metrics for each bin, including:
        - Minimum, mean, and maximum predicted values
        - Minimum, mean, and maximum true target values
        - Number of observations
        - R², MAE, and RMSE within each bin

    Args:
        log_transformer: Transformer for the target variable.
        n_bins (int, optional): Number of quantile bins. Defaults to 20.
    """

    def __init__(self, log_transformer, n_bins: int = 20):
        self.log_transformer = log_transformer
        self.n_bins = n_bins

    @staticmethod
    def calculate_total_metrics(
        data: pd.DataFrame, scores: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculates overall metrics for the entire dataset.

        Computes MAE, MAPE, RMSE, R², Pearson correlation, and Spearman correlation
        across all predictions and targets.

        Args:
            data (pd.DataFrame): DataFrame containing predictions and true values.
                                 Must include 'y_pred' and 'y_true' columns.
            scores (pd.DataFrame): DataFrame containing metrics per bin.

        Returns:
            pd.DataFrame: Updated scores DataFrame with overall metrics added.
        """
        num_row = scores.shape[0]

        scores.loc[num_row, "MAE"] = mean_absolute_error(data["y_true"], data["y_pred"])
        scores.loc[num_row, "MAPE"] = metrics_mapping["mape"]()(
            data["y_true"], data["y_pred"]
        )
        scores.loc[num_row, "RMSE"] = metrics_mapping["rmse"]()(
            data["y_true"], data["y_pred"]
        )
        scores.loc[num_row, "R2"] = 100 * r2_score(data["y_true"], data["y_pred"])
        scores.loc[num_row, "pearson-correlation"] = (
            100 * pearsonr(data["y_true"], data["y_pred"])[0]
        )
        scores.loc[num_row, "spearman-correlation"] = (
            100 * spearmanr(data["y_true"], data["y_pred"])[0]
        )
        scores.loc[num_row, "real 25p"] = np.percentile(data["y_true"], 25)
        scores.loc[num_row, "real 50p"] = np.percentile(data["y_true"], 50)
        scores.loc[num_row, "real 75p"] = np.percentile(data["y_true"], 75)

        return np.round(scores, 4)

    @staticmethod
    def bin_generator(data: pd.DataFrame) -> pd.Series:
        """
        Generates masks for each unique bin in the data.

        Args:
            data (pd.DataFrame): DataFrame containing a 'bin' column.

        Yields:
            pd.Series: Boolean mask for the current bin.
        """
        unique_bins = data["bin"].value_counts(ascending=True)
        sorted_bins = unique_bins.sort_index().index

        for bin_ in sorted_bins:
            mask = data["bin"] == bin_
            yield mask

    @staticmethod
    def calculate_total_stats(scores: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregates base metrics across all bins to provide total statistics.

        Computes the total number of observations and weighted average predictions and targets.

        Args:
            scores (pd.DataFrame): DataFrame containing metrics per bin.

        Returns:
            pd.DataFrame: Updated scores DataFrame with total statistics added.
        """
        num_row = scores.shape[0] - 1
        scores = scores.reset_index(drop=True)

        scores.loc[num_row, "bin"] = "Total"
        scores.loc[num_row, "#obs"] = scores["#obs"].sum()
        scores.loc[num_row, "pred_mean"] = (scores["pred_mean"] * scores["#obs"]).sum()
        scores.loc[num_row, "pred_mean"] /= scores.loc[num_row, "#obs"]

        scores.loc[num_row, "real_mean"] = (scores["real_mean"] * scores["#obs"]).sum()
        scores.loc[num_row, "real_mean"] /= scores.loc[num_row, "#obs"]

        return scores

    def calculate_base_bins_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates basic metrics for each prediction bin.

        Metrics include minimum, mean, and maximum predictions and true values,
        as well as the number of observations and percentiles of true values.

        Args:
            data (pd.DataFrame): DataFrame containing predictions, true values, and bins.

        Returns:
            pd.DataFrame: DataFrame containing base metrics for each bin.
        """
        data_gp = data.groupby(["bin"])
        scores = data_gp.agg(
            {
                "y_pred": ["min", "mean", "max"],
                "y_true": ["min", "mean", "max", "count"],
            }
        )
        scores["real 25p"] = data_gp["y_true"].apply(lambda x: np.percentile(a=x, q=25))
        scores["real 50p"] = data_gp["y_true"].apply(lambda x: np.percentile(a=x, q=50))
        scores["real 75p"] = data_gp["y_true"].apply(lambda x: np.percentile(a=x, q=75))

        scores.columns = [
            "pred_min",
            "pred_mean",
            "pred_max",
            "real_min",
            "real_mean",
            "real_max",
            "#obs",
            "real 25p",
            "real 50p",
            "real 75p",
        ]

        scores = scores.reset_index()
        scores["bin"] = np.arange(1, scores.shape[0] + 1)
        scores = scores.sort_values(by="bin", ascending=True)
        rounded = np.where(scores <= 100, np.round(scores, 2), np.round(scores, 0))
        scores = pd.DataFrame(rounded, columns=scores.columns)

        return scores

    def calculate_regression_metrics_in_bins(
        self, data: pd.DataFrame, scores: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculates regression metrics within each prediction bin.

        Metrics include MAE, MAPE, RMSE, R², Pearson correlation, and Spearman correlation.

        Args:
            data (pd.DataFrame): DataFrame containing predictions, true values, and bins.
            scores (pd.DataFrame): DataFrame containing base metrics per bin.

        Returns:
            pd.DataFrame: Updated scores DataFrame with regression metrics per bin.
        """
        gen = self.bin_generator(data)
        for num, mask in enumerate(gen):
            y_true = data.loc[mask, "y_true"]
            y_pred = data.loc[mask, "y_pred"]

            scores.loc[num, "MAE"] = mean_absolute_error(y_true, y_pred)
            scores.loc[num, "MAPE"] = metrics_mapping["mape"]()(y_true, y_pred)

            scores.loc[num, "RMSE"] = metrics_mapping["rmse"]()(y_true, y_pred)
            scores.loc[num, "R2"] = 100 * r2_score(y_true, y_pred)
            try:
                scores.loc[num, "pearson-correlation"] = (
                    100 * pearsonr(y_true, y_pred)[0]
                )
                scores.loc[num, "spearman-correlation"] = (
                    100 * spearmanr(y_true, y_pred)[0]
                )
            except ValueError:
                scores.loc[num, "pearson-correlation"] = 100
                scores.loc[num, "spearman-correlation"] = 100

        return scores

    def transform(self, y_true, y_pred) -> pd.DataFrame:
        """
        Calculates detailed metrics for each prediction bin.

        Args:
            y_true (array-like): True target values.
            y_pred (array-like): Predicted target values.

        Returns:
            pd.DataFrame: DataFrame containing detailed metrics per bin.
        """
        data = pd.DataFrame({"y_pred": y_pred, "y_true": y_true})
        data["bin"] = calculate_quantile_bins(
            data["y_pred"], self.n_bins, ascending=True
        )
        data["bin"] = data["bin"].fillna(-1)

        scores = self.calculate_base_bins_metrics(data)
        scores = self.calculate_regression_metrics_in_bins(data, scores)
        scores = self.calculate_total_metrics(data, scores)
        scores = self.calculate_total_stats(scores)
        return scores.fillna(".")