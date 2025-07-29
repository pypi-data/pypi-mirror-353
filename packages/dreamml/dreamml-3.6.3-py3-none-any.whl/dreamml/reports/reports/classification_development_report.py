import os.path
from copy import deepcopy
from typing import Optional, Dict, Tuple
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelBinarizer
from tqdm.auto import tqdm
from xlsxwriter.exceptions import InvalidWorksheetName

from dreamml.reports.reports._base import BaseReport
from dreamml.reports.reports._base import create_used_features_stats

from .._classification_metrics import CalculateClassificationMetrics
from .._classification_metrics import CalculateDataStatistics as Binary_DS
from .._classification_metrics import CalculateDetailedMetrics as Binary_DM
from dreamml.pipeline.cv_score import CVScores
from dreamml.utils.saver import ArtifactSaver
from dreamml.visualization.plots import (
    plot_binary_graph,
    plot_multi_graph,
    plot_token_length_distribution_for_text_features,
)
from dreamml.logging import get_logger
from dreamml.validation.classification import (
    ValidationReport,
    prepare_artifacts_config,
)
from dreamml.validation.nlp.classification.part_3_specification.test_3_1_tokens_importance_check import (
    ModelTokensImportanceAnalysis,
)
from dreamml.modeling.models.estimators import BaseModel

_logger = get_logger(__name__)

CV_SCORE_COL = "cv score"
MODEL_NAME_COL = "Model Name"


class ClassificationDevelopmentReport(BaseReport):
    """Report on developed classification models in DS-Template.

    The report includes:
        - Statistics on the data used for building models: statistics on datasets (train/valid/...)
          and features.
        - Report on univariate analysis of variables (feature selection using Gini metric).
        - Comparison of built models based on GINI, PR_AUC, and Log-Loss metrics on datasets
          (train/valid/...).
        - Detailed metrics for each model and dataset pair.

    Args:
        models (Dict[str, BaseModel]):
            Dictionary containing instances of built models.
        other_models (Dict[str, BaseModel]):
            Dictionary containing instances of models built during batch selection stages.
        oot_potential (Any):
            Out-of-time potential data.
        experiment_path (str):
            Path to the experiment directory.
        config (dict):
            Configuration file with experiment parameters.
        n_bins (int, optional):
            Number of bins for splitting the prediction vector. Defaults to 20.
        bootstrap_samples (int, optional):
            Number of bootstrap samples for constructing confidence intervals. Defaults to 200.
        p_value (float, optional):
            Size of the critical zone for confidence intervals (p_value / 2 on each side).
            Defaults to 0.05.
        max_feat_per_model (int, optional):
            Maximum number of features in a model for building the validation traffic light.
            Defaults to 50.
        predictions (Optional[Dict] = None):
            Optional dictionary of predictions.
        cv_scores (CVScores, optional):
            CVScores object containing cv score values for main pipeline models and other models.
            The cv score value is the average metric value across folds in cross-validation for each model.
            key: str - model name
            value: float - metric value
        artifact_saver (Optional[ArtifactSaver] = None):
            Optional ArtifactSaver instance.
        vectorizers_dict (Optional[dict] = None):
            Optional dictionary of vectorizers.
        etna_pipeline (Optional[dict] = None):
            Optional ETNA pipeline configuration.
        etna_eval_set (Optional[dict] = None):
            Optional ETNA evaluation set.
        analysis (Optional[dict] = None):
            Optional analysis configuration.

    Raises:
        ValueError: If an invalid task is specified.
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
        # DataFrame with models and metrics for some Excel sheets, created in create_third_page
        self.models_metrics_df = None
        self.cv_scores = cv_scores

    def create_first_page(self, **eval_sets):
        """Create the first page of the report containing data statistics.

        The report includes:
            - Statistics for datasets used for building/validation/testing models: dataset name,
              number of observations, number of target events, and proportion of target events in the dataset.
            - Overall statistics for variables: target variable name, number of categorical variables,
              and number of continuous variables.
            - Detailed statistics for each variable: number of non-missing values, mean, standard deviation,
              and percentiles (0, 25, 50, 75, 100).

        Args:
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of datasets for which to calculate statistics.
                The key is the dataset name (e.g., 'train', 'valid'), and the value is a tuple containing
                the feature matrix (data) and target vector (target).

        Raises:
            KeyError: If 'train' dataset is not present in eval_sets.
            Exception: For any other exceptions that occur during processing.
        """
        sheet_name = "Data_Statistics"
        features = eval_sets["train"][0].columns.to_series()
        transformer = Binary_DS(self.encoder, features, self.config, task=self.task)
        result = transformer.transform(**eval_sets)

        startows = [
            0,
            2 + result[0].shape[0],
            4 + result[0].shape[0] + result[1].shape[0],
        ]
        num_formats = [10, None, None]

        for data, startrow, num_format in zip(result, startows, num_formats):
            data.to_excel(
                self.writer,
                startrow=startrow,
                sheet_name=sheet_name,
                index=False,
            )
            self.set_style(data, "Data_Statistics", startrow, num_format=num_format)

        if self.task in ["multiclass", "multilabel"]:
            if self.task == "multiclass":
                eval_set_cols = self.config.pipeline.metric_params["labels"]
            else:
                eval_set_cols = eval_sets["train"][1].columns.tolist()
            classes = [f"# Event Rate {class_name}" for class_name in eval_set_cols]

            for column_number, column in enumerate(classes):
                self.add_eventrate_format(
                    result[0][column], "Data_Statistics", startcol=len(classes) + 2 + column_number, fmt="0.00%",
                )

        self.add_numeric_format(result[2], "Data_Statistics", startrow=startows[-1])
        self._write_distrib_text_feature_hist(eval_sets, sheet_name)
        self._write_token_importance_text_feature_graph(eval_sets, sheet_name)

    def create_second_page(self, **eval_sets):
        """Create the second page of the report containing univariate analysis statistics based on Gini metric.

        Args:
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of datasets for which to calculate statistics.
                The key is the dataset name (e.g., 'train', 'valid'), and the value is a tuple containing
                the feature matrix (data) and target vector (target).

        Raises:
            Exception: If any error occurs during Excel writing or formatting.
        """
        self.gini.to_excel(self.writer, "GINI-Importance", index=False)
        self.set_style(self.gini, "GINI-Importance", 0)
        ws = self.sheets["GINI-Importance"]

        ws.write_string("H2", "Selected - flag indicating feature inclusion in the model")
        ws.write_string("H3", "Selected = 1 - feature included in the model")
        ws.write_string("H4", "Selected = 0 - feature excluded from the model")
        ws.write_string(
            "H6", "Categorical variables are automatically included in training"
        )

        ws.set_column(7, 7, 62)
        gini_columns = [col for col in self.gini.columns if "GINI" in col]
        for column_number, column in enumerate(gini_columns):
            self.add_eventrate_format(
                self.gini[column], "GINI-Importance", startcol=1 + column_number, fmt=2
            )

    def create_psi_report(self, **eval_sets):
        """Create an optional PSI statistics page in the report.

        This page is created if PSI has been calculated and is present in self.models.

        Args:
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of datasets for which to calculate statistics.
                The key is the dataset name (e.g., 'train', 'valid'), and the value is a tuple containing
                the feature matrix (data) and target vector (target).

        Raises:
            Exception: If any error occurs during Excel writing or formatting.
        """
        self.psi.to_excel(self.writer, sheet_name="PSI-Importance", index=False)
        self.set_style(self.psi, "PSI-Importance", 0)
        ws = self.sheets["PSI-Importance"]

        ws.write_string("F2", "Selected - flag indicating feature inclusion in the model")
        ws.write_string("F3", "Selected = 1 - feature included in the model")
        ws.write_string("F4", "Selected = 0 - feature excluded from the model")
        ws.set_column(5, 5, 62)
        self.add_eventrate_format(
            self.psi["PSI"], "PSI-Importance", startcol=1, fmt="0.0000"
        )

    def create_third_page(
        self, metric_name, metric_col_name, def_gini_flag=False, **eval_sets
    ):
        """Create the third page of the report containing classification metrics for each model and dataset.

        Args:
            metric_name (str):
                Name of the metric to be calculated.
            metric_col_name (str):
                Column name for the metric in the Excel sheet.
            def_gini_flag (bool, optional):
                Flag indicating whether to use default Gini. Defaults to False.
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of datasets for which to calculate statistics.
                The key is the dataset name (e.g., 'train', 'valid'), and the value is a tuple containing
                the feature matrix (data) and target vector (target).

        Raises:
            Exception: If any error occurs during metric calculation or Excel writing.
        """
        transformer = CalculateClassificationMetrics(
            self.models,
            bootstrap_samples=self.bootstrap_samples,
            p_value=self.p_value,
            config=self.config,
            metric_name=metric_name,
            task=self.task,
            predictions=self.predictions,
            vectorizers=self.vectorizers_dict,
        )
        result = transformer.transform(**eval_sets)
        self.predictions = transformer.predictions_

        if not def_gini_flag:
            result = self.add_cv_scores(
                result, self.cv_scores.stage_models, metric_name, metric_col_name
            )

        result = result.round(decimals=2)

        self.models_metrics_df = result

        result.to_excel(
            self.writer, sheet_name="Compare Models " + metric_col_name, index=False
        )
        self.set_style(result, "Compare Models " + metric_col_name, 0)

        df_a = result.drop("Model Details", axis=1)

        self.add_numeric_format(
            df_a, "Compare Models " + metric_col_name, startrow=0, min_value=100
        )

        ws = self.sheets["Compare Models " + metric_col_name]
        best_test_format = self.wb.add_format({"fg_color": "F0D3F7"})
        best_oot_format = self.wb.add_format({"fg_color": "B7C3F3"})
        self.cv_score_legend(result, ws, 20)

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
                    "Best model for Test and OOT datasets",
                    best_oot_format,
                )

                list_of_args = ["train", "test", "OOT"]
                list_of_letters = ["D", "E", "F"]
                for i in range(len(list_of_args)):
                    sheet_name = f"{list_of_args[i]} {best_model_info['oot']['name']}"
                    url = f"internal:'{sheet_name}'!A1"
                    string = f"Link: {list_of_args[i]}"
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
                    "Best model for Test dataset",
                    best_test_format,
                )
                ws.write(
                    result.shape[0] + 3,
                    0,
                    "Best model for OOT dataset",
                    best_oot_format,
                )

                list_of_args = ["train", "test", "OOT"]
                list_of_letters = ["D", "E", "F"]
                for i in range(len(list_of_args)):
                    sheet_name = f"{list_of_args[i]} {best_model_info['test']['name']}"
                    url = f"internal:'{sheet_name}'!A1"
                    string = f"Link: {list_of_args[i]}"
                    ws.write_url(
                        f"{list_of_letters[i]}{result.shape[0] + 2 + 1}",
                        url=url,
                        string=string,
                    )
                    sheet_name = f"{list_of_args[i]} {best_model_info['oot']['name']}"
                    url = f"internal:'{sheet_name}'!A1"
                    string = f"Link: {list_of_args[i]}"
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
                "Best model for Test dataset",
                best_test_format,
            )

            list_of_args = ["train", "test"]
            list_of_letters = ["D", "E"]
            for i in range(len(list_of_args)):
                sheet_name = f"{list_of_args[i]} {best_model_info['test']['name']}"
                url = f"internal:'{sheet_name}'!A1"
                string = f"Link: {list_of_args[i]}"
                ws.write_url(
                    f"{list_of_letters[i]}{result.shape[0] + 2 + 1}",
                    url=url,
                    string=string,
                )

        msg = "This model selection is advisory in nature!"
        ws.write(result.shape[0] + 10, 0, msg, self.wb.add_format({"bold": True}))
        msg = "Model selection is determined using the following methodology:"
        ws.write(result.shape[0] + 11, 0, msg)
        msg = (
            f"For the model with the highest {metric_name} metric on the Test dataset, a confidence interval is built."
        )
        ws.write(result.shape[0] + 12, 0, msg)
        msg = (
            f"From all models whose {metric_name} metric on the Test dataset falls within this confidence interval, "
            "the model with the fewest features is selected."
        )
        ws.write(result.shape[0] + 13, 0, msg)
        msg = (
            "If an Out-of-Time dataset is available, the same procedure is applied to it."
        )
        ws.write(result.shape[0] + 14, 0, msg)

        msg = (
            "It is recommended to select a model with 20 to 40 features, provided there are no quality degradations."
        )
        ws.write(result.shape[0] + 16, 0, msg)
        msg = (
            "Additional models obtained during dynamic feature selection stages are available via the link below:"
        )
        ws.write(result.shape[0] + 17, 0, msg)

        url = "internal:'Other Models'!A1"
        string = "Link to 'Other Models' sheet"
        ws.write_url(f"A{result.shape[0] + 18 + 1}", url=url, string=string)

        # Confidence intervals
        bold_cell_format = self.wb.add_format(
            {"bold": True, "top": 1, "bottom": 1, "left": 1, "right": 1}
        )
        bold_cell_format.set_align("right")
        normal_cell_format = self.wb.add_format(
            {"top": 1, "bottom": 1, "left": 1, "right": 1}
        )
        ws.write(
            result.shape[0] + 6,
            0,
            "Confidence Intervals:",
            self.wb.add_format({"bold": True}),
        )
        ws.write(result.shape[0] + 7, 0, "Test", bold_cell_format)
        ws.write(
            result.shape[0] + 7,
            1,
            round(best_model_info["test"]["ci"][0], 2),
            normal_cell_format,
        )
        ws.write(
            result.shape[0] + 7,
            2,
            round(best_model_info["test"]["ci"][1], 2),
            normal_cell_format,
        )
        if "OOT" in eval_sets.keys():
            ws.write(result.shape[0] + 8, 0, "OOT", bold_cell_format)
            ws.write(
                result.shape[0] + 8,
                1,
                round(best_model_info["oot"]["ci"][0], 2),
                normal_cell_format,
            )
            ws.write(
                result.shape[0] + 8,
                2,
                round(best_model_info["oot"]["ci"][1], 2),
                normal_cell_format,
            )

        ws.write(
            result.shape[0] + 7,
            4,
            f"Alpha = {self.p_value} (p_value/2 on each side)",
        )
        ws.set_column(0, 0, 37)

    def cv_score_legend(self, result, ws, add_row):
        """Add a legend for CV score in the Excel sheet.

        Args:
            result (pd.DataFrame):
                DataFrame containing model metrics.
            ws (xlsxwriter worksheet):
                The worksheet where the legend will be added.
            add_row (int):
                The row number to start adding the legend.

        Raises:
            None
        """
        if CV_SCORE_COL not in result.columns.tolist():
            return
        msg = "The 'cv_score' column shows the average metric value across CV folds."
        ws.write(result.shape[0] + add_row, 0, msg, self.wb.add_format({"bold": False}))
        msg = "A value of 0 in the 'cv_score' column indicates that it could not be calculated for the specific model."
        ws.write(
            result.shape[0] + add_row + 1, 0, msg, self.wb.add_format({"bold": False})
        )

    @staticmethod
    def add_cv_scores(
        metrics: pd.DataFrame, cv_scores: dict, metric_name: str, metric_col_name: str
    ) -> pd.DataFrame:
        """Add CV scores column to the metrics DataFrame.

        Replaces the 'GINI valid' column with 'cv_score' in the 'Compare Models GINI' sheet.

        Args:
            metrics (pd.DataFrame):
                DataFrame containing GINI metric values for each model and dataset.
            cv_scores (dict):
                Dictionary containing CV scores for different models.
            metric_name (str):
                Name of the metric being used.
            metric_col_name (str):
                Column name for the metric in the Excel sheet.

        Returns:
            pd.DataFrame:
                DataFrame with an added 'cv_score' column replacing 'GINI valid'.

        Raises:
            None
        """
        if not cv_scores:
            return metrics
        with_cv_score = deepcopy(metrics)
        cv_scores_df = pd.DataFrame(
            list(cv_scores.items()), columns=[MODEL_NAME_COL, CV_SCORE_COL]
        )
        with_cv_score = with_cv_score.merge(cv_scores_df, on=MODEL_NAME_COL, how="left")
        with_cv_score = with_cv_score.fillna(0)
        # TODO: Add capability to calculate cv_score for different metrics
        index1 = with_cv_score.columns.tolist().index(metric_name + " valid")
        index2 = with_cv_score.columns.tolist().index(CV_SCORE_COL)
        new_order = with_cv_score.columns.tolist()
        new_order[index1] = new_order.pop(index2)
        return with_cv_score[new_order]

    def create_other_model_page(self, metric_name, metric_col_name, **eval_sets):
        """Create a page in the report containing metrics for other models built during batch selection stages.

        Args:
            metric_name (str):
                Name of the metric to be calculated.
            metric_col_name (str):
                Column name for the metric in the Excel sheet.
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of datasets for which to calculate statistics.
                The key is the dataset name (e.g., 'train', 'valid'), and the value is a tuple containing
                the feature matrix (data) and target vector (target).

        Raises:
            Exception: If any error occurs during metric calculation or Excel writing.
        """
        transformer = CalculateClassificationMetrics(
            self.other_models,
            bootstrap_samples=self.bootstrap_samples,
            p_value=self.p_value,
            config=self.config,
            metric_name=metric_name,
            task=self.task,
            vectorizers=self.vectorizers_dict,
        )
        result = transformer.transform(**eval_sets)

        result = self.add_cv_scores(
            result, self.cv_scores.other_models, metric_name, metric_col_name
        )
        result = result.round(decimals=2)

        df_a = result.drop("Model Details", axis=1)

        df_a.to_excel(self.writer, sheet_name="Other Models", index=False)
        self.set_style(df_a, "Other Models", 0)

        self.add_numeric_format(df_a, "Other Models", startrow=0, min_value=100)

        ws = self.sheets["Other Models"]
        msg = "This sheet presents all models obtained during dynamic feature selection stages."
        ws.write(df_a.shape[0] + 3, 0, msg)
        msg = (
            "These models are automatically saved to disk and stored in the 'other_models' directory within the experiment folder. "
            "By default, the threshold for saving is up to 100 features per model."
        )
        ws.write(df_a.shape[0] + 4, 0, msg)
        msg = (
            "It is recommended to select a model with 20 to 40 features, provided there are no quality degradations."
        )
        ws.write(df_a.shape[0] + 5, 0, msg)

        self.cv_score_legend(df_a, ws, 7)

    def create_oot_pot_page(self):
        """Create a page in the report containing OOT potential metrics.

        This page is created if OOT potential is used and the OOT path is specified in the configuration.

        Raises:
            None
        """
        if (
            self.config.pipeline.use_oot_potential
            and self.config.data.oot_path is not None
        ):
            df_a = pd.DataFrame(data=[self.oot_potential[0]])
            df_shap = self.oot_potential[1]
            df_a.to_excel(self.writer, sheet_name="OOT Potential", index=False)
            df_shap.to_excel(
                self.writer,
                sheet_name="OOT Potential",
                startrow=df_a.shape[0] + 2,
                index=False,
            )

            self.set_style(df_a, "OOT Potential", 0)
            self.add_numeric_format(df_a, "OOT Potential", startrow=0, min_value=100)
            self.set_style(df_shap, "OOT Potential", df_a.shape[0] + 2)

            ws = self.sheets["OOT Potential"]
            msg = "Introducing the OOT data potential metric."
            ws.write("E4", msg)
            msg = "Used as an upper bound estimate for the selected model."
            ws.write("E5", msg)
            msg = (
                "This value may be irrelevant due to a large ratio between dev and OOT datasets "
                "or differences in distributions between dev and OOT datasets."
            )
            ws.write("E6", msg)
            msg = (
                "Adversarial Validation is used to assess distribution similarity."
            )
            ws.write("E9", msg)
            msg = "A value close to zero indicates that dev and OOT datasets are from similar distributions."
            ws.write("E10", msg)

    def create_traffic_light_page(self, metric_name, metric_col_name, **eval_sets):
        """Create a traffic light page in the report with validation tests.

        Builds a final traffic light for each model corresponding to the declared complexity.

        Args:
            metric_name (str):
                Name of the metric to be used.
            metric_col_name (str):
                Column name for the metric in the Excel sheet.
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of datasets for which to calculate statistics.
                The key is the dataset name (e.g., 'train', 'valid'), and the value is a tuple containing
                the feature matrix (data) and target vector (target).

        Raises:
            Exception: If any error occurs during traffic light creation or Excel writing.
        """
        df = self.models_metrics_df
        n = 6 if "OOT" in eval_sets.keys() else 5
        # TODO: Make dynamic expansion, as regression has more metric columns
        url_col = "K" if "OOT" in eval_sets.keys() else "J"

        traffic_light_df = pd.DataFrame(
            columns=df.columns[:n].to_list()
            + ["Test 1", "Test 2", "Test 3", "Test 4", "Final"]
            + df.columns[-1:].to_list()
        )

        models_for_traffic_light = df[df["# Features"] <= self.max_feat_per_model][
            MODEL_NAME_COL
        ].to_numpy()

        for model_idx, model in enumerate(models_for_traffic_light):
            experiment_path = Path(self.experiment_path)
            experiment_dir_name = str(experiment_path.name)
            results_path = str(experiment_path.parent)

            model_: BaseModel = self.models[model]
            vectorizer_name = None
            if model_.vectorization_name is not None:
                if model_.vectorization_name != "bert":
                    vectorizer_name = f"{model_.vectorization_name}_vectorizer"

            config = {
                "dir_name": experiment_dir_name,
                "results_path": results_path,
                "model_name": model,
                "vectorizer_name": vectorizer_name,
                "task": self.task,
                "subtask": self.config.pipeline.subtask,
                "text_column": self.config.get("text_column", []),
                "text_preprocessed_column": self.config.get(
                    "text_preprocessed_column", []
                ),
            }
            artifacts_config, data = prepare_artifacts_config(
                config,
                experiment_config=self.config,
                model=model_,
                encoder=self.encoder,
            )
            artifacts_config["metric_name"] = metric_name
            artifacts_config["metric_col_name"] = metric_col_name
            artifacts_config["metric_params"] = self.config.pipeline.metric_params
            artifacts_config["task"] = self.task
            artifacts_config["subtask"] = self.config.pipeline.task
            artifacts_config["text_column"] = self.config.get("text_column", [])
            artifacts_config["text_preprocessed_column"] = self.config.get(
                "text_preprocessed_column", []
            )

            # TODO: Make report class selection dynamic
            report = ValidationReport(
                config=config, create_file=False, **artifacts_config
            )

            traffic_light = report.create_traffic_light(**data)
            traffic_light_df.loc[model_idx] = (
                df[df[MODEL_NAME_COL] == model][df.columns[:n]].values[0].tolist()
                + traffic_light
                + df[df[MODEL_NAME_COL] == model][df.columns[-1:]].values[0].tolist()
            )

        traffic_light_df.to_excel(
            self.writer, sheet_name="Validation " + metric_col_name, index=False
        )
        try:
            self.set_style(traffic_light_df, "Validation " + metric_col_name, 0)
        except IndexError:
            _logger.exception("Unable to apply formatting to the Excel table.")

        ws = self.sheets["Validation " + metric_col_name]

        # Traffic light coloring
        red_format = self.wb.add_format({"bg_color": "CC0000"})
        yellow_format = self.wb.add_format({"bg_color": "FFFF33"})
        green_format = self.wb.add_format({"bg_color": "66CC99"})
        ws.conditional_format(
            "A2:Z100",
            {
                "type": "cell",
                "criteria": "equal to",
                "value": '"red"',
                "format": red_format,
            },
        )
        ws.conditional_format(
            "A2:Z100",
            {
                "type": "cell",
                "criteria": "equal to",
                "value": '"yellow"',
                "format": yellow_format,
            },
        )
        ws.conditional_format(
            "A2:Z100",
            {
                "type": "cell",
                "criteria": "equal to",
                "value": '"green"',
                "format": green_format,
            },
        )

        # Hyperlinks
        sheet_format = self.wb.add_format({"left": True, "right": True, "bottom": True})
        for model_idx, model in enumerate(models_for_traffic_light):
            url = f"internal:'train {model}'!A1"
            string = f"Link to sheet train {model}"
            ws.write_url(f"{url_col}{model_idx + 2}", url, sheet_format, string)

        msg = "Sheet with validation tests"
        ws.write(traffic_light_df.shape[0] + 3, 0, msg)
        msg = "Test 2 - Test 2.1 on model quality."
        ws.write(traffic_light_df.shape[0] + 4, 0, msg)
        msg = "Test 3 - Test 3.1 model calibration."
        ws.write(traffic_light_df.shape[0] + 5, 0, msg)
        msg = "Test 5 - Results of tests 5.2, 5.6, 5.7 on model stability."
        ws.write(traffic_light_df.shape[0] + 6, 0, msg)
        msg = "Data quality test was not conducted as it does not depend on the model and has a final assessment"
        ws.write(traffic_light_df.shape[0] + 7, 0, msg)
        msg = "only yellow or green. This test is conducted in the full validation report."
        ws.write(traffic_light_df.shape[0] + 8, 0, msg)

    def create_fourth_page(self, **eval_sets):
        """Create the fourth page of the report containing PR-AUC metrics for each model and dataset.

        Args:
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of datasets for which to calculate statistics.
                The key is the dataset name (e.g., 'train', 'valid'), and the value is a tuple containing
                the feature matrix (data) and target vector (target).

        Raises:
            Exception: If any error occurs during PR-AUC metric calculation or Excel writing.
        """
        transformer = CalculateClassificationMetrics(
            self.models,
            bootstrap_samples=self.bootstrap_samples,
            p_value=self.p_value,
            config=self.config,
            metric_name="precision_recall_auc",
            task=self.task,
            vectorizers=self.vectorizers_dict,
        )
        result = transformer.transform(**eval_sets)

        result = result.round(decimals=2)

        result.to_excel(self.writer, sheet_name="Compare Models PR-AUC", index=False)
        self.set_style(result, "Compare Models PR-AUC", 0)

        df_a = result.drop("Model Details", axis=1)

        self.add_numeric_format(
            df_a, "Compare Models PR-AUC", startrow=0, min_value=100
        )

    def create_fifth_page(self, **eval_sets):
        """Create the fifth page of the report listing the used features.

        Raises:
            Exception: If any error occurs during feature statistics calculation or Excel writing.
        """
        result = create_used_features_stats(
            self.models, self.vectorizers_dict, **eval_sets
        )

        if isinstance(result, pd.DataFrame):
            result.to_excel(self.writer, sheet_name="Used Features", index=False)
            self.set_style(result, "Used Features", 0)
        else:
            for vec_name, df in result.items():
                sheet_name = f"UF {vec_name}"[:30]
                df.to_excel(self.writer, sheet_name=sheet_name, index=False)
                self.set_style(df, sheet_name, 0)

    def create_model_report(self, **eval_sets):
        """Create report pages for each model and dataset pair.

        Args:
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of datasets for which to calculate statistics.
                The key is the dataset name (e.g., 'train', 'valid'), and the value is a tuple containing
                the feature matrix (data) and target vector (target).

        Raises:
            InvalidWorksheetName: If the worksheet name exceeds Excel's limit.
            Exception: If any other error occurs during report creation.
        """
        metric_params = self.config.pipeline.metric_params
        metric_name = self.config.pipeline.eval_metric

        for model in tqdm(self.models):
            for sample in eval_sets:
                sheet_name = f"{sample} {model}"
                y_true, y_pred = eval_sets[sample][1], self.predictions[model][sample]

                transformer = Binary_DM(
                    self.n_bins, metric_name, metric_params, task=self.task
                )
                data = transformer.transform(y_true, y_pred)

                try:
                    self._write_graphs(
                        sample,
                        eval_sets,
                        y_true,
                        y_pred,
                        data,
                        sheet_name,
                        metric_params,
                    )
                except InvalidWorksheetName:
                    # Excel worksheet name must be <= 31 chars.
                    sheet_name = sheet_name[:31]

                    for i in range(10):
                        if sheet_name in self.sheets:
                            sheet_name = sheet_name[:-3] + f"({i})"
                        else:
                            break

                    if sheet_name in self.sheets:
                        _logger.error(
                            f"Couldn't create worksheet with name '{sheet_name}'"
                        )
                        continue
                    self._write_graphs(
                        sample,
                        eval_sets,
                        y_true,
                        y_pred,
                        data,
                        sheet_name,
                        metric_params,
                    )

    def _write_graphs(
        self, sample, eval_sets, y_true, y_pred, data, sheet_name, metric_params
    ):
        """Internal method to write graphs based on the task type.

        Args:
            sample (str):
                Name of the dataset sample.
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of evaluation sets.
            y_true (pandas.Series or np.ndarray):
                True target values.
            y_pred (pandas.Series or np.ndarray):
                Predicted target values.
            data (Any):
                Transformed data containing metrics.
            sheet_name (str):
                Name of the Excel sheet.
            metric_params (dict):
                Parameters for the metric calculation.

        Raises:
            ValueError: If the task type is unsupported.
            Exception: If any error occurs during graph writing.
        """
        if self.task in ["binary", "multiclass"]:
            self._write_graphs_binary_multiclass(
                eval_sets,
                y_true,
                y_pred,
                data,
                sheet_name,
                metric_params["labels"],
            )
        elif self.task == "multilabel":
            self._write_graphs_multilabel(
                sample, eval_sets, y_true, y_pred, data, sheet_name
            )
        else:
            raise ValueError(
                'Supports only "multilabel", "multiclass" and "binary" tasks.'
            )

    def _write_graphs_binary_multiclass(
        self, eval_sets, y_true, y_pred, data, sheet_name, labels
    ):
        """Internal method to write binary and multiclass graphs.

        Args:
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of evaluation sets.
            y_true (pandas.Series):
                True target values.
            y_pred (pandas.Series or np.ndarray):
                Predicted target values.
            data (pd.DataFrame):
                DataFrame containing metrics.
            sheet_name (str):
                Name of the Excel sheet.
            labels (List[str]):
                List of label names.

        Raises:
            Exception: If any error occurs during graph plotting or Excel writing.
        """
        data.to_excel(self.writer, sheet_name=sheet_name, index=False)
        self.set_style(data, sheet_name, 0)
        self.add_numeric_format(data, sheet_name, min_value=200)
        if self.task == "binary":
            self.add_eventrate_format(data["eventrate"], sheet_name)
        self.create_compare_models_url(data, sheet_name, fmt_col_4=2)
        self.create_model_url(**eval_sets)

        ws = self.sheets[sheet_name]
        if self.task == "binary":
            plot_binary_graph(
                y_true, y_pred, f"{self.experiment_path}/images/{sheet_name}.png"
            )
            ws.insert_image(
                f"A{len(data) + 5}",
                f"{self.experiment_path}/images/{sheet_name}.png",
            )

        elif self.task == "multiclass" and self.plot_multi_graphs:
            arange_labels = np.arange(len(labels))
            label_binarizer = LabelBinarizer().fit(arange_labels)
            y_true_binarized = pd.DataFrame(
                data=label_binarizer.transform(y_true), columns=arange_labels
            )

            pic_path = f"{self.experiment_path}/images/{sheet_name}_macro.png"
            plot_multi_graph(
                y_true=y_true_binarized.values,
                y_pred_proba=y_pred,
                save_path=pic_path,
                classes=arange_labels,
            )
            ws.insert_image(
                f"A{len(data) + 5}",
                f"{self.experiment_path}/images/{sheet_name}_macro.png",
            )

    def _write_graphs_multilabel(
        self, sample, eval_sets, y_true, y_pred, data, sheet_name: str
    ):
        """Internal method to write multilabel classification graphs.

        Args:
            sample (str):
                Name of the dataset sample.
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of evaluation sets.
            y_true (pandas.DataFrame):
                True target values for multilabel classification.
            y_pred (np.ndarray):
                Predicted target values for multilabel classification.
            data (List[Any]):
                List containing metrics data for each class.
            sheet_name (str):
                Name of the Excel sheet.

        Raises:
            Exception: If any error occurs during graph plotting or Excel writing.
        """
        for class_idx, item in enumerate(data):
            y_true_class = y_true.iloc[:, class_idx]
            y_pred_class = y_pred[:, class_idx]

            if self.target_with_nan_values is True:
                y_true_mask = y_true_class.isnull()
                y_true_class = y_true_class[~y_true_mask]
                y_pred_class = y_pred_class[~y_true_mask]

            class_name = item[0]
            score = item[1]
            startrow = class_idx * 25
            table_name = pd.DataFrame(columns=[class_name, sample])
            score.to_excel(
                self.writer,
                sheet_name=sheet_name,
                index=False,
                startrow=startrow,
                startcol=27,
            )
            self.set_style(score, sheet_name, startrow=startrow)
            self.add_numeric_format(score, sheet_name, min_value=100, startrow=startrow)
            self.add_eventrate_format(score["eventrate"], sheet_name, startrow=startrow)
            self.create_compare_models_url(score, sheet_name)
            self.create_model_url(**eval_sets)
            ws = self.sheets[sheet_name]

            # Graph for each class
            if sample in self.samples_to_plot and class_idx < self.max_classes_plot:
                pic_path = (
                    f"{self.experiment_path}/images/{sheet_name}_{class_name}.png"
                )
                plot_binary_graph(y_true_class, y_pred_class, pic_path)
                table_name.to_excel(
                    self.writer,
                    sheet_name=sheet_name,
                    index=False,
                    startrow=startrow,
                    startcol=27,
                )
                ws.insert_image(
                    f"AA{3+ startrow}",
                    f"{self.experiment_path}/images/{sheet_name}_{class_name}.png",
                )
                if self.show_save_paths:
                    _logger.debug(
                        f"Saving graph {self.experiment_path}/images/{sheet_name}_{class_name}.png"
                    )

        if self.plot_multi_graphs:
            # Overall graph
            pic_path = f"{self.experiment_path}/images/{sheet_name}_macro.png"
            plot_multi_graph(
                y_true=y_true.values,
                y_pred_proba=y_pred,
                save_path=pic_path,
                classes=y_true.columns.tolist(),
            )
            ws.insert_image(
                f"A{25 * len(data) + 5}",
                f"{self.experiment_path}/images/{sheet_name}_macro.png",
            )
            if self.show_save_paths:
                _logger.debug(
                    f"Saving graph {self.experiment_path}/images/{sheet_name}_multi.png"
                )

    def _write_distrib_text_feature_hist(self, eval_set, sheet_name):
        """Internal method to write token length distribution histograms for text features.

        Args:
            eval_set (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of evaluation sets.
            sheet_name (str):
                Name of the Excel sheet.

        Raises:
            Exception: If any error occurs during histogram plotting or Excel writing.
        """
        ws = self.sheets[sheet_name]
        rownum = 7

        text_features = (
            self.config.data.columns.text_features
            + self.config.data.columns.text_features_preprocessed
        )

        if text_features:
            for sample_name, (x_sample, _) in eval_set.items():
                for text_feature in text_features:
                    save_path = f"{self.experiment_path}/images/{sheet_name}_{sample_name}_{text_feature}.png"

                    plot_token_length_distribution_for_text_features(
                        sample_name, text_feature, x_sample, save_path, n_bins=50
                    )
                    ws.insert_image(f"J{rownum}", save_path)
                    rownum += 20

    def _write_token_importance_text_feature_graph(self, eval_set, sheet_name):
        """Internal method to write token importance graphs for preprocessed text features.

        Args:
            eval_set (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of evaluation sets.
            sheet_name (str):
                Name of the Excel sheet.

        Raises:
            Exception: If any error occurs during token importance calculation or Excel writing.
        """
        ws = self.sheets[sheet_name]
        rownum = 7

        text_features_preprocessed = self.config.data.columns.text_features_preprocessed

        for text_feature in text_features_preprocessed:
            eval_set_cp = deepcopy(eval_set)

            for sample_name, (X_sample, y_sample) in eval_set_cp.items():
                eval_set_cp[sample_name] = (X_sample[text_feature], y_sample)

            images_dir_path = f"{self.experiment_path}/images/"
            split_test = ModelTokensImportanceAnalysis(None, images_dir_path)
            chi_results = split_test.calculate_stats(eval_set_cp, text_feature)[1]
            for col in chi_results.columns:
                save_path = f"{images_dir_path}{text_feature}_{col}.png"
                if os.path.exists(save_path):
                    ws.insert_image(f"U{rownum}", save_path)
                    rownum += 40

    def transform(self, **eval_sets):
        """Generate the report on developed models.

        Args:
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
                Dictionary of datasets for which to calculate statistics.
                The key is the dataset name (e.g., 'train', 'valid'), and the value is a tuple containing
                the feature matrix (data) and target vector (target).

        Raises:
            Exception: If any error occurs during report generation.
        """
        self.create_dml_info_page()
        self.create_zero_page()
        self.create_first_page(**eval_sets)
        # self.create_second_page(**eval_sets)  # Gini metric
        if isinstance(self.psi, pd.DataFrame):
            self.create_psi_report(**eval_sets)
        if (
            self.task in ("binary", "multiclass", "multilabel")
            and self.config.pipeline.eval_metric != "gini"
        ):
            self.create_third_page("gini", "gini", def_gini_flag=True, **eval_sets)
            self.create_traffic_light_page("gini", "gini", **eval_sets)

        self.create_third_page(
            self.config.pipeline.eval_metric,
            self.config.pipeline.eval_metric,
            **eval_sets,
        )
        self.create_traffic_light_page(
            self.config.pipeline.eval_metric,
            self.config.pipeline.eval_metric,
            **eval_sets,
        )

        if self.other_models:
            self.create_other_model_page(
                self.config.pipeline.eval_metric,
                self.config.pipeline.eval_metric,
                **eval_sets,
            )
        self.create_oot_pot_page()
        self.create_fourth_page(**eval_sets)
        self.create_fifth_page(**eval_sets)
        self.create_model_report(**eval_sets)
        self.writer.save()