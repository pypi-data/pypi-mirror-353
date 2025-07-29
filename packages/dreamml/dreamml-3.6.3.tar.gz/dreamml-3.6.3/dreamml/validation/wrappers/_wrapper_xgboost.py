from typing import Optional, List
import json

import shap
import xgboost
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


def _create_xgb_params(booster: xgboost.core.Booster):
    """
    Creates a dictionary of XGBoost parameters from a Booster object.

    Args:
        booster (xgboost.core.Booster): The XGBoost Booster object.

    Returns:
        dict: A dictionary containing XGBoost parameters.

    Raises:
        json.JSONDecodeError: If the Booster configuration cannot be decoded.
        KeyError: If expected keys are missing in the Booster configuration.
    """
    params = json.loads(booster.save_config())
    tree_params = params["learner"]["gradient_booster"]
    tree_params = tree_params["updater"]["grow_colmaker"]["train_param"]

    params = {
        "objective": params["learner"]["objective"]["name"],
        "base_score": params["learner"]["learner_model_param"]["base_score"],
        "booster": params["learner"]["learner_train_param"]["booster"],
        "colsample_bylevel": tree_params["colsample_bylevel"],
        "colsample_bynode": tree_params["colsample_bynode"],
        "colsample_bytree": tree_params["colsample_bytree"],
        "gamma": tree_params["gamma"],
        "gpu_id": params["learner"]["generic_param"]["gpu_id"],
        "learning_rate": tree_params["learning_rate"],
        "max_delta_step": tree_params["max_delta_step"],
        "max_depth": tree_params["max_depth"],
        "min_child_weight": tree_params["min_child_weight"],
        "monotone_constraints": tree_params["monotone_constraints"],
        "n_estimators": booster.best_iteration,
        "n_jobs": params["learner"]["generic_param"]["n_jobs"],
        "num_parallel_tree": params["learner"]["gradient_booster"][
            "gbtree_train_param"
        ]["num_parallel_tree"],
        "reg_alpha": tree_params["reg_alpha"],
        "reg_lambda": tree_params["reg_lambda"],
        "random_state": params["learner"]["generic_param"]["random_state"],
        "scale_pos_weight": params["learner"]["objective"]["reg_loss_param"][
            "scale_pos_weight"
        ],
        "subsample": tree_params["subsample"],
        "tree_method": params["learner"]["gradient_booster"]["gbtree_train_param"][
            "tree_method"
        ],
        "validate_parameters": params["learner"]["generic_param"][
            "validate_parameters"
        ],
    }
    return params


class _XGBoostWrapper(BaseEstimator, TransformerMixin):
    """
    A universal estimator wrapper for XGBoost models.
    Used for calculating validation tests and preparing reports.

    Args:
        estimator (callable): An estimator object after applying the `fit` method.
        used_features (Optional[List[str]], optional): List of used feature names. Defaults to None.
        categorical_features (Optional[List[str]], optional): List of used categorical feature names. Defaults to None.
        task (str, optional): The type of task, e.g., "binary". Defaults to "binary".
        metric_name (str, optional): The name of the evaluation metric. Defaults to "gini".

    Attributes:
        estimator (callable): The fitted estimator object.
        used_features (Optional[List[str]]): The list of used feature names.
        categorical_features (Optional[List[str]]): The list of used categorical feature names.
        task (str): The type of task.
        metric_name (str): The name of the evaluation metric.
    """

    def __init__(
        self,
        estimator: callable,
        used_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        task: str = "binary",
        metric_name: str = "gini",
    ):
        self.estimator = estimator
        self.used_features = used_features
        self.categorical_features = categorical_features
        self.task = task
        self.metric_name = metric_name

    def _validate_input_data(self, X):
        """
        Prepares the input data for the model by selecting the required features.

        Args:
            X (pd.DataFrame): Feature matrix to be used by the model.

        Returns:
            tuple:
                pd.DataFrame: The transformed feature matrix.
                pd.Index: The feature names used.

        Raises:
            ValueError: If X is not a pandas DataFrame.
            KeyError: If any of the used_features are not present in X.
        """
        if self.used_features:
            X_, feature_names = X[self.used_features], self.used_features
        else:
            X_, feature_names = X.copy(), X.columns

        return X_, feature_names

    @property
    def get_estimator_params(self):
        """
        Retrieves the parameters of the underlying estimator.

        Returns:
            dict: A dictionary of estimator parameters.

        Raises:
            AttributeError: If the estimator does not have the required attributes.
        """
        try:
            params = self.estimator.get_params()
            params["n_estimators"] = self.estimator.n_estimators
        except AttributeError:
            params = _create_xgb_params(self.estimator)

        return params

    def get_shap_importance(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Computes feature importance based on SHAP values.

        Args:
            X (pd.DataFrame): Feature matrix for computing feature importance.

        Returns:
            tuple:
                np.ndarray: SHAP values matrix with shape [n_samples, n_features].
                pd.DataFrame: DataFrame containing feature importance based on SHAP values.

        Raises:
            ValueError: If SHAP values cannot be computed.
            TypeError: If the estimator is not compatible with SHAP.
        """
        # Uncomment and modify the objective if necessary
        # if isinstance(self.estimator, xgboost.core.Booster):
        #     self.estimator.params["objective"] = "binary"
        # else:
        #     self.estimator.get_params()["objective"] = "binary"

        x, feature_names = self._validate_input_data(X)
        if isinstance(self.estimator, xgboost.core.Booster):
            x = xgboost.DMatrix(x)
        explainer = shap.TreeExplainer(self.estimator)
        shap_values = explainer.shap_values(x)

        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        shap_importance = pd.DataFrame(
            {
                "feature": feature_names,
                "importance": np.round(np.abs(shap_values).mean(axis=0), 5),
            }
        )
        shap_importance = shap_importance.sort_values(by="importance", ascending=False)
        shap_importance = shap_importance.reset_index(drop=True)

        return shap_values, shap_importance

    def transform(self, X):
        """
        Applies the model to the input data X to generate predictions.

        Args:
            X (pd.DataFrame): Feature matrix to be used by the model.

        Returns:
            np.ndarray: Model predictions for the input data.

        Raises:
            AttributeError: If the estimator does not have the required prediction methods.
            ValueError: If the input data X is not in the expected format.
        """
        data, _ = self._validate_input_data(X)
        if isinstance(self.estimator, xgboost.core.Booster):
            data = xgboost.DMatrix(data)
        if hasattr(self.estimator, "transform"):
            return self.estimator.transform(data)
        elif hasattr(self.estimator, "predict_proba"):
            predicts = self.estimator.predict_proba(data)
            return (
                predicts
                if self.task in ("multiclass", "multilabel")
                else predicts[:, 1]
            )
        else:
            return self.estimator.predict(data)