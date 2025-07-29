import pandas as pd
from typing import List, Dict, Optional
from dreamml.data._dataset import DataSet

from dreamml.pipeline.fitter import FitterBase
from dreamml.utils import ValidationType


class FitterClustering(FitterBase):
    """A fitter class specialized for clustering algorithms.

    This class extends the FitterBase to provide training and evaluation
    mechanisms specifically tailored for clustering models within the dreamml_base pipeline.
    """

    def __init__(self):
        """Initializes the FitterClustering with a holdout validation type.

        Sets the validation strategy to HOLDOUT by default.
        """
        self.validation_type = ValidationType.HOLDOUT

    @staticmethod
    def _fit_final_model(
        estimator,
        data: Dict,
    ):
        """Fits the estimator on the training data and evaluates it.

        This static method trains the provided estimator using the training subset
        of the data and then evaluates its performance.

        Args:
            estimator: The machine learning model to be trained.
            data (Dict): A dictionary containing the training and evaluation datasets.

        Returns:
            The trained estimator after fitting and evaluation.

        Raises:
            Any exception raised by estimator.fit or estimator.evaluate_and_print.
        """
        estimator.fit(data["train"])
        estimator.evaluate_and_print(**data)
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
        """Trains the estimator using the provided dataset and evaluation metric.

        Retrieves the evaluation set from the data storage, fits the estimator
        using the training data, and returns the trained estimator along with
        a list of estimators.

        Args:
            estimator: The machine learning model to be trained.
            data_storage (DataSet): The dataset storage containing training and evaluation data.
            metric (callable): The evaluation metric to assess model performance.
            used_features (List, optional): List of feature names to be used for training. Defaults to None.
            sampling_flag (bool, optional): Flag indicating whether to perform sampling. Defaults to None.
            vectorization_name (Optional[str], optional): Name of the vectorization strategy to use. Defaults to None.

        Returns:
            Tuple containing:
                - estimator: The trained machine learning model.
                - estimators (List): A list containing the trained estimator.
                - None: Placeholder for additional return values if needed.

        Raises:
            Any exception raised during data retrieval or model training.
        """
        data: Dict = data_storage.get_eval_set(vectorization_name=vectorization_name)
        estimator = self._fit_final_model(estimator, data)
        estimators = [estimator]
        return estimator, estimators, None

    def get_validation_target(self, data_storage: DataSet):
        """Retrieves the validation target from the data storage.

        This method is intended to extract the target variable used for validation purposes.

        Args:
            data_storage (DataSet): The dataset storage containing validation data.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
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
        """Calculates feature importance based on the trained estimators.

        This method computes the importance of each feature used in the model by
        analyzing the trained estimators and the provided dataset.

        Args:
            estimators: The trained machine learning models.
            data_storage (DataSet): The dataset storage containing data for importance calculation.
            used_features (List, optional): List of feature names used in training. Defaults to None.
            splitter_df (pd.DataFrame, optional): DataFrame used for splitting the dataset. Defaults to None.
            fraction_sample (float, optional): Fraction of the dataset to sample for importance calculation. Defaults to 1.
            vectorization_name (Optional[str], optional): Name of the vectorization strategy used. Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame containing feature importance scores.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError