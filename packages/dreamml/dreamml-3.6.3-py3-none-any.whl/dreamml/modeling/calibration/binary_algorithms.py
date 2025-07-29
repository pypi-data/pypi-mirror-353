import pandas as pd
import numpy as np
from scipy.special import logit, expit

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier

from dreamml.modeling.metrics.utils import calculate_quantile_bins


class IsotonicCalibration(BaseEstimator, TransformerMixin):
    """
    Isotonic Calibration using Isotonic Regression.

    This class calibrates predicted probabilities using isotonic regression,
    mapping y_pred to y_target.

    Attributes:
        calibration (IsotonicRegression): The isotonic regression model used for calibration.
    """

    def __init__(self):
        """
        Initializes the IsotonicCalibration instance.

        Initializes an IsotonicRegression model with out_of_bounds set to "clip".
        """
        self.calibration = IsotonicRegression(out_of_bounds="clip")

    def fit(self, y_pred: pd.Series, y_true: pd.Series):
        """
        Fits the isotonic regression model to the data.

        Args:
            y_pred (pd.Series): The predicted probabilities.
            y_true (pd.Series): The true target values.

        Returns:
            self: Returns the instance itself.
        """
        self.calibration.fit(y_pred, y_true)
        return self

    def transform(self, y_pred):
        """
        Transforms the predicted probabilities using the fitted calibration model.

        Args:
            y_pred (array-like): The predicted probabilities to be calibrated.

        Returns:
            np.ndarray: The calibrated probabilities.
        """
        return self.calibration.transform(y_pred)


class LogisticCalibration(BaseEstimator, TransformerMixin):
    """
    Logistic Calibration using Logistic Regression.

    This class calibrates predicted probabilities using logistic regression,
    mapping y_pred to y_target.

    Attributes:
        calibration (LogisticRegression): The logistic regression model used for calibration.
        is_logit (bool): Indicates whether logit transformation is applied.
        is_odds (bool): Indicates whether odds transformation is applied.
    """

    def __init__(self, is_logit=False, is_odds=False):
        """
        Initializes the LogisticCalibration instance.

        Args:
            is_logit (bool, optional): Whether to apply logit transformation to predictions. Defaults to False.
            is_odds (bool, optional): Whether to apply odds transformation to predictions. Defaults to False.
        """
        self.calibration = LogisticRegression()
        self.is_logit = is_logit
        self.is_odds = is_odds

    def _fit_odds(self, y_pred: pd.Series, y_true: pd.Series):
        """
        Fits the logistic regression model using odds-transformed predictions.

        Args:
            y_pred (pd.Series): The predicted probabilities.
            y_true (pd.Series): The true target values.
        """
        x = np.array(y_pred / (1 - y_pred)).reshape(-1, 1)
        self.calibration.fit(x, y_true)

    def _fit_logit(self, y_pred: pd.Series, y_true: pd.Series):
        """
        Fits the logistic regression model using logit-transformed predictions.

        Args:
            y_pred (pd.Series): The predicted probabilities.
            y_true (pd.Series): The true target values.
        """
        x = logit(np.array(y_pred).reshape(-1, 1))
        self.calibration.fit(x, y_true)

    def _fit_logreg(self, y_pred: pd.Series, y_true: pd.Series):
        """
        Fits the logistic regression model using raw predicted probabilities.

        Args:
            y_pred (pd.Series): The predicted probabilities.
            y_true (pd.Series): The true target values.
        """
        x = np.array(y_pred).reshape(-1, 1)
        self.calibration.fit(x, y_true)

    def fit(self, y_pred: pd.Series, y_true: pd.Series):
        """
        Fits the calibration model to the data.

        Depending on the configuration, fits the logistic regression model using logit,
        odds, or raw predicted probabilities.

        Args:
            y_pred (pd.Series): The predicted probabilities.
            y_true (pd.Series): The true target values.

        Returns:
            self: Returns the instance itself.
        """
        if self.is_odds:
            self._fit_odds(y_pred, y_true)
        elif self.is_logit:
            self._fit_logit(y_pred, y_true)
        else:
            self._fit_logreg(y_pred, y_true)

        return self

    def get_equation(self):
        """
        Retrieves the calibration equation based on the fitted model.

        Returns:
            str: A string representation of the calibration equation.
        """
        k = float(self.calibration.coef_)
        b = float(self.calibration.intercept_)

        if self.is_odds:
            return f"1/(1 + exp(-{k}*(x/(1 - x)) + {b}))"
        elif self.is_logit:
            return f"1/(1 + exp(-{k}*ln(x/(1 - x)) + {b}))"
        else:
            return f"1/(1 + exp(-{k}*x + {b}))"

    def transform(self, y_pred):
        """
        Transforms the predicted probabilities using the fitted calibration model.

        Args:
            y_pred (array-like): The predicted probabilities to be calibrated.

        Returns:
            np.ndarray: The calibrated probabilities.
        """
        if self.is_odds:
            x = np.array(y_pred / (1 - y_pred)).reshape(-1, 1)
        elif self.is_logit:
            x = logit(np.array(y_pred).reshape(-1, 1))
        else:
            x = np.array(y_pred).reshape(-1, 1)

        return self.calibration.predict_proba(x)[:, 1]


class LinearCalibration(BaseEstimator, TransformerMixin):
    """
    Linear Calibration using Linear Regression.

    This class calibrates predicted probabilities by fitting a linear regression
    model on the mean predictions and mean targets within quantile bins.

    Attributes:
        calibration (LinearRegression): The linear regression model used for calibration.
        is_weighted (bool): Indicates whether to apply weighted fitting based on event share.
        is_logit (bool): Indicates whether to apply logit transformation.
        is_odds (bool): Indicates whether to apply odds transformation.
    """

    def __init__(
        self, is_weighted: bool = False, is_logit: bool = False, is_odds=False
    ):
        """
        Initializes the LinearCalibration instance.

        Args:
            is_weighted (bool, optional): Whether to apply weighted fitting based on event share. Defaults to False.
            is_logit (bool, optional): Whether to apply logit transformation to predictions and targets. Defaults to False.
            is_odds (bool, optional): Whether to apply odds transformation to predictions and targets. Defaults to False.
        """
        self.calibration = LinearRegression()
        self.is_weighted = is_weighted
        self.is_logit = is_logit
        self.is_odds = is_odds

    def fit(self, y_pred, y_true):
        """
        Fits the linear regression model to the binned data.

        The data is binned into quantiles, and the mean predictions and mean targets within each bin
        are used to train the linear regression model.

        Args:
            y_pred (array-like): The predicted probabilities.
            y_true (array-like): The true target values.

        Returns:
            self: Returns the instance itself.
        """
        # Prepare the dataframe for binning
        pred_df = pd.DataFrame({"y_true": y_true, "y_pred": y_pred})
        pred_df["pred_bin"] = calculate_quantile_bins(
            y_pred, 20, percentile_implementation=True
        )
        pred_df_grouped = pred_df.groupby(by="pred_bin").agg(
            {"y_pred": "mean", "y_true": ["mean", "sum"]}
        )

        pred_df_grouped.columns = ["y_pred", "y_true", "#events"]
        pred_df_grouped["events_share"] = (
            pred_df_grouped["#events"] / pred_df_grouped["#events"].sum()
        )

        # Handle critical values
        pred_df_grouped["y_pred"].replace({1: 0.9999, 0: 0.0001}, inplace=True)
        pred_df_grouped["y_true"].replace({1: 0.9999, 0: 0.0001}, inplace=True)

        x = np.array(pred_df_grouped["y_pred"]).reshape(-1, 1)
        y = pred_df_grouped["y_true"]

        # Store the average event rate in the prediction bin for weighting
        weights = pred_df_grouped["events_share"]

        if self.is_odds:
            x = np.array(x / (1 - x))
            y = np.array(y / (1 - y))

        if self.is_logit:
            x = logit(x)
            y = logit(y)

        if self.is_weighted:
            self.calibration.fit(x, y, sample_weight=weights)
        else:
            self.calibration.fit(x, y)

        return self

    def get_equation(self):
        """
        Retrieves the calibration equation based on the fitted linear model.

        Returns:
            str: A string representation of the calibration equation.
        """
        k = float(self.calibration.coef_)
        b = float(self.calibration.intercept_)

        if self.is_odds:
            return f"y_odds = {k}*(x/(1 - x)) + {b}"
        elif self.is_logit:
            return f"y_ln_odds = {k}*ln(x/(1 - x)) + {b}"
        else:
            return f"y = {k}*x + {b}"

    def transform(self, y_pred):
        """
        Transforms the predicted probabilities using the fitted calibration model.

        Args:
            y_pred (array-like): The predicted probabilities to be calibrated.

        Returns:
            np.ndarray: The calibrated probabilities.
        """
        x = np.array(y_pred).reshape(-1, 1)

        if self.is_logit:
            x = logit(x)
            pred = self.calibration.predict(x)
            pred = expit(pred)

        elif self.is_odds:
            x = x / (1 - x)
            pred = self.calibration.predict(x)
            pred = pred / (pred + 1)
        else:
            pred = self.calibration.predict(x)

        return pred


class DecisionTreeCalibration(BaseEstimator, TransformerMixin):
    """
    Decision Tree Calibration with Logistic Regression Models in Leaves.

    This class calibrates predicted probabilities by fitting a decision tree classifier
    to partition the feature space and then fitting logistic regression models within each leaf.

    Attributes:
        model: The base model used for predictions.
        rs (int): The random state for reproducibility.
        dt_calib (DecisionTreeClassifier): The decision tree classifier used for calibration.
        logits (dict): A dictionary mapping each leaf to its corresponding logistic regression model.
    """

    def __init__(self, model, tree_max_depth=3, rs=17):
        """
        Initializes the DecisionTreeCalibration instance.

        Args:
            model: The base model which includes the used_features attribute and transform method.
            tree_max_depth (int, optional): The maximum depth of the decision tree. Defaults to 3.
            rs (int, optional): The random state for reproducibility. Defaults to 17.
        """
        self.model = model
        self.rs = rs
        self.dt_calib = DecisionTreeClassifier(
            max_depth=tree_max_depth, random_state=rs
        )
        self.logits = {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """
        Fits the decision tree and logistic regression models to the data.

        The decision tree is trained to partition the data based on the used features.
        For each leaf, a logistic regression model is trained to calibrate the predictions.

        Args:
            X (pd.DataFrame): The input features.
            y (pd.Series): The true target values.

        Returns:
            self: Returns the instance itself.
        """
        # Train the decision tree
        self.dt_calib.fit(X[self.model.used_features], y)
        leafs = self.dt_calib.apply(X[self.model.used_features])

        # Train logistic regression for each leaf
        for leaf in np.unique(leafs):
            lr = LogisticRegression(random_state=self.rs)

            X_sub = X[leafs == leaf]
            y_pred_sub = self.model.transform(X_sub)
            y_sub = y[leafs == leaf]

            lr.fit(y_pred_sub.reshape(-1, 1), y_sub)
            self.logits[leaf] = lr

        return self

    def transform(self, X: pd.DataFrame):
        """
        Transforms the input features using the fitted calibration models.

        The method applies the decision tree to determine the leaf for each sample and then
        applies the corresponding logistic regression model to calibrate the predictions.

        Args:
            X (pd.DataFrame): The input features to be calibrated.

        Returns:
            pd.Series: The calibrated predicted probabilities.
        """
        pred_df = pd.DataFrame(
            {
                "y_pred": self.model.transform(X),
                "leaf": self.dt_calib.apply(X[self.model.used_features]),
            },
            index=X.index,
        )

        y_calib = pd.Series(dtype=float)

        # Apply the corresponding logistic regression model for each leaf
        for lf in np.unique(pred_df.leaf):
            idx_sub = pred_df[pred_df.leaf == lf].index
            y_pred_sub = np.array(pred_df[pred_df.leaf == lf].y_pred).reshape(-1, 1)

            y_calib_sub = pd.Series(
                self.logits[lf].predict_proba(y_pred_sub)[:, 1], index=idx_sub
            )

            y_calib = y_calib.append(y_calib_sub)

        return y_calib