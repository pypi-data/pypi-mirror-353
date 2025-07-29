import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from dreamml.validation._base import BaseTest


class DataStatisticsTest(BaseEstimator, TransformerMixin, BaseTest):
    """
    Calculates statistics for datasets. Includes:

    - Statistics for each dataset (train, valid, etc.):
      number of observations, number of target events,
      and the proportion of target events.

    - Statistics for variables: target variable name,
      number of categorical features, and number of continuous
      features.

    - Statistics for each variable: variable name, number
      of non-missing values, minimum value, mean value,
      maximum value, and 25th, 50th, and 75th percentiles.

    Args:
        artifacts_config (dict): Dictionary containing artifacts necessary for building the validation report.
        validation_test_config (dict): Dictionary containing parameters for validation tests.

    Attributes:
        used_features (List[str]): List of features used.
        categorical_features (List[str]): List of categorical features.
        artifacts_config (dict): Configuration dictionary for artifacts.
        multiclass_artifacts (dict): Configuration dictionary for multiclass artifacts.
    """

    def __init__(
        self,
        artifacts_config: dict,
        validation_test_config: dict,
    ):
        self.used_features = artifacts_config["used_features"]
        self.categorical_features = artifacts_config.get("categorical_features", list())
        self.artifacts_config = artifacts_config
        self.multiclass_artifacts = self.artifacts_config["multiclass_artifacts"]

    def _calculate_samples_stats(self, **eval_sets):
        """
        Calculates statistics for each dataset and target vector.
        Computes the number of observations, number of target events,
        and the proportion of target events.

        Args:
            **eval_sets: 
                Arbitrary keyword arguments representing datasets.
                Each key is the name of the dataset (e.g., 'train', 'valid'),
                and each value is a tuple containing a feature matrix (pandas.DataFrame)
                and a target vector (pandas.Series or pandas.DataFrame).

        Returns:
            pd.DataFrame: A DataFrame containing the calculated statistics with columns
                          ['Dataset', '# Observations', '# Events', '# Event Rate']
                          for binary tasks, or additional columns for multiclass and multilabel tasks.

        Raises:
            ValueError: If the task specified in artifacts_config is not one of
                        ["binary", "multiclass", "multilabel"].
        """
        if self.artifacts_config["task"] in ["binary"]:
            result = {}
            for data_name in eval_sets:
                data, target = eval_sets[data_name]
                result[data_name] = [len(data), np.sum(target), np.mean(target)]
            result = pd.DataFrame(result).T.reset_index()
            result.columns = ["Dataset", "# Observations", "# Events", "# Event Rate"]
            return result.fillna(0)

        elif self.artifacts_config["task"] in ["multiclass", "multilabel"]:
            columns = ["Dataset", "# Observations"]
            if isinstance(eval_sets["train"][1], pd.Series):
                eval_set_cols = eval_sets["train"][1].to_frame().columns.tolist()
            else:
                eval_set_cols = eval_sets["train"][1].columns.tolist()
            columns.extend([f"# Events {class_name}" for class_name in eval_set_cols])
            columns.extend(
                [f"# Event Rate {class_name}" for class_name in eval_set_cols]
            )

            result = {}
            for data_name in eval_sets:
                data, target = eval_sets[data_name]
                if isinstance(eval_sets[data_name][1], pd.Series):
                    target = target.to_frame()

                events = np.sum(target).tolist()
                event_rate = np.mean(target).tolist()
                result[data_name] = [len(data)] + events + event_rate

            result = pd.DataFrame(result).T.reset_index()
            assert len(columns) == result.shape[1]
            result.columns = columns
            return result.fillna(0)

        else:
            raise ValueError('Task must be one of ["binary", "multiclass", "multilabel"]')

    @staticmethod
    def _calculate_variables_stats(**data) -> pd.DataFrame:
        """
        Calculates statistics for variables. Computes the number of
        non-missing values, mean, standard deviation, minimum,
        25th percentile, median, 75th percentile, and maximum
        values for each feature.

        Args:
            **data: 
                Arbitrary keyword arguments representing datasets.
                Each key is the name of the dataset (e.g., 'train', 'valid'),
                and each value is a tuple containing a feature matrix (pandas.DataFrame)
                and a target vector (pandas.Series or pandas.DataFrame).

        Returns:
            pd.DataFrame: A DataFrame containing the calculated statistics for each variable with columns
                          ['Variable name', 'Number of Filled Values', 'AVG-value', 'STD-value',
                           'MIN-value', '25% Percentile Value', '50% Percentile Value',
                           '75% Percentile Value', 'MAX-value'].

        """
        sample_name = next(iter(data))
        x, _ = data[sample_name]

        result = x.describe().T.reset_index()
        result.columns = [
            "Variable name",
            "Number of Filled Values",
            "AVG-value",
            "STD-value",
            "MIN-value",
            "25% Percentile Value",
            "50% Percentile Value",
            "75% Percentile Value",
            "MAX-value",
        ]
        return result.fillna(0)

    def _calculate_variables_types_stats(self, **data) -> pd.DataFrame:
        """
        Calculates statistics based on variable types. Computes the number
        of categorical variables, the number of continuous variables,
        and the name of the target variable.

        Args:
            **data: 
                Arbitrary keyword arguments representing datasets.
                Each key is the name of the dataset (e.g., 'train', 'valid'),
                and each value is a tuple containing a feature matrix (pandas.DataFrame)
                and a target vector (pandas.Series or pandas.DataFrame).

        Returns:
            pd.DataFrame: A DataFrame containing the calculated statistics with columns
                          ['Target Variable', '# Categorical', '# Continuous'].

        """
        sample_name = next(iter(data))
        _, y = data[sample_name]

        if self.multiclass_artifacts is not None:
            target_name = self.multiclass_artifacts["target_name"]
        elif isinstance(y, pd.DataFrame):
            target_name = y.columns.tolist()
        else:
            target_name = y.name

        stats = pd.DataFrame(
            {
                "Target Variable": [target_name],
                "# Categorical": [len(self.categorical_features)],
                "# Continuous": [
                    len(self.used_features) - len(self.categorical_features)
                ],
            }
        )
        return stats.fillna(0)

    def transform(self, **data):
        """
        Transforms the input data by calculating various statistics.

        Args:
            **data: 
                Arbitrary keyword arguments representing datasets.
                Each key is the name of the dataset (e.g., 'train', 'valid'),
                and each value is a tuple containing a feature matrix (pandas.DataFrame)
                and a target vector (pandas.Series or pandas.DataFrame).

        Returns:
            Tuple[pd.DataFrame]: A tuple containing:
                - Sample statistics DataFrame
                - Variable types statistics DataFrame
                - Variable statistics DataFrame
        """
        if self.artifacts_config["task"] == "multiclass":
            data = self.label_binarizing(**self.multiclass_artifacts, **data)

        result = (
            self._calculate_samples_stats(**data),
            self._calculate_variables_types_stats(**data),
            self._calculate_variables_stats(**data),
        )
        return result