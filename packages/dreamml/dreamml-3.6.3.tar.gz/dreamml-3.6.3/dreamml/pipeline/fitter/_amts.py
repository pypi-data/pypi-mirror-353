import pandas as pd
from typing import List, Dict, Optional
from dreamml.data._dataset import DataSet
from dreamml.pipeline.fitter import FitterBase

from dreamml.logging import get_logger

_logger = get_logger(__name__)


class FitterAMTS(FitterBase):
    """FitterAMTS is responsible for training and managing AMTS and NBeats_Revin models.

    This class extends the FitterBase and provides methods to train estimators,
    fit final models, and handle model-specific training procedures.
    """

    def __init__(self):
        """Initialize the FitterAMTS instance."""
        pass

    @staticmethod
    def _fit_final_model(
        estimator,
        data: Dict,
    ):
        """Fit the final model using the provided estimator and data.

        Args:
            estimator: The estimator to be fitted.
            data (Dict): The data used for fitting the final model.

        Returns:
            The fitted estimator.

        Raises:
            Exception: If fitting the estimator fails.
        """
        estimator.fit(data, final=True)
        return estimator

    @staticmethod
    def _fit(estimator, data: Dict):
        """Fit the estimator with the given data and evaluate its performance.

        Args:
            estimator: The estimator to be fitted.
            data (Dict): The data used for fitting the estimator.

        Raises:
            Exception: If fitting or evaluation fails.
        """
        estimator.fit(data)
        if estimator.model_name == "nbeats_revin":
            estimator.evaluate_and_print(data)
        else:
            estimator.evaluate_and_print(**data)

    def train(
        self,
        estimator,
        data_storage: DataSet,
        metric: callable,
        used_features: List = None,
        sampling_flag: bool = None,
        vectorization_name: Optional[str] = None,
    ):
        """Train the estimator using the provided data storage and parameters.

        This method performs initial and final training phases based on the
        model type of the estimator.

        Args:
            estimator: The estimator to be trained.
            data_storage (DataSet): The data storage containing training and final data.
            metric (callable): The metric function used for evaluation.
            used_features (List, optional): The list of features to be used for training. Defaults to None.
            sampling_flag (bool, optional): Flag indicating whether sampling should be applied. Defaults to None.
            vectorization_name (Optional[str], optional): The name of the vectorization method to be used. Defaults to None.

        Returns:
            tuple: A tuple containing the trained estimator, a list of estimators, and None.

        Raises:
            Exception: If training fails at any step.
        """
        data = data_storage.get_eval_set()
        if estimator.model_name == "AMTS":
            train_data = data["amts_train_data"]
            final_data = data["amts_final_data"]
        elif estimator.model_name == "nbeats_revin":
            train_data = data["nbeats_train_data"]
            final_data = data["nbeats_final_data"]

        _logger.info(
            f"Initial training of the '{estimator.model_name}' model has been launched"
        )
        self._fit(estimator, train_data)

        _logger.info(
            f"The final training of the '{estimator.model_name}' model has been launched"
        )
        estimator = self._fit_final_model(estimator, final_data)

        estimators = [estimator]
        return estimator, estimators, None

    def get_validation_target(self, data_storage: DataSet):
        """Retrieve the validation target from the data storage.

        Args:
            data_storage (DataSet): The data storage containing the validation target.

        Raises:
            NotImplementedError: This method is not implemented and should be overridden.
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
        """Calculate feature importance using the provided estimators and data.

        Args:
            estimators: The list of estimators used for calculating importance.
            data_storage (DataSet): The data storage containing the data for importance calculation.
            used_features (List, optional): The list of features to consider. Defaults to None.
            splitter_df (pd.DataFrame, optional): DataFrame used for splitting the data. Defaults to None.
            fraction_sample (float, optional): Fraction of the sample to be used. Defaults to 1.
            vectorization_name (Optional[str], optional): The name of the vectorization method to be used. Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame containing the feature importances.

        Raises:
            NotImplementedError: This method is not implemented and should be overridden.
        """
        raise NotImplementedError