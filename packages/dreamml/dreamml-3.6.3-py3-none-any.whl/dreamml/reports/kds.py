import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def print_labels():
    """
    Prints descriptions of labels used in the decile table.

    This function outputs information about various metrics utilized in the decile table,
    including probability ranges, counts of events and responders, cumulative sums,
    KS statistic, and lift values for each decile.
    """
    print(
        "LABELS INFO:\n\n",
        "prob_min         : Minimum probability in a particular decile\n",
        "prob_max         : Maximum probability in a particular decile\n",
        "prob_avg         : Average probability in a particular decile\n",
        "cnt_cust         : Count of customers in a particular decile\n",
        "cnt_resp         : Count of responders in a particular decile\n",
        "cnt_non_resp     : Count of non-responders in a particular decile\n",
        "cnt_resp_rndm    : Count of responders if events were assigned randomly in a particular decile\n",
        "cnt_resp_wiz     : Count of best possible responders in a particular decile\n",
        "resp_rate        : Response rate in a particular decile [(cnt_resp/cnt_cust)*100]\n",
        "cum_cust         : Cumulative count of customers decile-wise\n",
        "cum_resp         : Cumulative count of responders decile-wise\n",
        "cum_resp_wiz     : Cumulative count of best possible responders decile-wise\n",
        "cum_non_resp     : Cumulative count of non-responders decile-wise\n",
        "cum_cust_pct     : Cumulative percentage of customers decile-wise\n",
        "cum_resp_pct     : Cumulative percentage of responders decile-wise\n",
        "cum_resp_pct_wiz : Cumulative percentage of best possible responders decile-wise\n",
        "cum_non_resp_pct : Cumulative percentage of non-responders decile-wise\n",
        "KS               : KS statistic decile-wise\n",
        "lift             : Cumulative lift value decile-wise",
    )


def decile_table(y_true, y_prob, change_deciles=10, labels=True, round_decimal=3):
    """
    Generates a decile table from true labels and predicted probabilities.

    The decile table is created by sorting the customers based on their predicted
    probabilities in descending order and then splitting them into equally sized
    deciles. Each decile contains the same percentage of the customer base, allowing
    for analysis of model performance across different segments.

    Args:
        y_true (array-like, shape (n_samples,)):
            Ground truth (actual) binary target values.
        y_prob (array-like, shape (n_samples,)):
            Predicted probabilities for the positive class.
        change_deciles (int, optional):
            Number of deciles to split the data into. Defaults to 10.
        labels (bool, optional):
            If True, prints a legend explaining the abbreviations used in the decile table.
            Defaults to True.
        round_decimal (int, optional):
            Number of decimal places to round the results to. Defaults to 3.

    Returns:
        pd.DataFrame:
            A DataFrame representing the decile table with metrics for each decile.

    Raises:
        ValueError:
            If the number of deciles is greater than the number of observations.
    """
    if len(y_true) < change_deciles:
        raise ValueError(
            f"Number of deciles ({change_deciles}) can't be less than number of observations ({len(y_true)})"
        )

    y_true = np.array(y_true)
    y_prob = np.array(y_prob)

    df = pd.DataFrame()
    df["y_true"] = y_true
    df["y_prob"] = y_prob

    df.sort_values("y_prob", ascending=False, inplace=True)
    df["decile"] = np.linspace(1, change_deciles + 1, len(df), False, dtype=int)

    # dt abbreviation for decile_table
    dt = (
        df.groupby("decile")
        .apply(
            lambda x: pd.Series(
                [
                    np.min(x["y_prob"]),
                    np.max(x["y_prob"]),
                    np.mean(x["y_prob"]),
                    np.size(x["y_prob"]),
                    np.sum(x["y_true"]),
                    np.size(x["y_true"][x["y_true"] == 0]),
                ],
                index=(
                    [
                        "prob_min",
                        "prob_max",
                        "prob_avg",
                        "cnt_cust",
                        "cnt_resp",
                        "cnt_non_resp",
                    ]
                ),
            )
        )
        .reset_index()
    )

    dt["prob_min"] = dt["prob_min"].round(round_decimal)
    dt["prob_max"] = dt["prob_max"].round(round_decimal)
    dt["prob_avg"] = round(dt["prob_avg"], round_decimal)

    tmp = df[["y_true"]].sort_values("y_true", ascending=False)
    tmp["decile"] = np.linspace(1, change_deciles + 1, len(tmp), False, dtype=int)

    dt["cnt_resp_rndm"] = np.sum(df["y_true"]) / change_deciles
    dt["cnt_resp_wiz"] = tmp.groupby("decile", as_index=False)["y_true"].sum()["y_true"]

    dt["resp_rate"] = round(dt["cnt_resp"] / dt["cnt_cust"], round_decimal)
    dt["cum_cust"] = np.cumsum(dt["cnt_cust"])
    dt["cum_resp"] = np.cumsum(dt["cnt_resp"])
    dt["cum_resp_wiz"] = np.cumsum(dt["cnt_resp_wiz"])
    dt["cum_non_resp"] = np.cumsum(dt["cnt_non_resp"])
    dt["cum_cust_pct"] = round(
        dt["cum_cust"] * 100 / np.sum(dt["cnt_cust"]), round_decimal
    )
    dt["cum_resp_pct"] = round(
        dt["cum_resp"] * 100 / np.sum(dt["cnt_resp"]), round_decimal
    )
    dt["cum_resp_pct_wiz"] = round(
        dt["cum_resp_wiz"] * 100 / np.sum(dt["cnt_resp_wiz"]), round_decimal
    )
    dt["cum_non_resp_pct"] = round(
        dt["cum_non_resp"] * 100 / np.sum(dt["cnt_non_resp"]), round_decimal
    )
    dt["KS"] = round(dt["cum_resp_pct"] - dt["cum_non_resp_pct"], round_decimal)
    dt["lift"] = round(dt["cum_resp_pct"] / dt["cum_cust_pct"], round_decimal)

    # if labels is True:
    #    print_labels()
    #
    return dt


def plot_lift(
    y_true, y_prob, title="Lift Plot", title_fontsize=14, text_fontsize=10, figsize=None
):
    """
    Generates a cumulative lift plot based on true labels and predicted probabilities.

    The lift plot visualizes the effectiveness of a binary classifier by comparing
    the model's lift against a random selection. It helps in understanding how much
    better the model is at identifying positive cases compared to random guessing.

    Args:
        y_true (array-like, shape (n_samples,)):
            Ground truth (actual) binary target values.
        y_prob (array-like, shape (n_samples,)):
            Predicted probabilities for the positive class.
        title (str, optional):
            Title of the plot. Defaults to "Lift Plot".
        title_fontsize (int or str, optional):
            Font size of the plot title. Defaults to 14.
        text_fontsize (int or str, optional):
            Font size of the axis labels. Defaults to 10.
        figsize (tuple of int, optional):
            Size of the figure in inches as (width, height). Defaults to None.

    Returns:
        None

    Raises:
        None

    Example:
        >>> import kds
        >>> from sklearn.datasets import load_iris
        >>> from sklearn.model_selection import train_test_split
        >>> from sklearn import tree
        >>> X, y = load_iris(return_X_y=True)
        >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=3)
        >>> clf = tree.DecisionTreeClassifier(max_depth=1, random_state=3)
        >>> clf = clf.fit(X_train, y_train)
        >>> y_prob = clf.predict_proba(X_test)[:, 1]
        >>> kds.metrics.plot_lift(y_test, y_prob)
    """
    # Cumulative Lift Plot
    # plt.subplot(2, 2, 1)

    pl = decile_table(y_true, y_prob, labels=False)
    plt.plot(pl.decile.values, pl.lift.values, marker="o", label="Model")
    # plt.plot(list(np.arange(1,11)), np.ones(10), 'k--',marker='o')
    plt.plot([1, 10], [1, 1], "k--", marker="o", label="Random")
    plt.title(title, fontsize=title_fontsize)
    plt.xlabel("Deciles", fontsize=text_fontsize)
    plt.ylabel("Lift", fontsize=text_fontsize)
    plt.legend()
    plt.grid(True)
    # plt.show()


def plot_lift_decile_wise(
    y_true,
    y_prob,
    title="Decile-wise Lift Plot",
    title_fontsize=14,
    text_fontsize=10,
    figsize=None,
):
    """
    Generates a decile-wise lift plot based on true labels and predicted probabilities.

    This plot illustrates the lift at each decile, showing how much better the model
    is at identifying positive cases in each decile compared to random selection.

    Args:
        y_true (array-like, shape (n_samples,)):
            Ground truth (actual) binary target values.
        y_prob (array-like, shape (n_samples,)):
            Predicted probabilities for the positive class.
        title (str, optional):
            Title of the plot. Defaults to "Decile-wise Lift Plot".
        title_fontsize (int or str, optional):
            Font size of the plot title. Defaults to 14.
        text_fontsize (int or str, optional):
            Font size of the axis labels. Defaults to 10.
        figsize (tuple of int, optional):
            Size of the figure in inches as (width, height). Defaults to None.

    Returns:
        None

    Raises:
        None

    Example:
        >>> import kds
        >>> from sklearn.datasets import load_iris
        >>> from sklearn.model_selection import train_test_split
        >>> from sklearn import tree
        >>> X, y = load_iris(return_X_y=True)
        >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=3)
        >>> clf = tree.DecisionTreeClassifier(max_depth=1, random_state=3)
        >>> clf = clf.fit(X_train, y_train)
        >>> y_prob = clf.predict_proba(X_test)[:, 1]
        >>> kds.metrics.plot_lift_decile_wise(y_test, y_prob)
    """
    # Decile-wise Lift Plot
    # plt.subplot(2, 2, 2)
    pldw = decile_table(y_true, y_prob, labels=False)
    plt.plot(
        pldw.decile.values,
        pldw.cnt_resp.values / pldw.cnt_resp_rndm.values,
        marker="o",
        label="Model",
    )
    # plt.plot(list(np.arange(1,11)), np.ones(10), 'k--',marker='o')
    plt.plot([1, 10], [1, 1], "k--", marker="o", label="Random")
    plt.title(title, fontsize=title_fontsize)
    plt.xlabel("Deciles", fontsize=text_fontsize)
    plt.ylabel("Lift @ Decile", fontsize=text_fontsize)
    plt.legend()
    plt.grid(True)
    # plt.show()


def plot_cumulative_gain(
    y_true,
    y_prob,
    title="Cumulative Gain Plot",
    title_fontsize=14,
    text_fontsize=10,
    figsize=None,
):
    """
    Generates a cumulative gain plot based on true labels and predicted probabilities.

    The cumulative gain plot shows the proportion of positive cases captured by the model
    as the deciles increase. It helps in assessing the model's ability to identify positive
    cases early in the ranking.

    Args:
        y_true (array-like, shape (n_samples,)):
            Ground truth (actual) binary target values.
        y_prob (array-like, shape (n_samples,)):
            Predicted probabilities for the positive class.
        title (str, optional):
            Title of the plot. Defaults to "Cumulative Gain Plot".
        title_fontsize (int or str, optional):
            Font size of the plot title. Defaults to 14.
        text_fontsize (int or str, optional):
            Font size of the axis labels. Defaults to 10.
        figsize (tuple of int, optional):
            Size of the figure in inches as (width, height). Defaults to None.

    Returns:
        None

    Raises:
        None

    Example:
        >>> import kds
        >>> from sklearn.datasets import load_iris
        >>> from sklearn.model_selection import train_test_split
        >>> from sklearn import tree
        >>> X, y = load_iris(return_X_y=True)
        >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=3)
        >>> clf = tree.DecisionTreeClassifier(max_depth=1, random_state=3)
        >>> clf = clf.fit(X_train, y_train)
        >>> y_prob = clf.predict_proba(X_test)[:, 1]
        >>> kds.metrics.plot_cumulative_gain(y_test, y_prob)
    """
    # Cumulative Gains Plot
    # plt.subplot(2, 2, 3)
    pcg = decile_table(y_true, y_prob, labels=False)
    plt.plot(
        np.append(0, pcg.decile.values),
        np.append(0, pcg.cum_resp_pct.values),
        marker="o",
        label="Model",
    )
    plt.plot(
        np.append(0, pcg.decile.values),
        np.append(0, pcg.cum_resp_pct_wiz.values),
        "c--",
        label="Wizard",
    )
    # plt.plot(list(np.arange(1,11)), np.ones(10), 'k--',marker='o')
    plt.plot([0, 10], [0, 100], "k--", marker="o", label="Random")
    plt.title(title, fontsize=title_fontsize)
    plt.xlabel("Deciles", fontsize=text_fontsize)
    plt.ylabel("% Responders", fontsize=text_fontsize)
    plt.legend()
    plt.grid(True)
    # plt.show()


def plot_ks_statistic(
    y_true,
    y_prob,
    title="KS Statistic Plot",
    title_fontsize=14,
    text_fontsize=10,
    figsize=None,
):
    """
    Generates a KS (Kolmogorov-Smirnov) statistic plot based on true labels and predicted probabilities.

    The KS statistic measures the maximum difference between the cumulative distributions of
    responders and non-responders. This plot visualizes the KS statistic across deciles to
    evaluate the model's ability to distinguish between the two classes.

    Args:
        y_true (array-like, shape (n_samples,)):
            Ground truth (actual) binary target values.
        y_prob (array-like, shape (n_samples,)):
            Predicted probabilities for the positive class.
        title (str, optional):
            Title of the plot. Defaults to "KS Statistic Plot".
        title_fontsize (int or str, optional):
            Font size of the plot title. Defaults to 14.
        text_fontsize (int or str, optional):
            Font size of the axis labels. Defaults to 10.
        figsize (tuple of int, optional):
            Size of the figure in inches as (width, height). Defaults to None.

    Returns:
        None

    Raises:
        None

    Example:
        >>> import kds
        >>> from sklearn.datasets import load_iris
        >>> from sklearn.model_selection import train_test_split
        >>> from sklearn import tree
        >>> X, y = load_iris(return_X_y=True)
        >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=3)
        >>> clf = tree.DecisionTreeClassifier(max_depth=1, random_state=3)
        >>> clf = clf.fit(X_train, y_train)
        >>> y_prob = clf.predict_proba(X_test)[:, 1]
        >>> kds.metrics.plot_ks_statistic(y_test, y_prob)
    """
    # KS Statistic Plot
    # plt.subplot(2, 2, 4)
    pks = decile_table(y_true, y_prob, labels=False)

    plt.plot(
        np.append(0, pks.decile.values),
        np.append(0, pks.cum_resp_pct.values),
        marker="o",
        label="Responders",
    )
    plt.plot(
        np.append(0, pks.decile.values),
        np.append(0, pks.cum_non_resp_pct.values),
        marker="o",
        label="Non-Responders",
    )
    # plt.plot(list(np.arange(1,11)), np.ones(10), 'k--',marker='o')
    ksmx = pks.KS.max()
    ksdcl = pks[pks.KS == ksmx].decile.values
    plt.plot(
        [ksdcl, ksdcl],
        [
            pks[pks.KS == ksmx].cum_resp_pct.values,
            pks[pks.KS == ksmx].cum_non_resp_pct.values,
        ],
        "g--",
        marker="o",
        label=f"KS Statistic: {ksmx} at decile {ksdcl[0]}",
    )
    plt.title(title, fontsize=title_fontsize)
    plt.xlabel("Deciles", fontsize=text_fontsize)
    plt.ylabel("% Responders", fontsize=text_fontsize)
    plt.legend()
    plt.grid(True)
    # plt.show()


def report(
    y_true,
    y_prob,
    labels=True,
    plot_style=None,
    round_decimal=3,
    title_fontsize=14,
    text_fontsize=10,
    figsize=(16, 10),
    n_bins=20,
):
    """
    Generates a decile table and returns it based on true labels and predicted probabilities.

    This function creates a comprehensive decile table that summarizes various metrics
    across different deciles. It can also generate four plots (Lift, Lift@Decile, Cumulative Gain,
    and KS Statistic) if the plotting code is uncommented.

    Args:
        y_true (array-like, shape (n_samples,)):
            Ground truth (actual) binary target values.
        y_prob (array-like, shape (n_samples,)):
            Predicted probabilities for the positive class.
        labels (bool, optional):
            If True, prints a legend explaining the abbreviations used in the decile table.
            Defaults to True.
        plot_style (str, optional):
            Matplotlib style to apply to the plots. Examples include 'ggplot', 'seaborn', etc.
            Defaults to None.
        round_decimal (int, optional):
            Number of decimal places to round the results to. Defaults to 3.
        title_fontsize (int or str, optional):
            Font size of the plot titles. Defaults to 14.
        text_fontsize (int or str, optional):
            Font size of the axis labels. Defaults to 10.
        figsize (tuple of int, optional):
            Size of the figure in inches as (width, height). Defaults to (16, 10).
        n_bins (int, optional):
            Number of bins (deciles) to split the data into. Defaults to 20.

    Returns:
        pd.DataFrame:
            A DataFrame representing the decile table with renamed and filtered columns.

    Raises:
        None

    Example:
        >>> import kds
        >>> from sklearn.datasets import load_iris
        >>> from sklearn.model_selection import train_test_split
        >>> from sklearn import tree
        >>> X, y = load_iris(return_X_y=True)
        >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=3)
        >>> clf = tree.DecisionTreeClassifier(max_depth=1, random_state=3)
        >>> clf = clf.fit(X_train, y_train)
        >>> y_prob = clf.predict_proba(X_test)[:, 1]
        >>> dc = kds.metrics.report(y_test, y_prob)
        >>> print(dc)
    """
    dc = decile_table(
        y_true,
        y_prob,
        labels=labels,
        round_decimal=round_decimal,
        change_deciles=n_bins,
    )
    dc = dc.rename(
        columns={
            "prob_avg": "prob_mean",
            "cnt_cust": "#obs",
            "cnt_resp": "#event",
            "cnt_non_resp": "#nonevent",
            "resp_rate": "eventrate",
            "cum_cust": "cum # obs",
            "cum_resp": "cum # ev",
            "cum_non_resp": "cum # nonev",
            "cum_cust_pct": "cum # obsrate",
            "cum_resp_pct": "cum_eventrate",
            "cum_non_resp_pct": "cum_noneventrate",
            "KS": "KS-Statistics",
            "lift": "Lift",
        }
    )
    dc = dc.drop(
        ["cnt_resp_rndm", "cnt_resp_wiz", "cum_resp_wiz", "cum_resp_pct_wiz"], axis=1
    )

    """
    if plot_style is not None:
        plt.style.use(plot_style)

    fig = plt.figure(figsize=figsize))

    # Cumulative Lift Plot
    plt.subplot(2, 2, 1)
    plot_lift(y_true, y_prob)

    # Decile-wise Lift Plot
    plt.subplot(2, 2, 2)
    plot_lift_decile_wise(y_true, y_prob)

    # Cumulative Gains Plot
    plt.subplot(2, 2, 3)
    plot_cumulative_gain(y_true, y_prob)

    # KS Statistic Plot
    plt.subplot(2, 2, 4)
    plot_ks_statistic(y_true, y_prob)
    """
    return dc