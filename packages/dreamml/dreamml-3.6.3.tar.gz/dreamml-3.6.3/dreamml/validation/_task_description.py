import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from ._base import BaseTest


class TaskDescriptionTest(BaseEstimator, TransformerMixin, BaseTest):
    """
    Provides a detailed description of the business task and the complete pipeline used.

    Args:
        artifacts_config (dict): Dictionary containing artifacts necessary for building the validation report.
        validation_test_config (dict): Dictionary containing parameters for validation tests.

    Attributes:
        used_features (List[str]): List of features used.
        categorical_features (List[str]): List of categorical features.
        validation_test_config (dict): Configuration for validation tests.
    """

    def __init__(self, artifacts_config: dict, validation_test_config: dict):
        self.used_features = artifacts_config["used_features"]
        self.categorical_features = artifacts_config.get("categorical_features", list())
        self.validation_test_config = validation_test_config

    def _create_description(self, **data):
        """
        Creates a DataFrame containing the stages of the pipeline and their descriptions.

        Args:
            **data: Arbitrary keyword arguments.

        Returns:
            pd.DataFrame: A DataFrame with stage names and their corresponding descriptions.

        Raises:
            KeyError: If required keys are missing in the data.
            ValueError: If data provided is invalid.
        """
        _stagies = [
            "Data Collection",
            "Dataset Splitting into Train/Validation/Test",
            "Missing Value Handling",
            "Categorical Feature Processing",
            "Feature Selection",
            "Model Building",
            "Model Hyperparameter Optimization",
        ]
        _descriptions = [
            "<Attach the script for collecting the training dataset>",
            (
                "<By default, dreamml_base splits the data into three parts: "
                "train, valid, test with a ratio of 60%, 20%, 20%.>"
            ),
            (
                "<By default, dreamml_base fills missing values for categorical "
                "features with 'NA'. Missing values for numerical features are not filled.>"
            ),
            (
                "<By default, dreamml_base processes categorical features using an enhanced LabelEncoder, "
                "after which features are passed as categorical to models that can handle categories.>"
            ),
            (
                "<By default, dreamml_base uses the following feature selection pipeline: "
                "Gini -> PSI -> Permutation -> ShapUplift -> ShapDelta.>"
            ),
            (
                "<By default, dreamml_base uses models such as LightGBM, XGBoost, CatBoost, "
                "and WhiteBox AutoML.>"
            ),
            (
                "<By default, Bayesian Optimization is used in dreamml_base for "
                "model hyperparameter optimization.>"
            ),
        ]
        stats = pd.DataFrame({"Stage Name": _stagies, "Description": _descriptions})
        return stats


class BusinessCaseDescription(BaseEstimator, TransformerMixin, BaseTest):
    """
    Provides a description of the business case being addressed.

    Args:
        artifacts_config (dict): Dictionary containing artifacts necessary for building the validation report.
        validation_test_config (dict): Dictionary containing parameters for validation tests.

    Attributes:
        used_features (List[str]): List of features used.
        categorical_features (List[str]): List of categorical features.
        validation_test_config (dict): Configuration for validation tests.
    """

    def __init__(self, artifacts_config: dict, validation_test_config: dict):
        self.used_features = artifacts_config["used_features"]
        self.categorical_features = artifacts_config.get("categorical_features", list())
        self.validation_test_config = validation_test_config

    def _create_description(self, **data):
        """
        Creates a DataFrame containing parameters of the business case and their descriptions.

        Args:
            **data: Arbitrary keyword arguments.

        Returns:
            pd.DataFrame: A DataFrame with parameters and their corresponding descriptions.

        Raises:
            KeyError: If required keys are missing in the data.
            ValueError: If data provided is invalid.
        """
        stats = pd.DataFrame()
        stats["Parameter"] = [
            "Business Task",
            "Task Description",
            "Data Collection Dates",
            "Observation Selection",
            "Target Variable Description",
            "Used ML Algorithm",
        ]
        stats["train"] = "1"
        stats["valid"] = "1"
        stats["test"] = "1"
        stats["Out-Of-Time"] = "1"
        return stats