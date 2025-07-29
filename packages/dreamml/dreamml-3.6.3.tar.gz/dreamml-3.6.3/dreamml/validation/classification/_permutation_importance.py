import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xgboost
from tqdm.auto import tqdm
from sklearn.model_selection import train_test_split

from dreamml.logging import get_logger
from dreamml.modeling.metrics import BaseMetric
from dreamml.utils._time import execution_time
from dreamml.reports.calibration.format_excel_writer import FormatExcelWriter
from dreamml.modeling.metrics.metrics_mapping import metrics_mapping

_logger = get_logger(__name__)


def _to_frame(X: pd.DataFrame, values: np.array, prefix: str) -> pd.DataFrame:
    """
    Creates a DataFrame with ranked feature importance values.

    Args:
        X (pd.DataFrame): The feature matrix.
        values (np.array): The array of feature importance scores.
        prefix (str): The prefix for the importance column.

    Returns:
        pd.DataFrame: A DataFrame containing features and their ranked importance.
    
    Raises:
        None
    """
    df = pd.DataFrame({"feature": X.columns, f"{prefix}_importance": values})
    df = df.sort_values(by=f"{prefix}_importance", ascending=False)
    df = df.reset_index(drop=True)
    return df


def make_prediction(model_info: tuple, X: pd.DataFrame, task: str = "binary"):
    """
    Generates predictions using the provided model and feature matrix.

    Args:
        model_info (tuple): A tuple where the first element is the trained model instance,
                            and the second element is the list of features used by the model.
        X (pd.DataFrame): The feature matrix.
        task (str, optional): The type of task, either "binary" or other supported types. Defaults to "binary".

    Returns:
        np.ndarray or pd.Series: The predicted values.

    Raises:
        AttributeError: If the estimator does not have `predict`, `predict_proba`, or `transform` methods.
    """
    estimator, features = model_info
    data = X[features]
    if isinstance(estimator, xgboost.core.Booster):
        # FIXME: old xgboost
        data = xgboost.DMatrix(data)
    if getattr(estimator, "transform", None):
        y_pred = estimator.transform(data)
    elif getattr(estimator, "predict_proba", None):
        if str(type(estimator)).endswith("RandomForestClassifier'>"):
            y_pred = estimator.predict_proba(data).fillna(-9999)[:, 1]
        else:
            y_pred = estimator.predict_proba(data)
            if task == "binary":
                y_pred = y_pred[:, 1]
    elif getattr(estimator, "predict", None):
        y_pred = estimator.predict(data)
    else:
        raise AttributeError(
            "Estimator must have `predict`, `predict_proba` or `transform` method"
        )
    return y_pred


def calculate_permutation_feature_importance(
    estimator,
    metric,
    y: pd.Series,
    X: pd.DataFrame,
    fraction_sample: float = 0.15,
    task: str = "binary",
) -> pd.DataFrame:
    """
    Calculates permutation feature importance based on the change in the evaluation metric
    when feature values are randomly shuffled.

    Args:
        estimator: The trained model instance supporting sklearn API.
        metric (function): The metric function to evaluate model performance.
        y (pd.Series): The true target values.
        X (pd.DataFrame): The feature matrix.
        fraction_sample (float, optional): The fraction of samples to use for evaluation. Must be between 0 and 1. Defaults to 0.15.
        task (str, optional): The type of task, either "binary" or other supported types. Defaults to "binary".

    Returns:
        pd.DataFrame: A DataFrame containing features and their permutation importance scores.

    Raises:
        ValueError: If `fraction_sample` is not in the range (0, 1].
        TypeError: If `X` is not a pandas DataFrame.
    """
    if fraction_sample > 1:
        raise ValueError(
            f"fraction_sample must be in range (0, 1], "
            f"but fraction_sample is {fraction_sample}"
        )
    if isinstance(X, pd.DataFrame):
        x = X.copy()
        x, _, y, _ = train_test_split(x, y, train_size=fraction_sample, random_state=1)
    else:
        raise TypeError(
            f"x_valid must be pandas.core.DataFrame, " f"but x_valid is {type(X)}"
        )
    feature_importance = np.zeros(x.shape[1])
    baseline_prediction = make_prediction(
        (estimator, x.columns),
        x,
        task,
    )

    baseline_score = metric(y, baseline_prediction)
    for num, feature in enumerate(tqdm(x.columns)):
        x[feature] = np.random.permutation(x[feature])
        score = metric(y, make_prediction((estimator, x.columns), x, task))
        feature_importance[num] = score
        x[feature] = X[feature]
    feature_importance = (baseline_score - feature_importance) / baseline_score  # * 100
    return _to_frame(x, feature_importance, "permutation")


def plot_permutation_importance(
    df: pd.DataFrame, x_column: str, save_path: str
) -> None:
    """
    Plots the permutation feature importance and saves the figure.

    Args:
        df (pd.DataFrame): DataFrame containing features and their permutation importance scores.
        x_column (str): The name of the column to plot on the X-axis.
        save_path (str): The file path to save the plot.

    Returns:
        None

    Raises:
        None
    """
    plt.figure(figsize=(10, 6))
    plt.grid()
    n = len(df.columns) - 1
    color = iter(plt.cm.rainbow(np.linspace(0, 1, n)))
    leg = []
    for col in df.drop(x_column, axis=1).columns:
        c = next(color)
        plt.plot(df[x_column], df[col], c=c, linewidth=3, marker="o", markersize=12)
        leg.append(col)
    plt.legend(leg)
    plt.xticks(df[x_column], rotation="vertical")
    plt.xlabel(x_column)
    plt.ylabel("permutation_importance")
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")


from abc import ABC, abstractmethod


class Checker(ABC):
    """
    Abstract base class for implementing validation checks.
    """

    def __init__(self):
        """
        Initializes the abstract Checker class.
        """
        pass

    @abstractmethod
    def validate(self):
        """
        Abstract method to execute the validation procedure.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        pass


class PermutationImportanceChecker(Checker):
    """
    Implements permutation feature importance validation.

    Calculates the relative change in the specified metric when feature values are randomly shuffled.
    The validation is performed for each feature used in the model.

    Args:
        writer (pd.ExcelWriter): Excel writer object for report generation. The report file should be created beforehand.
        model: The trained model instance following the scikit-learn API.
        features_list (list): List of features used by the model.
        cat_features (list): List of categorical features.
        plot_size (tuple, optional): Size of the plot. Defaults to (10, 10).
        current_path (str, optional): Path to the working directory for saving images and the report file.
        images_dir_path (str, optional): Directory path to save images.
        metric_name (str, optional): Name of the metric to use. Defaults to "gini".
        metric_col_name (str, optional): Column name for the metric. Defaults to "gini".
        metric_params (dict, optional): Additional parameters for the metric function. Defaults to None.
        task (str, optional): Type of task, either "binary" or other supported types. Defaults to "binary".

    Attributes:
        writer (pd.ExcelWriter): Excel writer for report.
        model: Trained model.
        features_list (list): List of model features.
        cat_features (list): List of categorical features.
        metric_name (str): Name of the evaluation metric.
        metric (BaseMetric): Instance of the evaluation metric.
        metric_params (dict): Parameters for the metric.
        plot_size (tuple): Size of the plot.
        images_dir_path (str): Path to save images.
        current_path (str): Current working directory path.
        task (str): Type of task.
    """

    def __init__(
        self,
        writer: pd.ExcelWriter,
        model,
        features_list: list,
        cat_features: list,
        plot_size=(10, 10),
        current_path=None,
        images_dir_path=None,
        metric_name: str = "gini",
        metric_col_name: str = "gini",
        metric_params: dict = None,
        task: str = "binary",
    ):
        self.writer = writer
        self.features_list = features_list
        self.cat_features = cat_features
        self.model = model
        self.metric_name = metric_name
        self.metric: BaseMetric = metrics_mapping.get(metric_name)(
            task=task, **metric_params
        )
        self.metric_params = metric_params
        self.plot_size = plot_size
        self.images_dir_path = images_dir_path
        self.current_path = current_path
        self.task = task

    def _to_excel(self, df: pd.DataFrame, sheet_name: str, plot=False) -> None:
        """
        Writes the DataFrame to an Excel file on the specified sheet and position.

        Args:
            df (pd.DataFrame): The DataFrame to write to the Excel file.
            sheet_name (str): The name of the sheet where the data will be written.
            plot (bool, optional): Flag indicating whether to include a plot in the report. Defaults to False.

        Returns:
            None

        Raises:
            None
        """
        float_number_low = "## ##0.0000"
        # Custom format for the table
        fmt = {
            "num_format": {
                float_number_low: [
                    "permutation_importance_test",
                    "permutation_importance_valid",
                    "permutation_importance_OOT",
                ]
            }
        }
        bold_row = {"bold": {True: df.index[df["feature"] == "factors_relevancy"]}}
        excelWriter = FormatExcelWriter(self.writer)
        excelWriter.write_data_frame(
            df, (0, 0), sheet=sheet_name, formats=fmt, row_formats=bold_row
        )
        # Apply conditional format to highlight validation_report test results
        for col in [
            "permutation_importance_test",
            "permutation_importance_valid",
            "permutation_importance_OOT",
        ]:
            if col in df.columns:
                excelWriter.set_col_cond_format_tail(
                    df, (0, 0), col, lower=200, upper=0.0, order="reverse"
                )

        if plot:
            # Permutation importance plot
            sheet = self.writer.sheets[sheet_name]
            file_path = os.path.join(self.images_dir_path, f"{sheet_name}.png")
            sheet.insert_image(f"A{df.shape[0] + 4}", file_path)
        # Test description
        sheet.write_string(
            "E2",
            "Permutation importance - the metric of feature importance in the built model",
        )
        sheet.write_string(
            "E3",
            "Calculated as the relative change in the model performance metric ("
            + self.metric_name
            + ") when the feature values are shuffled randomly",
        )
        sheet.write_string(
            "E5",
            "Factors relevancy - the proportion of factors with "
            "importance of 20% or more relative to the factor with the highest importance",
        )
        sheet.write_string("E7", "* - this test is informative")

    def _calc_perm_importance(self, **data) -> pd.DataFrame:
        """
        Calculates the permutation importance for features used in the model across different datasets.

        Args:
            **data (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                A dictionary where each key is the name of a dataset, and the value is a tuple containing the feature matrix X and target vector y.

        Returns:
            pd.DataFrame: A DataFrame with the calculated permutation importance for each feature across datasets.

        Raises:
            None
        """
        X_test, y_test = data.get("test", (None, None))
        X_valid, y_valid = data.get("valid", (None, None))
        X_test2, y_test2 = data.get("test2", (None, None))
        X_OOT, y_OOT = data.get("OOT", (None, None))
        perm_importance_final = pd.DataFrame()
        # Calculate PI on test or valid
        if X_test is not None:
            perm_importance_final = calculate_permutation_feature_importance(
                self.model,
                self.metric,
                X=X_test[self.features_list],
                y=y_test,
                fraction_sample=0.95,
                task=self.task,
            )
            perm_importance_final.rename(
                columns={"permutation_importance": "permutation_importance_test"},
                inplace=True,
            )
            perm_importance_final.set_index("feature", inplace=True)
        elif X_valid is not None:
            perm_importance_final = calculate_permutation_feature_importance(
                self.model,
                self.metric,
                X=X_valid[self.features_list],
                y=y_valid,
                fraction_sample=0.95,
                task=self.task,
            )
            perm_importance_final.rename(
                columns={"permutation_importance": "permutation_importance_valid"},
                inplace=True,
            )
            perm_importance_final.set_index("feature", inplace=True)
        # Calculate PI on OOT if available
        if X_OOT is not None:
            perm_importance = calculate_permutation_feature_importance(
                self.model,
                self.metric,
                X=X_OOT[self.features_list],
                y=y_OOT,
                fraction_sample=0.95,
                task=self.task,
            )
            perm_importance.rename(
                columns={"permutation_importance": "permutation_importance_OOT"},
                inplace=True,
            )
            perm_importance.set_index("feature", inplace=True)
            perm_importance_final = pd.concat(
                [perm_importance_final, perm_importance], axis=1
            )
        # Calculate PI on test2 if available
        if X_test2 is not None:
            perm_importance = calculate_permutation_feature_importance(
                self.model,
                self.metric,
                X=X_test2[self.features_list],
                y=y_test2,
                fraction_sample=0.95,
                task=self.task,
            )
            perm_importance.rename(
                columns={"permutation_importance": "permutation_importance_test2"},
                inplace=True,
            )
            perm_importance.set_index("feature", inplace=True)
            perm_importance_final = pd.concat(
                [perm_importance_final, perm_importance], axis=1
            )
        return perm_importance_final

    @execution_time
    def validate(self, **data) -> pd.DataFrame:
        """
        Executes the permutation feature importance validation procedure.

        Adds a 'factors_relevancy' metric to the final dataset, representing the proportion
        of features with importance at least 20% of the most important feature.
        Generates and saves a permutation importance plot.
        Writes the validation results to the "Permutation importance" sheet in the Excel report.

        Args:
            **data (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                A dictionary where each key is the name of a dataset, and the value is a tuple containing the feature matrix X and target vector y.

        Returns:
            pd.DataFrame: The final DataFrame with calculated permutation importance and factors relevancy.

        Raises:
            None
        """
        _logger.info("Calculating permutation importance...")
        PI = self._calc_perm_importance(**data)
        psi = []
        cols = []
        for col in PI.columns:
            PI_share = 100 * PI[col] / PI[col].max()
            psi.append(100 * ((PI_share > 20).sum()) / PI_share.count())
            cols.append(col)
        psi_df = pd.DataFrame(data=[psi], columns=cols, index=["factors_relevancy"])
        # Save plot:
        # Sort by relative change
        PI = PI.sort_values(by=PI.columns[0], ascending=False)
        PI_plot = PI.reset_index()
        PI_plot.rename(columns={"index": "feature"}, inplace=True)

        # Permutation importance plot
        sheet_name = "Permutation importance"
        save_path = os.path.join(self.images_dir_path, f"{sheet_name}.png")
        plot_permutation_importance(PI_plot, x_column="feature", save_path=save_path)

        # Add factors relevancy to the table
        PI = PI.append(psi_df)
        PI.reset_index(inplace=True)
        PI.rename(columns={"index": "feature"}, inplace=True)
        # self._to_excel(PI, sheet_name, plot=True)

        return PI