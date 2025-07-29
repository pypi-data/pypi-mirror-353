from copy import deepcopy
from typing import List, Optional, Dict, Union
import pandas as pd
from dreamml.configs.config_storage import ConfigStorage
from dreamml.features.feature_extraction._outliers import (
    filter_outliers_by_train_valid,
    get_min_max_perc,
    filter_outliers_by_perc,
)
import numpy as np

from dreamml.logging import get_logger

np.random.seed(27)
_logger = get_logger(__name__)


class DataSet:
    """Represents the input data for dreamml_base.

    Attributes:
        dev_data (pd.DataFrame): Development dataset.
        oot_data (pd.DataFrame or None): Out-of-time dataset.
        target_name (str or None): Name of the target column.
        dev_target (pd.Series or None): Target values for the development dataset.
        oot_target (pd.Series or None): Target values for the out-of-time dataset.
        cat_features (list): List of categorical feature names.
        text_features (list): List of text feature names.
        text_features_preprocessed (list): List of preprocessed text feature names.
        drop_features (list): List of features to drop.
        task (str): Task type specified in the configuration.
        features (pd.Index): Feature columns in the development dataset.
        folds (int): Number of cross-validation folds.
        indexes (tuple): Tuple containing indices for train, validation, and test splits.
        group_column (str): Column name for grouping data.
        split_by_group (bool): Flag indicating whether to split by group.
        time_column (str or None): Column name for time features.
        oot_data_path (str): Path to the out-of-time dataset.
        multitarget (list): List of multitarget features.
        never_used_features (list): List of features that are never used.
        etna_artifacts (None): Placeholder for ETNA artifacts.
        train_indexes_before_augmentations (None): Placeholder for train indexes before augmentations.
        outliers_config (dict): Configuration for outlier detection.
        embeddings (dict): Dictionary to store embeddings.
        text_augs (list): List of text augmentations.
        _service_fields (list): List of service field names.
        text_transformer (None): Text transformer object.
    """

    def __init__(
        self,
        dev_data: pd.DataFrame,
        oot_data: Optional[pd.DataFrame],
        config: ConfigStorage,
        indexes: tuple,
        cat_features: list,
        text_features: list,
        text_features_preprocessed: list,
        text_transformer: Optional[None],
    ):
        """Initializes the DataSet with provided data and configurations.

        Args:
            dev_data (pd.DataFrame): Development dataset.
            oot_data (pd.DataFrame or None): Out-of-time dataset.
            config (ConfigStorage): Configuration storage object.
            indexes (tuple): Tuple containing indices for train, validation, and test splits.
            cat_features (list): List of categorical feature names.
            text_features (list): List of text feature names.
            text_features_preprocessed (list): List of preprocessed text feature names.
            text_transformer (None): Text transformer object.
        """
        self.dev_data = dev_data
        self.oot_data = oot_data
        self.target_name = config.data.columns.target_name
        if self.target_name is None:
            self.dev_target = None
        else:
            self.dev_target = self.dev_data[self.target_name]
        if oot_data is not None:
            if self.target_name is None:
                self.oot_target = None
            else:
                self.oot_target = self.oot_data[self.target_name]
        self.cat_features = cat_features
        self.text_features = text_features
        self.text_features_preprocessed = text_features_preprocessed
        self.drop_features = list(
            set(
                config.data.columns.drop_features
                if config.data.columns.drop_features is not None
                else []
            )
        )
        self.task = config.pipeline.task

        self.features = self.dev_data.columns
        self.folds = config.data.splitting.cv_n_folds
        self.indexes = indexes
        self.group_column = config.data.columns.group_column
        self.split_by_group = config.data.splitting.split_by_group

        self.time_column = config.data.columns.time_column
        if (
            self.time_column
            and self.task != "amts"
            and self.time_column not in self.drop_features
        ):
            self.drop_features.append(self.time_column)

        self.oot_data_path = config.data.oot_path
        self.multitarget = []
        self.never_used_features = config.data.columns.never_used_features
        self.etna_artifacts = None
        self.train_indexes_before_augmentations = None
        self.outliers_config = {
            "min_percentile": config.pipeline.preprocessing.min_percentile,
            "max_percentile": config.pipeline.preprocessing.max_percentile,
        }
        self.embeddings: dict = {}
        self.text_augs: list = config.data.augmentation.text_augmentations
        self._service_fields = config.service_fields
        self.text_transformer = text_transformer

    def __len__(self):
        """Returns the number of samples in the development dataset.

        Returns:
            int: Number of samples.
        """
        return len(self.dev_data)

    def set_embedding_sample(
        self, vectorization_name: str, sample_name: str, embeddings_df: pd.DataFrame
    ):
        """Sets the embedding sample for a given vectorization method and sample name.

        Args:
            vectorization_name (str): Name of the vectorization method.
            sample_name (str): Name of the sample.
            embeddings_df (pd.DataFrame): DataFrame containing embeddings.

        Raises:
            ValueError: If the vectorization name is not supported.
        """
        if vectorization_name not in [
            "tfidf",
            "glove",
            "fasttext",
            "word2vec",
            "bert",
            "bow",
        ]:
            msg = f"{vectorization_name.title()} is not in the list of available ones."
            raise ValueError(msg)
        elif vectorization_name not in self.embeddings:
            self.embeddings[vectorization_name] = {}
        self.embeddings[vectorization_name][sample_name] = embeddings_df

    def _get_embedding_sample(self, vectorization_name: str, sample_name: str) -> pd.DataFrame:
        """Retrieves the embedding sample for a given vectorization method and sample name.

        Args:
            vectorization_name (str): Name of the vectorization method.
            sample_name (str): Name of the sample.

        Returns:
            pd.DataFrame: DataFrame containing the embeddings.

        Raises:
            ValueError: If the vectorization name or sample name is missing.
        """
        if vectorization_name == "bert":
            return pd.DataFrame()
        if vectorization_name == "all":
            concat_all_embedds_df = pd.DataFrame()
            for vec_name, embedds in self.embeddings.items():
                concat_all_embedds_df = pd.concat(
                    [concat_all_embedds_df, embedds[sample_name]], axis=1
                )
            return concat_all_embedds_df

        elif vectorization_name not in self.embeddings:
            msg = f"{vectorization_name} embeddings is missing in embeddings."
            raise ValueError(msg)
        elif sample_name not in self.embeddings[vectorization_name]:
            msg = f"{sample_name.title()} sample is missing in {vectorization_name} embeddings."
            raise ValueError(msg)
        else:
            return self.embeddings[vectorization_name][sample_name]

    def sample(self, used_features: Optional[List[str]] = None, vectorization_name: Optional[str] = None) -> Union[pd.DataFrame, pd.Series]:
        """Performs Reservoir Sampling to sample large datasets.

        Args:
            used_features (list or None, optional): List of features to use. Defaults to None.
            vectorization_name (str or None, optional): Name of the vectorization method. Defaults to None.

        Returns:
            tuple: Sampled features and target series.
        """
        if used_features is None:
            used_features = list(self.dev_data.drop(self.target_name, axis=1).columns)
        data, target = self.get_train(used_features, vectorization_name)

        dict_of_shapes_and_fractions = {
            200000: 0.7,
            400000: 0.6,
            600000: 0.5,
        }

        sample_frac = 1
        for key, value in dict_of_shapes_and_fractions.items():
            if len(data) > key:
                sample_frac = value

        # Determine sample size based on training set size
        num_samples = int(sample_frac * len(data))

        reservoir = np.array(data.iloc[:num_samples].index)
        for i in range(num_samples + 1, data.shape[0]):
            r = np.random.randint(0, i)
            if r < num_samples:
                reservoir[r] = data.iloc[[i]].index.values

        return data.loc[reservoir][used_features], target.loc[reservoir]

    def get_eval_set(
        self,
        used_features: Optional[List[str]] = None,
        vectorization_name: Optional[str] = None,
        drop_service_fields: bool = True,
    ) -> Dict[str, Union[pd.DataFrame, pd.Series]]:
        """Retrieves the evaluation set with specified features and vectorization.

        Args:
            used_features (List[str], optional): List of features to use. Defaults to None.
            vectorization_name (str, optional): Name of the vectorization method. Defaults to None.
            drop_service_fields (bool, optional): Whether to drop service fields. Defaults to True.

        Returns:
            Dict[str, Union[pd.DataFrame, pd.Series]]: Dictionary containing evaluation datasets.
        """
        eval_set = self.get_clean_eval_set(used_features, vectorization_name)

        garbage_features = []
        if self.multitarget:
            garbage_features.extend(self.multitarget)
        if not used_features:
            garbage_features.extend(self.drop_features)
            if self.group_column not in garbage_features and self.task == "timeseries":
                garbage_features.extend([self.group_column])
            if vectorization_name not in [None, "all"] and self.task in [
                "multiclass",
                "binary",
            ]:
                garbage_features.extend(self.text_features)
        if self.task in ["regression"]:
            eval_set = filter_outliers_by_train_valid(
                eval_set, self.get_cv_data_set(), self.outliers_config
            )

        extra_features_to_drop = []
        for sample in eval_set:
            data, target = eval_set[sample]

            if vectorization_name != "bow":
                garbage_features = [
                    col for col in garbage_features if col in data.columns
                ]
                data = data.drop(garbage_features, axis=1)
                extra_features_to_drop = list(
                    set(data.columns) & set(self.never_used_features)
                )
                if extra_features_to_drop:
                    data = data.drop(extra_features_to_drop, axis=1)

                if drop_service_fields:
                    _existed_service_fields = [
                        _field
                        for _field in self._service_fields
                        if _field in data.columns
                    ]
                    data = data.drop(_existed_service_fields, axis=1)

            eval_set[sample] = (data, target)

        if extra_features_to_drop or garbage_features:
            _logger.debug(f"Drop features: {garbage_features + extra_features_to_drop}")

        return eval_set

    def get_dropped_data(self, used_features: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """Retrieves the data with dropped features based on configuration.

        Args:
            used_features (List[str], optional): List of features to use. Defaults to None.

        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing dropped data for each sample.
        """
        eval_set = self.get_clean_eval_set(used_features)
        if self.task in ("regression", "timeseries"):
            eval_set = filter_outliers_by_train_valid(
                eval_set, self.get_cv_data_set(), self.outliers_config
            )

        dropped_data = {}
        dropped_features = [
            f
            for f in self.never_used_features
            if f in eval_set["train"][0].columns and f not in self.drop_features
        ]
        dropped_features.extend(self.drop_features)
        if dropped_features:
            for sample in eval_set:
                try:
                    dropped_data[sample] = eval_set[sample][0][dropped_features]
                except KeyError:
                    pass

        return dropped_data

    def get_dev_n_samples(self) -> int:
        """Gets the number of samples in the development dataset.

        Returns:
            int: Number of samples.
        """
        return self.dev_data.shape[0]

    def get_data_shapes(self) -> tuple:
        """Retrieves the shapes of development and out-of-time datasets.

        Returns:
            tuple: Shapes of development data, out-of-time data, and number of columns.
        """
        dev_data, cols = self.dev_data.shape
        oot_data = self.oot_data.shape[0] if self.oot_data is not None else None
        return dev_data, oot_data, cols

    def get_set(
        self,
        used_features: Optional[List[str]] = None,
        type_of_data: str = "train",
        vectorization_name: Optional[str] = None,
    ) -> Union[pd.DataFrame, pd.Series]:
        """Retrieves the specified data split with embeddings.

        Args:
            used_features (List[str], optional): List of features to use. Defaults to None.
            type_of_data (str, optional): Type of data to retrieve ('train', 'valid', 'test', 'OOT', 'train_cv'). Defaults to "train".
            vectorization_name (str, optional): Name of the vectorization method. Defaults to None.

        Returns:
            Union[pd.DataFrame, pd.Series]: Features and target for the specified data split.
        """
        if used_features is None:
            if self.target_name is None:
                used_features = list(self.dev_data.columns)
            else:
                used_features = list(
                    self.dev_data.drop(self.target_name, axis=1).columns
                )
            if vectorization_name is not None:
                if vectorization_name == "bow":
                    vectorization_columns = list(
                        self._get_embedding_sample(
                            vectorization_name, sample_name="train"
                        ).keys()
                    )
                else:
                    vectorization_columns = self._get_embedding_sample(
                        vectorization_name, sample_name="train"
                    ).columns.tolist()
                used_features.extend(vectorization_columns)

        if type_of_data == "OOT":
            data = self.oot_data
            target = self.oot_target
            data = self._concat_embeddings(
                data, vectorization_name, type_of_data, used_features
            )
            return data[used_features], target
        elif type_of_data == "train_cv":
            return self.get_train_cv(used_features, vectorization_name)
        else:
            if type_of_data == "train":
                idx = self.indexes[0]
            elif type_of_data == "valid":
                idx = self.indexes[1]
            elif type_of_data == "test":
                idx = self.indexes[2]
            else:
                idx = None
            data = self.dev_data
            data = data.loc[idx]
            data = self._concat_embeddings(
                data, vectorization_name, type_of_data, used_features
            )
            if self.target_name is None:
                target = None
            else:
                target = self.dev_target.loc[idx]

            if vectorization_name == "bow":
                return data, target

            return data[used_features], target

    def _concat_embeddings(
        self,
        data: pd.DataFrame,
        vectorization_name: Optional[str],
        sample_name: str,
        used_features: List[str],
    ) -> pd.DataFrame:
        """Concatenates embedding features to the data based on the vectorization method.

        Args:
            data (pd.DataFrame): Original data.
            vectorization_name (str or None): Name of the vectorization method.
            sample_name (str): Name of the sample.
            used_features (List[str]): List of used features.

        Returns:
            pd.DataFrame: Data with concatenated embeddings.
        """
        used_features_cp = deepcopy(used_features)
        if vectorization_name is None:
            return data

        elif vectorization_name == "all":
            for vec_name, embedding_df in self.embeddings.items():
                sample_embedding_df = self._get_embedding_sample(
                    vectorization_name=vec_name, sample_name=sample_name
                )
                data = pd.concat(
                    [data, sample_embedding_df], axis=1, ignore_index=False
                )
                embedding_columns = sample_embedding_df.columns.tolist()

        else:
            sample_embedding_df = self._get_embedding_sample(
                vectorization_name=vectorization_name, sample_name=sample_name
            )
            if vectorization_name == "bow":
                return sample_embedding_df
            data = pd.concat([data, sample_embedding_df], axis=1, ignore_index=False)
            embedding_columns = sample_embedding_df.columns.tolist()

        return data

    def get_train_cv(self, used_features: List[str], vectorization_name: Optional[str] = None) -> Union[pd.DataFrame, tuple]:
        """Retrieves the training and validation datasets for cross-validation.

        Args:
            used_features (List[str]): List of features to use.
            vectorization_name (str or None, optional): Name of the vectorization method. Defaults to None.

        Returns:
            tuple: Concatenated training and validation features and targets.

        Raises:
            ValueError: If outlier filtering fails.
        """
        train_idx, valid_idx = self.indexes[0], self.indexes[1]
        data = self.dev_data
        target = self.dev_target

        train_data = self._concat_embeddings(
            data=data.loc[train_idx],
            vectorization_name=vectorization_name,
            sample_name="train",
            used_features=used_features,
        )

        valid_data = self._concat_embeddings(
            data=data.loc[valid_idx],
            vectorization_name=vectorization_name,
            sample_name="valid",
            used_features=used_features,
        )

        if self.target_name is None:
            train_cv = pd.concat([train_data[used_features], valid_data[used_features]])
        else:
            train_cv = (
                pd.concat([train_data[used_features], valid_data[used_features]]),
                pd.concat([target.loc[train_idx], target.loc[valid_idx]]),
            )

        if self.task in ("regression", "timeseries"):
            min_perc, max_perc = get_min_max_perc(self.outliers_config, train_cv[1])
            train_cv = filter_outliers_by_perc(*train_cv, min_perc, max_perc)
        return train_cv

    def get_train(self, used_features: Optional[List[str]] = None, vectorization_name: Optional[str] = None) -> Union[pd.DataFrame, pd.Series]:
        """Retrieves the training dataset.

        Args:
            used_features (List[str], optional): List of features to use. Defaults to None.
            vectorization_name (str or None, optional): Name of the vectorization method. Defaults to None.

        Returns:
            tuple: Training features and target series.
        """
        return self.get_set(used_features, "train", vectorization_name)

    def get_valid(self, used_features: Optional[List[str]] = None, vectorization_name: Optional[str] = None) -> Union[pd.DataFrame, pd.Series]:
        """Retrieves the validation dataset.

        Args:
            used_features (List[str], optional): List of features to use. Defaults to None.
            vectorization_name (str or None, optional): Name of the vectorization method. Defaults to None.

        Returns:
            tuple: Validation features and target series.
        """
        return self.get_set(used_features, "valid", vectorization_name)

    def get_test(self, used_features: Optional[List[str]] = None, vectorization_name: Optional[str] = None) -> Union[pd.DataFrame, pd.Series]:
        """Retrieves the test dataset.

        Args:
            used_features (List[str], optional): List of features to use. Defaults to None.
            vectorization_name (str or None, optional): Name of the vectorization method. Defaults to None.

        Returns:
            tuple: Test features and target series.
        """
        return self.get_set(used_features, "test", vectorization_name)

    def get_oot(self, used_features: Optional[List[str]] = None, vectorization_name: Optional[str] = None) -> Union[pd.DataFrame, pd.Series]:
        """Retrieves the out-of-time (OOT) dataset.

        Args:
            used_features (List[str], optional): List of features to use. Defaults to None.
            vectorization_name (str or None, optional): Name of the vectorization method. Defaults to None.

        Returns:
            tuple: OOT features and target series.
        """
        return self.get_set(used_features, "OOT", vectorization_name)

    def get_cv_data_set(self, used_features: Optional[List[str]] = None, vectorization_name: Optional[str] = None) -> Union[pd.DataFrame, tuple]:
        """Retrieves the cross-validation dataset.

        Args:
            used_features (List[str], optional): List of features to use. Defaults to None.
            vectorization_name (str or None, optional): Name of the vectorization method. Defaults to None.

        Returns:
            tuple: Training and validation features and targets.
        """
        return self.get_set(used_features, "train_cv", vectorization_name)

    def get_cv_splitter_df(self, splitter_columns: List[str]) -> pd.DataFrame:
        """Obtains a DataFrame with columns necessary for splitting in cross-validation.

        Args:
            splitter_columns (List[str]): List of columns to use for splitting.

        Returns:
            pd.DataFrame: DataFrame containing splitter columns.
        """
        if len(splitter_columns) == 0:
            splitter_columns = (
                self.target_name
                if isinstance(self.target_name, list)
                else [self.target_name]
            )

        return self.get_cv_data_set(splitter_columns)[0]

    def get_clean_eval_set(self, used_features: Optional[List[str]] = None, vectorization_name: Optional[str] = None) -> Dict[str, Union[pd.DataFrame, pd.Series]]:
        """Creates a dictionary for evaluation sets with feature matrices and target vectors.

        Args:
            used_features (List[str], optional): List of features to use. Defaults to None.
            vectorization_name (str, optional): Name of the vectorization method. Defaults to None.

        Returns:
            Dict[str, Union[pd.DataFrame, pd.Series]]: Dictionary containing cleaned evaluation sets.
        """
        eval_set = {
            "train": (self.get_train(used_features, vectorization_name)),
            "valid": (self.get_valid(used_features, vectorization_name)),
            "test": (self.get_test(used_features, vectorization_name)),
        }
        if self.oot_data is not None:
            eval_set["OOT"] = self.get_oot(used_features, vectorization_name)
        return eval_set