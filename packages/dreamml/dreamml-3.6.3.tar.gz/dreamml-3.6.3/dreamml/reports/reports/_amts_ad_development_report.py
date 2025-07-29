import numpy as np
import pandas as pd
from typing import Optional, Dict, List

from dreamml.reports.reports._base import BaseReport
from ..data_statistics.calculate_data_statistics_amts import CalculateDataStatisticsAMTS
from .._amts_ad_metrics import CalculateAMTSADMetrics

from dreamml.visualization.plots import (
    plot_STL,
    plot_hist_loss_amts_ad,
    plot_scatter_mark_amts_ad,
)

from dreamml.utils.saver import ArtifactSaver

# FIXME AMTS
drop_params = [
    "drop_features",
    "never_used_features",
    "categorical_features",
    "feature_threshold",
    "validation",
    "split_by_time_period",
    "shuffle",
    "stratify",
    "split_params",
    "oot_split_test",
    "oot_split_valid",
    "split_oot_from_dev",
    "oot_split_n_values",
    "time_series_split",
    "time_series_window_split",
    "time_series_split_test_size",
    "time_series_split_gap",
    "cv_n_folds",
    "sample_strategy",
    "boostaroota_type",
    "use_sampling",
    "gini_threshold",
    "gini_selector_abs_difference",
    "gini_selector_rel_difference",
    "gini_selector_valid_sample",
    "permutation_threshold",
    "permutation_top_n",
    "psi_threshold",
    "psi_sample",
    "min_n_features_to_stop",
    "min_n_features_to_start",
    "max_boostaroota_stage_iters",
    "bootstrap_samples",
    "stop_criteria",
    "sample_for_validation",
    "weights_column",
    "weights",
    "min_percentile",
    "max_percentile",
    "show_save_paths",
    "samples_to_plot",
    "plot_multi_graphs",
    "max_classes_plot",
    "path_to_exog_data",
    "known_future",
    "time_column_frequency",
    "use_whitebox_automl",
    "use_oot_potential",
    "use_lama",
    "use_etna",
    "corr_threshold",
    "corr_coef",
    "n_estimators",
    "verbose",
    "lama_time",
    "save_to_ps",
    "multitarget",
    "ignore_third_party_warnings",
    "metric_col_name",
    "n_neighbors",
    "n_components",
    "min_dist",
    "metric_umap",
    "umap_epochs",
    "min_cluster_size",
    "max_cluster_size",
    "min_samples",
    "metric_hdbscan",
    "cluster_selection_method",
    "_service_fields",
    "remaining_features",
    "embedding_normalization",
    "text_features",
    "text_features_preprocessed",
    "text_preprocessing_stages",
    "text_augmentations",
    "aug_p",
    "bert_model_path",
    "unfreeze_layers",
    "max_length",
    "sampler_type",
    "optimizer_type",
    "scheduler_type",
    "learning_rate",
    "epochs",
    "batch_size",
    "weight_decay",
    "latent_dim",
]


class AMTS_ad_DevelopmentReport(BaseReport):
    """Class for generating AMTS AD Development Reports.

    This class extends the BaseReport to create a comprehensive development report
    for AMTS (Automated Machine Learning Time Series) anomaly detection models. It
    handles the creation of various report pages, including configuration details,
    data statistics, model comparisons, and visualizations.

    Attributes:
        split_by_group (bool): Indicates if the data should be split by group.
        group_column (str): The name of the column used for grouping.
        target_name (str): The name of the target variable.
        analysis: The analysis results used in the report.
    """

    def __init__(
        self,
        models: List,
        other_models: List,
        oot_potential: Dict,
        experiment_path: str,
        config: Dict,
        analysis,
        artifact_saver: Optional[ArtifactSaver] = None,
        n_bins: Optional[dict] = None,
        bootstrap_samples: Optional[dict] = None,
        p_value: Optional[dict] = None,
        max_feat_per_model: Optional[dict] = None,
        predictions: Optional[dict] = None,
        cv_scores: Optional[dict] = None,
        etna_pipeline: Optional[dict] = None,
        etna_eval_set: Optional[dict] = None,
        vectorizers_dict: Optional[dict] = None,
    ):
        """Initializes the AMTS_ad_DevelopmentReport.

        Args:
            models (List): A list of primary models to include in the report.
            other_models (List): A list of additional models for comparison.
            oot_potential (Dict): Out-of-time potential metrics.
            experiment_path (str): The file system path to the experiment directory.
            config (Dict): Configuration parameters for the report and models.
            analysis: Analysis results to be included in the report.
            artifact_saver (Optional[ArtifactSaver], optional): Utility to save artifacts.
                Defaults to None.
            n_bins (Optional[dict], optional): Number of bins for histogram plots.
                Defaults to None.
            bootstrap_samples (Optional[dict], optional): Parameters for bootstrap sampling.
                Defaults to None.
            p_value (Optional[dict], optional): P-value thresholds for statistical tests.
                Defaults to None.
            max_feat_per_model (Optional[dict], optional): Maximum features per model.
                Defaults to None.
            predictions (Optional[dict], optional): Prediction results from models.
                Defaults to None.
            cv_scores (Optional[dict], optional): Cross-validation scores.
                Defaults to None.
            etna_pipeline (Optional[dict], optional): ETNA pipeline configurations.
                Defaults to None.
            etna_eval_set (Optional[dict], optional): ETNA evaluation sets.
                Defaults to None.
            vectorizers_dict (Optional[dict], optional): Dictionary of vectorizers used.
                Defaults to None.
        """
        super().__init__(
            experiment_path,
            artifact_saver=artifact_saver,
            config=config,
            models=models,
            other_models=other_models,
            oot_potential=oot_potential,
        )
        self.split_by_group = self.config["split_by_group"]
        self.group_column = self.config["group_column"]
        self.target_name = self.config["target_name"]
        self.analysis = analysis

    def create_zero_page(self, drop_params: Optional[List[str]] = None):
        """Creates the zero page of the development report.

        The zero page includes the dreamml_base configuration used to run the experiment.
        It filters out specified parameters and formats the configuration for presentation.

        Args:
            drop_params (Optional[List[str]], optional): List of parameter names to exclude
                from the configuration. Defaults to None.

        Raises:
            KeyError: If a required configuration key is missing.
            IOError: If there is an error writing the Excel file.
        """
        # FIXME: duplicates reports/_base.py method
        drop_params = [] if not drop_params else drop_params
        config_for_report = dict(
            [
                (k, str(v))
                for k, v in self.config.get_dotted_key_dict().items()
                if k not in drop_params
            ]
        )

        config_df = pd.Series(config_for_report).to_frame().reset_index()
        config_df.columns = ["parameter", "value"]

        config_df.to_excel(
            self.writer,
            sheet_name=self.DREAMML_CONFIGURATION_SHEET_NAME,
            index=False,
            startrow=0,
        )
        self.add_table_borders(
            config_df, sheet_name=self.DREAMML_CONFIGURATION_SHEET_NAME, num_format=None
        )
        self.add_header_color(
            config_df, sheet_name=self.DREAMML_CONFIGURATION_SHEET_NAME, color="77d496"
        )
        self.add_cell_width(
            config_df,
            sheet_name=self.DREAMML_CONFIGURATION_SHEET_NAME,
        )

    def create_first_page(self, **eval_sets):
        """Creates the first page of the development report with data statistics.

        This page includes various statistical analyses such as KPSS tests, ADF tests,
        Levene's tests, and period analyses. It also generates STL plots for each segment
        and inserts the visualizations into the Excel report.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.

        Raises:
            Exception: If data transformation or plotting fails.
            IOError: If there is an error writing to the Excel file.
        """
        transformer = CalculateDataStatisticsAMTS(self.encoder, self.config)
        result = transformer.transform(**eval_sets)

        df_kpss_test = pd.DataFrame(self.analysis.analysis_result.kpss_test_dict)
        df_adfuller_test = pd.DataFrame(
            self.analysis.analysis_result.adfuller_test_dict
        )
        df_levene_test = pd.DataFrame(self.analysis.analysis_result.levene_dict)
        df_period = pd.DataFrame(self.analysis.analysis_result.period_dict)

        result = result + (
            df_kpss_test,
            df_adfuller_test,
            df_levene_test,
            df_period,
        )

        startrows = [
            0,
            2 + result[0].shape[0],
            4 + result[0].shape[0] + result[1].shape[0],
            6 + np.sum(res.shape[0] for res in result[:3]),
            8 + np.sum(res.shape[0] for res in result[:4]),
            10 + np.sum(res.shape[0] for res in result[:5]),
            12 + np.sum(res.shape[0] for res in result[:6]),
            14 + np.sum(res.shape[0] for res in result[:7]),
        ]
        num_formats = [10, 10, None, None, None, None, None, None]

        for data, startrow, num_format in zip(result, startrows, num_formats):
            data.to_excel(
                self.writer,
                startrow=startrow,
                sheet_name="Data_Statistics",
                index=False,
            )
            self.set_style(data, "Data_Statistics", startrow, num_format=None)

        self.add_numeric_format(result[0], "Data_Statistics", startrow=startrows[0])

        for i, (segment_name, segment_params) in enumerate(
            self.analysis.analysis_result.stl_dict.items()
        ):
            plot_STL(
                segment_name=segment_name,
                stl_dict=segment_params,
                name=f"{self.experiment_path}/images/stl_{segment_name}",
            )
            ws = self.sheets["Data_Statistics"]
            ws.insert_image(
                f"A{len(data) + ((i+1) * 37)}",
                f"{self.experiment_path}/images/stl_{segment_name}.png",
            )

    def create_third_page(self, **eval_sets):
        """Creates the third page of the development report, comparing different models.

        This page includes metrics comparison between models, generates histograms of
        loss functions, scatter plots of anomaly marks, and inserts the visualizations
        into the Excel report.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.

        Raises:
            Exception: If metrics calculation or plotting fails.
            IOError: If there is an error writing to the Excel file.
        """
        transformer = CalculateAMTSADMetrics(
            self.models, self.group_column, self.split_by_group
        )
        result = transformer.transform(**eval_sets)

        self.target = transformer.target_
        self.predictions = transformer.predictions_
        self.predictions_loss = transformer.predictions_loss_
        self.predictions_mark = transformer.predictions_mark_

        result = result.round(3)
        result.to_excel(self.writer, sheet_name="Compare Models", index=False)
        self.set_style(result, "Compare Models", 0)

        for i, (segment_name, segment_params) in enumerate(self.predictions.items()):
            plot_hist_loss_amts_ad(
                data=self.predictions_loss[segment_name],
                save_path=f"{self.experiment_path}/images/hist_loss_{segment_name}",
                title=f"Histogram of Loss Function Distribution for {segment_name}",
                xlabel="Loss",
            )
            plot_scatter_mark_amts_ad(
                target=self.target[segment_name],
                mark=self.predictions_mark[segment_name],
                save_path=f"{self.experiment_path}/images/scatter_mark_{segment_name}",
                title=f"Anomaly Scatter Plot for {segment_name}",
                ylabel=self.target_name,
            )
            ws = self.sheets["Compare Models"]
            ws.insert_image(
                f"A{len(result) + 5 + (i * 37)}",
                f"{self.experiment_path}/images/hist_loss_{segment_name}.png",
            )
            ws.insert_image(
                f"I{len(result) + 5 + (i * 37)}",
                f"{self.experiment_path}/images/scatter_mark_{segment_name}.png",
            )

    def transform(self, **eval_sets):
        """Generates the development report by creating all necessary report pages.

        This method orchestrates the creation of the dreamml_base information page, zero page,
        first page with data statistics, and the third page comparing models. It saves
        the final report to the specified Excel writer.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.

        Raises:
            Exception: If any step in the report generation process fails.
            IOError: If there is an error saving the Excel report.
        """
        self.create_dml_info_page()
        self.create_zero_page(drop_params=drop_params)
        self.create_first_page(**eval_sets)
        self.create_third_page(**eval_sets)
        self.writer.save()