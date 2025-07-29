from typing import Optional, Dict, List, Tuple, Any, Union
import numpy as np
import pandas as pd
from pandas import DataFrame
from tqdm.auto import tqdm

from dreamml.configs.config_storage import ConfigStorage
from dreamml.modeling.metrics import metrics_mapping
from dreamml.modeling.models.base import BoostingBaseModel
from dreamml.modeling.models.estimators import BaseModel
from dreamml.reports.metrics_calculation import BaseMetricsCalculator
from dreamml.reports.reports._base import BaseReport
from dreamml.reports.reports._base import create_used_features_stats

from dreamml.utils.saver import ArtifactSaver
from dreamml.logging import get_logger
from dreamml.utils.splitter import concatenate_all_samples
from dreamml.visualization.plots import (
    _plot_hist_anomaly_detection,
    _plot_training_progress,
)

_logger = get_logger(__name__)

CV_SCORE_COL = "cv score"
MODEL_NAME_COL = "Model Name"

drop_params = [
    "metric_hdbscan",
    "min_cluster_size",
    "max_cluster_size",
    "min_samples",
    "cluster_selection_method",
    "prediction_data",
    "pipeline.task_specific.topic_modeling.umap_epochs",
    "pipeline.task_specific.topic_modeling.metric_umap",
    "min_dist",
    "n_components",
    "n_neighbors",
    "iterations",
    "num_models",
    "eta",
    "alpha",
    "pipeline.task_specific.topic_modeling.lda_passes",
    "pipeline.task_specific.topic_modeling.num_topics",
    "parallelism",
    "pipeline.vectorization.vectorization_algos",
    "data.columns.text_features_preprocessed",
    "text_preprocessing_params",
    "text_features",
    "data.columns.never_used_features",
    "categorical_features",
    "feature_threshold",
    "validation",
    "data.splitting.split_by_time_period",
    "shuffle",
    "data.splitting.stratify",
    "data.splitting.split_params",
    "data.splitting.oot_split_test",
    "data.splitting.oot_split_valid",
    "data.splitting.split_oot_from_dev",
    "data.splitting.oot_split_n_values",
    "data.splitting.time_series_split",
    "data.splitting.time_series_window_split",
    "data.splitting.time_series_split_test_size",
    "data.splitting.time_series_split_gap",
    "data.splitting.cv_n_folds",
    "sample_strategy",
    "stages.boostaroota.boostaroota_type",
    "data.use_sampling",
    "stages.gini_selection.gini_threshold",
    "stages.gini_selection.gini_selector_abs_difference",
    "stages.gini_selection.gini_selector_rel_difference",
    "stages.gini_selection.gini_selector_valid_sample",
    "stages.permuation.permutation_threshold",
    "stages.permuation.permutation_top_n",
    "stages.psi_selection.psi_threshold",
    "stages.psi_selection.psi_sample",
    "stages.boostaroota.min_n_features_to_stop",
    "stages.boostaroota.min_n_features_to_start",
    "stages.boostaroota.max_boostaroota_stage_iters",
    "stages.batch_selection.bootstrap_samples",
    "stages.batch_selection.stop_criteria",
    "stages.batch_selection.sample_for_validation",
    "data.columns.weights_columnn",
    "weights",
    "pipeline.preprocessing.min_percentile",
    "pipeline.preprocessing.max_percentile",
    "pipeline.task_specific.multilabel.show_save_paths",
    "pipeline.task_specific.multilabel.samples_to_plot",
    "pipeline.task_specific.multilabel.plot_multi_graphs",
    "pipeline.task_specific.multilabel.max_classes_plot",
    "pipeline.task_specific.time_series.path_to_exog_data",
    "pipeline.task_specific.time_series.known_future",
    "pipeline.task_specific.time_series.time_column_frequency",
    "pipeline.alt_mode.use_whitebox_automl",
    "pipeline.use_oot_potential",
    "pipeline.alt_mode.use_lama",
    "pipeline.alt_mode.use_etna",
    "stages.corr_selection.corr_threshold",
    "stages.corr_selection.corr_coef",
    "pipeline.verbose",
    "pipeline.alt_mode.lama_time",
    "save_to_ps",
    "multitarget",
    "ignore_third_party_warnings",
    "metric_col_name",
    "group_column",
    "time_column",
    "data.columns.time_column_format",
    "time_column_period",
    "split_by_group",
    "data.splitting.custom_cv",
    "models.bert.params.unfreeze_layers",
    "data.augmentation.text_augmentations",
    "data.augmentation.aug_p",
    "log_target",
    "pipeline.task_specific.multilabel.target_with_nan_values",
    "pipeline.task_specific.time_series.ts_transforms",
    "horizon",
]

class CalculateDataStatistics:
    """
    Calculates statistical metrics for datasets, including sample statistics and variable statistics.

    This class provides methods to compute:
        - Statistics for each dataset (e.g., train, valid) such as the number of observations.
        - Statistics for variables including the target variable name, the count of categorical features, and the count of continuous features.
        - Detailed statistics for each variable, including the number of filled values, minimum, mean, maximum, and percentiles.

    Attributes:
        transformer (CategoricalFeaturesTransformer): Transformer for categorical features.
        categorical (List[str]): List of categorical feature names.
        config (ConfigStorage): Configuration storage for the experiment.
    """

    def __init__(self, encoder, config: ConfigStorage) -> None:
        """
        Initializes the CalculateDataStatistics instance.

        Args:
            encoder: Transformer for encoding categorical features.
            config (ConfigStorage): Configuration storage for the experiment.
        """
        self.transformer = encoder
        self.categorical = self.transformer.cat_features
        self.config = config

    def _calculate_samples_stats(self, **eval_sets) -> pd.DataFrame:
        """
        Calculates statistics for each dataset provided.

        Specifically, it calculates the number of observations in each dataset.

        Args:
            **eval_sets: Arbitrary keyword arguments where each key is the name of the dataset (e.g., train, valid) and the value is a tuple containing the feature matrix (DataFrame) and the target vector.

        Returns:
            pd.DataFrame: A DataFrame containing the number of observations for each dataset.
        """
        result = {}
        for data_name in eval_sets:
            data, _ = eval_sets[data_name]
            result[data_name] = [len(data)]
        result = pd.DataFrame(result).T.reset_index()
        result.columns = ["Sample", "# Observations"]
        return result.fillna(0)

    def _calculate_variables_stats(self, **eval_sets) -> pd.DataFrame:
        """
        Calculates detailed statistics for each variable in the dataset.

        The statistics include the number of filled values, average value, standard deviation, minimum value, 25th percentile, median, 75th percentile, and maximum value.

        Args:
            **eval_sets: Arbitrary keyword arguments where each key is the name of the dataset (e.g., train, valid) and the value is a tuple containing the feature matrix (DataFrame) and the target vector.

        Returns:
            pd.DataFrame: A DataFrame containing detailed statistics for each variable.
        """
        sample_name = next(iter(eval_sets))
        data, _ = eval_sets[sample_name]

        result = data.describe().T.reset_index()
        result.columns = [
            "Variable Name",
            "Number of Filled Values",
            "Average Value",
            "STD Value",
            "Minimum Value",
            "25% Percentile Value",
            "50% Percentile Value",
            "75% Percentile Value",
            "Maximum Value",
        ]
        if self.categorical:
            mask = result["Variable Name"].isin(self.categorical)
            features = [
                "Average Value",
                "STD Value",
                "Minimum Value",
                "25% Percentile Value",
                "50% Percentile Value",
                "75% Percentile Value",
                "Maximum Value",
            ]
            result.loc[mask, features] = "."

        return result.fillna(0)

    def _calculate_variables_types_stats(self) -> pd.DataFrame:
        """
        Calculates statistics based on the types of variables.

        Specifically, it calculates the number of categorical and continuous variables and identifies the target variable.

        Returns:
            pd.DataFrame: A DataFrame containing statistics based on variable types.
        """
        stats = pd.DataFrame(
            {
                "Target Variable": ["-"],
                "Loss Function": self.config.pipeline.loss_function,
                "Eval Metric": self.config.pipeline.eval_metric,
                "# Categorical Features": [len(self.transformer.cat_features)],
            }
        )

        return stats.fillna(0)

    def transform(self, **eval_sets):
        """
        Generates a comprehensive data statistics report.

        The report includes:
            - Statistics for each dataset, including the number of observations.
            - Overall statistics based on variable types.
            - Detailed statistics for each variable.

        Args:
            **eval_sets: Arbitrary keyword arguments where each key is the name of the dataset (e.g., train, valid) and the value is a tuple containing the feature matrix (DataFrame) and the target vector.

        Returns:
            tuple: A tuple containing three DataFrames:
                - Sample statistics
                - Variable types statistics
                - Detailed variable statistics
        """
        result = (
            self._calculate_samples_stats(**eval_sets),
            self._calculate_variables_types_stats(),
            self._calculate_variables_stats(**eval_sets),
        )
        return result


class CalculateAnomalyDetectionMetrics(BaseMetricsCalculator):
    """
    Calculates metrics for anomaly detection tasks including MAE, RMSE, and R2.

    This class extends the BaseMetricsCalculator to compute specific metrics relevant to anomaly detection.

    Args:
        models (Dict[str, BaseModel]): A dictionary where the key is the model name and the value is the ML model instance.
        log_transformer (Optional): Optional transformer for log transformations.
        predictions (Optional[Dict]): Optional dictionary of predictions.
        vectorizers (Optional[Dict]): Optional dictionary of vectorizers.

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
        """
        Initializes the CalculateAnomalyDetectionMetrics instance.

        Args:
            models (Dict[str, BaseModel]): A dictionary where the key is the model name and the value is the ML model instance.
            log_transformer (Optional): Optional transformer for log transformations.
            predictions (Optional[Dict]): Optional dictionary of predictions.
            vectorizers (Optional[Dict]): Optional dictionary of vectorizers.
        """
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

    def _get_metrics_to_calculate(self) -> Dict[str, Any]:
        """
        Retrieves the metrics to be calculated based on the models provided.

        It ensures that at least one `BoostingBaseModel` is present and includes metrics such as MAE, RMSE, MAPE, and R2.

        Returns:
            Dict[str, Any]: A dictionary of metrics to be calculated.

        Raises:
            RuntimeError: If no instances of `BoostingBaseModel` are found in the provided models.
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

        return metrics

    def create_prediction(self, model: BaseModel, data: pd.DataFrame) -> np.array:
        """
        Creates predictions using the specified model and data.

        Args:
            model (BaseModel): The model to use for making predictions.
            data (pd.DataFrame): The input data for which predictions are to be made.

        Returns:
            np.array: An array of predictions.
        """
        pred = super().create_prediction(model, data)
        return pred


class AnomalyDetectionDevReport(BaseReport):
    """
    Generates a development report for anomaly detection models.

    This report includes data statistics, model performance metrics, used features, and visualizations related to anomaly detection.

    Args:
        models: Dictionary of primary models.
        other_models: Dictionary of additional models.
        oot_potential: Out-of-time potential data.
        experiment_path: Path to the experiment directory.
        config: Configuration storage.
        n_bins (int, optional): Number of bins for histograms. Defaults to 20.
        bootstrap_samples (int, optional): Number of bootstrap samples. Defaults to 200.
        p_value (float, optional): P-value for statistical tests. Defaults to 0.05.
        max_feat_per_model (int, optional): Maximum number of features per model. Defaults to 50.
        predictions (Optional[Dict], optional): Dictionary of predictions. Defaults to None.
        cv_scores (optional): Cross-validation scores. Defaults to None.
        artifact_saver (Optional[ArtifactSaver], optional): Artifact saver instance. Defaults to None.
        vectorizers_dict (Optional[dict], optional): Dictionary of vectorizers. Defaults to None.
        etna_pipeline (Optional[dict], optional): ETNA pipeline configuration. Defaults to None.
        etna_eval_set (Optional[dict], optional): ETNA evaluation set. Defaults to None.
        analysis (Optional[dict], optional): Additional analysis parameters. Defaults to None.
    """

    def __init__(
        self,
        models,
        other_models,
        oot_potential,
        experiment_path,
        config,
        n_bins: int = 20,
        bootstrap_samples: int = 200,
        p_value: float = 0.05,
        max_feat_per_model: int = 50,
        predictions: Optional[Dict] = None,
        cv_scores=None,
        artifact_saver: Optional[ArtifactSaver] = None,
        vectorizers_dict: Optional[dict] = None,
        etna_pipeline: Optional[dict] = None,
        etna_eval_set: Optional[dict] = None,
        analysis: Optional[dict] = None,
    ):
        super().__init__(
            experiment_path=experiment_path,
            artifact_saver=artifact_saver,
            config=config,
            models=models,
            other_models=other_models,
            oot_potential=oot_potential,
            vectorizers_dict=vectorizers_dict,
        )
        if "psi_importance" in self.models:
            self.psi = self.models.pop("psi_importance")
        else:
            self.psi = None

        self.quantiles = [0.9, 0.95, 0.97, 0.99, "std_thr"]
        self.bootstrap_samples = bootstrap_samples
        self.p_value = p_value
        self.max_feat_per_model = (
            max_feat_per_model if vectorizers_dict is None else 10_000
        )
        self.predictions = predictions or {}
        self.models_metrics_df = None
        self.mad_threshold = 3  # > 3 sigma

    def create_first_page(self, **eval_sets):
        """
        Creates the first page of the report containing data statistics.

        The page includes:
            - Statistics for each dataset used for training, validation, and testing, including the number of observations.
            - Overall statistics based on variable types such as the target variable name, the number of categorical features, and the number of continuous features.
            - Detailed statistics for each variable, including the number of filled values, average value, standard deviation, and percentiles.

        Args:
            **eval_sets: Arbitrary keyword arguments where each key is the name of the dataset (e.g., train, valid) and the value is a tuple containing the feature matrix (DataFrame) and the target vector.
        """
        transformer = CalculateDataStatistics(self.encoder, self.config)
        result = transformer.transform(**eval_sets)

        startrows = [
            0,
            2 + result[0].shape[0],
            4 + result[0].shape[0] + result[1].shape[0],
        ]
        num_formats = [10, None, None]

        for data, startrow, num_format in zip(result, startrows, num_formats):
            data.to_excel(
                self.writer,
                startrow=startrow,
                sheet_name="Data_Statistics",
                index=False,
            )
            self.set_style(data, "Data_Statistics", startrow, num_format=None)

        self.add_numeric_format(result[0], "Data_Statistics", startrow=startrows[0])
        self.add_numeric_format(result[2], "Data_Statistics", startrow=startrows[-1])

    def create_third_page(self, **eval_sets):
        """
        Creates the third (or fourth) page of the report containing regression metrics for each model.

        The page includes metrics such as MAE, RMSE, and R2 for each model across different datasets.

        Args:
            **eval_sets: Arbitrary keyword arguments where each key is the name of the dataset (e.g., train, valid) and the value is a tuple containing the feature matrix (DataFrame) and the target vector.
        """
        models = {
            model_name: model
            for model_name, model in self.models.items()
            if model.model_name not in ["iforest"]
        }
        transformer = CalculateAnomalyDetectionMetrics(
            models=models,
            log_transformer=None,
            vectorizers=None,
        )
        result = transformer.transform(**eval_sets)
        self.predictions = transformer.predictions_

        startcol, endcol = 2 + len(eval_sets), 2 + 3 * len(eval_sets) - 1
        result = result.round(3)  # Rounding for numerical format compatibility
        result.to_excel(self.writer, sheet_name="Compare Models", index=False)
        self.set_style(result, "Compare Models", 0)

        cols = [col for col in result.columns if "MAE" in col]
        cols = cols + [MODEL_NAME_COL, "Model Details"]
        df_a = result.drop("Model Details", axis=1)
        df_b = result.drop(cols, axis=1)
        ws = self.sheets["Compare Models"]

    def create_fourth_page(self, **eval_sets):
        """
        Creates the fourth (or fifth) page of the report listing the features used by the models.

        The page includes statistics about the features used across different models.

        Args:
            **eval_sets: Arbitrary keyword arguments where each key is the name of the dataset and the value is a tuple containing the feature matrix and the target vector.
        """
        df = create_used_features_stats(self.models, **eval_sets)
        df.to_excel(self.writer, sheet_name="Used Features", index=False)
        self.set_style(df, "Used Features", 0)

    def create_model_report(self, **eval_sets):
        """
        Generates report pages for each model and dataset pair.

        For each model, it creates detailed metrics, loss distributions, and training progress visualizations.

        Args:
            **eval_sets: Arbitrary keyword arguments where each key is the name of the dataset and the value is a tuple containing the feature matrix and the target vector.
        """
        all_data = concatenate_all_samples(eval_sets)

        for model_name, model in tqdm(self.models.items()):
            transformer = CalculateDetailedMetrics(model, self.quantiles)

            sheet_name = f"{model_name}"

            X_true = all_data.copy()
            data, losses = transformer.transform(X_true)
            data.to_excel(self.writer, sheet_name=sheet_name, index=False)

            self.set_style(data, sheet_name, 0)
            self.add_numeric_format(data, sheet_name, min_value=100)
            self.create_compare_models_url(data, sheet_name)
            self.create_model_url(**eval_sets)

            ws = self.sheets[sheet_name]

            if model.model_name in ["ae", "vae"]:
                # Histogram of loss distribution by quantiles
                cnt = 7
                for q in self.quantiles:
                    if q == "mad_thr":
                        m = np.median(losses)
                        threshold = m + self.mad_threshold / 0.6745
                    elif q == "std_thr":
                        threshold = np.mean(losses) + (np.std(losses))
                    else:
                        threshold = np.quantile(losses, q, axis=0)

                    plt_1_save_path = f"{self.experiment_path}/images/{sheet_name}_{model_name}_{q}.png"
                    plt_1_title_name = (
                        f"Distribution of the Reconstruction Loss | Threshold: {q}"
                    )
                    figsize = (10, 5)
                    _plot_hist_anomaly_detection(
                        losses, threshold, plt_1_save_path, plt_1_title_name, figsize
                    )
                    ws.insert_image(f"A{len(data) + cnt}", plt_1_save_path)
                    cnt += figsize[0] + 15

                # Training progress plot
                plt_2_save_path = (
                    f"{self.experiment_path}/images/{sheet_name}_{model_name}.png"
                )
                title_name = (
                    f"Training and Validation Loss per Epoch | Model: {model_name}"
                )
                _plot_training_progress(
                    model.callback_info, plt_2_save_path, title_name, (10, 6)
                )
                ws.insert_image(f"N{len(data) + 7}", plt_2_save_path)

    def create_model_url(self, **eval_sets):
        """
        Placeholder method for creating model URLs.

        Args:
            **eval_sets: Arbitrary keyword arguments where each key is the name of the dataset and the value is a tuple containing the feature matrix and the target vector.
        """
        pass

    def transform(self, **eval_sets):
        """
        Executes the transformation to generate the full development report.

        This includes creating data statistics pages, model comparison metrics, used features, and detailed model reports.

        Args:
            **eval_sets: Arbitrary keyword arguments where each key is the name of the dataset and the value is a tuple containing the feature matrix and the target vector.
        """
        self.create_dml_info_page()
        self.create_zero_page(drop_params=drop_params)
        self.create_first_page(**eval_sets)
        self.create_third_page(**eval_sets)
        self.create_fourth_page(**eval_sets)
        self.create_model_report(**eval_sets)
        self.create_model_url(**eval_sets)
        self.writer.save()


class CalculateDetailedMetrics:
    """
    Calculates detailed metrics for anomaly detection tasks.

    For each model, it generates training plots and determines anomalies based on specified quantiles.

    Args:
        model (BaseModel): The anomaly detection model.
        quantiles (List[Union[float, str]]): List of quantiles or threshold types to determine anomalies.
    """

    def __init__(self, model, quantiles: List[Union[float, str]]):
        """
        Initializes the CalculateDetailedMetrics instance.

        Args:
            model (BaseModel): The anomaly detection model.
            quantiles (List[Union[float, str]]): List of quantiles or threshold types to determine anomalies.
        """
        self.model = model
        self.objective_name = model.objective.name
        self.quantiles = quantiles
        self.mad_threshold = 3  # > 3 sigma

    def calculate_loss(self, X_true: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the loss for the provided data using the model.

        Args:
            X_true (pd.DataFrame): The input data for which loss is to be calculated.

        Returns:
            pd.DataFrame: A DataFrame containing the loss values.
        """
        scores = pd.DataFrame()
        losses = self.model.transform(X_true[self.model.used_features])
        scores["loss"] = losses
        return scores

    def calculate_anomaly_by_quantiles(
        self, scores: pd.DataFrame
    ) -> Tuple[pd.DataFrame, Any]:
        """
        Determines anomalies based on specified quantiles.

        For each quantile, it calculates the threshold and identifies anomalies.

        Args:
            scores (pd.DataFrame): DataFrame containing loss scores.

        Returns:
            Tuple[pd.DataFrame, Any]: A tuple containing a DataFrame with anomaly counts and the raw loss values.
        """
        losses = scores["loss"].to_numpy()

        if self.model.model_name in ["iforest"]:
            result = pd.DataFrame(
                columns=[
                    f"threshold_0",
                    "non_anomalies",
                    "predicted_anomalies",
                ]
            )
            threshold = 0
            y_pred = np.array([0 if loss > threshold else 1 for loss in losses])
            non_anomalies = y_pred[y_pred == 0].shape[0]
            anomalies = y_pred[y_pred == 1].shape[0]
            result.loc[len(result)] = [threshold, non_anomalies, anomalies]

        else:
            result = pd.DataFrame(
                columns=[
                    "quantile",
                    f"threshold_{self.objective_name.upper()}",
                    "non_anomalies",
                    "predicted_anomalies",
                ]
            )
            for q in self.quantiles:
                if q == "mad_thr":
                    m = np.median(losses)
                    ad = np.abs(losses - m)
                    mad = np.median(ad)
                    z_scores = 0.6745 * ad / mad
                    y_pred = np.array(
                        [1 if loss > self.mad_threshold else 0 for loss in z_scores]
                    )
                    threshold = m + self.mad_threshold / 0.6745
                elif q == "std_thr":
                    threshold = np.mean(losses) + (np.std(losses))
                    y_pred = np.array([1 if loss > threshold else 0 for loss in losses])
                else:
                    threshold = np.quantile(losses, q, axis=0)
                    y_pred = np.array([1 if loss > threshold else 0 for loss in losses])

                non_anomalies = y_pred[y_pred == 0].shape[0]
                anomalies = y_pred[y_pred == 1].shape[0]
                result.loc[len(result)] = [q, threshold, non_anomalies, anomalies]

        result.loc[len(result)] = ["-"] * result.shape[1]
        return result, losses

    def transform(self, X_true: pd.DataFrame) -> Tuple[pd.DataFrame, Any]:
        """
        Performs the transformation to calculate detailed metrics.

        This includes calculating loss and determining anomalies based on quantiles.

        Args:
            X_true (pd.DataFrame): The input data for which metrics are to be calculated.

        Returns:
            Tuple[pd.DataFrame, Any]: A tuple containing a DataFrame with anomaly counts and the raw loss values.
        """
        scores = self.calculate_loss(X_true)
        result, losses = self.calculate_anomaly_by_quantiles(scores)
        return result, losses