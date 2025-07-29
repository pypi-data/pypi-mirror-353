import pandas as pd
from typing import List, Dict, Optional
from dreamml.data._dataset import DataSet

from dreamml.pipeline.fitter import FitterBase
from dreamml.utils import ValidationType
from dreamml.utils.splitter import concatenate_all_samples


class FitterIsolationForest(FitterBase):
    """Fitter for the Isolation Forest algorithm.

    This class provides methods to train and evaluate an Isolation Forest model
    using the provided dataset and configuration.
    """

    def __init__(self):
        """Initialize the FitterIsolationForest with a holdout validation type.

        Sets the validation_type attribute to ValidationType.HOLDOUT.
        """
        self.validation_type = ValidationType.HOLDOUT

    @staticmethod
    def _fit_final_model(
        estimator,
        data: pd.DataFrame,
    ):
        """Fit the final Isolation Forest model using the provided estimator and data.

        Args:
            estimator: The Isolation Forest estimator to be fitted.
            data (pd.DataFrame): The data used to train the estimator.

        Returns:
            The fitted estimator.

        Raises:
            ValueError: If the estimator fails to fit the data.
        """
        estimator.fit(data, None, None)
        return estimator

    def train(
        self,
        estimator,
        data_storage: DataSet,
        metric: callable,
        used_features: List = None,
        sampling_flag: bool = None,
        vectorization_name: Optional[str] = None,
    ):
        """Train the Isolation Forest model using the provided data storage and estimator.

        Args:
            estimator: The Isolation Forest estimator to be trained.
            data_storage (DataSet): The dataset storage containing the evaluation set.
            metric (callable): The metric used to evaluate the model's performance.
            used_features (List, optional): List of features to be used for training.
                Defaults to None.
            sampling_flag (bool, optional): Flag indicating whether sampling should be applied.
                Defaults to None.
            vectorization_name (Optional[str], optional): The name of the vectorization
                to be used. Defaults to None.

        Returns:
            tuple: A tuple containing the trained estimator, None, and the predictions
                made by the estimator.

        Raises:
            ValueError: If the data cannot be concatenated or the estimator fails to fit.
        """
        data: Dict[pd.DataFrame, None] = data_storage.get_eval_set(
            vectorization_name=vectorization_name
        )
        all_data = concatenate_all_samples(data)
        estimator = self._fit_final_model(estimator, all_data)
        predictions = estimator.transform(all_data)

        return estimator, None, predictions

    def get_validation_target(self, data_storage: DataSet):
        """Retrieve the validation target from the data storage.

        Args:
            data_storage (DataSet): The dataset storage from which to retrieve the validation target.

        Raises:
            NotImplementedError: Indicates that this method should be implemented by subclasses.
        """
        raise NotImplementedError

    def calculate_importance(
        self,
        estimators,
        data_storage: DataSet,
        used_features: List = None,
        splitter_df: pd.DataFrame = None,
        fraction_sample: float = 1,
        vectorization_name: Optional[str] = None,
    ) -> pd.DataFrame:
        """Calculate feature importance using the provided estimators and data storage.

        Args:
            estimators: The trained estimators used to calculate feature importance.
            data_storage (DataSet): The dataset storage containing the data for importance calculation.
            used_features (List, optional): List of features to consider for importance calculation.
                Defaults to None.
            splitter_df (pd.DataFrame, optional): DataFrame used to split the data. Defaults to None.
            fraction_sample (float, optional): Fraction of the sample to use for calculation.
                Defaults to 1.
            vectorization_name (Optional[str], optional): The name of the vectorization to be used.
                Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame containing the calculated feature importances.

        Raises:
            NotImplementedError: Indicates that this method should be implemented by subclasses.
        """
        raise NotImplementedError