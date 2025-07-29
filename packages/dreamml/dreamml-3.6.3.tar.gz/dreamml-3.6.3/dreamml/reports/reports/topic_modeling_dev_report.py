from typing import Optional, Dict, List

import pandas as pd
from tqdm.auto import tqdm

from dreamml.reports.reports._base import BaseReport

from .._topic_modeling_metrics import CalculateTopicModelingMetrics
from ..data_statistics.calculate_data_statistics_topic_modeling import (
    CalculateDataStatistics as TopicModeling_DS,
)
from ..detailed_metrics.calculate_detailed_metrics_topic_modeling import (
    CalculateDetailedMetricsTopicModeling,
)
from dreamml.pipeline.cv_score import CVScores
from dreamml.utils.saver import ArtifactSaver
from dreamml.logging import get_logger

_logger = get_logger(__name__)

CV_SCORE_COL = "cv score"
MODEL_NAME_COL = "Название модели"

drop_params = [
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
    "metric_col_name",
    "group_column",
    "time_column",
    "data.columns.time_column_format",
    "time_column_period",
    "data.splitting.split_by_group",
    "data.splitting.custom_cv",
    "models.bert.params.unfreeze_layers",
    "models.bert.params.sampler_type",
    "optimizer_type",
    "scheduler_type",
    "learning_rate",
    "models.bert.params.epochs",
    "batch_size",
    "models.bert.params.weight_decay",
    "data.augmentation.text_augmentations",
    "data.augmentation.aug_p",
    "log_target",
    "pipeline.task_specific.multilabel.target_with_nan_values",
    "pipeline.task_specific.time_series.ts_transforms",
    "pipeline.task_specific.time_series.horizon",
]


class TopicModelingDevReport(BaseReport):
    """
    Report class for Topic Modeling development, extending the BaseReport.

    This class generates various reports and metrics related to topic modeling,
    including data statistics, model comparisons, and detailed metrics for each model.

    Args:
        models: Dictionary of models to include in the report.
        other_models: Dictionary of additional models to include.
        oot_potential: Out-of-time potential data.
        experiment_path: Path to the experiment directory.
        config: Configuration object containing pipeline settings.
        n_bins (int, optional): Number of bins for metrics. Defaults to 20.
        bootstrap_samples (int, optional): Number of bootstrap samples. Defaults to 200.
        p_value (float, optional): P-value threshold for statistical tests. Defaults to 0.05.
        max_feat_per_model (int, optional): Maximum number of features per model. Defaults to 50.
        predictions (Optional[Dict], optional): Dictionary of predictions. Defaults to None.
        cv_scores (CVScores, optional): Cross-validation scores. Defaults to None.
        artifact_saver (Optional[ArtifactSaver], optional): Artifact saver instance. Defaults to None.
        vectorizers_dict (Optional[dict], optional): Dictionary of vectorizers. Defaults to None.
        etna_pipeline (Optional[dict], optional): ETNA pipeline configuration. Defaults to None.
        etna_eval_set (Optional[dict], optional): ETNA evaluation set. Defaults to None.
        analysis (Optional[dict], optional): Additional analysis data. Defaults to None.

    Attributes:
        psi (Optional): PSI importance model if present.
        n_bins (int): Number of bins for metrics.
        bootstrap_samples (int): Number of bootstrap samples.
        p_value (float): P-value threshold.
        max_feat_per_model (int): Maximum features per model.
        predictions (Dict): Predictions dictionary.
        models_metrics_df (Optional[pd.DataFrame]): DataFrame of models metrics.
        cv_scores (CVScores): Cross-validation scores.
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
        cv_scores: CVScores = None,
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

        self.n_bins = n_bins
        self.bootstrap_samples = bootstrap_samples
        self.p_value = p_value
        self.max_feat_per_model = (
            max_feat_per_model if vectorizers_dict is None else 10_000
        )
        self.predictions = predictions or {}
        self.models_metrics_df = None
        self.cv_scores = cv_scores

    def create_zero_page(self, drop_params: Optional[List[str]] = None):
        """
        Creates the zero page of the report, containing the dreamml_base run configuration.

        This method extracts the configuration parameters, excluding those specified
        in `drop_params`, and writes them to an Excel sheet named as defined in
        `DREAMML_CONFIGURATION_SHEET_NAME`. It also applies formatting such as
        table borders, header colors, and cell widths.

        Args:
            drop_params (Optional[List[str]], optional): List of parameter keys to exclude
                from the report. Defaults to None.

        Raises:
            Exception: If there is an error writing to the Excel sheet.
        """
        # FIXME: duplicates repots/_base.py method
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
        """
        Creates the first page of the report with data statistics.

        This method processes the training data to compute statistics and writes the results
        to an Excel sheet named "Data_Statistics". It applies styling to the written data.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.

        Raises:
            Exception: If there is an error during data transformation or writing to Excel.
        """
        sheet_name = "Data_Statistics"
        features = eval_sets["train"][0].columns.to_series()
        transformer = TopicModeling_DS(
            self.encoder, features, self.config, task=self.task
        )
        result = transformer.transform(**eval_sets)

        startows = [0, 3, 6]
        num_formats = [None, None, None]

        for data, startrow, num_format in zip(result, startows, num_formats):
            data.to_excel(
                self.writer,
                startrow=startrow,
                sheet_name=sheet_name,
                index=False,
            )
            self.set_style(data, "Data_Statistics", startrow, num_format=num_format)

    def create_third_page(self, metric_name, metric_col_name, **eval_sets):
        """
        Creates the third page of the report, comparing models based on a specific metric.

        This method calculates topic modeling metrics, writes the results to an Excel sheet
        named "Compare Models {metric_col_name}", and highlights the best models for Test and OOT
        datasets. It also adds hyperlinks to detailed sheets for each dataset.

        Args:
            metric_name (str): The name of the metric to evaluate.
            metric_col_name (str): The column name for the metric in the report.
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.

        Raises:
            Exception: If there is an error during metric calculation or writing to Excel.
        """
        transformer = CalculateTopicModelingMetrics(
            self.models,
            bootstrap_samples=self.bootstrap_samples,
            p_value=self.p_value,
            config=self.config,
            metric_name=metric_name,
            metric_col_name=metric_col_name,
            task=self.task,
            vectorizers=self.vectorizers_dict,
        )
        transformer.predictions_ = self.predictions
        result = transformer.transform(**eval_sets)

        result = result.round(decimals=2)
        self.models_metrics_df = result
        result.to_excel(
            self.writer, sheet_name="Compare Models " + metric_col_name, index=False
        )
        self.set_style(result, "Compare Models " + metric_col_name, 0)

        df_a = result.drop("детали о модели", axis=1)

        self.add_numeric_format(
            df_a, "Compare Models " + metric_col_name, startrow=0, min_value=100
        )

        ws = self.sheets["Compare Models " + metric_col_name]
        best_test_format = self.wb.add_format({"fg_color": "F0D3F7"})
        best_oot_format = self.wb.add_format({"fg_color": "B7C3F3"})

        best_model_info = transformer.get_best_models(stats_df=result, **eval_sets)
        if "OOT" in eval_sets.keys():
            for cell_number, data_value in enumerate(result.columns.values):
                ws.write(
                    best_model_info["test"]["index"] + 1,
                    cell_number,
                    result[data_value][best_model_info["test"]["index"]],
                    best_test_format,
                )

            for cell_number, data_value in enumerate(result.columns.values):
                ws.write(
                    best_model_info["oot"]["index"] + 1,
                    cell_number,
                    result[data_value][best_model_info["oot"]["index"]],
                    best_oot_format,
                )

            if best_model_info["test"]["name"] == best_model_info["oot"]["name"]:
                ws.write(result.shape[0] + 2, 1, best_model_info["oot"]["name"])
                ws.write(
                    result.shape[0] + 2,
                    0,
                    "Лучшая модель для выборки Test и OOT",
                    best_oot_format,
                )

                list_of_args = ["train", "test", "OOT"]
                list_of_letters = ["D", "E", "F"]
                for i in range(len(list_of_args)):
                    sheet_name = f"{list_of_args[i]} {best_model_info['oot']['name']}"
                    url = f"internal:'{sheet_name}'!A1"
                    string = f"Ссылка: {list_of_args[i]}"
                    ws.write_url(
                        f"{list_of_letters[i]}{result.shape[0] + 2 + 1}",
                        url=url,
                        string=string,
                    )

            else:
                ws.write(result.shape[0] + 2, 1, best_model_info["test"]["name"])
                ws.write(result.shape[0] + 3, 1, best_model_info["oot"]["name"])
                ws.write(
                    result.shape[0] + 2,
                    0,
                    "Лучшая модель для выборки Test",
                    best_test_format,
                )
                ws.write(
                    result.shape[0] + 3,
                    0,
                    "Лучшая модель для выборки OOT",
                    best_oot_format,
                )

                list_of_args = ["train", "test", "OOT"]
                list_of_letters = ["D", "E", "F"]
                for i in range(len(list_of_args)):
                    sheet_name = f"{list_of_args[i]} {best_model_info['test']['name']}"
                    url = f"internal:'{sheet_name}'!A1"
                    string = f"Ссылка: {list_of_args[i]}"
                    ws.write_url(
                        f"{list_of_letters[i]}{result.shape[0] + 2 + 1}",
                        url=url,
                        string=string,
                    )
                    sheet_name = f"{list_of_args[i]} {best_model_info['oot']['name']}"
                    url = f"internal:'{sheet_name}'!A1"
                    string = f"Ссылка: {list_of_args[i]}"
                    ws.write_url(
                        f"{list_of_letters[i]}{result.shape[0] + 3 + 1}",
                        url=url,
                        string=string,
                    )
        else:
            for cell_number, data_value in enumerate(result.columns.values):
                ws.write(
                    best_model_info["test"]["index"] + 1,
                    cell_number,
                    result[data_value][best_model_info["test"]["index"]],
                    best_test_format,
                )
            ws.write(result.shape[0] + 2, 1, best_model_info["test"]["name"])
            ws.write(
                result.shape[0] + 2,
                0,
                "Лучшая модель для выборки Test",
                best_test_format,
            )

            list_of_args = ["train", "test"]
            list_of_letters = ["D", "E"]
            for i in range(len(list_of_args)):
                sheet_name = f"{list_of_args[i]} {best_model_info['test']['name']}"
                url = f"internal:'{sheet_name}'!A1"
                string = f"Ссылка: {list_of_args[i]}"
                ws.write_url(
                    f"{list_of_letters[i]}{result.shape[0] + 2 + 1}",
                    url=url,
                    string=string,
                )

    def create_model_report(self, **eval_sets):
        """
        Creates individual reports for each model, including detailed metrics and visualizations.

        This method iterates over each model, calculates detailed topic modeling metrics,
        writes the data to separate Excel sheets, and inserts relevant images. It also
        applies formatting to highlight key information.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.

        Raises:
            Exception: If there is an error during metric calculation or writing to Excel.
        """
        metric_params = self.config.pipeline.metric_params
        metric_name = self.config.pipeline.eval_metric

        for model_name in tqdm(self.models):
            sheet_name = f"{model_name}"[:30]

            umap_params = {
                "n_neighbors": self.config.pipeline.task_specific.topic_modeling.n_neighbors,
                "min_dist": self.config.pipeline.task_specific.topic_modeling.min_dist,
                "metric": self.config.pipeline.task_specific.topic_modeling.metric_umap,
                "n_epochs": self.config.pipeline.task_specific.topic_modeling.umap_epochs,
            }

            transformer = CalculateDetailedMetricsTopicModeling(
                self.models,
                self.experiment_path,
                self.vectorizers_dict,
                self.config.data.columns.text_features[0],
                metric_name,
                metric_params,
                umap_params=umap_params,
            )

            data = transformer.transform(model_name)

            data.to_excel(
                self.writer,
                startrow=32,
                sheet_name=sheet_name,
                index=False,
            )

            sheets = self.writer.sheets
            ws = sheets[sheet_name]
            sheet_format = self.wb.add_format(
                {
                    "bold": True,
                    "text_wrap": True,
                    "fg_color": "77d496",
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                }
            )
            ws.merge_range("A30:D30", "Топ-10 слов по каждому кластеру.", sheet_format)
            try:
                ws.insert_image(
                    "A1", f"{self.experiment_path}/images/umap_{model_name}.png"
                )
            except Exception as e:
                pass

    def transform(self, **eval_sets):
        """
        Transforms the data and generates the complete report.

        This method orchestrates the creation of various report pages, including
        the DML info page, zero page, first page with data statistics, third page
        with model comparisons, and individual model reports. It then saves the
        finalized Excel report.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.

        Raises:
            Exception: If there is an error during the transformation or report generation.
        """
        self.create_dml_info_page()
        self.create_zero_page(drop_params=drop_params)
        self.create_first_page(**eval_sets)

        self.create_third_page(
            self.config.pipeline.eval_metric,
            self.config.pipeline.eval_metric,
            **eval_sets,
        )

        # self.create_traffic_light_page(
        #     self.config.pipeline.eval_metric,
        #     self.config.pipeline.eval_metric,
        #     **eval_sets,
        # )

        # if self.other_models:
        #     self.create_other_model_page(
        #         self.config.pipeline.eval_metric,
        #         self.config.pipeline.eval_metric,
        #         **eval_sets,
        #     )

        # self.create_fourth_page(**eval_sets)
        # self.create_fifth_page(**eval_sets)
        self.create_model_report(**eval_sets)
        self.writer.save()