import numpy as np
import pandas as pd
from typing import Dict, List

from dreamml.data import DataSet
from dreamml.configs.config_storage import ConfigStorage
from dreamml.data._enums import FrequencyEnums
from dreamml.logging import get_logger

np.random.seed(27)
_logger = get_logger(__name__)


class AMTSDataset(DataSet):
    """
    AMTSDataset is a specialized dataset class for handling AMTS-related data,
    extending the functionalities of the base DataSet class. It prepares and
    splits the data for training, validation, and inference tasks specific to
    time series models like N-BEATS.

    Args:
        dev_data (pd.DataFrame): Development dataset.
        oot_data (pd.DataFrame or None): Out-of-time dataset.
        config (ConfigStorage): Configuration storage object.
        indexes (tuple): Tuple of indexes.
        cat_features (list): List of categorical feature names.
        text_features (list): List of text feature names.
        text_features_preprocessed (list): List of preprocessed text feature names.
        text_transformer (None): Transformer for text features.

    Attributes:
        horizon (int): Forecast horizon from the config.
        time_column_frequency (FrequencyEnums): Frequency of the time column.
        backcast_length (int): Backcast length parameter for N-BEATS.
        sequence (int): Sequence length parameter for N-BEATS RevIn.
    """

    def __init__(
        self,
        dev_data: pd.DataFrame,
        oot_data: pd.DataFrame or None,
        config: ConfigStorage,
        indexes: tuple,
        cat_features: list,
        text_features: list,
        text_features_preprocessed: list,
        text_transformer: None,
    ):
        super().__init__(
            dev_data=dev_data,
            oot_data=oot_data,
            config=config,
            indexes=indexes,
            cat_features=cat_features,
            text_features=text_features,
            text_features_preprocessed=text_features_preprocessed,
            text_transformer=text_transformer,
        )
        self.horizon = config.pipeline.task_specific.time_series.horizon
        self.time_column_frequency = (
            config.pipeline.task_specific.time_series.time_column_frequency
        )
        self.backcast_length = config.models.nbeats_revin.params["backcast_length"]
        self.sequence = config.models.nbeats_revin.params["sequence"]

    def get_eval_set(
        self,
        used_features: List[str] = None,
        vectorization_name: str = None,
        drop_service_fields: bool = True,
    ) -> Dict:
        """
        Retrieves the evaluation set based on the task type.

        Args:
            used_features (List[str], optional): List of features to use. Defaults to None.
            vectorization_name (str, optional): Name of the vectorization method. Defaults to None.
            drop_service_fields (bool, optional): Whether to drop service fields. Defaults to True.

        Returns:
            Dict: A dictionary containing the evaluation datasets.
        """
        if self.task == "amts_ad":
            data = {
                "amts_train_data": self.get_amts_data(),
                "amts_final_data": self.get_amts_final_data(),
                "nbeats_train_data": self.get_nbeats_data_ad(),
                "nbeats_inference_data": self.get_nbeats_inference_data_ad(),
            }
        elif self.task == "amts":
            data = {
                "amts_train_data": self.get_amts_data(),
                "amts_final_data": self.get_amts_final_data(),
                "nbeats_train_data": self.get_nbeats_data(),
                "nbeats_final_data": self.get_nbeats_final_data(),
                "nbeats_inference_data": self.get_nbeats_inference_data(),
            }
        return data

    def amts_split_train_test(self, df):
        """
        Splits the dataset into training and testing sets based on unique group identifiers.

        This method partitions the data for each unique group, reserving the last
        `horizon` number of samples for testing and the remaining for training.

        Args:
            df (pd.DataFrame): The dataframe to split.

        Returns:
            tuple: A tuple containing the training dataframe and testing dataframe.
        """
        df_train = pd.DataFrame()
        df_test = pd.DataFrame()
        for id in df[self.group_column].unique():
            df_unique = df[df[self.group_column] == id]
            test = df_unique.tail(self.horizon)
            train = df_unique.iloc[: -self.horizon]
            df_train = pd.concat([df_train, train], axis=0)
            df_test = pd.concat([df_test, test], axis=0)
        return df_train, df_test

    def compute_train_data(self, df):
        """
        Prepares training data for the N-BEATS RevIn model.

        This method constructs input sequences and corresponding targets for training
        by sliding a window of `backcast_length` over the time series data.

        Args:
            df (pd.DataFrame): The dataframe to process.

        Returns:
            tuple: Three numpy arrays containing the input features (X), targets (y),
                   and group identifiers (ids).
        """
        X, y, ids = [], [], []

        for id in df[self.group_column].unique():
            ts_value = df[df[self.group_column] == id]
            for epoch in range(self.backcast_length, len(ts_value) - self.horizon):
                ids.append(id)
                X.append(
                    ts_value[ts_value[self.group_column] == id][
                        epoch - self.backcast_length : epoch
                    ][self.target_name]
                )
                y.append(
                    ts_value[ts_value[self.group_column] == id][
                        epoch : epoch + self.horizon
                    ][self.target_name]
                )
        X = np.array(X)
        y = np.array(y)
        ids = np.array(ids)
        return X, y, ids

    def compute_train_data_ad(self, df):
        """
        Prepares training data for the N-BEATS RevIn model in Anomaly Detection tasks.

        This method constructs input sequences and corresponding targets for training
        by sliding a window of `sequence` over the time series data.

        Args:
            df (pd.DataFrame): The dataframe to process.

        Returns:
            tuple: Three numpy arrays containing the input features (X), targets (y),
                   and group identifiers (ids).
        """
        X, y, ids = [], [], []

        for id in df[self.group_column].unique():
            ts_value = df[df[self.group_column] == id]
            for epoch in range(self.sequence, len(ts_value) - self.horizon):
                ids.append(id)
                X.append(
                    ts_value[ts_value[self.group_column] == id][
                        epoch - self.sequence : epoch
                    ][self.target_name]
                )
                y.append(
                    ts_value[ts_value[self.group_column] == id][
                        epoch - self.sequence : epoch
                    ][self.target_name]
                )
        X = np.array(X)
        y = np.array(y)
        ids = np.array(ids)
        return X, y, ids

    def compute_test_data(self, df_train, df_test):
        """
        Prepares testing data for the N-BEATS RevIn model.

        This method constructs input sequences for testing by taking the last
        `backcast_length` samples from the training data for each group and
        pairing them with the corresponding targets from the testing data.

        Args:
            df_train (pd.DataFrame): The training dataframe.
            df_test (pd.DataFrame): The testing dataframe.

        Returns:
            tuple: Three numpy arrays containing the input features (X), targets (y),
                   and group identifiers (ids).
        """
        X, y, ids = [], [], []

        for id in df_test[self.group_column].unique():
            ids.append(id)
            X.append(
                df_train[df_train[self.group_column] == id][self.target_name][
                    -self.backcast_length :
                ]
            )
            y.append(df_test[df_test[self.group_column] == id][self.target_name])
        X = np.array(X)
        y = np.array(y)
        ids = np.array(ids)
        return X, y, ids

    def compute_inference_data(self, df):
        """
        Prepares inference data for the N-BEATS RevIn model.

        This method constructs input sequences for inference by taking the last
        `backcast_length` samples from each group in the dataset.

        Args:
            df (pd.DataFrame): The dataframe to process.

        Returns:
            tuple: Two numpy arrays containing the input features (X) and group
                   identifiers (ids).
        """
        X, ids = [], []
        for id in df[self.group_column].unique():
            ids.append(id)
            X.append(
                df[df[self.group_column] == id][self.target_name][
                    -self.backcast_length :
                ]
            )
        X = np.array(X)
        ids = np.array(ids)
        return X, ids

    def compute_inference_data_ad(self, df):
        """
        Prepares inference data for the N-BEATS RevIn model in Anomaly Detection tasks.

        This method constructs input sequences and corresponding targets for inference
        by dividing the time series data into segments of length `sequence`.

        Args:
            df (pd.DataFrame): The dataframe to process.

        Returns:
            tuple: Three numpy arrays containing the input features (X), targets (y),
                   and group identifiers (ids).
        """
        X, y, ids = [], [], []
        for id in df[self.group_column].unique():
            for i in range(int(len(df[df[self.group_column] == id]) / self.sequence)):
                ids.append(id)
                X.append(
                    df[df[self.group_column] == id][self.target_name][
                        self.sequence * i : self.sequence * (i + 1)
                    ]
                )
                y.append(
                    df[df[self.group_column] == id][self.target_name][
                        self.sequence * i : self.sequence * (i + 1)
                    ]
                )

        X = np.array(X)
        y = np.array(y)
        ids = np.array(ids)
        return X, y, ids

    def get_nbeats_data_ad(self) -> Dict:
        """
        Assembles training data for the N-BEATS RevIn model in Anomaly Detection tasks.

        This method computes the training data specific to anomaly detection.

        Returns:
            Dict: A dictionary containing the input features (X), targets (y),
                  and group identifiers (ids) for training.
        """
        X, y, ids = self.compute_train_data_ad(self.dev_data)
        data = {"X": X, "y": y, "ids": ids}
        return data

    def get_nbeats_data(self) -> Dict:
        """
        Assembles initial training data for the N-BEATS RevIn model.

        This method splits the development data into training and testing sets,
        computes the respective input features and targets, and organizes them
        into a dictionary for model training.

        Returns:
            Dict: A dictionary containing training and testing datasets with
                  their respective input features, targets, and group identifiers.
        """
        df_train, df_test = self.amts_split_train_test(self.dev_data)

        X_train, y_train, ids_train = self.compute_train_data(df_train)
        X_test, y_test, ids_test = self.compute_test_data(df_train, df_test)

        data = {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "ids_train": ids_train,
            "ids_test": ids_test,
        }
        return data

    def get_nbeats_final_data(self) -> Dict:
        """
        Assembles final training data for the N-BEATS RevIn model.

        This method computes the complete training data using the entire development
        dataset, preparing it for the final training phase.

        Returns:
            Dict: A dictionary containing the input features (X), targets (y),
                  and group identifiers (ids) for final training.
        """
        X, y, ids = self.compute_train_data(self.dev_data)
        data = {
            "X": X,
            "y": y,
            "ids": ids,
        }
        return data

    def get_nbeats_inference_data(self) -> Dict:
        """
        Assembles inference data for the N-BEATS RevIn model.

        This method prepares the input features and group identifiers required
        for making predictions using the trained model.

        Returns:
            Dict: A dictionary containing the input features (X) and group
                  identifiers (ids) for inference.
        """
        X, ids = self.compute_inference_data(self.dev_data)
        data = {
            "X": X,
            "ids": ids,
        }
        return data

    def get_nbeats_inference_data_ad(self) -> Dict:
        """
        Assembles inference data for the N-BEATS RevIn model in Anomaly Detection tasks.

        This method prepares the input features, targets, and group identifiers
        required for making predictions in anomaly detection scenarios.

        Returns:
            Dict: A dictionary containing the input features (X), targets (y),
                  and group identifiers (ids) for inference in anomaly detection.
        """
        X, y, ids = self.compute_inference_data_ad(self.dev_data)
        data = {
            "X": X,
            "y": y,
            "ids": ids,
        }
        return data

    def get_amts_data(self) -> Dict:
        """
        Retrieves the complete initial training dataset for AMTS-related models.

        This method prepares the training and validation datasets required for
        models like Prophet and Linear Regression by including trend and
        additional temporal features if applicable.

        Returns:
            Dict: A dictionary mapping sample names to tuples of
                  (pd.DataFrame, pd.Series) for training and validation.
        """
        trend_dev = np.array([i for i in range(len(self.dev_data))])

        df_train = pd.DataFrame(
            {
                "ds": self.dev_data[: -self.horizon][self.time_column],
                "trend": trend_dev[: -self.horizon],
            }
        )
        df_valid = pd.DataFrame(
            {
                "ds": self.dev_data[-self.horizon :][self.time_column],
                "trend": trend_dev[-self.horizon :],
            }
        )

        if self.time_column_frequency == FrequencyEnums.DAYS and self.task == "amts":
            columns = [
                "is_weekend",
                "is_holiday",
                "is_pre_holiday",
                "is_pre_pre_holiday",
            ]
            for column in columns:
                df_train[column] = self.dev_data[: -self.horizon][
                    f"{self.time_column}_{column}"
                ]
            for column in columns:
                df_valid[column] = self.dev_data[-self.horizon :][
                    f"{self.time_column}_{column}"
                ]

        if self.split_by_group:
            df = pd.concat([df_train, df_valid], axis=0)
            df[self.group_column] = self.dev_data[self.group_column]
            return {"train": (df, self.dev_data[self.target_name])}

        return {
            "train": (df_train, self.dev_data[: -self.horizon][self.target_name]),
            "valid": (df_valid, self.dev_data[-self.horizon :][self.target_name]),
        }

    def get_amts_final_data(self) -> Dict:
        """
        Retrieves the complete final training dataset for AMTS-related models.

        This method prepares the training and validation datasets for final training
        by including trend and additional temporal features if applicable.

        Returns:
            Dict: A dictionary mapping sample names to tuples of
                  (pd.DataFrame, pd.Series) for training and validation.
        """
        trend_dev = np.array([i for i in range(len(self.dev_data))])

        df_train = pd.DataFrame(
            {
                "ds": self.dev_data[self.time_column],
                "trend": trend_dev,
            }
        )
        df_valid = pd.DataFrame(
            {
                "ds": self.dev_data[self.time_column],
                "trend": trend_dev,
            }
        )

        if self.time_column_frequency == FrequencyEnums.DAYS and self.task == "amts":
            columns = [
                "is_weekend",
                "is_holiday",
                "is_pre_holiday",
                "is_pre_pre_holiday",
            ]
            for column in columns:
                df_train[column] = self.dev_data[f"{self.time_column}_{column}"]
            for column in columns:
                df_valid[column] = self.dev_data[f"{self.time_column}_{column}"]

        if self.split_by_group:
            df = pd.concat([df_train, df_valid], axis=0)
            df[self.group_column] = self.dev_data[self.group_column]
            return {"train": (df, self.dev_data[self.target_name])}

        return {
            "train": (df_train, self.dev_data[self.target_name]),
            "valid": (df_valid, self.dev_data[self.target_name]),
        }