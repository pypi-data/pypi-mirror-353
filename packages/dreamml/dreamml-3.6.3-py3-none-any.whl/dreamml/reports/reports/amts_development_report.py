import numpy as np
import pandas as pd
from typing import Optional, Dict, List

from dreamml.reports.reports._base import BaseReport
from ..data_statistics.calculate_data_statistics_amts import CalculateDataStatisticsAMTS
from .._amts_metrics import CalculateAMTSMetrics

from dreamml.visualization.plots import plot_STL

from dreamml.utils.saver import ArtifactSaver

# FIXME AMTS
drop_params = [
    "drop_features",
    "data.columns.never_used_features",
    "data.columns.categorical_features",
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
    "models.n_estimators",
    "pipeline.verbose",
    "pipeline.alt_mode.lama_time",
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


class AMTSDevelopmentReport(BaseReport):
    """A report class for developing AMTS models, inheriting from BaseReport.

    This class generates various pages of the AMTS development report, including
    configuration details, data statistics, model comparisons, and more.

    Attributes:
        split_by_group (bool): Indicates if the data is split by group.
        group_column (str): The name of the group column.
        analysis (Any): The analysis results used in the report.
        predictions (Optional[dict]): Predictions made by the models.
    """

    def __init__(
        self,
        models,
        other_models,
        oot_potential,
        experiment_path,
        config,
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
        """Initializes the AMTSDevelopmentReport with necessary parameters.

        Args:
            models: A collection of models to be included in the report.
            other_models: Additional models for comparison.
            oot_potential: Out-of-time potential metrics.
            experiment_path: Path to the experiment directory.
            config: Configuration settings for the report.
            analysis: Analysis results used for generating the report.
            artifact_saver (Optional[ArtifactSaver]): Utility to save artifacts. Defaults to None.
            n_bins (Optional[dict]): Number of bins for various metrics. Defaults to None.
            bootstrap_samples (Optional[dict]): Number of bootstrap samples. Defaults to None.
            p_value (Optional[dict]): P-values for statistical tests. Defaults to None.
            max_feat_per_model (Optional[dict]): Maximum features per model. Defaults to None.
            predictions (Optional[dict]): Predictions made by the models. Defaults to None.
            cv_scores (Optional[dict]): Cross-validation scores. Defaults to None.
            etna_pipeline (Optional[dict]): ETNA pipeline configuration. Defaults to None.
            etna_eval_set (Optional[dict]): ETNA evaluation set. Defaults to None.
            vectorizers_dict (Optional[dict]): Dictionary of vectorizers used. Defaults to None.
        """
        super().__init__(
            experiment_path,
            artifact_saver=artifact_saver,
            config=config,
            models=models,
            other_models=other_models,
            oot_potential=oot_potential,
        )
        self.split_by_group = self.config.data.splitting.split_by_group
        self.group_column = self.config.data.columns.group_column
        self.analysis = analysis

    def create_zero_page(self, drop_params: Optional[List[str]] = None):
        """Creates the zero page of the report containing dreamml_base configuration.

        This page includes the configuration parameters used to run dreamml_base, excluding
        any parameters specified in the drop_params list.

        Args:
            drop_params (Optional[List[str]]): List of parameter names to exclude from the configuration. Defaults to None.
        """
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
        """Creates the first page of the report with data statistics and tests.

        This page includes various statistical analyses such as KPSS test, ADFuller test,
        Levene test, and period analysis. It also generates STL plots for different segments.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.
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

        startows = [
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

        for data, startrow, num_format in zip(result, startows, num_formats):
            data.to_excel(
                self.writer,
                startrow=startrow,
                sheet_name="Data_Statistics",
                index=False,
            )
            self.set_style(data, "Data_Statistics", startrow, num_format=None)

        self.add_numeric_format(result[0], "Data_Statistics", startrow=startows[0])

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
        """Creates the third page of the report comparing different models.

        This page includes metrics computed for each model, allowing for easy comparison.
        It also stores the predictions made by each model.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.
        """
        transformer = CalculateAMTSMetrics(
            self.models, self.group_column, self.split_by_group
        )
        result = transformer.transform(**eval_sets)
        self.predictions = transformer.predictions_

        result = result.round(3)
        result.to_excel(self.writer, sheet_name="Compare Models", index=False)
        self.set_style(result, "Compare Models", 0)

    def transform(self, **eval_sets):
        """Generates the full AMTS development report.

        This method orchestrates the creation of all report pages, including configuration,
        data statistics, and model comparisons, and then saves the report to the designated path.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.

        Raises:
            Exception: If there is an error during report generation or saving.
        """
        self.create_dml_info_page()
        self.create_zero_page(drop_params=drop_params)
        self.create_first_page(**eval_sets)
        self.create_third_page(**eval_sets)
        self.writer.save()