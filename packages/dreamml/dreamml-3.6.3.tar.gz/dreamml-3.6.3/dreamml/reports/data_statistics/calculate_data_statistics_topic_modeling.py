from typing import Optional, Tuple
import numpy as np
import pandas as pd

from dreamml.configs.config_storage import ConfigStorage
from dreamml.logging import get_logger

_logger = get_logger(__name__)


class CalculateDataStatistics:
    """Calculates statistical metrics for data samples.

    Processes data samples to compute statistics such as length of text features and
    word count metrics based on the provided configuration.
    """

    def __init__(
        self, transformer, features: pd.Series, config: ConfigStorage, task: str
    ) -> None:
        """
        Initializes the CalculateDataStatistics.

        Args:
            transformer: Object responsible for data transformations, containing categorical features.
            features (pd.Series): Series of features to analyze.
            config (ConfigStorage): Configuration storage with settings and parameters.
            task (str): Identifier or name of the task.
        """
        self.features = features
        self.transformer = transformer
        self.categorical = self.transformer.cat_features
        self.config = config
        self.task = task

    def _calculate_samples_stats(self, **eval_sets):
        """
        Calculates statistical metrics for each evaluation set.

        Computes statistics such as the length of text features,
        maximum, minimum, and mean number of words per sample.

        Args:
            **eval_sets: Variable keyword arguments representing evaluation datasets.
                Each key is the name of the evaluation set, and the value is the dataset.

        Returns:
            list of pd.DataFrame: A list containing DataFrame objects with statistical metrics for each evaluation set.

        Raises:
            KeyError: If expected columns are missing in the provided datasets.
            AttributeError: If transformer or config attributes are not properly initialized.
        """
        results = []
        for key, sample in eval_sets.items():

            item = (
                sample[0][self.config.data.columns.text_features[0]]
                if "bertopic" in self.config.pipeline.model_list
                else sample[0][self.config.data.columns.text_features_preprocessed[0]]
            )

            df = pd.DataFrame(
                {
                    f"{key}": ["True"],
                    "length": [len(item)],
                    "max_words": [item.apply(lambda x: len(x.split())).max()],
                    "min_words": [item.apply(lambda x: len(x.split())).min()],
                    "mean_words": [item.apply(lambda x: len(x.split())).mean()],
                }
            )
            results.append(df)
        return results

    def transform(self, **eval_sets) -> Tuple[Optional[pd.DataFrame]]:
        """
        Transforms evaluation datasets by calculating statistical metrics.

        Args:
            **eval_sets: Variable keyword arguments representing evaluation datasets.
                Each key is the name of the evaluation set, and the value is the dataset.

        Returns:
            Tuple[Optional[pd.DataFrame]]: A tuple containing DataFrame objects with statistical metrics for each evaluation set.

        Raises:
            KeyError: If expected columns are missing in the provided datasets.
            AttributeError: If transformer or config attributes are not properly initialized.
        """
        return self._calculate_samples_stats(**eval_sets)