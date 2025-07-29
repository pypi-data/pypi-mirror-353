"""
Module implementing the interface for machine learning models.

Available entities:
- BoostingBaseModel: API for ML models.
- BaseClassifier: Implementation of a base classifier.
- BaseRegressor: Implementation of a base regressor.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from copy import deepcopy

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.exceptions import NotFittedError
from sklearn.metrics import roc_auc_score

from dreamml.logging import get_logger
from dreamml.utils.errors import MissedColumnError
from dreamml.features.feature_selection._permutation_importance import (
    calculate_permutation_feature_importance,
)

_logger = get_logger(__name__)


class BoostingBaseModel(ABC, BaseEstimator, TransformerMixin):
    """
    API for machine learning models to be used in DS-Template.

    This abstract base class serves as a foundation for implementing specific models.
    It contains common methods that are utilized by any type of model.

    Args:
        params (dict): Dictionary of model hyperparameters.
        used_features (List[str]): List of features used for training.
        categorical_features (Optional[List[str]], optional): List of categorical features.
            Defaults to None.
        lr_reduce (Optional[int], optional): Number of possible learning rate reductions.
            Defaults to 0.

    Attributes:
        params (dict): Model hyperparameters.
        used_features (List[str]): Features used for training.
        categorical_features (Optional[List[str]]): Categorical features used for training.
        estimator (Optional[callable]): Instance of the trained model.
        lr_reduce (int): Number of remaining learning rate reductions.
    """

    def __init__(
        self,
        params: dict,
        used_features: List[str],
        categorical_features: Optional[List[str]] = None,
        lr_reduce: Optional[int] = 0,
    ):
        self.params = deepcopy(params)
        self.used_features = used_features
        if categorical_features:
            self.categorical_features = list(
                set(categorical_features) & set(used_features)
            )
        else:
            self.categorical_features = None
        self.estimator = None
        self.lr_reduce = lr_reduce

    def validate_input_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Validates the input data to ensure all required features are present.

        If any expected features are missing from the dataset, a MissedColumnError is raised.

        Args:
            data (pd.DataFrame): Feature matrix to validate.

        Returns:
            pd.DataFrame: Validated feature matrix containing only the required features.

        Raises:
            MissedColumnError: If any required features are missing from the input data.
        """
        if self.used_features:
            missed_features = list(set(self.used_features) - set(data.columns))
            if missed_features:
                raise MissedColumnError(f"Missed {list(missed_features)} columns.")
            return data[self.used_features]

        return data

    @property
    def check_is_fitted(self):
        """
        Checks if the model has been fitted.

        Raises:
            NotFittedError: If the model is not yet fitted.

        Returns:
            bool: True if the model is fitted.
        """
        if not bool(self.estimator):
            msg = (
                "This estimator is not fitted yet. Call 'fit' with"
                " appropriate arguments before using this estimator."
            )
            raise NotFittedError(msg)
        return True

    @abstractmethod
    def fit(self, data: pd.DataFrame, target: pd.Series, *eval_set) -> None:
        """
        Abstract method to train the model on the provided data and target.

        Args:
            data (pd.DataFrame): Feature matrix for training.
            target (pd.Series): Target vector for training.
            *eval_set: Additional evaluation datasets.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        pass

    @abstractmethod
    def transform(self, data: pd.DataFrame) -> None:
        """
        Abstract method to apply the model to the provided data.

        Args:
            data (pd.DataFrame): Feature matrix to transform.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        pass


class BaseClassifier(BoostingBaseModel):
    """
    Base classifier for DS-Template.

    This class serves as a foundation for implementing specific classifiers.
    It contains common methods that are used by any classifier implementation
    and are independent of the specific details of the classifier.

    Args:
        params (dict): Dictionary of model hyperparameters.
        used_features (List[str]): List of features used for training.
        categorical_features (Optional[List[str]], optional): List of categorical features.
            Defaults to None.

    Attributes:
        params (dict): Model hyperparameters.
        used_features (List[str]): Features used for training.
        categorical_features (Optional[List[str]]): Categorical features used for training.
        estimator (Optional[callable]): Instance of the trained model.
        lr_reduce (int): Number of remaining learning rate reductions.
    """

    def evaluate_model(self, **eval_sets) -> None:
        """
        Evaluates the model's performance using the GINI metric on the provided evaluation sets.

        Args:
            **eval_sets (Dict[str, Tuple[pd.DataFrame, pd.Series]]): 
                Arbitrary number of evaluation datasets where each key is the name of the 
                dataset and the value is a tuple containing the feature matrix and 
                the true target vector.

        Raises:
            ValueError: If the ROC AUC score cannot be computed.
        """
        for sample in eval_sets:
            data, target = eval_sets[sample]
            prediction = self.transform(data)

            try:
                score = roc_auc_score(target, prediction)
                score = 2 * score - 1
                score = 100 * score
            except ValueError:
                score = 0

            _logger.info(f"{sample}-score:\t GINI = {round(score, 2)}")

    def feature_importance(self, data: pd.DataFrame, target: pd.Series) -> pd.DataFrame:
        """
        Calculates feature importance based on permutation.

        The importance is calculated if `self.eval_set` is defined and the `fit` method 
        has been applied to the model. If `self.eval_set` is not defined, a ValueError is raised.

        Args:
            data (pd.DataFrame): Feature matrix (training data).
            target (pd.Series): Target vector.

        Returns:
            pd.DataFrame: DataFrame containing the feature importance scores.
        """
        return calculate_permutation_feature_importance(
            self, roc_auc_score, data[self.used_features], target
        )

    def refit(self, data: pd.DataFrame, target: pd.Series, *eval_set) -> None:
        """
        Reduces the learning rate and retrains the model.

        This method decreases the learning rate and reapplies the `fit` method to the model.

        Args:
            data (pd.DataFrame): Feature matrix (training data).
            target (pd.Series): Target vector.
            *eval_set: Additional evaluation datasets.

        Raises:
            NotFittedError: If the model has not been fitted yet.
        """
        self.lr_reduce -= 1
        _logger.info(25 * "-" + "overfitting" + 25 * "-")
        _logger.info(
            "learning_rate_before = ",
            self.params["learning_rate"],
            " learning_rate_after = ",
            self.params["learning_rate"] / 2,
        )
        self.params["learning_rate"] /= 2
        self.fit(data, target, *eval_set)