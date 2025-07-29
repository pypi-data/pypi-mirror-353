"""
Module for implementing functions to plot various graphs.

Available entities:
- plot_roc_curve: Plotting the ROC curve.
- plot_precision_recall_curve: Plotting the Precision-Recall curve.
- plot_mean_pred_and_target: Plotting the mean prediction and target curves within bins.
- plot_binary_graph: Plotting all binary classification curves on a single canvas.
- plot_scatter: Plotting scatter plot of true vs predicted values.
- plot_model_quality_per_segment_graph: Plotting model quality per segment.
- plot_quality_dynamics_per_segment_graph: Plotting quality dynamics per segment over time.
- plot_data_decile_statistics_graph: Plotting decile statistics of the data.
- plot_regression_graph: Plotting graphs for regression tasks.
- plot_STL: Plotting STL decomposition.
- plot_multi_graph: Plotting graphs for multi-class classification.
- plot_token_length_distribution_for_text_features: Plotting token length distribution for text features.
- _plot_hist_anomaly_detection: Plotting histogram for anomaly detection.
- _plot_training_progress: Plotting training progress.
- plot_hist_loss_amts_ad: Plotting histogram of loss for AMTS anomaly detection.
- plot_scatter_mark_amts_ad: Plotting scatter plot with anomaly markers for AMTS anomaly detection.
"""

from collections import defaultdict

import numpy as np
import pandas as pd
from typing import Dict, List

from nltk import word_tokenize
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import average_precision_score, precision_recall_curve
import matplotlib.pyplot as plt
import seaborn as sns

from dreamml.logging import get_logger
from dreamml.modeling.metrics.metrics_mapping import metrics_mapping
from dreamml.modeling.metrics.utils import calculate_quantile_bins

_logger = get_logger(__name__)


def plot_roc_curve(y_true, y_pred):
    """
    Plot the Receiver Operating Characteristic (ROC) curve.

    Args:
        y_true (array-like): True binary labels, shape = [n_samples].
        y_pred (array-like): Predicted scores or probabilities, shape = [n_samples].

    Returns:
        None

    Raises:
        KeyError: If "gini" metric is not found in metrics_mapping.
    """
    plt.title("ROC Curve", size=13)
    fpr, tpr, _ = roc_curve(y_true, y_pred)
    gini = metrics_mapping["gini"](task="binary")(y_true, y_pred)
    label = "GINI: {:.4f}".format(gini)

    plt.plot(fpr, tpr, linewidth=3, label=label, color="#534275")
    plt.plot([0, 1], [0, 1], linestyle="--", color="black", alpha=0.25)
    plt.legend(loc="best", fontsize=13)
    plt.xlabel("False Positive Rate (Sensitivity)", size=13)
    plt.ylabel("True Positive Rate (1 - Specificity)", size=13)
    plt.xlim(0, 1)
    plt.ylim(0, 1)


def plot_precision_recall_curve(y_true, y_pred):
    """
    Plot the Precision-Recall (PR) curve.

    Args:
        y_true (array-like): True binary labels, shape = [n_samples].
        y_pred (array-like): Predicted scores or probabilities, shape = [n_samples].

    Returns:
        None

    Raises:
        None
    """
    plt.title("Precision-Recall Curve", size=13)
    precision, recall, _ = precision_recall_curve(y_true, y_pred)
    pr_auc = average_precision_score(y_true, y_pred)

    plt.plot(
        recall,
        precision,
        color="#534275",
        linewidth=3,
        label="PR-AUC:{:.4f}".format(pr_auc),
    )
    plt.axhline(np.mean(y_true), color="black", alpha=0.5, linestyle="--")
    plt.legend(loc="best", fontsize=13)
    plt.ylabel("Precision", size=13)
    plt.xlabel("Recall", size=13)
    plt.xlim(0, 1)
    plt.ylim(0, 1)


def plot_mean_prediction_in_bin(y_true, y_pred, n_bins: int = 20):
    """
    Plot the relationship between the mean prediction and the mean target value within each bin.

    Args:
        y_true (array-like): True target values, shape = [n_samples].
        y_pred (array-like): Predicted scores or probabilities, shape = [n_samples].
        n_bins (int, optional): Number of quantile bins. Defaults to 20.

    Returns:
        None

    Raises:
        None
    """
    y_pred_mean, y_true_mean, bins = mean_by_bin(n_bins, y_pred, y_true)
    plt.plot(y_pred_mean.values, linewidth=3, color="#534275", label="y-pred")
    plt.plot(y_true_mean.values, linewidth=3, color="#427553", label="y-true")
    plt.xticks(ticks=range(n_bins), labels=range(0, n_bins, 1))
    plt.xlim(0, np.max(bins[bins <= n_bins]))
    plt.xlabel("Bin Number", size=13)

    if y_true.nunique() <= 2:
        plt.ylabel("Event Rate", size=13)
    else:
        plt.ylabel("Mean Target", size=13)

        y_true_bins = pd.Series(y_true).groupby(bins)
        y_true_25p = y_true_bins.apply(lambda x: np.percentile(x, 25))
        y_true_50p = y_true_bins.apply(lambda x: np.percentile(x, 50))
        y_true_75p = y_true_bins.apply(lambda x: np.percentile(x, 75))
        plt.plot(
            y_true_25p.values,
            label="Real 25th Percentile",
            color="orange",
            linestyle="--",
            alpha=0.5,
        )
        plt.plot(
            y_true_50p.values,
            label="Real 50th Percentile",
            color="orange",
            linewidth=2,
            alpha=0.5,
        )
        plt.plot(
            y_true_75p.values,
            label="Real 75th Percentile",
            color="orange",
            linestyle="--",
            alpha=0.5,
        )

    plt.legend(loc="best", fontsize=13)


def plot_mean_pred_and_target(y_true, y_pred, n_bins: int = 20):
    """
    Plot the mean prediction in each bin against the mean target value in each bin.

    Args:
        y_true (array-like): True target values, shape = [n_samples].
        y_pred (array-like): Predicted scores or probabilities, shape = [n_samples].
        n_bins (int, optional): Number of quantile bins. Defaults to 20.

    Returns:
        None

    Raises:
        None
    """
    y_pred_mean, y_true_mean, _ = mean_by_bin(n_bins, y_pred, y_true)
    plt.plot(y_pred_mean.values, y_true_mean.values, linewidth=3, color="#534275")
    plt.plot(
        [0, max(y_pred_mean.values)],
        [0, max(y_true_mean.values)],
        color="black",
        alpha=0.5,
        linestyle="--",
    )
    plt.xlim(min(y_pred_mean.values), max(y_pred_mean.values))
    plt.ylim(min(y_pred_mean.values), max(y_true_mean.values))
    plt.xlabel("Mean Prediction", size=13)

    if y_true.nunique() <= 2:
        plt.ylabel("Event Rate", size=13)
    else:
        plt.ylabel("Mean Target", size=13)


def mean_by_bin(n_bins, y_pred, y_true):
    """
    Calculate the mean prediction and mean target values within each bin.

    Args:
        n_bins (int): Number of quantile bins.
        y_pred (array-like): Predicted scores or probabilities.
        y_true (array-like): True target values.

    Returns:
        Tuple[pd.Series, pd.Series, pd.Series]:
            - Mean predictions per bin.
            - Mean target values per bin.
            - Bin assignments.

    Raises:
        None
    """
    df = pd.DataFrame()
    df["y_true"] = np.array(y_true)
    df["y_pred"] = np.array(y_pred)
    df.sort_values("y_pred", ascending=True, inplace=True)
    bins = calculate_quantile_bins(df["y_pred"], n_bins=n_bins)
    y_pred_mean = pd.Series(df["y_pred"]).groupby(bins).mean()
    y_true_mean = pd.Series(df["y_true"]).groupby(bins).mean()
    del df
    return y_pred_mean, y_true_mean, bins


def plot_scatter(y_true, y_pred):
    """
    Plot a scatter plot of true target values versus predicted values.

    Args:
        y_true (array-like): True target values, shape = [n_samples].
        y_pred (array-like): Predicted values, shape = [n_samples].

    Returns:
        None

    Raises:
        None
    """
    y_true = np.array(y_true.tolist())
    y_pred = np.array(y_pred.tolist())
    n_points = np.max([10000, int(0.1 * len(y_pred))])
    n_points = np.min([n_points, len(y_pred)])

    indexes = np.random.randint(0, len(y_true), int(n_points))
    y_true_, y_pred_ = y_true[indexes], y_pred[indexes]

    plt.scatter(y_true_, y_pred_, alpha=0.25, color="#534275")
    plt.plot(
        [y_true_.min(), y_true_.max()],
        [y_true_.min(), y_true_.max()],
        color="orange",
        linestyle="--",
        linewidth=3,
    )
    plt.xlim(np.percentile(y_pred, 1), np.percentile(y_pred, 99))
    plt.ylim(np.percentile(y_pred, 1), np.percentile(y_pred, 99))
    plt.ylabel("y_real", size=14)
    plt.xlabel("y_true", size=14)


def plot_binary_graph(y_true, y_pred, save_path: str, plot_dim=(18, 4)):
    """
    Plot various evaluation graphs for binary classification on a single canvas.

    Args:
        y_true (array-like): True binary labels, shape = [n_samples].
        y_pred (array-like): Predicted scores or probabilities, shape = [n_samples].
        save_path (str): File path to save the plotted graphs.
        plot_dim (tuple, optional): Dimensions of the plot. Defaults to (18, 4).

    Returns:
        None

    Raises:
        None
    """
    mask = ~np.isnan(y_true)
    y_true, y_pred = y_true[mask], y_pred[mask]

    fig = plt.figure(figsize=plot_dim)
    plt.subplot(141)
    plot_roc_curve(y_true, y_pred)

    plt.subplot(142)
    plot_precision_recall_curve(y_true, y_pred)

    plt.subplot(143)
    try:
        plot_mean_prediction_in_bin(y_true, y_pred)
    except (ValueError, TypeError) as e:
        _logger.exception(f"Error occurred during plot_mean_prediction_in_bin: {e}")

    plt.subplot(144)
    try:
        plot_mean_pred_and_target(y_true, y_pred)
    except (ValueError, TypeError) as e:
        _logger.exception(f"Error occurred during plot_mean_pred_and_target: {e}")

    plt.savefig(save_path, bbox_inches="tight", pad_inches=0.1)
    plt.close()


def plot_model_quality_per_segment_graph(target_per_group: Dict, save_path: str):
    """
    Plot ROC curves for model quality per segment.

    Args:
        target_per_group (Dict): Dictionary containing target data per group.
        save_path (str): File path to save the plotted graphs.

    Returns:
        None

    Raises:
        None
    """
    fig, axes = plt.subplots(
        len(target_per_group),
        1,
        figsize=(4, 3 * len(target_per_group)),
        squeeze=False,
    )

    for idx, (group, target_per_sample) in enumerate(target_per_group.items()):
        for sample_name, targets in target_per_sample.items():
            y_true, y_pred = targets

            if len(y_true) == 0:
                continue

            fpr, tpr, _ = roc_curve(y_true, y_pred)
            metric = metrics_mapping["gini"](task="binary")
            score = metric(y_true, y_pred) * 100
            label = f"{sample_name}, Gini: {score:.1f}%"

            axes[idx][0].plot(fpr, tpr, linewidth=3, label=label)

        axes[idx][0].legend(loc="best", fontsize=8)

        axes[idx][0].set_xlabel("False Positive Rate (Sensitivity)", size=7)
        axes[idx][0].set_ylabel("True Positive Rate (1 - Specificity)", size=7)

        axes[idx][0].set_xlim(0, 1)
        axes[idx][0].set_ylim(0, 1)

        axes[idx][0].plot([0, 1], [0, 1], linestyle="--", color="red", alpha=0.25)
        axes[idx][0].set_title(f"Segment {group}", size=13)
        plt.subplots_adjust(hspace=0.3)

    fig.savefig(save_path, bbox_inches="tight", pad_inches=0.1)
    plt.close()


def plot_quality_dynamics_per_segment_graph(
    time_per_group: Dict, target_per_group: Dict, save_path: str
):
    """
    Plot the dynamics of model quality per segment over time.

    Args:
        time_per_group (Dict): Dictionary containing time data per group.
        target_per_group (Dict): Dictionary containing target data per group.
        save_path (str): File path to save the plotted graphs.

    Returns:
        None

    Raises:
        None
    """
    fig, axes = plt.subplots(
        len(target_per_group),
        1,
        figsize=(6, 4 * len(target_per_group)),
        squeeze=False,
    )

    for idx, (group, target_per_sample) in enumerate(target_per_group.items()):
        all_target_sum_per_time = defaultdict(dict)
        all_data_len_per_time = defaultdict(dict)

        for sample_name, targets in target_per_sample.items():
            y_true, y_pred = targets
            time_array = time_per_group[group][sample_name]

            if len(y_true) == 0:
                continue

            metric = metrics_mapping["gini"](task="binary")

            unique_times = sorted(time_array.unique())
            time_scores = []
            for time in unique_times:
                mask = time_array == time

                y_true_per_time = y_true[mask]
                if y_true_per_time.nunique() == 1:
                    _logger.warning(
                        f"Only one class represented in target variable at time {time}. "
                        f"Cannot compute GINI metric for this case, setting metric to 0."
                    )
                    time_score = 0.0
                else:
                    time_score = metric(y_true_per_time, y_pred[mask]) * 100
                time_scores.append(time_score)

                all_target_sum_per_time[time][sample_name] = y_true[mask].sum()
                all_data_len_per_time[time][sample_name] = len(y_true[mask])

            label = f"GINI_{sample_name}"

            axes[idx][0].plot(
                unique_times, time_scores, linewidth=3, label=label, marker="o"
            )

        times = sorted(list(all_target_sum_per_time.keys()))
        event_rates = []
        for time in times:
            all_samples_target_sum = sum(all_target_sum_per_time[time].values())
            all_samples_data_len = sum(all_data_len_per_time[time].values())

            event_rates.append(all_samples_target_sum / all_samples_data_len * 100)

        axes[idx][0].plot(
            times, event_rates, linewidth=3, label="Event Rate", marker="o"
        )

        axes[idx][0].legend(loc="best", fontsize=8)
        axes[idx][0].set_title(f"Segment {group}", size=13)
        axes[idx][0].tick_params(axis="x", labelrotation=45)
        axes[idx][0].grid(alpha=0.3)

    plt.subplots_adjust(hspace=0.4)
    fig.savefig(save_path, bbox_inches="tight", pad_inches=0.1)
    plt.close()


def plot_data_decile_statistics_graph(data, save_path: str):
    """
    Plot decile statistics of the data.

    Args:
        data (pd.DataFrame): DataFrame containing decile statistics.
        save_path (str): File path to save the plotted graph.

    Returns:
        None

    Raises:
        None
    """
    fig, ax = plt.subplots(1, 1, figsize=(4, 3))

    ax.bar(np.arange(len(data)), data["Кол-во наблюдений"], label="Number of Observations")

    handles1, labels1 = ax.get_legend_handles_labels()

    ax2 = ax.twinx()
    ax2.plot(
        np.arange(len(data)),
        data["Event-rate (факт.)"],
        label="Event Rate (Actual)",
        color="tab:orange",
        marker="o",
    )

    ax2.set_ylim(0, 100)
    ax2.set_yticks(np.linspace(0, 100, 11))
    vals = ax2.get_yticks()
    ax2.set_yticklabels([f"{int(x)}%" for x in vals])

    handles2, labels2 = ax2.get_legend_handles_labels()

    ax.legend(handles1 + handles2, labels1 + labels2)

    fig.savefig(save_path, bbox_inches="tight", pad_inches=0.1)
    plt.close()


def plot_regression_graph(y_true, y_pred, name: str, plot_dim=(10, 4)):
    """
    Plot various evaluation graphs for regression tasks.

    Args:
        y_true (array-like): True target values, shape = [n_samples].
        y_pred (array-like): Predicted values, shape = [n_samples].
        name (str): Base name for saving the plot.
        plot_dim (tuple, optional): Dimensions of the plot. Defaults to (10, 4).

    Returns:
        None

    Raises:
        None
    """
    fig = plt.figure(figsize=plot_dim)
    plt.subplot(131)
    plot_scatter(y_true, y_pred)

    plt.subplot(132)
    try:
        plot_mean_prediction_in_bin(y_true, y_pred)
    except (ValueError, TypeError) as e:
        _logger.exception(f"Error occurred during plot_mean_prediction_in_bin: {e}")

    plt.subplot(133)
    try:
        plot_mean_pred_and_target(y_true, y_pred)
    except (ValueError, TypeError) as e:
        _logger.exception(f"Error occurred during plot_mean_prediction_in_bin: {e}")

    plt.savefig(f"{name}.png")
    plt.close()


def plot_STL(segment_name: str, stl_dict: Dict, name: str, plot_dim=(12, 8)):
    """
    Plot the STL decomposition components: trend, seasonal, and residual.

    Args:
        segment_name (str): Name of the segment.
        stl_dict (Dict): Dictionary containing STL decomposition components.
        name (str): Base name for saving the plot.
        plot_dim (tuple, optional): Dimensions of the plot. Defaults to (12, 8).

    Returns:
        None

    Raises:
        None
    """
    fig = plt.figure(figsize=plot_dim)
    plt.title(f"Segment: {segment_name}")

    ax_1 = fig.add_subplot(4, 1, 1)
    ax_1.plot(stl_dict["timeseries"], stl_dict["target"], label="Target", color="blue")
    ax_1.legend(loc="best")
    ax_1.grid(True)

    ax_2 = fig.add_subplot(4, 1, 2)
    ax_2.plot(stl_dict["timeseries"], stl_dict["trend"], label="Trend", color="orange")
    ax_2.legend(loc="best")
    ax_2.grid(True)

    ax_3 = fig.add_subplot(4, 1, 3)
    ax_3.plot(
        stl_dict["timeseries"], stl_dict["seasonal"], label="Seasonal", color="green"
    )
    ax_3.legend(loc="best")
    ax_3.grid(True)

    ax_4 = fig.add_subplot(4, 1, 4)
    ax_4.plot(stl_dict["timeseries"], stl_dict["resid"], label="Residual", color="red")
    ax_4.legend(loc="best")
    ax_4.grid(True)

    plt.savefig(f"{name}.png")
    plt.close()


def plot_multi_graph(y_true, y_pred_proba, save_path, classes, plot_dim=(14, 4)):
    """
    Plot various evaluation graphs for multi-class classification.

    Args:
        y_true (array-like): True binary labels for each class, shape = [n_samples, n_classes].
        y_pred_proba (array-like): Predicted probabilities for each class, shape = [n_samples, n_classes].
        save_path (str): File path to save the plotted graphs.
        classes (List[str]): List of class names.
        plot_dim (tuple, optional): Dimensions of the plot. Defaults to (14, 4).

    Returns:
        None

    Raises:
        None
    """
    fig, axes = plt.subplots(1, 3, figsize=plot_dim, dpi=100)

    # ROC curve
    ax = axes[0]
    ax.set_title("ROC Curve", size=13)
    for i, class_name in enumerate(classes):
        y_true_class = y_true[:, i]
        y_pred_class = y_pred_proba[:, i]

        y_true_mask = np.isnan(y_true_class)
        y_true_class = y_true_class[~y_true_mask]
        y_pred_class = y_pred_class[~y_true_mask]

        fpr, tpr, _ = roc_curve(y_true_class, y_pred_class)
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, label=f"Class {class_name} (AUC = {roc_auc:.3f})")

    ax.plot([0, 1], [0, 1], linestyle="--", color="black", alpha=0.25)
    ax.legend(loc="best", fontsize=5)
    ax.set_xlabel("False Positive Rate", size=10)
    ax.set_ylabel("True Positive Rate", size=10)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])

    # Precision-Recall curve
    ax = axes[1]
    ax.set_title("Precision-Recall Curve", size=13)
    for i, class_name in enumerate(classes):
        y_true_class = y_true[:, i]
        y_pred_class = y_pred_proba[:, i]

        y_true_mask = np.isnan(y_true_class)
        y_true_class = y_true_class[~y_true_mask]
        y_pred_class = y_pred_class[~y_true_mask]

        precision, recall, _ = precision_recall_curve(y_true_class, y_pred_class)
        pr_auc = average_precision_score(y_true_class, y_pred_class)
        ax.plot(recall, precision, label=f"Class {class_name} (AP = {pr_auc:.3f})")

    ax.legend(loc="best", fontsize=5)
    ax.set_xlabel("Recall", size=10)
    ax.set_ylabel("Precision", size=10)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])

    # Distribution of predicted probabilities
    ax = axes[2]
    ax.set_title("Predicted Probabilities Distribution", size=13)
    for i, class_name in enumerate(classes):
        y_true_class = y_true[:, i]
        y_pred_class = y_pred_proba[:, i]

        y_true_mask = np.isnan(y_true_class)
        y_true_class = y_true_class[~y_true_mask]
        y_pred_class = y_pred_class[~y_true_mask]

        ax.hist(
            y_pred_class, bins=20, alpha=0.5, label=f"Class {class_name}", density=True
        )
    ax.legend(loc="best", fontsize=5)
    ax.set_xlabel("Predicted Probability", size=10)
    ax.set_ylabel("Density", size=10)

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", pad_inches=0.1)


def plot_token_length_distribution_for_text_features(
    sample_name: str,
    text_feature: str,
    x_sample: pd.DataFrame,
    save_path: str,
    n_bins=50,
):
    """
    Plot the distribution of token lengths for a specific text feature.

    Args:
        sample_name (str): Name of the sample.
        text_feature (str): Name of the text feature.
        x_sample (pd.DataFrame): DataFrame containing the text data.
        save_path (str): File path to save the plotted histogram.
        n_bins (int, optional): Number of bins for the histogram. Defaults to 50.

    Returns:
        None

    Raises:
        None
    """
    token_length_series = x_sample[text_feature].apply(
        lambda text: len(word_tokenize(str(text), language="russian"))
    )

    len_token_quantiles_dict = {}
    for quantile in [0.25, 0.5, 0.75, 0.9, 0.95, 0.97, 0.99]:
        q_len = token_length_series.quantile(quantile)
        len_token_quantiles_dict[str(quantile)] = q_len

    plt.figure(figsize=(7, 4))
    sns.histplot(token_length_series, bins=n_bins, kde=True, color="lightgreen")

    colors = ["green", "blue", "purple", "orange", "red", "brown", "magenta"]
    for i, (quantile, value) in enumerate(len_token_quantiles_dict.items()):
        plt.axvline(
            x=value,
            color=colors[i],
            linestyle="--",
            linewidth=1,
            label=f"{quantile} quantile={int(value)}",
        )

    plt.title(
        f"Distribution of Token Length | Feature: {text_feature} | Sample: {sample_name}",
        fontsize=10,
    )
    plt.xlabel("Token Length", fontsize=8)
    plt.ylabel("Frequency", fontsize=8)
    plt.legend(title="Quantile | Length", fontsize=6, title_fontsize=6)

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", pad_inches=0.1)
    plt.close()


def _plot_hist_anomaly_detection(
    losses: np.ndarray,
    threshold: float,
    save_path: str,
    title_name: str = "Distribution of the Reconstruction Loss",
    figsize=(10, 5),
    n_bins: int = 100,
):
    """
    Plot the histogram of reconstruction losses for anomaly detection.

    Args:
        losses (np.ndarray): Array of reconstruction loss values.
        threshold (float): Threshold for classifying anomalies.
        save_path (str): File path to save the plotted histogram.
        title_name (str, optional): Title of the plot. Defaults to "Distribution of the Reconstruction Loss".
        figsize (tuple, optional): Dimensions of the plot. Defaults to (10, 5).
        n_bins (int, optional): Number of bins for the histogram. Defaults to 100.

    Returns:
        None

    Raises:
        None
    """
    data = pd.DataFrame({"loss": losses})
    data["y_pred"] = (data["loss"] > threshold).astype(int)
    data = data[data["loss"] >= data["loss"].quantile(0.05)]

    plt.figure(figsize=figsize)
    palette = {0: "blue", 1: "orange"}

    sns.histplot(
        data=data,
        x=data["loss"],
        bins=n_bins,
        kde=False,
        hue="y_pred",
        log_scale=True,
        common_norm=False,
        multiple="layer",
        alpha=0.5,
        palette=palette,
        legend=False,
    )

    plt.axvline(x=threshold, color="red", linestyle="--")
    plt.legend(
        title="Classes",
        labels=[f"THR = {round(threshold, 3)}", "Anomaly", "Non-anomaly"],
    )
    plt.title(title_name)
    plt.xlabel("Loss")
    plt.ylabel("Frequency")
    plt.savefig(save_path)
    plt.close()


def _plot_training_progress(
    callback_info: dict,
    save_path: str,
    title_name: str = "Training and Validation Loss per Epoch",
    figsize=(10, 6),
):
    """
    Plot the training and validation loss over epochs.

    Args:
        callback_info (dict): Dictionary containing loss information per epoch.
        save_path (str): File path to save the plotted graph.
        title_name (str, optional): Title of the plot. Defaults to "Training and Validation Loss per Epoch".
        figsize (tuple, optional): Dimensions of the plot. Defaults to (10, 6).

    Returns:
        None

    Raises:
        None
    """
    epochs = list(callback_info.keys())
    train_losses = [callback_info[epoch]["train"] for epoch in epochs]
    valid_losses = [callback_info[epoch]["valid"] for epoch in epochs]

    plt.figure(figsize=figsize)
    plt.plot(epochs, train_losses, label="Train Loss", marker="o")
    plt.plot(epochs, valid_losses, label="Validation Loss", marker="o")
    plt.title(title_name)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()


def plot_hist_loss_amts_ad(
    data,
    save_path,
    bins=100,
    kde=False,
    alpha=0.7,
    title="none",
    xlabel="none",
    ylabel="frequency",
    color="blue",
):
    """
    Plot a histogram of loss values for AMTS anomaly detection.

    Args:
        data (array-like): Data to plot the histogram for.
        save_path (str): File path to save the plotted histogram.
        bins (int, optional): Number of bins for the histogram. Defaults to 100.
        kde (bool, optional): Whether to include a kernel density estimate. Defaults to False.
        alpha (float, optional): Transparency level of the histogram bars. Defaults to 0.7.
        title (str, optional): Title of the plot. Defaults to "none".
        xlabel (str, optional): Label for the x-axis. Defaults to "none".
        ylabel (str, optional): Label for the y-axis. Defaults to "frequency".
        color (str, optional): Color of the histogram bars. Defaults to "blue".

    Returns:
        None

    Raises:
        None
    """
    plt.figure(figsize=(7, 5))
    sns.histplot(x=data, bins=bins, kde=kde, alpha=alpha, color=color)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()


def plot_scatter_mark_amts_ad(
    target,
    mark,
    save_path,
    title="none",
    xlabel="none",
    ylabel="none",
    color="blue",
    color_mark="red",
):
    """
    Plot a scatter plot with marked anomalies for AMTS anomaly detection.

    Args:
        target (array-like): Target values to plot on the y-axis.
        mark (array-like): Binary markers indicating anomalies.
        save_path (str): File path to save the plotted scatter plot.
        title (str, optional): Title of the plot. Defaults to "none".
        xlabel (str, optional): Label for the x-axis. Defaults to "none".
        ylabel (str, optional): Label for the y-axis. Defaults to "none".
        color (str, optional): Color for normal points. Defaults to "blue".
        color_mark (str, optional): Color for anomaly points. Defaults to "red".

    Returns:
        None

    Raises:
        None
    """
    plt.figure(figsize=(20, 5))
    sns.scatterplot(
        x=list(range(len(target))),
        y=target,
        hue=mark,
        palette={0: color, 1: color_mark},
        legend="full",
    )
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()