import pandas as pd
from typing import List, Dict, Optional
from dreamml.data._dataset import DataSet
from dreamml.pipeline.fitter import FitterBase

from dreamml.logging import get_logger

_logger = get_logger(__name__)


class FitterAMTSab(FitterBase):
    """A fitter class for training and managing AMT Sab models.

    This class provides methods to train estimators, retrieve validation targets,
    and calculate feature importances for AMT Sab models. It inherits from
    FitterBase and extends its functionality with specific implementations.

    Args:
        None

    Attributes:
        None
    """

    def __init__(self):
        """Initializes the FitterAMTSab instance.

        Args:
            None

        Returns:
            None
        """
        pass

    @staticmethod
    def _fit(estimator, data: Dict):
        """Fits the provided estimator using the given data.

        This static method trains the estimator on the provided dataset.

        Args:
            estimator: The machine learning estimator to be trained.
            data (Dict): A dictionary containing the training data.

        Returns:
            None

        Raises:
            Exception: If the estimator fails to fit the data.
        """
        estimator.fit(data)
        # estimator.evaluate_and_print(data)

    def train(
        self,
        estimator,
        data_storage: DataSet,
        metric: callable,
        used_features: List = None,
        sampling_flag: bool = None,
        vectorization_name: Optional[str] = None,
    ):
        """Trains the estimator using the provided dataset and parameters.

        This method initiates the training process for the estimator using the
        training data retrieved from the data storage. It logs the start of
        training and returns the trained estimator along with a list of estimators.

        Args:
            estimator: The machine learning estimator to be trained.
            data_storage (DataSet): The data storage containing datasets.
            metric (callable): A callable metric function for evaluation.
            used_features (List, optional): A list of feature names to be used.
            sampling_flag (bool, optional): A flag indicating whether sampling is used.
            vectorization_name (Optional[str], optional): The name of the vectorization process.

        Returns:
            tuple: A tuple containing the trained estimator, a list of estimators,
                   and None.

        Raises:
            Exception: If the training process fails.
        """
        data = data_storage.get_eval_set()
        train_data = data["nbeats_train_data"]

        _logger.info(
            f"Initial training of the '{estimator.model_name}' model has been launched"
        )
        self._fit(estimator, train_data)

        estimators = [estimator]
        return estimator, estimators, None

    def get_validation_target(self, data_storage: DataSet):
        """Retrieves the validation target from the data storage.

        This method is intended to extract the target variable for validation
        purposes from the provided data storage.

        Args:
            data_storage (DataSet): The data storage containing datasets.

        Returns:
            None

        Raises:
            NotImplementedError: This method is not implemented.
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
        """Calculates feature importances using the provided estimators and data.

        This method is intended to compute the importance of each feature in the
        dataset based on the trained estimators. It processes the data according
        to the specified parameters and returns a DataFrame of feature importances.

        Args:
            estimators: A list of trained machine learning estimators.
            data_storage (DataSet): The data storage containing datasets.
            used_features (List, optional): A list of feature names to consider.
            splitter_df (pd.DataFrame, optional): A DataFrame used for splitting data.
            fraction_sample (float, optional): The fraction of data to sample for importance calculation.
            vectorization_name (Optional[str], optional): The name of the vectorization process.

        Returns:
            pd.DataFrame: A DataFrame containing feature importances.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError