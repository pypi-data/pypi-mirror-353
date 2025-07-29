import pickle
from abc import abstractmethod

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import log_loss, mean_absolute_error, mean_squared_error

from dreamml.modeling.metrics.utils import calculate_quantile_bins
from dreamml.logging import get_logger
from dreamml.reports.calibration.base import BaseCalibrationReport

_logger = get_logger(__name__)


class BinaryCalibrationReport(BaseCalibrationReport):
    """
    Binary Calibration Report.

    This class implements the creation and saving of a model calibration report.

    Args:
        calibrators (dict): A dictionary with calibration names as keys and Calibration class objects as values.
            Dictionary containing all calibrations for which the report needs to be generated.
        config (dict): A dictionary containing configuration parameters.

    """

    def create_report(self, calibration_method_name, calibration_model, **eval_sets):
        """
        Creates calibration reports for each evaluation set and saves the calibration objects.

        Args:
            calibration_method_name (str): The name of the calibration method.
            calibration_model (Calibration): The calibration model.
            **eval_sets (dict): Keyword arguments representing the evaluation sets on which to perform calculations.
                Each key is the name of the dataset, and the value is a tuple (X, y).

        """
        for sample_name, (X, y) in eval_sets.items():
            pred_df = pd.DataFrame(
                {
                    "y_true": y,
                    "y_pred": calibration_model.get_y_pred(X),
                    "y_calib": calibration_model.transform(X),
                }
            )

            report = self.create_calib_stats(pred_df)
            self.reports[f"{calibration_method_name}_{sample_name}"] = report

            self.plot_calib_curves(
                pred_df,
                self.images_dir_path / f"{calibration_method_name}_{sample_name}.png",
            )

    def create_comparison(self, **eval_sets):
        """
        Creates a comparison of calibration metrics across different calibration methods and evaluation sets.

        Args:
            **eval_sets (dict): Keyword arguments representing the evaluation sets.
                Each key is the name of the dataset, and the value is a tuple (X, y).

        """
        # Format for printing in Excel
        float_percentage = "0.00%"
        float_number_low = "## ##0.00000"

        table_format = {
            "num_format": {
                float_number_low: [
                    "MAE_train",
                    "MAE_calibrated_train",
                    "MAE_valid",
                    "MAE_calibrated_valid",
                    "MAE_OOT",
                    "MAE_calibrated_OOT",
                    "Brier_train",
                    "Brier_calibrated_train",
                    "Brier_valid",
                    "Brier_calibrated_valid",
                    "Brier_OOT",
                    "Brier_calibrated_OOT",
                    "logloss_train",
                    "logloss_calibrated_train",
                    "logloss_valid",
                    "logloss_calibrated_valid",
                    "logloss_OOT",
                    "logloss_calibrated_OOT",
                ],
                float_percentage: [
                    "delta MAE_train",
                    "delta Brier_train",
                    "delta logloss_train",
                    "delta MAE_valid",
                    "delta Brier_valid",
                    "delta logloss_valid",
                    "delta MAE_OOT",
                    "delta Brier_OOT",
                    "delta logloss_OOT",
                ],
            }
        }

        plt.figure(figsize=(35, 30))
        summary = pd.DataFrame(index=list(self.calibrators.keys()))

        # Comparison table
        sample_names = list(eval_sets.keys())
        for calibration_method_name, calibrator in self.calibrators.items():

            # Weighted MAE
            for line_num, sample_name in enumerate(sample_names):
                report = self.reports[f"{calibration_method_name}_{sample_name}"]
                summary.loc[calibration_method_name, f"MAE_{sample_name}"] = report.loc[
                    "Total", "MAE"
                ]
                summary.loc[
                    calibration_method_name, f"MAE_calibrated_{sample_name}"
                ] = report.loc["Total", "MAE calibrated"]

            # Brier score = MSE for classification
            for sample_name in sample_names:
                report = self.reports[f"{calibration_method_name}_{sample_name}"]
                summary.loc[calibration_method_name, f"Brier_{sample_name}"] = (
                    report.loc["Total", "Brier"]
                )
                summary.loc[
                    calibration_method_name, f"Brier_calibrated_{sample_name}"
                ] = report.loc["Total", "Brier calibrated"]
            # Logloss

            for sample_name in sample_names:
                report = self.reports[f"{calibration_method_name}_{sample_name}"]
                summary.loc[calibration_method_name, f"logloss_{sample_name}"] = (
                    report.loc["Total", "logloss"]
                )
                summary.loc[
                    calibration_method_name, f"logloss_calibrated_{sample_name}"
                ] = report.loc["Total", "logloss calibrated"]

            for sample_name in sample_names:
                # Deltas
                # Delta MAE
                summary[f"delta MAE_{sample_name}"] = (
                    summary[f"MAE_calibrated_{sample_name}"]
                    - summary[f"MAE_{sample_name}"]
                )

                # Delta Brier
                summary[f"delta Brier_{sample_name}"] = (
                    summary[f"Brier_calibrated_{sample_name}"]
                    - summary[f"Brier_{sample_name}"]
                )

                # Delta logloss
                summary[f"delta logloss_{sample_name}"] = (
                    summary[f"logloss_calibrated_{sample_name}"]
                    - summary[f"logloss_{sample_name}"]
                )

        # Comparison plots
        plot_lines = len(eval_sets)
        subplot_pos = 1
        for sample_name, (x, y) in eval_sets.items():
            for calibration_method_name, calibrator in self.calibrators.items():
                # Add subplot
                plt.subplot(2 * plot_lines, 7, subplot_pos)
                pred_df = pd.DataFrame(
                    {
                        "y_true": y,
                        "y_pred": calibrator.get_y_pred(x),
                        "y_calib": calibrator.transform(x),
                    }
                )
                self.plot_calibration_curve(
                    pred_df, f"{calibration_method_name}_{sample_name}"
                )
                plt.subplot(2 * plot_lines, 7, subplot_pos + plot_lines * 7)
                self.plot_bin_curve(pred_df, f"{calibration_method_name}_{sample_name}")

                subplot_pos += 1

        # Save figure
        plt.savefig(
            self.images_dir_path / "calibration_comparison.png",
            bbox_inches="tight",
        )
        # Reset index
        summary.insert(loc=0, column="calibration", value=summary.index)
        desc = [
            "Linear regression on prediction bins",
            "Linear regression on probabilities in prediction bins",
            "Linear regression on log odds in prediction bins",
            "Logistic regression on all observations",
            "Logistic regression on prediction probabilities of observations",
            "Logistic regression on log odds of predictions of observations",
            "Isotonic regression",
        ]
        summary.insert(loc=1, column="description", value=desc)

        self._to_excel(
            summary,
            sheet_name="calibration_comparison",
            formats=table_format,
            plot=True,
        )

    def print_equations(self):
        """
        Logs the calibration equations for calibration methods that have an equation.

        Raises:
            AttributeError: If a calibration method does not have a 'get_equation' method.
        """
        for name, calibration in self.calibrators.items():
            if name in ["linear", "logit"]:
                _logger.info(f"{name}: {calibration.get_equation()}")

    def create_equations(self):
        """
        Creates an Excel sheet with the equations of the calibration methods that have equations.

        Returns:
            None
        """
        equations = pd.DataFrame(columns=["equation"])
        for name, calib in self.calibrators.items():
            if hasattr(calib, "get_equation"):
                equations.loc[name] = calib.get_equation()

        equations = equations.reset_index()
        self._to_excel(equations, "equations", None, False)

    def create_data_stats(self, **eval_sets):
        """
        Generates a report on the data used for training and validating the model.

        Args:
            **eval_sets (dict): Keyword arguments representing the evaluation sets.
                Each key is the name of the dataset, and the value is a tuple (X, y).

        """
        data_dict = {}
        for data_name, (x, y) in eval_sets.items():
            data_dict[data_name] = [x.shape[0], np.sum(y), np.mean(y)]
        data_stats = pd.DataFrame(data_dict).T
        data_stats = data_stats.reset_index()
        data_stats.columns = ["dataset", "# observations", "# events", "# event rate"]

        # Standard number formats
        int_number = "## ##0"
        float_percentage = "0.00%"
        table_format = {
            "num_format": {
                int_number: ["# observations", "# events"],
                float_percentage: ["# event rate"],
            }
        }
        self._to_excel(data_stats, "Data sets", table_format)

    @staticmethod
    def create_calib_stats(df: pd.DataFrame):
        """
        Generates a DataFrame containing calibration statistics for a specific evaluation set
        by binning the model predictions.

        Args:
            df (pd.DataFrame): A DataFrame with three columns:
                - y_pred (float): The model's prediction scores.
                - y_calib (float): The calibrated prediction scores.
                - y_true (int): The true binary outcomes.

        Returns:
            pd.DataFrame: A DataFrame containing calibration statistics segmented by prediction bins.
                Columns include:
                    - bin (int): The bin number.
                    - mean proba (float): The average model prediction within the bin.
                    - calibration proba (float): The average calibrated prediction within the bin.
                    - event rate (float): The proportion of positive events within the bin.
                    - # obs (int): The number of observations within the bin.
                    - MAE (float): The weighted mean absolute error for model predictions within the bin.
                    - MAE calibrated (float): The weighted mean absolute error for calibrated predictions within the bin.
                    - Brier (float): The Brier score (MSE) for model predictions across all observations.
                    - Brier calibrated (float): The Brier score (MSE) for calibrated predictions across all observations.
                    - logloss (float): The log loss for model predictions across all observations.
                    - logloss calibrated (float): The log loss for calibrated predictions across all observations.
        """
        # Assign bins based on prediction quantiles
        df["bin"] = calculate_quantile_bins(df["y_pred"], n_bins=21)

        # Group by bin and calculate statistics
        df_group = df.groupby(by="bin")
        stats = df_group.agg(
            {"y_pred": ["mean"], "y_calib": ["mean"], "y_true": ["mean", "count"]}
        )

        stats.columns = ["mean proba", "calibration proba", "event rate", "# obs"]

        # Metrics:

        # Expected calibration error = weighted mean absolute error
        mae = mean_absolute_error(
            stats["event rate"], stats["mean proba"], sample_weight=stats["# obs"]
        )
        mae_calib = mean_absolute_error(
            stats["event rate"],
            stats["calibration proba"],
            sample_weight=stats["# obs"],
        )
        stats.loc["Total", "MAE"] = mae
        stats.loc["Total", "MAE calibrated"] = mae_calib

        # Mean square error = Brier score
        stats.loc["Total", "Brier"] = mean_squared_error(df["y_true"], df["y_pred"])
        stats.loc["Total", "Brier calibrated"] = mean_squared_error(
            df["y_true"], df["y_calib"]
        )

        # Logloss
        stats.loc["Total", "logloss"] = log_loss(df["y_true"], df["y_pred"], eps=1e-5)
        stats.loc["Total", "logloss calibrated"] = log_loss(
            df["y_true"], df["y_calib"], eps=1e-5
        )

        # Total row
        stats.loc["Total", "mean proba"] = df["y_pred"].mean()
        stats.loc["Total", "calibration proba"] = df["y_calib"].mean()
        stats.loc["Total", "event rate"] = df["y_true"].mean()
        stats.loc["Total", "# obs"] = stats["# obs"].sum()

        stats.insert(loc=0, column="bin", value=stats.index)

        return stats.fillna(".")
    
    @abstractmethod
    def transform(self, **eval_sets):
        """
        Executes the calibration process by creating data statistics, generating reports for each calibration method,
        saving calibrated models, creating comparison tables, generating calibration equations,
        printing reports, and saving the Excel writer.

        Args:
            **eval_sets (dict): Keyword arguments representing the evaluation sets.
                Each key is the name of the dataset, and the value is a tuple (X, y).

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        self.create_data_stats(**eval_sets)

        for method_name, calibration_model in self.calibrators.items():
            self.create_report(method_name, calibration_model, **eval_sets)
            self._save_calibrated_model(method_name, calibration_model)

        self.create_comparison(**eval_sets)
        self.create_equations()
        self.print_reports(**eval_sets)
        self.writer.save()