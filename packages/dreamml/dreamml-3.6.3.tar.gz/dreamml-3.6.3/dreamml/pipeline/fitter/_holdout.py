import pandas as pd
from typing import List, Dict, Optional

from dreamml.features.feature_selection.shap_importance import (
    calculate_shap_feature_importance,
)
from dreamml.data._dataset import DataSet
from dreamml.modeling.metrics import BaseMetric
from dreamml.pipeline.fitter import FitterBase
from dreamml.utils import ValidationType
from dreamml.modeling.models.estimators import BaseModel


class FitterHO(FitterBase):
    """Fitter class using Hold-Out validation strategy.

    This class implements feature importance calculation and model training
    using a hold-out validation approach.

    Attributes:
        validation_type (ValidationType): The type of validation used, set to HOLDOUT.
    """

    validation_type = ValidationType.HOLDOUT

    @staticmethod
    def get_validation_target(
        data_storage: DataSet, vectorization_name: Optional[str] = None
    ) -> pd.Series:
        """Retrieve true target values for metric calculation.

        This method fetches the true target values from the validation data
        stored in the provided DataSet.

        Args:
            data_storage (DataSet): An instance of the data storage class.
            vectorization_name (Optional[str], optional): The name of the
                vectorization to use. Defaults to None.

        Returns:
            pd.Series: The true target values for metric evaluation.

        Raises:
            KeyError: If the 'valid' key is not present in the evaluation set.
            AttributeError: If the data_storage does not have a get_eval_set method.
        """
        data = data_storage.get_eval_set(vectorization_name=vectorization_name)
        _, y_true = data["valid"]

        return y_true

    def calculate_importance(
        self,
        estimators: BaseModel,
        data_storage: DataSet,
        used_features: List = None,
        splitter_df: pd.DataFrame = None,
        fraction_sample: float = 1,
        vectorization_name: Optional[str] = None,
    ) -> pd.DataFrame:
        """Calculate feature importance using SHAP values on hold-out split.

        This method computes the importance of each feature based on SHAP
        values using the provided estimator and training data.

        Args:
            estimators (BaseModel): An instance of the model to train.
            data_storage (DataSet): An instance of the data storage class.
            used_features (List, optional): A list of features to be used.
                Defaults to None.
            splitter_df (pd.DataFrame, optional): A DataFrame for splitting data,
                used for interface consistency with cross-validation. Defaults to None.
            fraction_sample (float, optional): The fraction of data to sample for
                importance calculation. Defaults to 1.0.
            vectorization_name (Optional[str], optional): The name of the
                vectorization to use. Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame containing the importance scores of features.

        Raises:
            ValueError: If no importance column is found in the calculated SHAP values.
            AttributeError: If the estimator does not have a fit or transform method.
        """
        data = data_storage.get_eval_set(
            used_features, vectorization_name=vectorization_name
        )
        x_train, y_train = data["train"]

        importance = calculate_shap_feature_importance(
            estimator=estimators, data=x_train, fraction_sample=fraction_sample
        )

        column_name = [x for x in importance.columns.tolist() if "importance" in x][0]
        importance = importance.sort_values(by=column_name, ascending=False)

        return importance.reset_index(drop=True)

    def train(
        self,
        estimator: BaseModel,
        data_storage: DataSet,
        metric: BaseMetric,
        used_features: List = None,
        sampling_flag: bool = False,
        vectorization_name: Optional[str] = None,
    ):
        """Train the model using the hold-out validation set.

        This method fits the estimator on the training data and evaluates it
        on the validation set. It optionally samples the training data if the
        sampling_flag is set and the dataset is large.

        Args:
            estimator (BaseModel): An instance of the model to train.
            data_storage (DataSet): An instance of the data storage class.
            metric (BaseMetric): The metric used to evaluate the model's performance.
            used_features (List, optional): A list of features to be used for training.
                Defaults to None.
            sampling_flag (bool, optional): Whether to sample the training data.
                Useful for permutation stage with large datasets. Defaults to False.
            vectorization_name (Optional[str], optional): The name of the
                vectorization to use. Defaults to None.

        Returns:
            tuple:
                BaseModel: The trained estimator.
                None: Placeholder for compatibility with FitterCV.
                pd.Series: The model's predictions on the validation set.

        Raises:
            AttributeError: If the estimator does not have fit, transform, or evaluate_and_print methods.
            KeyError: If required keys are missing in the evaluation set.
            ValueError: If training or validation data is not properly provided.
        """
        eval_set = data_storage.get_eval_set(
            used_features, vectorization_name=vectorization_name
        )
        if sampling_flag and data_storage.get_dev_n_samples() >= 250000:
            eval_set["train"] = data_storage.sample(
                used_features, vectorization_name=vectorization_name
            )

        estimator.fit(*eval_set["train"], *eval_set["valid"])
        predictions = estimator.transform(eval_set["valid"][0])

        estimator.evaluate_and_print(**eval_set)

        return estimator, None, predictions