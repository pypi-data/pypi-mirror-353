import json
import os
import socket
import sys
from copy import deepcopy
from pathlib import Path
from typing import Optional, List

import numpy as np
import pandas as pd
from xlsxwriter.utility import xl_col_to_name

import dreamml as dml
from dreamml.configs.config_storage import ConfigStorage
from dreamml.logging import get_logger
from dreamml.utils.saver import ArtifactSaver
from dreamml.utils.vectorization_eval_set import get_eval_set_with_embeddings

_logger = get_logger(__name__)


class BaseReport:
    """
    A set of rules and styles for formatting the report.

    Args:
        experiment_path: Path to the experiment directory.
        artifact_saver (ArtifactSaver): An instance of ArtifactSaver for saving output files.
        config (ConfigStorage): An instance of ConfigStorage containing configuration settings.
        models (dict): Dictionary of models to include in the report.
        other_models (dict): Dictionary of additional models.
        oot_potential: Potential Out-Of-Time data.
        vectorizers_dict (Optional[dict], optional): Dictionary of vectorizers. Defaults to None.
    """

    def __init__(
        self,
        experiment_path,
        artifact_saver: ArtifactSaver,
        config: ConfigStorage,
        models,
        other_models,
        oot_potential,
        vectorizers_dict: Optional = None,
    ):
        self.DREAMML_CONFIGURATION_SHEET_NAME = "Конфигурация dreamml_base"
        self.MODEL_NAME_COL = "Название модели"

        self.models = deepcopy(models)
        self.encoder = self.models.pop("encoder")
        self.other_models = deepcopy(other_models)
        self.oot_potential = deepcopy(oot_potential)
        self.config = config
        self.experiment_path = experiment_path
        self.task = config.pipeline.task
        self.artifact_saver = artifact_saver
        self.vectorizers_dict = (
            deepcopy(vectorizers_dict) if vectorizers_dict != {} else None
        )

        # if_sheet_exists="overlay", позволяет перезаписать текущую ячейку - ValueError: Append mode is not
        #  supported with xlsxwriter!
        self.writer = pd.ExcelWriter(
            path=f"{self.experiment_path}/docs/{self.artifact_saver.dev_report_name}.xlsx",
            options={"nan_inf_to_errors": True},
        )
        self.sheets = self.writer.sheets
        self.wb = self.writer.book
        self.predictions = None
        self.target_with_nan_values = (
            config.pipeline.task_specific.multilabel.target_with_nan_values
        )
        self.show_save_paths: bool = (
            config.pipeline.task_specific.multilabel.show_save_paths
        )
        self.samples_to_plot: list = (
            config.pipeline.task_specific.multilabel.samples_to_plot
        )
        self.max_classes_plot: int = (
            config.pipeline.task_specific.multilabel.max_classes_plot
        )
        self.plot_multi_graphs: bool = (
            config.pipeline.task_specific.multilabel.plot_multi_graphs
        )

    def add_table_borders(
        self, data, sheet_name: str, startrow: int = 0, num_format: int = 10
    ):
        """
        Sets table borders on an Excel sheet.

        Args:
            data (pandas.DataFrame): The dataset to write to Excel.
            sheet_name (str): The name of the sheet in the Excel workbook where data will be written.
            startrow (int, optional): The row number to start writing data from. Defaults to 0.
            num_format (int, optional): The numerical format for data. Defaults to 10.

        Raises:
            ValueError: If attempting to append data in an unsupported mode.
        """
        ws = self.sheets[sheet_name]
        last_col = data.columns[-1]

        # Apply number format if specified
        if num_format:
            sheet_format = self.wb.add_format({"right": 1, "num_format": num_format})
        else:
            sheet_format = self.wb.add_format({"right": 1})

        for cell_number, data_value in enumerate(data[last_col]):
            row_idx, col_idx = startrow + cell_number + 1, data.shape[1] - 1

            # FIXME адаптировать для задач multiclass & multilabel
            if isinstance(data_value, pd.Series):
                content = data_value.to_string(index=False).replace("\n", ", ")
                ws.write(row_idx, col_idx, content, sheet_format)
            else:
                ws.write(row_idx, col_idx, data_value, sheet_format)

        # Write the last row in data
        sheet_format = self.wb.add_format({"bottom": 1})
        for cell_number, data_value in enumerate(data.values[-1]):
            row_idx, col_idx = startrow + data.shape[0], cell_number

            # FIXME адаптировать для задач multiclass & multilabel
            if isinstance(data_value, pd.Series):
                data_value = data_value.to_string(index=False).replace("\n", ", ")
            if isinstance(data_value, list):
                data_value = ", ".join(data_value)
            ws.write(row_idx, col_idx, data_value, sheet_format)

        # Write the last cell in the last row
        if num_format:
            sheet_format = self.wb.add_format(
                {"right": 1, "bottom": 1, "num_format": num_format}
            )
        else:
            sheet_format = self.wb.add_format({"right": 1, "bottom": 1})

        row_idx, col_idx = startrow + data.shape[0], data.shape[1] - 1

        # FIXME адаптировать для задач multiclass & multilabel
        if isinstance(data.values[-1, -1], pd.Series):
            content = data.values[-1, -1].to_string(index=False).replace("\n", ", ")
            ws.write(row_idx, col_idx, content, sheet_format)
        else:
            ws.write(row_idx, col_idx, data.values[-1, -1], sheet_format)

    def add_cell_width(self, data, sheet_name: str):
        """
        Sets the width of cells on an Excel sheet.

        Args:
            data (pandas.DataFrame): The dataset to write to Excel.
            sheet_name (str): The name of the sheet in the Excel workbook where data will be written.
        """
        ws = self.sheets[sheet_name]
        for cell_number, table_column in enumerate(data.columns):
            max_value_len = data[table_column].astype("str").str.len().max()
            cell_len = max(max_value_len, len(table_column)) + 2
            ws.set_column(cell_number, cell_number, cell_len)

    def add_header_color(
        self, data, sheet_name: str, startrow: int = 0, color: str = "77d496"
    ):
        """
        Sets the header color on an Excel sheet.

        Args:
            data (pandas.DataFrame): The dataset to write to Excel.
            sheet_name (str): The name of the sheet in the Excel workbook where data will be written.
            startrow (int, optional): The row number to start writing data from. Defaults to 0.
            color (str, optional): The RGB color of the header. Defaults to "77d496".
        """
        ws = self.sheets[sheet_name]
        sheet_format = self.wb.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "fg_color": color,
                "border": 1,
                "align": "center",
            }
        )

        for cell_number, data_value in enumerate(data.columns.values):
            ws.write(startrow, cell_number, data_value, sheet_format)

    def add_numeric_format(
        self,
        data,
        sheet_name: str,
        startrow: int = 0,
        startcol: int = 0,
        min_value: int = 10,
        color: str = "#000000",
    ):
        """
        Applies numeric formatting to a numeric table on an Excel sheet.

        Args:
            data (pandas.DataFrame): The dataset to write to Excel.
            sheet_name (str): The name of the sheet in the Excel workbook where data will be written.
            startrow (int, optional): The row number to start writing data from. Defaults to 0.
            startcol (int, optional): The column number to start writing data from. Defaults to 0.
            min_value (int, optional): The minimum value for special formatting. Defaults to 10.
            color (str, optional): The RGB color of the font. Defaults to "#000000".

        Raises:
            numpy.core._exceptions.UFuncTypeError: If there is a type error during formatting.
        """
        ws = self.sheets[sheet_name]

        for col_number, column in enumerate(data.columns[1:]):
            if col_number == data.shape[1] - 2:
                fmt = {"right": 1}
            else:
                fmt = {}

            for row_number, value in enumerate(data[column]):
                try:
                    if row_number == data.shape[0] - 1:
                        fmt.update({"bottom": 1, "font_color": color})

                    if np.abs(value) > min_value or np.abs(value) in range(min_value):
                        fmt.update({"num_format": 1, "font_color": color})
                        sheet_format = self.wb.add_format(fmt)
                    elif np.abs(value) <= min_value:
                        fmt.update({"num_format": 2, "font_color": color})
                        sheet_format = self.wb.add_format(fmt)

                except np.core._exceptions.UFuncTypeError:
                    fmt = {"right": 1}
                    sheet_format = self.wb.add_format(fmt)

                ws.write(
                    startrow + row_number + 1,
                    startcol + col_number + 1,
                    value,
                    sheet_format,
                )

    def add_text_color(
        self, sheet_name: str, startcol: int, endcol: int, color: str = "C8C8C8"
    ):
        """
        Adds a specific text color to a range of columns on an Excel sheet.

        Args:
            sheet_name (str): The name of the sheet in the Excel workbook where data will be modified.
            startcol (int): The starting column number (0-indexed) to apply the text color.
            endcol (int): The ending column number (0-indexed) to apply the text color.
            color (str, optional): The RGB color of the text. Defaults to "C8C8C8".
        """
        ws = self.sheets[sheet_name]
        cols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        startcol, endcol = cols[startcol], cols[endcol]

        sheet_format = self.wb.add_format({"font_color": color})
        ws.set_column(f"{startcol}:{endcol}", None, sheet_format)

    def add_eventrate_format(
        self, data, sheet_name: str, startcol: int = 7, startrow: int = 0, fmt: int = 10
    ):
        """
        Adds formatting for event rates on an Excel sheet.

        Args:
            data (pandas.Series): The column containing event rate values.
            sheet_name (str): The name of the sheet in the Excel workbook where data will be modified.
            startcol (int, optional): The column number to apply the format. Defaults to 7.
            startrow (int, optional): The row number to start applying the format from. Defaults to 0.
            fmt (int, optional): The xlsxwriter format code. Defaults to 10.

        Raises:
            ValueError: If the specified sheet does not exist.
        """
        ws = self.sheets[sheet_name]
        sheet_format = self.wb.add_format({"num_format": fmt})

        for cell_number, data_value in enumerate(data):
            ws.write(1 + cell_number + startrow, startcol, data_value, sheet_format)

        sheet_format = self.wb.add_format({"num_format": fmt, "bottom": True})
        ws.write(len(data) + startrow, startcol, data_value, sheet_format)

    def add_bottom_table_borders(
        self, data, sheet_name: str, startrow: int = 0, fmt_col_4: int = 10
    ):
        """
        Sets the top and bottom borders of a table on an Excel sheet.

        Args:
            data (pandas.Series): The column containing table values.
            sheet_name (str): The name of the sheet in the Excel workbook where data will be modified.
            startrow (int, optional): The row number to start applying the borders from. Defaults to 0.
            fmt_col_4 (int, optional): The format code for column 4. Defaults to 10.
        """
        ws = self.sheets[sheet_name]

        for cell_number, data_value in enumerate(data):
            if isinstance(data_value, str):
                fmt = {"bottom": 1, "left": 1, "right": 1, "top": 1, "bold": True}
            elif data_value > 100:
                fmt = {
                    "bottom": 1,
                    "left": 1,
                    "right": 1,
                    "top": 1,
                    "num_format": 1,
                    "bold": True,
                }
            elif data_value < 100 and cell_number != 4:
                fmt = {
                    "bottom": 1,
                    "left": 1,
                    "right": 1,
                    "top": 1,
                    "num_format": 2,
                    "bold": True,
                }
            elif cell_number == 4:
                fmt = {
                    "bottom": 1,
                    "left": 1,
                    "right": 1,
                    "top": 1,
                    "num_format": fmt_col_4,
                    "bold": True,
                }
            else:
                fmt = {"bottom": 1, "left": 1, "right": 1, "top": 1, "bold": True}
            sheet_format = self.wb.add_format(fmt)
            ws.write(startrow, cell_number, data_value, sheet_format)

    def create_compare_models_url(self, data, sheet_name: str, fmt_col_4: int = 10):
        """
        Creates a hyperlink to the "Compare Models" sheet and adds it to the report sheet for each model/sample pair.

        Args:
            data (pandas.DataFrame): The dataset to write to Excel.
            sheet_name (str): The name of the sheet in the Excel workbook where the URL will be added.
            fmt_col_4 (int, optional): The format code for column 4. Defaults to 10.
        """
        destination_sheet = None
        for destination_sheet in self.sheets:
            if "compare models" in destination_sheet.lower():
                break
        if destination_sheet is None:
            _logger.warning("Compare Models sheet not found.")
            return

        ws = self.sheets[sheet_name]

        # last column in destination sheet
        cell_name = xl_col_to_name(len(self.sheets[destination_sheet].table[0]) - 1)
        string = "Link to Compare Models sheet"
        url = f"internal:'{destination_sheet}'!{cell_name}1"

        df = data.loc[max(data.index)]
        ws.write_url(f"A{len(data) + 2}", url, string=string)
        self.add_bottom_table_borders(
            df, sheet_name, data.shape[0], fmt_col_4=fmt_col_4
        )
        self.add_cell_width(data, sheet_name)

    def create_model_url(self, **eval_sets):
        """
        Creates a hyperlink to the model/report sheet and adds it to the "Compare Models" sheet.

        Args:
            eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]): Dictionary containing evaluation sets.
                The key is the name of the set (e.g., train, valid), and the value is a tuple containing
                the feature matrix (data) and the target vector (target).

        Raises:
            KeyError: If a specified metric sheet does not exist.
        """
        metrics = set([self.config.pipeline.eval_metric] + ["PR-AUC"])
        for metric in metrics:
            ws = self.sheets[f"Compare Models {metric}"]
            cols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            sheet_format = self.wb.add_format({"left": True, "right": True})
            train_sheets = [sheet for sheet in self.sheets if "train" in sheet]

            for sheet_number, sheet_name in enumerate(train_sheets):
                url = f"internal:'{sheet_name}'!A1"
                string = f"Link to sheet {sheet_name}"
                cell_number = len(eval_sets) + 2

                if "test" in eval_sets:
                    cell_number += 2
                if "OOT" in eval_sets:
                    cell_number += 2

                cell_name = cols[cell_number]
                ws.write_url(
                    f"{cell_name}{sheet_number + 2}", url, sheet_format, string
                )

            sheet_format = self.wb.add_format(
                {"left": True, "right": True, "bottom": True}
            )
            ws.write_url(f"{cell_name}{sheet_number + 2}", url, sheet_format, string)

    def set_style(
        self,
        data,
        sheet_name: str,
        startrow: int = 0,
        color: str = "77d496",
        num_format: Optional[int] = None,
    ):
        """
        Sets the base style for all Excel workbook sheets. The base style includes:
            - Setting table borders
            - Adjusting cell widths to optimal sizes
            - Setting header colors
            - Formatting fonts

        Args:
            data (pandas.DataFrame): The dataset to write to Excel.
            sheet_name (str): The name of the sheet in the Excel workbook where data will be written.
            startrow (int, optional): The row number to start writing data from. Defaults to 0.
            color (str, optional): The RGB color of the header. Defaults to "77d496".
            num_format (Optional[int], optional): The numerical format for data. Defaults to None.
        """
        self.add_table_borders(data, sheet_name, startrow, num_format)
        self.add_header_color(data, sheet_name, startrow, color)
        self.add_cell_width(data, sheet_name)

    def create_dml_info_page(self):
        """
        Creates an information page for dreamml_base within the Excel report. This page includes module version,
        kernel information, and host name details.
        
        Raises:
            FileNotFoundError: If the kernel.json file is not found in the expected directory.
        """
        # FIXME: duplicating code fragment with report_classification.py
        kernel_folder_path = Path(sys.executable).parent.parent
        kernel_name = os.path.basename(kernel_folder_path)
        kernel_version = ""
        try:
            kernel_path = os.path.join(kernel_folder_path, "jh_kernel", "kernel.json")
            with open(kernel_path, "r") as file:
                kernel = json.load(file)
            kernel_version = kernel["display_name"]
        except FileNotFoundError:
            kernel_version = kernel_name

        host_name = socket.gethostname()
        df = pd.DataFrame(
            {
                "Module": ["dreamml_base", "Kernel", "Host_name"],
                "Version": [dml.__version__, kernel_version, host_name],
            }
        )
        df.to_excel(self.writer, sheet_name="V", index=False)
        self.set_style(df, "V", 0)

        ws = self.sheets["V"]
        msg = "Made in dreamml_base"
        ws.write(df.shape[0] + 4, 0, msg, self.wb.add_format({"italic": True}))

    def create_zero_page(self, drop_params: Optional[List[str]] = None):
        """
        Creates the zero page of the report, which contains the dreamml_base run configuration.

        Args:
            drop_params (Optional[List[str]], optional): List of parameters to exclude from the report.
                Defaults to None.
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

    def _create_business_task_description_page(self, **data):
        """
        Creates a page with a description of the business task.

        Args:
            **data: Arbitrary keyword arguments representing data to include in the business task description.
        """
        _logger.info("0. Collecting statistics about the business task.")
        bcd = BusinessCaseDescription(
            self.artifacts_config, self.validation_test_config
        )
        stats = bcd._create_description(**data)
        stats.to_excel(self.writer, sheet_name="Описание бизнес-задачи", index=False)
        self.sheet_descriptions["Описание бизнес-задачи"] = ""

        ws = self.writer.sheets["Описание бизнес-задачи"]

        b_task_cell_format = NamedStyle(name="b_task_cell_format")
        b_task_cell_format.font = Font(color="808080")
        b_task_cell_format.alignment = Alignment(
            wrap_text=True, horizontal="center", vertical="center"
        )
        brd = Side(border_style="thin", color="000000")
        b_task_cell_format.border = Border(left=brd, right=brd, top=brd, bottom=brd)

        self.wb.add_named_style(b_task_cell_format)

        b_task_row_title_format = NamedStyle(name="b_task_row_title_format")
        b_task_row_title_format.font = Font(bold=True)
        b_task_row_title_format.alignment = Alignment(
            horizontal="center", vertical="center"
        )
        brd = Side(border_style="thin", color="000000")
        b_task_row_title_format.border = Border(
            left=brd, right=brd, top=brd, bottom=brd
        )

        self.wb.add_named_style(b_task_row_title_format)

        b_task_col_title_format = NamedStyle(name="b_task_col_title_format")
        b_task_col_title_format.font = Font(bold=True)
        b_task_col_title_format.fill = PatternFill(
            start_color="00CC99", end_color="00CC99", fill_type="solid"
        )
        b_task_col_title_format.alignment = Alignment(
            horizontal="center", vertical="center"
        )
        brd = Side(border_style="thin", color="000000")
        b_task_col_title_format.border = Border(
            left=brd, right=brd, top=brd, bottom=brd
        )

        self.wb.add_named_style(b_task_col_title_format)

        business_task_text = (
            "<Enter the model name> \n"
            "for example: Rental rate prediction model for commercial real estate"
        )
        task_description_text = (
            "<Enter the model description: modeling goal, \n"
            "which business process the model is built for, what data is used> \n"
            "for example: Rental rate prediction model for commercial real estate. \n"
            "The model is built on data from the data center about the opening/closing of new bank branches."
        )
        report_dt_description_text = (
            "<Specify report dates> \n" "for example: 31.01.2022, 28.02.2022, 31.03.2022"
        )
        target_description_text = "<Enter the definition of the target event/variable>"
        data_selection_text = (
            "<Enter population selection criteria: filters, exclusions>\n"
            "for example: 1. Offices open on the report date."
        )
        used_algo_text = "<dreamml_base XGBRegressor>"
        ws.merge_cells("B2:E2")
        ws.merge_cells("B3:E3")
        ws.merge_cells("B4:D4")
        ws.merge_cells("B5:D5")
        ws.merge_cells("B6:E6")
        ws.merge_cells("B7:E7")

        ws["B2"] = business_task_text
        ws["B3"] = task_description_text
        ws["B4"] = report_dt_description_text
        ws["B5"] = data_selection_text
        ws["B6"] = target_description_text
        ws["B7"] = used_algo_text
        ws["E4"] = report_dt_description_text
        ws["E5"] = data_selection_text
        ws["A1"] = "Parameter"
        ws["A2"] = "Business Task"
        ws["A3"] = "Task Description"
        ws["A4"] = "Data Collection Dates"
        ws["A5"] = "Observation Selection"
        ws["A6"] = "Target Variable Description"
        ws["A7"] = "Used ML Algorithm"
        ws["B1"] = "train set"
        ws["C1"] = "valid set"
        ws["D1"] = "test set"
        ws["E1"] = "Out-Of-Time set"

        for row in ws["B2":"E7"]:
            for cell in row:
                cell.style = "b_task_cell_format"
        for row in ws["A1":"E1"]:
            for cell in row:
                cell.style = "b_task_col_title_format"
        for row in ws["A2":"A7"]:
            for cell in row:
                cell.style = "b_task_row_title_format"

        for i in range(1, 6):
            ws.column_dimensions[get_column_letter(i)].width = 30
        for i in range(1, 8):
            ws.row_dimensions[i].height = 75

        # Hyperlink to the table of contents
        ws[f"A9"] = "<<< Return to Table of Contents"
        ws[f"A9"].hyperlink = f"#'Оглавление'!A1"
        ws[f"A9"].style = "Hyperlink"

    def _create_pipeline_description_page(self, **data):
        """
        Creates a page describing all stages of the pipeline.

        Args:
            **data: Arbitrary keyword arguments representing data to include in the pipeline description.
        """
        _stagies = [
            "Data Collection",
            "Splitting dataset into train/validation/test",
            "Missing value handling method",
            "Categorical feature processing method",
            "Feature selection method",
            "Built models",
            "Model hyperparameter optimization",
        ]
        _descriptions = [
            "<Attach the script for collecting the training dataset>",
            (
                "<In dreamml_base, by default, the split is done into 3 parts: "
                "train, valid, test. The split ratio is: 60%, 20%, 20%.>"
            ),
            (
                "<In dreamml_base, by default, missing values for categorical "
                "features are filled with 'NA'. For numerical features, "
                "missing values are not filled.>"
            ),
            (
                "<In dreamml_base, by default, categorical features are processed "
                "using an enhanced LabelEncoder, after which the features are passed "
                "to a model that can handle categories.>"
            ),
            (
                "<In dreamml_base, by default, the following feature selection chain is used: "
                "Tree importance -> PSI -> Permutation -> ShapUplift -> ShapDelta>"
            ),
            (
                "<In dreamml_base, by default, models such as LightGBM, XGBoost, CatBoost, "
                "WhiteBox AutoML are used.>"
            ),
            (
                "<In dreamml_base, by default, Bayesian Optimization is used for "
                "model hyperparameter optimization.>"
            ),
        ]
        stats = pd.DataFrame({"Stage Name": _stagies, "Description": _descriptions})

        stats.to_excel(self.writer, sheet_name="Pipeline Description", index=False)
        self.sheet_descriptions["Pipeline Description"] = "Page describing all pipeline stages"

        self.add_table_borders(stats, sheet_name="Pipeline Description")
        self.add_cell_width(sheet_name="Pipeline Description")
        self.add_header_color(stats, sheet_name="Pipeline Description", color="00CC99")
        self.add_numeric_format(
            stats[["Description"]], sheet_name="Pipeline Description", startcol=1
        )

        ws = self.sheets["Pipeline Description"]
        # Hyperlink to the table of contents
        ws[f"A{stats.shape[0] + 3}"] = "<<< Return to Table of Contents"
        ws[f"A{stats.shape[0] + 3}"].hyperlink = f"#'Оглавление'!A1"
        ws[f"A{stats.shape[0] + 3}"].style = "Hyperlink"


def create_used_features_stats(
    models: dict, vectorizers_dict: Optional[dict] = None, **eval_sets
):
    """
    Creates a DataFrame listing the features used by each model. If a feature is used in a model,
    it is marked with 1; otherwise, it is marked with 0.

    Args:
        models (dict): A dictionary of model instances.
        vectorizers_dict (Optional[dict], optional): A dictionary of vectorizer instances. Defaults to None.
        **eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]): 
            A dictionary containing evaluation sets. The key is the name of the set (e.g., train, valid),
            and the value is a tuple containing the feature matrix (data) and the target vector (target).

    Returns:
        pd.DataFrame or dict: 
            - If vectorizers_dict is provided, returns a dictionary where each key is the vectorizer name
              and the value is a DataFrame with feature usage flags.
            - If vectorizers_dict is not provided, returns a single DataFrame with feature usage flags.

    Raises:
        KeyError: If a model does not have a 'used_features' attribute.
    """
    if vectorizers_dict is not None:
        dfs_dict = {}

        for vec_name, vectorizer in vectorizers_dict.items():
            eval_set_cp = deepcopy(eval_sets)
            eval_set_cp = get_eval_set_with_embeddings(vectorizer, eval_set_cp)

            df = pd.DataFrame({"Variable": eval_set_cp["train"][0].columns.tolist()})

            for model_name, model in models.items():
                used_features = model.used_features
                vectorizer_name = f"{model.vectorization_name}_vectorizer"

                if vectorizer_name == vec_name:
                    df[f"{model_name} include variable"] = (
                        df["Variable"].isin(used_features).astype(int)
                    )
                    dfs_dict[vec_name] = df

        return dfs_dict

    else:
        df = pd.DataFrame({"Variable": eval_sets["train"][0].columns.tolist()})

        for model in models:
            used_features = models[model].used_features
            df[f"{model} include variable"] = (
                df["Variable"].isin(used_features).astype(int)
            )

        return df


def _create_business_task_description_page(self, **data):
    """
    Creates a page with a description of the business task.

    Args:
        **data: Arbitrary keyword arguments representing data to include in the business task description.
    """
    _logger.info("0. Collecting statistics about the business task.")
    bcd = BusinessCaseDescription(
        self.artifacts_config, self.validation_test_config
    )
    stats = bcd._create_description(**data)
    stats.to_excel(self.writer, sheet_name="Описание бизнес-задачи", index=False)
    self.sheet_descriptions["Описание бизнес-задачи"] = ""

    ws = self.writer.sheets["Описание бизнес-задачи"]

    b_task_cell_format = NamedStyle(name="b_task_cell_format")
    b_task_cell_format.font = Font(color="808080")
    b_task_cell_format.alignment = Alignment(
        wrap_text=True, horizontal="center", vertical="center"
    )
    brd = Side(border_style="thin", color="000000")
    b_task_cell_format.border = Border(left=brd, right=brd, top=brd, bottom=brd)

    self.wb.add_named_style(b_task_cell_format)

    b_task_row_title_format = NamedStyle(name="b_task_row_title_format")
    b_task_row_title_format.font = Font(bold=True)
    b_task_row_title_format.alignment = Alignment(
        horizontal="center", vertical="center"
    )
    brd = Side(border_style="thin", color="000000")
    b_task_row_title_format.border = Border(
        left=brd, right=brd, top=brd, bottom=brd
    )

    self.wb.add_named_style(b_task_row_title_format)

    b_task_col_title_format = NamedStyle(name="b_task_col_title_format")
    b_task_col_title_format.font = Font(bold=True)
    b_task_col_title_format.fill = PatternFill(
        start_color="00CC99", end_color="00CC99", fill_type="solid"
    )
    b_task_col_title_format.alignment = Alignment(
        horizontal="center", vertical="center"
    )
    brd = Side(border_style="thin", color="000000")
    b_task_col_title_format.border = Border(
        left=brd, right=brd, top=brd, bottom=brd
    )

    self.wb.add_named_style(b_task_col_title_format)

    business_task_text = (
        "<Enter the model name> \n"
        "for example: Rental rate prediction model for commercial real estate"
    )
    task_description_text = (
        "<Enter the model description: modeling goal, \n"
        "which business process the model is built for, what data is used> \n"
        "for example: Rental rate prediction model for commercial real estate. \n"
        "The model is built on data from the data center about the opening/closing of new bank branches."
    )
    report_dt_description_text = (
        "<Specify report dates> \n" "for example: 31.01.2022, 28.02.2022, 31.03.2022"
    )
    target_description_text = "<Enter the definition of the target event/variable>"
    data_selection_text = (
        "<Enter population selection criteria: filters, exclusions>\n"
        "for example: 1. Offices open on the report date."
    )
    used_algo_text = "<dreamml_base XGBRegressor>"
    ws.merge_cells("B2:E2")
    ws.merge_cells("B3:E3")
    ws.merge_cells("B4:D4")
    ws.merge_cells("B5:D5")
    ws.merge_cells("B6:E6")
    ws.merge_cells("B7:E7")

    ws["B2"] = business_task_text
    ws["B3"] = task_description_text
    ws["B4"] = report_dt_description_text
    ws["B5"] = data_selection_text
    ws["B6"] = target_description_text
    ws["B7"] = used_algo_text
    ws["E4"] = report_dt_description_text
    ws["E5"] = data_selection_text
    ws["A1"] = "Parameter"
    ws["A2"] = "Business Task"
    ws["A3"] = "Task Description"
    ws["A4"] = "Data Collection Dates"
    ws["A5"] = "Observation Selection"
    ws["A6"] = "Target Variable Description"
    ws["A7"] = "Used ML Algorithm"
    ws["B1"] = "train set"
    ws["C1"] = "valid set"
    ws["D1"] = "test set"
    ws["E1"] = "Out-Of-Time set"

    for row in ws["B2":"E7"]:
        for cell in row:
            cell.style = "b_task_cell_format"
    for row in ws["A1":"E1"]:
        for cell in row:
            cell.style = "b_task_col_title_format"
    for row in ws["A2":"A7"]:
        for cell in row:
            cell.style = "b_task_row_title_format"

    for i in range(1, 6):
        ws.column_dimensions[get_column_letter(i)].width = 30
    for i in range(1, 8):
        ws.row_dimensions[i].height = 75

    # Hyperlink to the table of contents
    ws[f"A9"] = "<<< Return to Table of Contents"
    ws[f"A9"].hyperlink = f"#'Оглавление'!A1"
    ws[f"A9"].style = "Hyperlink"

def _create_pipeline_description_page(self, **data):
    """
    Creates a page describing all stages of the pipeline.

    Args:
        **data: Arbitrary keyword arguments representing data to include in the pipeline description.
    """
    _stagies = [
        "Data Collection",
        "Splitting dataset into train/validation/test",
        "Missing value handling method",
        "Categorical feature processing method",
        "Feature selection method",
        "Built models",
        "Model hyperparameter optimization",
    ]
    _descriptions = [
        "<Attach the script for collecting the training dataset>",
        (
            "<In dreamml_base, by default, the split is done into 3 parts: "
            "train, valid, test. The split ratio is: 60%, 20%, 20%.>"
        ),
        (
            "<In dreamml_base, by default, missing values for categorical "
            "features are filled with 'NA'. For numerical features, "
            "missing values are not filled.>"
        ),
        (
            "<In dreamml_base, by default, categorical features are processed "
            "using an enhanced LabelEncoder, after which the features are passed "
            "to a model that can handle categories.>"
        ),
        (
            "<In dreamml_base, by default, the following feature selection chain is used: "
            "Tree importance -> PSI -> Permutation -> ShapUplift -> ShapDelta>"
        ),
        (
            "<In dreamml_base, by default, models such as LightGBM, XGBoost, CatBoost, "
            "WhiteBox AutoML are used.>"
        ),
        (
            "<In dreamml_base, by default, Bayesian Optimization is used for "
            "model hyperparameter optimization.>"
        ),
    ]
    stats = pd.DataFrame({"Stage Name": _stagies, "Description": _descriptions})

    stats.to_excel(self.writer, sheet_name="Pipeline Description", index=False)
    self.sheet_descriptions["Pipeline Description"] = "Page describing all pipeline stages"

    self.add_table_borders(stats, sheet_name="Pipeline Description")
    self.add_cell_width(sheet_name="Pipeline Description")
    self.add_header_color(stats, sheet_name="Pipeline Description", color="00CC99")
    self.add_numeric_format(
        stats[["Description"]], sheet_name="Pipeline Description", startcol=1
    )

    ws = self.sheets["Pipeline Description"]
    # Hyperlink to the table of contents
    ws[f"A{stats.shape[0] + 3}"] = "<<< Return to Table of Contents"
    ws[f"A{stats.shape[0] + 3}"].hyperlink = f"#'Оглавление'!A1"
    ws[f"A{stats.shape[0] + 3}"].style = "Hyperlink"