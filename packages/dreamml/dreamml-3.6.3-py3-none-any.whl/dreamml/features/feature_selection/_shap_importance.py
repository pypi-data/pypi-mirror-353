from copy import deepcopy
from typing import Union
import shap
import numpy as np
import pandas as pd
import xgboost as xgb
from tqdm.auto import tqdm
from sklearn.base import BaseEstimator, TransformerMixin

from dreamml.modeling.metrics import BaseMetric
from dreamml.modeling.metrics.metrics_mapping import metrics_mapping

from dreamml.modeling.models.estimators import PyBoostModel


class ShapFeatureSelection(BaseEstimator, TransformerMixin):
    """
    Feature selection based on SHAP values and uplift testing.

    This transformer calculates SHAP values for the provided model and then trains
    models on subsets of features, ranging from the most important to the least important.
    After training all models, it selects the model that meets the specified quality change
    within the given range.

    Args:
        estimator: A trained instance of the model.
        metric_name: The name of the metric to be used for evaluation.
        max_delta (int or float, optional): The maximum allowable absolute difference
            between the quality metric of the original estimator and the uplift-tested model.
            Defaults to 0.01.
        maximize (bool, optional): Flag indicating whether to maximize the quality metric.
            If True, the metric is to be maximized; otherwise, it is to be minimized.
            Defaults to True.
        relative (bool, optional): Flag indicating whether to use relative difference
            for the quality metric comparison. Defaults to False.
        metric_params (dict, optional): Additional parameters for the metric.
            Defaults to None.
        task (str, optional): The task type, e.g., "binary". Defaults to "binary".

    Attributes:
        estimator: The estimator provided during initialization.
        max_delta: The maximum allowable delta for the quality metric.
        used_features: List of features used by the estimator.
        metric: The metric instance used for evaluation.
        task: The task type.
        metric_params: Additional parameters for the metric.
        maximize: Flag indicating whether to maximize the metric.
        relative: Flag indicating whether to use relative difference for metric comparison.
        scores: Dictionary to store scores for different feature subsets after transformation.
    
    Raises:
        ValueError: If an error occurs during SHAP value calculation or model fitting.
    """

    def __init__(
        self,
        estimator,
        metric_name,
        max_delta: Union[int, float] = 0.01,
        maximize: bool = True,
        relative: bool = False,
        metric_params: dict = None,
        task: str = "binary",
    ):
        self.estimator = estimator
        if self.estimator.categorical_features is None:
            self.estimator.categorical_features = []
        self.max_delta = max_delta
        self.used_features = estimator.used_features
        self.metric: BaseMetric = metrics_mapping.get(metric_name)(
            task=task, **metric_params
        )
        self.task = task
        self.metric_params = metric_params
        self.maximize = maximize
        self.relative = relative

    def _calculate_shap_values(self, X: pd.DataFrame) -> list:
        """
        Calculate SHAP values for the estimator instance.

        Args:
            X (pd.DataFrame): Feature matrix for calculating SHAP values.

        Returns:
            list or numpy.array: Array of SHAP values.

        Raises:
            ValueError: If SHAP value calculation fails.
        """
        if isinstance(self.estimator, PyBoostModel):
            explainer = shap.PermutationExplainer(
                self.estimator, masker=shap.maskers._tabular.Tabular(X[self.used_features])
            )
        else:
            explainer = shap.TreeExplainer(self.estimator.estimator)

        try:
            if isinstance(explainer, shap.PermutationExplainer):
                shap_values = explainer.shap_values(
                    X=X[self.used_features], npermutations=5
                )
            else:
                shap_values = explainer.shap_values(X=X[self.used_features])
        except ValueError:
            X_dmatrix = xgb.DMatrix(X[self.used_features])
            shap_values = explainer.shap_values(X=X_dmatrix)

        if isinstance(shap_values, list):
            return shap_values[0]
        return shap_values

    def _calculate_feature_importance(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate and sort feature importance based on SHAP values.

        Args:
            X (pd.DataFrame): Feature matrix for calculating SHAP values.

        Returns:
            pd.DataFrame: DataFrame with features sorted by importance in descending order.
        
        Raises:
            ValueError: If feature importance calculation fails.
        """
        shap_values = self._calculate_shap_values(X=X)
        importance = pd.DataFrame(
            {
                "feature-name": self.used_features,
                "importance": np.abs(shap_values.mean(axis=0)),
            }
        )
        importance = importance.sort_values(by="importance", ascending=False)
        importance = importance.reset_index(drop=True)

        return importance

    def _calculate_uplift_iteration(self, X, y, features, *eval_set):
        """
        Calculate a single iteration of the uplift test.

        Args:
            X (pd.DataFrame): Feature matrix for training the model.
            y (pd.Series): Target variable for training the model.
            features (List[str]): List of features to train the model with.
            eval_set (Tuple[pd.DataFrame, pd.Series]): Tuple containing validation features
                and validation target.

        Returns:
            float: The quality metric value on the evaluation set.
        
        Raises:
            ValueError: If model fitting or prediction fails.
        """
        estimator = deepcopy(self.estimator)
        estimator.used_features = features
        estimator.categorical_features = list(
            set(estimator.categorical_features) & set(features)
        )
        estimator.fit(X, y, *eval_set)

        y_pred = estimator.transform(eval_set[0])

        score = self.metric(eval_set[1], y_pred)

        return score

    def transform(self, X, y, *eval_set):
        """
        Perform feature selection based on SHAP values and uplift testing.

        Args:
            X (pd.DataFrame): Feature matrix for calculating feature importance.
            y (pd.Series): Target variable for training the models.
            eval_set (Tuple[pd.DataFrame, pd.Series]): Tuple containing evaluation features
                and evaluation target.

        Returns:
            List[str]: List of selected features that meet the quality change criteria.
        
        Raises:
            ValueError: If transformation fails due to invalid inputs or model issues.
        """
        self.scores = {}
        importance = self._calculate_feature_importance(X)
        base_pred = self.estimator.transform(eval_set[0])
        base_score = self.metric(eval_set[1], base_pred)

        for num in tqdm(range(len(importance))):
            used_features = importance.loc[:num, "feature-name"]
            used_features = used_features.values.tolist()
            score = self._calculate_uplift_iteration(X, y, used_features, *eval_set)
            self.scores[num + 1] = [used_features, score]
            # TODO problem: relative scale for regression metrics. Delta is 0.001, not 1.0

            if self.relative and self.maximize:
                # Regression, relative difference
                # Maximizing the metric
                if (base_score - score) / base_score <= self.max_delta:
                    return used_features
            elif self.relative:
                # Regression, relative difference
                # Minimizing the metric
                if (score - base_score) / base_score <= self.max_delta:
                    return used_features
            else:
                if base_score - score <= self.max_delta:
                    return used_features


def finetune_features(shap_transformer: callable, threshold: float) -> list:
    """
    Final feature selection based on the relative improvement in quality during uplift testing.

    Args:
        shap_transformer (callable): Trained transformer for feature selection based on SHAP.
            Expected to be an instance of ShapFeatureSelection.
        threshold (float): Threshold value for selecting features.
            By default, it is assumed that the threshold is shap_threshold / 2.

    Returns:
        List[str]: List of selected features that exceed the specified threshold.
    
    Raises:
        ValueError: If feature finetuning fails due to invalid inputs or transformer issues.
    """
    num_features = len(shap_transformer.scores)
    total_features = shap_transformer.scores[num_features]
    total_features = total_features[0]

    scores = pd.DataFrame(shap_transformer.scores).T
    scores["delta"] = scores[1].diff().fillna(1)
    scores["features"] = total_features

    selected_features = scores[scores["delta"] > threshold]
    selected_features = selected_features["features"].values.tolist()

    return selected_features