import os
from abc import abstractmethod
from pathlib import Path
from typing import Optional, Tuple
from copy import deepcopy
import pickle

import pandas as pd
import matplotlib.pyplot as plt

from dreamml.reports.calibration.format_excel_writer import FormatExcelWriter
from dreamml.modeling.metrics.utils import calculate_quantile_bins
from dreamml.logging import get_logger
from dreamml.utils.get_last_experiment_directory import get_experiment_dir_path

_logger = get_logger(__name__)


class BaseCalibrationReport:
    """Base class for creating and saving model calibration reports.

    This class handles the initialization of calibration reports, including setting up directories,
    writing data to Excel, plotting calibration curves, and saving calibrated models.

    Attributes:
        calibrators (dict): A deep copy of the calibration methods provided.
        reports (dict): A dictionary to store generated reports.
        target_name (str, optional): The name of the target variable.
        model_id (str): The identifier for the model.
        model_name (str): The name of the model derived from the model path or config.
        current_path (Path): The current directory path for saving reports and models.
        images_dir_path (Path): Directory path for saving images.
        docs_dir_path (Path): Directory path for saving documentation.
        models_dir_path (Path): Directory path for saving calibrated models.
        writer (pd.ExcelWriter): Excel writer object for writing reports.
    """

    def __init__(self, calibrations: dict, config: dict):
        """Initializes the BaseCalibrationReport with calibrations and configuration.

        Args:
            calibrations (dict): A dictionary of calibration methods with their names as keys.
            config (dict): A dictionary containing configuration parameters.

        """
        self.calibrators = deepcopy(calibrations)
        self.reports = {}

        self.target_name = config.get("target_name", None)
        (
            self.target_name.lower()
            if isinstance(self.target_name, str)
            else self.target_name
        )
        self.model_id = config.get("model_id", "model_id").lower()

        if config.get("model_path"):
            model_path = Path(config["model_path"])
            self.model_name = model_path.stem
            self.current_path = model_path.parent / "calibration"
        else:
            self.model_name = config["model_name"]
            self.current_path = Path(
                get_experiment_dir_path(
                    config["results_path"],
                    experiment_dir_name=config.get("dir_name"),
                    use_last_experiment_directory=config.get(
                        "use_last_experiment_directory", False
                    ),
                )
            )

        self.images_dir_path = self.current_path / "images"
        self.docs_dir_path = self.current_path / "docs"
        self.models_dir_path = self.current_path / "models"

        os.makedirs(self.current_path, exist_ok=True)
        os.makedirs(self.images_dir_path, exist_ok=True)
        os.makedirs(self.docs_dir_path, exist_ok=True)
        os.makedirs(self.models_dir_path, exist_ok=True)

        self.writer = pd.ExcelWriter(
            path=self.current_path
            / "docs"
            / f"calibration_report_{self.model_name}.xlsx"
        )

    def _to_excel(
        self,
        df: pd.DataFrame,
        sheet_name: str,
        formats: dict = None,
        plot: bool = False,
        pos: Tuple = (0, 0),
        path_to_image: str = None,
    ):
        """Writes a DataFrame to an Excel sheet with optional formatting and plot insertion.

        Args:
            df (pd.DataFrame): The DataFrame to write to the Excel sheet.
            sheet_name (str): The name of the sheet where the DataFrame will be written.
            formats (dict, optional): A dictionary specifying column formats.
            plot (bool, optional): If True, inserts a plot image into the sheet.
            pos (Tuple, optional): The top-left position (row, column) to start writing the DataFrame.
            path_to_image (str, optional): The path to the image to insert. If None, uses the sheet name.

        Raises:
            KeyError: If the specified sheet name does not exist in the Excel writer.

        """
        # write table
        format_writer = FormatExcelWriter(self.writer)
        format_writer.write_data_frame(
            df=df, pos=pos, sheet=sheet_name, formats=formats
        )

        # insert plot
        if plot:
            sheet = self.writer.sheets[sheet_name]

            if path_to_image is not None:
                save_path = self.current_path / "images" / f"{path_to_image}.png"
                sheet.insert_image(f"P{pos[0]+1}", save_path)
            else:
                save_path = self.current_path / "images" / f"{sheet_name}.png"
                sheet.insert_image(f"A{df.shape[0] + 4}", save_path)

    def plot_calib_curves(
        self, df: pd.DataFrame, save_path: Optional[os.PathLike] = None
    ):
        """Plots and saves calibration and bin curves based on the provided DataFrame.

        This method generates two subplots:
            1. Calibration curve.
            2. Bin curve.

        Args:
            df (pd.DataFrame): The DataFrame containing calibration data. Must include:
                - y_pred: Model predictions.
                - y_calib: Calibrated predictions.
                - y_true: True target values.
            save_path (os.PathLike, optional): The file path to save the plotted image.

        Raises:
            KeyError: If required columns are missing from the DataFrame.

        """
        plt.figure(figsize=(24, 6), dpi=80.0)
        plt.subplot(1, 2, 1)
        self.plot_bin_curve(df)
        plt.subplot(1, 2, 2)
        self.plot_calibration_curve(df)
        if save_path is not None:
            plt.savefig(save_path, bbox_inches="tight")

    def print_reports(self, **eval_sets):
        """Generates and writes calibration reports for each calibration method and dataset.

        This method iterates over all calibrators and evaluation sets, generating
        reports and writing them to the Excel workbook.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.
                Each key should be the dataset name, and the value should be the dataset itself.

        Raises:
            KeyError: If report data for a calibration method and dataset combination is missing.

        """
        int_number = "## ##0"
        float_number_high = "## ##0.00"
        float_number_low = "## ##0.00000"

        # Custom format for the table
        table_format = {
            "num_format": {
                int_number: ["bin", "#obs"],
                float_number_high: ["mean proba", "calibration proba", "event rate"],
                float_number_low: [
                    "MAE",
                    "MAE calibrated",
                    "Brier",
                    "Brier calibrated",
                    "logloss",
                    "logloss calibrated",
                ],
            }
        }

        for calib_name in self.calibrators.keys():
            for ds_name in eval_sets.keys():
                report = self.reports.get(f"{calib_name}_{ds_name}")
                if report is not None:
                    self._to_excel(report, f"{calib_name}_{ds_name}", table_format, True)
                else:
                    _logger.warning(
                        f"Report for calibration '{calib_name}' and dataset '{ds_name}' is missing."
                    )

    def create_comparison(self, **eval_sets):
        """Creates comparison reports across different calibration methods and datasets.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.
                Each key should be the dataset name, and the value should be the dataset itself.

        """
        pass

    def print_equations(self):
        """Logs the calibration equations for applicable calibration methods.

        Only calibration methods that have a 'get_equation' method will have their equations logged.

        """
        for name, calibration in self.calibrators.items():
            if name in ["linear", "logit"]:
                _logger.info(f"{name}: {calibration.get_equation()}")

    def create_equations(self):
        """Creates an Excel sheet containing the equations of calibration methods.

        This method collects equations from calibration methods that provide a 'get_equation' method
        and writes them to an Excel sheet named "equations".

        """
        equations = pd.DataFrame(columns=["equation"])
        for name, calib in self.calibrators.items():
            if hasattr(calib, "get_equation"):
                equations.loc[name] = calib.get_equation()

        equations = equations.reset_index()
        self._to_excel(equations, "equations", None, False)

    def create_data_stats(self, **eval_sets):
        """Generates a report on the data used for training and validating the model.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.
                Each key should be the dataset name, and the value should be a tuple containing:
                    - X (pd.DataFrame): Feature matrix.
                    - y (pd.Series): True target values.

        """
        pass

    @staticmethod
    def create_calib_stats(df: pd.DataFrame):
        """Generates calibration statistics for a specific dataset across prediction bins.

        This function calculates various statistics related to model calibration for each prediction bin.

        Args:
            df (pd.DataFrame): DataFrame containing at least the following columns:
                - y_pred: Model predictions.
                - y_calib: Calibrated predictions.
                - y_true: True target values.

        Returns:
            pd.DataFrame: A DataFrame containing calibration statistics per prediction bin with the following columns:
                - bin: Bin number.
                - mean proba: Mean model prediction in the bin.
                - calibration proba: Mean calibrated prediction in the bin.
                - event rate: Proportion of target events in the bin.
                - # obs: Number of observations in the bin.
                - MAE: Weighted mean absolute error of model predictions in the bin.
                - MAE calibrated: Weighted mean absolute error of calibrated predictions in the bin.
                - Brier: Mean squared error of model predictions across all observations.
                - Brier calibrated: Mean squared error of calibrated predictions across all observations.
                - logloss: Logarithmic loss of model predictions across all observations.
                - logloss calibrated: Logarithmic loss of calibrated predictions across all observations.

        """
        pass

    @staticmethod
    def plot_calibration_curve(pred_df: pd.DataFrame, title: str = None):
        """Plots the calibration curve to assess the need for calibration.

        This plot shows the relationship between mean predictions (both original and calibrated)
        and the mean true target values across prediction bins.

        Args:
            pred_df (pd.DataFrame): DataFrame containing at least the following columns:
                - y_pred: Model predictions.
                - y_calib: Calibrated predictions.
                - y_true: True target values.
            title (str, optional): The title of the plot.

        Raises:
            KeyError: If required columns are missing from the DataFrame.

        """
        # Bin the predictions
        pred_df["bin"] = calculate_quantile_bins(pred_df["y_pred"], 21)

        pred_df_grouped = pred_df.groupby(by="bin").mean()

        plt.plot(
            pred_df_grouped["y_pred"],
            pred_df_grouped["y_true"],
            marker="o",
            label="model",
            linewidth=3,
        )
        plt.plot(
            pred_df_grouped["y_calib"],
            pred_df_grouped["y_true"],
            marker="o",
            label="model calibrated",
            linewidth=4,
        )
        xlim = ylim = pred_df_grouped["y_true"].max()
        plt.plot([0, xlim], [0, ylim], "k--")
        plt.grid()
        plt.xlabel("mean prediction")
        plt.ylabel("mean target")
        plt.legend()
        if title is not None:
            plt.title(title)

    @staticmethod
    def plot_bin_curve(pred_df: pd.DataFrame, title: str = None):
        """Plots the mean predictions and event rates across prediction bins.

        This plot includes:
            - Bin vs. event rate.
            - Bin vs. mean model prediction.
            - Bin vs. mean calibrated prediction.

        Args:
            pred_df (pd.DataFrame): DataFrame containing at least the following columns:
                - y_pred: Model predictions.
                - y_calib: Calibrated predictions.
                - y_true: True target values.
            title (str, optional): The title of the plot.

        Raises:
            KeyError: If required columns are missing from the DataFrame.

        """
        # Bin the predictions
        pred_df["bin"] = calculate_quantile_bins(pred_df["y_pred"], 21)

        pred_df_grouped = pred_df.groupby(by="bin").mean()

        plt.plot(
            pred_df_grouped["y_true"], "green", marker="o", label="y_true", linewidth=3
        )
        plt.plot(pred_df_grouped["y_pred"], marker="o", label="y_pred", linewidth=3)
        plt.plot(
            pred_df_grouped["y_calib"], marker="o", label="y_calibrated", linewidth=4
        )
        plt.grid()
        plt.xlabel("bin")
        plt.ylabel("mean prediction")
        plt.legend()
        if title is not None:
            plt.title(title)

    @abstractmethod
    def transform(self, **eval_sets):
        """Transforms the evaluation datasets using the calibration methods.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.
                Each key should be the dataset name, and the value should be the dataset to transform.
        """
        pass

    @abstractmethod
    def create_report(self, calibration_method_name, calibration_model, **eval_sets):
        """Creates calibration reports for each evaluation dataset and saves calibration models.

        This method processes each evaluation dataset with the specified calibration model,
        generates reports, and saves the calibrated models.

        Args:
            calibration_method_name (str): The name of the calibration method.
            calibration_model (Calibration): The calibration model object.
            **eval_sets: Arbitrary keyword arguments representing evaluation datasets.
                Each key should be the dataset name, and the value should be a tuple containing:
                    - X (pd.DataFrame): Feature matrix.
                    - y (pd.Series): True target values.

        Raises:
            ValueError: If calibration_method_name or calibration_model is invalid.

        """
        pass

    def _save_calibrated_model(self, calibration_method_name, calibration_model):
        """Saves the calibrated model to a pickle file.

        Args:
            calibration_method_name (str): The name of the calibration method.
            calibration_model (Calibration): The calibrated model to save.

        Raises:
            IOError: If the file cannot be written.

        """
        with open(
            self.models_dir_path
            / f"calibrated_{self.model_name}_{calibration_method_name}.pkl",
            "wb",
        ) as f:
            pickle.dump(calibration_model, f)