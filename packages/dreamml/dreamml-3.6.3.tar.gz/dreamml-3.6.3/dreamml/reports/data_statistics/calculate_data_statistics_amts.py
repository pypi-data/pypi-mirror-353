import numpy as np
import pandas as pd

from dreamml.configs.config_storage import ConfigStorage


class CalculateDataStatisticsAMTS:
    """Calculates statistical metrics for AMTS datasets.

    This class provides methods to preprocess data, calculate sample statistics,
    variable statistics, and variable type statistics for AMTS (Automated
    Machine Tooling Systems) datasets. It leverages configuration settings
    from ConfigStorage and utilizes an encoder for data transformation.

    Attributes:
        transformer: Encoder used for data transformation.
        categorical (list): List of categorical feature names.
        config (ConfigStorage): Configuration settings for data processing.
    """

    def __init__(self, encoder, config: ConfigStorage) -> None:
        """Initializes the CalculateDataStatisticsAMTS instance.

        Args:
            encoder: Encoder used for data transformation.
            config (ConfigStorage): Configuration storage containing pipeline
                and data settings.
        """
        self.transformer = encoder
        self.categorical = self.transformer.cat_features
        self.config = config

    def _preprocessing_data(self, **eval_sets):
        """Preprocesses data by removing outliers based on target variable percentiles.

        Generates a message indicating the removal of outliers for specified
        evaluation sets based on configured minimum and maximum percentiles.

        Args:
            **eval_sets: Variable length keyword arguments representing different
                evaluation datasets.

        Returns:
            list: A list of messages indicating the removal of outliers for each
                evaluation set. If the evaluation set is not 'train', 'valid', or
                'test2', a hyphen '-' is returned instead.
        """
        msg = "Outliers removed based on target variable " \
              "({} and {} percentiles).".format(
            self.config.pipeline.preprocessing.min_percentile,
            self.config.pipeline.preprocessing.max_percentile,
        )
        values = [
            msg if sample in ["train", "valid", "test2"] else "-"
            for sample in eval_sets
        ]
        return values

    def _calculate_samples_stats(self, log_scale: bool, prefix: str = "", **eval_sets):
        """Calculates statistical metrics for each sample in the evaluation sets.

        Computes the number of observations, mean, standard deviation, minimum,
        25th percentile, median, 75th percentile, and maximum values for the
        target variable in each dataset. Optionally applies an inverse log
        transformation to the target variable.

        Args:
            log_scale (bool): Indicates whether to apply an inverse log transformation
                to the target variable.
            prefix (str, optional): Prefix to prepend to the column names in the
                resulting DataFrame. Defaults to an empty string.
            **eval_sets: Variable length keyword arguments representing different
                evaluation datasets.

        Returns:
            pd.DataFrame: A DataFrame containing the calculated statistical metrics
                for each sample, with columns named according to the specified prefix.

        Raises:
            KeyError: If 'amts_final_data' is not present in eval_sets.
        """
        _eval_set = eval_sets["amts_final_data"]

        result = {}
        for data_name in _eval_set:
            data, target = _eval_set[data_name]

            if log_scale:
                target = self.log_transformer.inverse_transform(target)

            result[data_name] = [
                len(data),
                np.mean(target),
                np.std(target),
                np.min(target),
                np.percentile(target, 25),
                np.percentile(target, 50),
                np.percentile(target, 75),
                np.max(target),
            ]
        result = pd.DataFrame(result).T.reset_index()
        result.columns = [
            "Sample",
            "# Observations",
            f"{prefix}Target AVG Value",
            f"{prefix}Target STD Value",
            f"{prefix}Target MIN Value",
            f"{prefix}Target 25% Percentile",
            f"{prefix}Target 50% Percentile",
            f"{prefix}Target 75% Percentile",
            f"{prefix}Target MAX Value",
        ]
        return result.fillna(0)

    def _calculate_variables_stats(self, **eval_sets) -> pd.DataFrame:
        """Calculates statistical metrics for each variable in the evaluation sets.

        Computes the number of filled values, mean, standard deviation, minimum,
        25th percentile, median, 75th percentile, and maximum values for each
        variable. For categorical variables, statistical metrics are not calculated
        and represented with a placeholder.

        Args:
            **eval_sets: Variable length keyword arguments representing different
                evaluation datasets.

        Returns:
            pd.DataFrame: A DataFrame containing the calculated statistical metrics
                for each variable.

        Raises:
            KeyError: If 'amts_final_data' is not present in eval_sets.
        """
        _eval_set = eval_sets["amts_final_data"]

        sample_name = next(iter(_eval_set))
        data, _ = _eval_set[sample_name]

        result = data.describe().T.reset_index()
        result.columns = [
            "Variable Name",
            "Number of Filled Values",
            "AVG Value",
            "STD Value",
            "MIN Value",
            "25% Percentile Value",
            "50% Percentile Value",
            "75% Percentile Value",
            "MAX Value",
        ]
        if self.categorical:
            mask = result["Variable Name"].isin(self.categorical)
            features = [
                "AVG Value",
                "STD Value",
                "MIN Value",
                "25% Percentile Value",
                "50% Percentile Value",
                "75% Percentile Value",
                "MAX Value",
            ]
            result.loc[mask, features] = "."

        return result.fillna(0)

    def _calculate_variables_types_stats(self) -> pd.DataFrame:
        """Calculates statistics related to variable types and model configuration.

        Gathers information about the target variable, loss function, evaluation
        metric, and the number of categorical features used in the model.

        Returns:
            pd.DataFrame: A DataFrame containing statistics about variable types
                and model configuration.

        Raises:
            AttributeError: If required configuration attributes are missing.
        """
        target_name = self.config.data.columns.target_name
        log_target = self.config.pipeline.preprocessing.log_target
        target_name = f"log({target_name})" if log_target else target_name

        stats = pd.DataFrame(
            {
                "Target Variable": [self.config.data.columns.target_name],
                "Loss Function": self.config.pipeline.loss_function,
                "Evaluation Metric": self.config.pipeline.eval_metric,
                "# Categories": [len(self.transformer.cat_features)],
            }
        )

        return stats.fillna(0)

    def transform(self, **eval_sets) -> None:
        """Transforms and aggregates statistical metrics for the provided evaluation sets.

        Invokes internal methods to calculate sample statistics, variable types
        statistics, and variable statistics, then aggregates the results into a
        tuple.

        Args:
            **eval_sets: Variable length keyword arguments representing different
                evaluation datasets.

        Returns:
            tuple: A tuple containing DataFrames with sample statistics, variable
                types statistics, and variable statistics.

        Raises:
            KeyError: If required keys are missing in eval_sets.
            AttributeError: If required attributes are missing in the instance.
        """
        result = (
            self._calculate_samples_stats(log_scale=False, **eval_sets),
            self._calculate_variables_types_stats(),
            self._calculate_variables_stats(**eval_sets),
        )

        return result