import pandas as pd
from typing import Optional, Dict
from tqdm.auto import tqdm
from xlsxwriter.exceptions import InvalidWorksheetName
from xlsxwriter.utility import xl_col_to_name
from scipy.stats import pearsonr, spearmanr

from dreamml.modeling.metrics.metrics_mapping import metrics_mapping
from dreamml.reports.reports._base import BaseReport
from dreamml.reports.reports._base import create_used_features_stats
from .._regression_metrics import CalculateRegressionMetrics
from .._regression_metrics import CalculateDetailedMetrics as Regression_DM
from .._regression_metrics import CalculateDataStatistics as Regression_DS
from dreamml.utils.saver import ArtifactSaver
from dreamml.visualization.plots import plot_regression_graph
from dreamml.logging import get_logger

_logger = get_logger(__name__)

CV_SCORE_COL = "cv score"
MODEL_NAME_COL = "Model Name"


class RegressionDevelopmentReport(BaseReport):
    """
    Report on developed regression models in dreamml_base.

    The report includes:
        - Statistics on the data used for model building, including sample statistics (train / valid / ...) and feature statistics.
        - Report on univariate analysis of variables (feature selection using the Gini metric).
        - Comparison of built models based on GINI, PR_AUC, Log-Loss metrics across different datasets (train / valid / ...).
        - Detailed metrics for each model-dataset pair.

    Args:
        models (dict): Dictionary containing instances of built models.
        other_models (dict): Dictionary containing other models built during the experiment.
        oot_potential (dict): Out-of-time potential data.
        experiment_path (str): Path to the experiment folder.
        config (dict): Configuration file with experiment parameters.
        n_bins (int, optional): Number of bins to divide the prediction vector. Defaults to 20.
        artifact_saver (Optional[ArtifactSaver], optional): Artifact saver instance. Defaults to None.
        etna_pipeline (Optional[dict], optional): ETNA pipeline configuration. Defaults to None.
        etna_eval_set (Optional[dict], optional): ETNA evaluation set. Defaults to None.
        vectorizers_dict (Optional[dict], optional): Dictionary of vectorizers. Defaults to None.
        bootstrap_samples (Optional[dict], optional): Dictionary of bootstrap samples. Defaults to None.
        p_value (Optional[dict], optional): Dictionary of p-values. Defaults to None.
        max_feat_per_model (Optional[dict], optional): Dictionary of maximum features per model. Defaults to None.
        predictions (Optional[dict], optional): Dictionary of predictions. Defaults to None.
        cv_scores (Optional[dict], optional): Dictionary of cross-validation scores. Defaults to None.
        analysis (Optional[dict], optional): Dictionary of analysis results. Defaults to None.
    """

    def __init__(
        self,
        models,
        other_models,
        oot_potential,
        experiment_path: str,
        config,
        n_bins: int = 20,
        artifact_saver: Optional[ArtifactSaver] = None,
        etna_pipeline: Optional[dict] = None,
        etna_eval_set: Optional[dict] = None,
        vectorizers_dict: Optional[dict] = None,
        bootstrap_samples: Optional[dict] = None,
        p_value: Optional[dict] = None,
        max_feat_per_model: Optional[dict] = None,
        predictions: Optional[dict] = None,
        cv_scores: Optional[dict] = None,
        analysis: Optional[dict] = None,
    ):
        super().__init__(
            experiment_path,
            artifact_saver=artifact_saver,
            config=config,
            models=models,
            other_models=other_models,
            oot_potential=oot_potential,
        )
        self.corr = self.models.pop("corr_importance", None)
        self.psi = self.models.pop("psi_importance", None)

        self.target_transformer = self.models.pop("log_target_transformer")

        self.n_bins = n_bins
        self.etna_pipeline = etna_pipeline
        self.etna_eval_set = etna_eval_set

    def create_first_page(self, **eval_sets):
        """
        Creates the first page of the report containing statistics of the examined data.

        The report includes:
            - Statistics of the datasets used for training, validation, and testing models, including dataset name, number of observations, number of target events, and the proportion of target events.
            - Overall statistics of variables, including target variable name, number of categorical variables, and number of continuous variables.
            - Detailed statistics for each variable, including number of non-missing values, mean, standard deviation, and percentiles (0, 25, 50, 75, 100).

        Args:
            eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                Dictionary containing datasets for which statistics need to be calculated.
                The key is the dataset name (train / valid / ...), and the value is a tuple with the feature matrix (data) and the target vector (target).

        Raises:
            None
        """
        transformer = Regression_DS(
            self.encoder, self.target_transformer, self.corr, self.config
        )

        if self.task == "multiregression":
            key, (X, y) = next(iter(eval_sets.items()))
            target_names = y.columns
            for i, target_name in enumerate(target_names):
                eval_sets_i = {k: (X, y.iloc[:, i]) for k, (X, y) in eval_sets.items()}
                result = transformer.transform(**eval_sets_i)
                sheet_name = f"Data_Statistics_{target_name}"
                self._process_and_write_result(result, sheet_name)
        else:
            result = transformer.transform(**eval_sets)
            self._process_and_write_result(result, "Data_Statistics")

    def _process_and_write_result(self, result, sheet_name):
        """
        Processes the transformation result and writes the data to an Excel sheet.

        Args:
            result (list[pd.DataFrame]): 
                List of DataFrames containing the transformation results.
            sheet_name (str): 
                Name of the Excel sheet where the result will be written.

        Raises:
            None
        """
        if len(result) < 4:
            startows = [
                0,
                2 + result[0].shape[0],
                4 + result[0].shape[0] + result[1].shape[0],
            ]
            num_formats = [10, None, None]
        else:
            startows = [
                0,
                2 + result[0].shape[0],
                4 + result[0].shape[0] + result[1].shape[0],
                6 + result[0].shape[0] + result[1].shape[0] + result[2].shape[0],
            ]
            num_formats = [10, 10, None, None]

        for data, startrow, num_format in zip(result, startows, num_formats):
            data.to_excel(
                self.writer,
                startrow=startrow,
                sheet_name=sheet_name,
                index=False,
            )
            self.set_style(data, sheet_name, startrow, num_format=None)

        self.add_numeric_format(result[0], sheet_name, startrow=startows[0])

        sheet_format = self.wb.add_format({"right": True, "bottom": True})

        ws = self.sheets[sheet_name]
        ws.write(len(result[0]), 9, result[0].values[-1, -1], sheet_format)

    def create_second_page(self, **eval_sets):
        """
        Creates the second page of the report containing univariate analysis statistics of variable separation ability measured by the Gini metric.

        Args:
            eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                Dictionary containing datasets for which statistics need to be calculated.
                The key is the dataset name (train / valid / ...), and the value is a tuple with the feature matrix (data) and the target vector (target).

        Raises:
            None
        """
        self.corr.to_excel(self.writer, "Correlation-Importance", index=False)
        self.set_style(self.corr, "Correlation-Importance", 0)
        ws = self.sheets["Correlation-Importance"]

        ws.write_string("E2", "Selected - flag indicating feature inclusion in the model")
        ws.write_string("E3", "Selected = 1 - feature is included in the model")
        ws.write_string("E4", "Selected = 0 - feature is not included in the model")
        ws.write_string(
            "E6", "Categorical variables are automatically included in the training"
        )
        ws.set_column(4, 4, 62)

        if self.corr.shape[1] > 3:
            self.add_eventrate_format(
                self.corr["Correlation-Train"],
                "Correlation-Importance",
                startcol=1,
                fmt=2,
            )
            self.add_eventrate_format(
                self.corr["Correlation-Valid"],
                "Correlation-Importance",
                startcol=2,
                fmt=2,
            )
        else:
            self.add_eventrate_format(
                self.corr["Correlation"], "Correlation-Importance", startcol=1, fmt=2
            )

    def create_psi_report(self, **eval_sets):
        """
        Creates an optional page in the report with PSI statistics. The page is created if PSI has been calculated and is present in self.models.

        Args:
            eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                Dictionary containing datasets for which statistics need to be calculated.
                The key is the dataset name (train / valid / ...), and the value is a tuple with the feature matrix (data) and the target vector (target).

        Raises:
            None
        """
        self.psi.to_excel(self.writer, sheet_name="PSI-Importance", index=False)
        self.set_style(self.psi, "PSI-Importance", 0)
        ws = self.sheets["PSI-Importance"]

        ws.write_string("E2", "Selected - flag indicating feature inclusion in the model")
        ws.write_string("E3", "Selected = 1 - feature is included in the model")
        ws.write_string("E4", "Selected = 0 - feature is not included in the model")
        ws.set_column(4, 4, 62)
        self.add_eventrate_format(
            self.psi["PSI"], "PSI-Importance", startcol=1, fmt="0.0000"
        )

    def create_third_page(self, **eval_sets):
        """
        Creates the third or fourth page of the report containing regression task metrics for each model in self.models and each dataset in eval_sets.

        Args:
            eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                Dictionary containing datasets for which metrics need to be calculated.
                The key is the dataset name (train / valid / ...), and the value is a tuple with the feature matrix (data) and the target vector (target).

        Raises:
            None
        """
        transformer = CalculateRegressionMetrics(
            models=self.models,
            log_transformer=self.target_transformer,
            vectorizers=self.vectorizers_dict,
        )
        result = transformer.transform(**eval_sets)
        self.predictions = transformer.predictions_

        if self.config.pipeline.alt_mode.use_etna:
            scores_df = self._get_etna_pipline_metrics()
            scores_df.to_excel(
                self.writer,
                sheet_name="Compare Models",
                index=False,
                startrow=len(result) + 2,
            )

        startcol, endcol = 2 + len(eval_sets), 2 + 3 * len(eval_sets) - 1
        result = result.round(
            3
        )  # Rounding because numeric format code does not work further
        result.to_excel(self.writer, sheet_name="Compare Models", index=False)
        self.set_style(result, "Compare Models", 0)

        cols = [col for col in result.columns if "MAE" in col]
        cols = cols + [MODEL_NAME_COL, "Model Details"]
        df_a = result.drop("Model Details", axis=1)
        df_b = result.drop(cols, axis=1)

        ws = self.sheets["Compare Models"]

        # FIXME: Subsequent code converts Excel cells to numeric,
        # but the functions are poorly written and cause data misalignment

        # Gray color for PR-AUC, Log-Loss metrics
        # self.add_text_color("Compare Models", startcol, endcol)
        # self.add_numeric_format(df_a, "Compare Models", 0, min_value=100)
        # self.add_numeric_format(
        #     df_b, "Compare Models", 0, 1 + len(eval_sets), color="C8C8C8"
        # )

    def _get_etna_pipline_metrics(self):
        """
        Retrieves ETNA pipeline metrics and formats them into a DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing the ETNA pipeline metrics.
        
        Raises:
            None
        """
        etna_used_features = (
            self.etna_pipeline.pipeline.model._base_model.model.feature_names_
        )
        num_features = len(etna_used_features)
        scores_dict, metrics = (
            {
                "Название модели": "etna_pipeline",
                "# признаков": num_features,
            },
            {},
        )

        for name in ["mae", "mape", "rmse", "r2"]:
            if name not in metrics:
                metrics[name] = metrics_mapping[name]()
        metrics["pearsonr"] = pearsonr
        metrics["spearmanr"] = spearmanr

        sample_names = ["train_ts", "valid_ts", "test_ts"]
        if "oot_ts" in self.etna_eval_set and self.etna_eval_set["oot_ts"] is not None:
            sample_names.append("oot_ts")
        for metric_name, metric in metrics.items():
            for sample_name in sample_names:
                column_name = f"{metric_name} {sample_name}"
                if (
                    sample_name in self.etna_eval_set
                    and self.etna_eval_set[sample_name] is not None
                ):
                    sample = self.etna_eval_set[sample_name]
                    y_true = sample.to_pandas(flatten=True)["target"]
                    y_pred = self.etna_pipeline.transform(sample, return_dataset=False)
                    score = metric(y_true, y_pred)
                    if isinstance(score, tuple):
                        score = score[0]
                    score = [round(score, 2)]
                    # score = [round(100 * score, 2)]
                else:
                    score = "-"
                scores_dict[column_name] = score
        scores_dict["Model Details"] = "-"
        scores_df = pd.DataFrame(scores_dict)
        return scores_df

    def create_other_model_page(self, **eval_sets):
        """
        Creates the third or fourth page of the report containing regression and classification metrics for each model in self.other_models (models built on batch selection stages) and each dataset in eval_sets.

        Args:
            eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                Dictionary containing datasets for which metrics need to be calculated.
                The key is the dataset name (train / valid / ...), and the value is a tuple with the feature matrix (data) and the target vector (target).

        Raises:
            None
        """
        transformer = CalculateRegressionMetrics(
            models=self.other_models,
            log_transformer=self.target_transformer,
        )
        result = transformer.transform(**eval_sets)
        result = result.round(decimals=2)

        df_a = result.drop("Model Details", axis=1)

        df_a.to_excel(self.writer, sheet_name="Other Models", index=False)
        self.set_style(df_a, "Other Models", 0)

        self.add_numeric_format(df_a, "Other Models", startrow=0, min_value=100)

        ws = self.sheets["Other Models"]

        msg = "This sheet presents all models obtained during the dynamic feature selection stages."
        ws.write(df_a.shape[0] + 5, 0, msg)
        msg = (
            "These models are automatically saved to disk and stored in the experiment folder under the 'other_models' directory. "
            "By default, the threshold for saving is up to 100 features per model."
        )
        ws.write(df_a.shape[0] + 6, 0, msg)
        msg = "It is recommended to select a model with 20 to 40 features, provided there are no performance degradations."
        ws.write(df_a.shape[0] + 7, 0, msg)

    def create_model_report(self, **eval_sets):
        """
        Creates report pages for each model-dataset pair in eval_sets.

        Args:
            eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                Dictionary containing datasets for which reports need to be created.
                The key is the dataset name (train / valid / ...), and the value is a tuple with the feature matrix (data) and the target vector (target).

        Raises:
            None
        """
        transformer = Regression_DM(self.target_transformer, self.n_bins)
        for model in tqdm(self.models):

            for sample in eval_sets:
                if self.task == "multiregression":
                    target_names = eval_sets[sample][1].columns

                    for i, target_name in enumerate(target_names):
                        sheet_name = f"{sample} {model} target_{i+1}"

                        # Excel doesn't support sheet names longer than 31 characters
                        sheet_name = sheet_name.replace("optimization", "opt")
                        sheet_name = sheet_name.replace("CatBoost", "CB")

                        y_true, y_pred = (
                            eval_sets[sample][1][target_name],
                            self.predictions[model][sample][:, i],
                        )

                        self._process_model_results(
                            y_true, y_pred, sheet_name, transformer, eval_sets
                        )

                else:
                    sheet_name = f"{sample} {model}"
                    y_true, y_pred = (
                        eval_sets[sample][1],
                        self.predictions[model][sample],
                    )

                    self._process_model_results(
                        y_true, y_pred, sheet_name, transformer, eval_sets
                    )

    def _process_model_results(
        self, y_true, y_pred, sheet_name, transformer, eval_sets
    ):
        """
        Processes model results, writes them to Excel, and adds plots.

        Args:
            y_true (pd.Series): True values of the target variable.
            y_pred (np.ndarray): Predicted values from the model.
            sheet_name (str): Name of the Excel sheet where data will be written.
            transformer (Regression_DM): Transformer instance for processing data.
            eval_sets (dict): Dictionary with datasets for further use.

        Raises:
            InvalidWorksheetName: If the sheet name exceeds Excel's limit and cannot be shortened uniquely.
        """
        if self.target_transformer.fitted:
            y_true = self.target_transformer.inverse_transform(y_true)

        data = transformer.transform(y_true, y_pred)

        try:
            data.to_excel(self.writer, sheet_name=sheet_name, index=False)
        except InvalidWorksheetName:
            # Excel worksheet name must be <= 31 characters.
            sheet_name = sheet_name[:31]

            for i in range(10):
                if sheet_name in self.sheets:
                    sheet_name = sheet_name[:-3] + f"({i})"
                else:
                    break

            if sheet_name in self.sheets:
                _logger.error(f"Couldn't create worksheet with name '{sheet_name}'")
                return

            data.to_excel(self.writer, sheet_name=sheet_name, index=False)

        self.set_style(data, sheet_name, 0)
        self.add_numeric_format(data, sheet_name, min_value=100)
        self.create_compare_models_url(data, sheet_name)
        self.create_model_url(**eval_sets)

        # Add regression plot
        ws = self.sheets[sheet_name]
        plot_regression_graph(
            y_true, y_pred, f"{self.experiment_path}/images/{sheet_name}"
        )
        ws.insert_image(
            f"A{len(data) + 7}",
            f"{self.experiment_path}/images/{sheet_name}.png",
        )

    def create_four_page(self, **eval_sets):
        """
        Creates the fourth or fifth page of the report listing the used features.

        Args:
            eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                Dictionary containing datasets used in the report.
                The key is the dataset name (train / valid / ...), and the value is a tuple with the feature matrix (data) and the target vector (target).

        Raises:
            None
        """
        df = create_used_features_stats(self.models, **eval_sets)
        df.to_excel(self.writer, sheet_name="Used Features", index=False)
        self.set_style(df, "Used Features", 0)

    def create_model_url(self, **eval_sets):
        """
        Creates links to model/report sheets and adds them to the "Compare Models" sheet.

        Args:
            eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                Dictionary containing datasets used in the report.
                The key is the dataset name (train / valid / ...), and the value is a tuple with the feature matrix (data) and the target vector (target).

        Raises:
            None
        """
        ws = self.sheets["Compare Models"]
        cols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        sheet_format = self.wb.add_format({"left": True, "right": True})
        train_sheets = [sheet for sheet in self.sheets if "train" in sheet]

        for sheet_number, sheet_name in enumerate(train_sheets):
            url = f"internal:'{sheet_name}'!A1"
            string = f"Link to sheet {sheet_name}"

            # Last column in sheet
            cell_name = xl_col_to_name(len(ws.table[0]) - 1)

            ws.write_url(f"{cell_name}{sheet_number + 2}", url, sheet_format, string)

        sheet_format = self.wb.add_format({"left": True, "right": True, "bottom": True})
        ws.write_url(f"{cell_name}{sheet_number + 2}", url, sheet_format, string)

    def transform(self, **eval_sets):
        """
        Generates the report on developed models.

        Args:
            eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                Dictionary containing datasets for which the report needs to be generated.
                The key is the dataset name (train / valid / ...), and the value is a tuple with the feature matrix (data) and the target vector (target).

        Raises:
            None
        """
        self.create_dml_info_page()
        self.create_zero_page()
        self.create_first_page(**eval_sets)
        if self.corr is not None:
            self.create_second_page(**eval_sets)

        if isinstance(self.psi, pd.DataFrame):
            self.create_psi_report(**eval_sets)

        self.create_third_page(**eval_sets)
        if self.other_models:
            self.create_other_model_page(**eval_sets)
        self.create_four_page(**eval_sets)
        self.create_model_report(**eval_sets)
        self.writer.save()