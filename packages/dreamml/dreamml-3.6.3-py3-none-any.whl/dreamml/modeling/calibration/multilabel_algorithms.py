from typing import Any
from copy import deepcopy

import pandas as pd
import numpy as np

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.tree import DecisionTreeClassifier


class MultiLabelCalibrationWrapper:
    """
    A wrapper for calibrating multi-label classification predictions.

    This class encapsulates calibration models for each class in a multi-label
    setting, allowing for separate calibration of predicted probabilities.

    Attributes:
        calibration_class (Any): The calibration class to be used for each label.
        calibration_models (dict): A dictionary mapping class names to their
            corresponding calibration models.
        classes (list): List of class names.
    """

    def __init__(self, calibration_class: Any):
        """
        Initializes the MultiLabelCalibrationWrapper with a specified calibration class.

        Args:
            calibration_class (Any): The calibration class to be used for each label.

        """
        self.calibration_class = calibration_class
        self.calibration_models = {}
        self.classes = None

    def fit(self, y_pred: pd.DataFrame, y_true: pd.DataFrame):
        """
        Fits calibration models for each class based on the provided predictions and true labels.

        Args:
            y_pred (pd.DataFrame): The predicted probabilities for each class.
            y_true (pd.DataFrame): The true binary labels for each class.

        Returns:
            self: Returns an instance of MultiLabelCalibrationWrapper.

        Raises:
            ValueError: If y_pred and y_true have mismatched dimensions or classes.
        """
        self.classes = y_true.columns.tolist()
        for class_idx, class_name in enumerate(self.classes):
            y_true_ = y_true.iloc[:, class_idx]
            y_pred_ = y_pred.iloc[:, class_idx]
            calib_model = deepcopy(self.calibration_class).fit(y_pred_, y_true_)
            self.calibration_models[class_name] = calib_model
        return self

    def transform(self, y_pred):
        """
        Transforms the predicted probabilities using the fitted calibration models.

        Args:
            y_pred (pd.DataFrame or np.ndarray): The predicted probabilities to be calibrated.

        Returns:
            pd.DataFrame: A DataFrame containing the calibrated predicted probabilities for each class.

        Raises:
            ValueError: If the calibration models have not been fitted.
            AttributeError: If a calibration model does not have a transform method.
        """
        y_pred_calibrated = pd.DataFrame()
        y_pred = y_pred.values if isinstance(y_pred, pd.DataFrame) else y_pred

        for class_idx, class_name in enumerate(self.classes):
            calib_model = self.calibration_models[class_name]
            y_pred_ = y_pred[:, class_idx]
            y_pred_calibrated[class_name] = calib_model.transform(y_pred_)
        return y_pred_calibrated

    def get_equation(self):
        """
        Retrieves the calibration equations for each class, if available.

        Returns:
            dict: A dictionary mapping class names to their calibration equations.

        Raises:
            AttributeError: If a calibration model does not have a get_equation method.
        """
        equations_by_each_class = {}
        for class_name, calibration in self.calibration_models.items():
            if hasattr(calibration, "get_equation"):
                equations_by_each_class[class_name] = calibration.get_equation()
        return equations_by_each_class


class DecisionTreeCalibrationForMultiLabel(BaseEstimator, TransformerMixin):
    """
    Calibrates multi-label classification models using Decision Trees and CalibratedClassifierCV.

    This transformer performs calibration for multi-label classification tasks by
    applying DecisionTreeClassifier and sklearn's CalibratedClassifierCV to each label.
    It supports parallel processing through the n_jobs parameter.

    Attributes:
        model (Any): The base multi-label classification model to be calibrated.
        rs (int): Random state for reproducibility.
        dt_calib (DecisionTreeClassifier): The Decision Tree classifier used for calibration.
        logits (dict): Stores logits for each class after calibration.
        n_jobs (int): Number of jobs to run in parallel.
        calib_method (str): Calibration method to use ('sigmoid', 'isotonic', etc.).
        classes (list): List of class names.
    """

    def __init__(
        self,
        model,
        tree_max_depth=5,
        rs=17,
        n_jobs: int = None,
        calib_method: str = "sigmoid",
    ):
        """
        Initializes the DecisionTreeCalibrationForMultiLabel with specified parameters.

        Args:
            model (Any): The base multi-label classification model to be calibrated.
            tree_max_depth (int, optional): Maximum depth of the Decision Tree. Defaults to 5.
            rs (int, optional): Random state for reproducibility. Defaults to 17.
            n_jobs (int, optional): Number of jobs to run in parallel. Defaults to None.
            calib_method (str, optional): Calibration method to use ('sigmoid', 'isotonic', etc.). Defaults to "sigmoid".

        """
        self.model = model
        self.rs = rs
        self.dt_calib = DecisionTreeClassifier(
            max_depth=tree_max_depth, random_state=rs
        )

        self.logits = {}
        self.n_jobs = n_jobs
        self.calib_method = calib_method
        self.classes = None

    def fit(self, X: pd.DataFrame, y: pd.DataFrame):
        """
        Fits the calibration models to the data.

        Args:
            X (pd.DataFrame): The input features for calibration.
            y (pd.DataFrame): The true binary labels for each class.

        Returns:
            self: Returns an instance of DecisionTreeCalibrationForMultiLabel.

        Raises:
            ValueError: If X and y have mismatched dimensions or if the model's used_features are not in X.
        """
        self.classes = y.columns.tolist()
        self.dt_calib = OneVsRestClassifier(self.dt_calib, n_jobs=self.n_jobs)
        self.dt_calib = CalibratedClassifierCV(
            base_estimator=self.dt_calib,
            cv=None,
            method=self.calib_method,
        )
        self.dt_calib = MultiOutputClassifier(self.dt_calib, n_jobs=self.n_jobs)
        self.dt_calib.fit(X[self.model.used_features], y)
        return self

    def transform(self, X: pd.DataFrame):
        """
        Transforms the input features by applying the calibrated models to predict probabilities.

        Args:
            X (pd.DataFrame): The input features to be transformed.

        Returns:
            pd.DataFrame: A DataFrame containing the calibrated predicted probabilities for each class.

        Raises:
            NotFittedError: If the calibration models have not been fitted.
            ValueError: If X does not contain the required features.
        """
        y_calib = self.dt_calib.predict_proba(X[self.model.used_features])
        y_calib = np.array([preds_by_class[:, 1] for preds_by_class in y_calib]).T
        return pd.DataFrame(data=y_calib, columns=self.classes)