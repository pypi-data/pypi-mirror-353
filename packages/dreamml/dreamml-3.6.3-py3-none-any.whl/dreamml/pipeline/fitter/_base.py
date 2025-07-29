from abc import ABC
import abc
from typing import List, Optional

import pandas as pd

from dreamml.data._dataset import DataSet


class FitterBase(ABC):
    """Base class for Fitter.

    This abstract base class defines the interface for fitting models, including methods
    for training and calculating feature importance.
    """

    validation_type = None

    @staticmethod
    @abc.abstractmethod
    def get_validation_target(
        data_storage: DataSet, vectorization_name: Optional[str] = None
    ) -> pd.Series:
        """Retrieve true values for metric calculation.

        Since this class handles all validation data, this method returns the true
        target values necessary for evaluating the model's performance.

        Args:
            data_storage (DataSet): An instance of the data storage class.
            vectorization_name (Optional[str], optional): The name of the vectorization
                algorithm to be used. Defaults to None.

        Returns:
            pd.Series: The true target values for metric calculation.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def train(
        self,
        estimator,
        data_storage: DataSet,
        metric: callable,
        used_features: List = None,
        sampling_flag: bool = None,
        vectorization_name: Optional[str] = None,
    ):
        """Train the estimator using the provided data and parameters.

        This is the main function for initiating the training module. It trains the
        estimator on the dataset and evaluates its performance using the specified metric.

        Args:
            estimator (dreamml.modeling.models.estimators.boosting_base.BoostingBaseModel):
                An instance of the model to be trained.
            data_storage (DataSet): An instance of the data storage class.
            metric (callable): The metric function to evaluate model performance.
            used_features (List, optional): A list of features to be used for training.
                Defaults to None.
            sampling_flag (bool, optional): Indicates whether sampling should be used
                (useful for permutation stage with large datasets). Defaults to None.
            vectorization_name (Optional[str], optional): The name of the vectorization
                algorithm to be used. Defaults to None.

        Returns:
            final_estimator (dreamml.modeling.models.estimators.boosting_base.BoostingBaseModel):
                The final model trained on the average number of iterations across all
                folds, adjusted by a coefficient.
            cv_estimators (None):
                Placeholder for compatibility with FitterCV.
            used_features (List): The list of features used for training.
            vectorization_name (Optional[str]): The name of the vectorization algorithm used.
            predictions (pd.Series): The model's predictions on the validation dataset.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def calculate_importance(
        self,
        estimators,
        data_storage: DataSet,
        used_features: List = None,
        splitter_df: pd.DataFrame = None,
        fraction_sample: float = 1,
        vectorization_name: Optional[str] = None,
    ) -> pd.DataFrame:
        """Calculate feature importance based on cross-validation.

        This method evaluates the importance of features by training the estimator(s)
        across different folds and aggregating the results.

        Args:
            estimators (List[dreamml.modeling.models.estimators.boosting_base.BoostingBaseModel] or dreamml.modeling.models.estimators.boosting_base.BoostingBaseModel):
                A list of estimator instances to train, or a single estimator instance
                that will be replicated across all folds.
            data_storage (DataSet): An instance of the data storage class.
            used_features (List, optional): A list of features to be used for calculating
                importance. Defaults to None.
            splitter_df (pd.DataFrame, optional): A DataFrame used for splitting the data.
                Defaults to None.
            fraction_sample (float, optional): The fraction of observations from the data
                to be used for evaluating feature importance. Defaults to 1.0.
            vectorization_name (Optional[str], optional): The name of the vectorization
                algorithm to be used. Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame containing the feature importance scores.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError