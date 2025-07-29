from copy import deepcopy
from typing import Union, Dict, List
import numpy as np
import pandas as pd
from sklearn.exceptions import NotFittedError
from sklearn.base import BaseEstimator, TransformerMixin

from dreamml.features.categorical._base import find_categorical_features
from dreamml.features.categorical._ordinal_encoder import DmlOrdinalEncoder
from dreamml.features.categorical._label_encoder import DmlLabelEncoder
from dreamml.features.categorical._one_hot_encoder import DmlOneHotEncoder
from dreamml.logging import get_logger
from dreamml.utils.serialize import SerializedObject, Serializable

_logger = get_logger(__name__)


class CategoricalFeaturesTransformer(BaseEstimator, TransformerMixin, Serializable):
    """
    Transformer for preparing categorical features by identifying categorical columns,
    handling missing values, and encoding categories into numerical representations.

    This transformer replaces missing values with a specified fill value and applies
    label encoding to convert categorical variables into integer codes.

    Attributes:
        fill_value (str): The value used to fill missing entries in categorical features.
        config (dict): Configuration dictionary containing parameters such as categorical
            features, task type, and target variable name.
        copy (bool): Determines whether to copy the input data before transforming.
        task (str): The machine learning task type (e.g., 'binary').
        target_name (str): The name of the target variable.
        max_unique_values (int): Maximum number of unique values to consider for encoding.
        encoders (Dict[str, LabelEncoder]): Dictionary mapping feature names to their respective encoders.
        _unique_values (Dict[str, List]): Dictionary mapping feature names to their unique values observed during fitting.
        cat_features (List[str]): List of categorical feature names.
        fitted (bool): Indicates whether the transformer has been fitted.
    """

    def __init__(
        self,
        config: dict,
        fill_value: str = "NA",
        copy: bool = True,
        max_unique_values: int = 5,
    ) -> None:
        """
        Initializes the CategoricalFeaturesTransformer.

        Args:
            config (dict): Configuration dictionary containing parameters such as categorical
                features, task type, and target variable name.
            fill_value (str, optional): Value to replace missing entries in categorical features.
                Defaults to "NA".
            copy (bool, optional): If True, a copy of the data is created for transformation.
                If False, transformations are applied in place. Defaults to True.
            max_unique_values (int, optional): Maximum number of unique values to determine encoding strategy.
                Defaults to 5.
        """
        self.fill_value = fill_value
        self.config = config
        self.copy = copy
        self.task = config.get("task", "binary")
        self.target_name = self.config.get("target_name")
        self.max_unique_values: int = max_unique_values
        self.encoders = {}
        self._unique_values = {}
        self.cat_features = None
        self.fitted = False
        self.target_name = self.config["target_name"]

    def _copy(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Creates a deep copy of the data if the copy flag is set.

        Args:
            data (pd.DataFrame): The input DataFrame to copy.

        Returns:
            pd.DataFrame: A deep copy of the input DataFrame if copy is True; otherwise, the original DataFrame.
        """
        return deepcopy(data) if self.copy else data

    @property
    def check_is_fitted(self):
        """
        Checks if the transformer has been fitted.

        Raises:
            NotFittedError: If the transformer has not been fitted.

        Returns:
            bool: True if the transformer is fitted.
        """
        if not self.fitted:
            msg = (
                "This estimator is not fitted yet. Call 'fit' with "
                "appropriate arguments before using this estimator."
            )
            raise NotFittedError(msg)
        return True

    def _add_pandas_category_for_fillna(self, data, is_fitting=False):
        """
        Adds the fill value as a category to categorical columns to enable filling missing values.

        Args:
            data (pd.DataFrame): The DataFrame containing categorical columns.
            is_fitting (bool, optional): Flag indicating if the method is called during fitting.
                Defaults to False.

        Raises:
            ValueError: If the fill value already exists as a category in any categorical column during fitting.

        Returns:
            pd.DataFrame: The DataFrame with updated categorical columns.
        """
        pandas_categorical_columns = data.dtypes[
            data.dtypes == "category"
        ].index.tolist()

        for column in pandas_categorical_columns:
            if self.fill_value in data.loc[:, column].cat.categories:
                if is_fitting:
                    raise ValueError(
                        f"Fill value '{self.fill_value}' already exists as a category in column '{column}'."
                    )
                else:
                    continue

            data.loc[:, column] = data.loc[:, column].cat.add_categories(
                self.fill_value
            )

        return data

    def _prepare_data_dtypes(self, series: pd.Series) -> pd.Series:
        """
        Prepares the data types of a categorical series for encoding by filling missing values
        and converting to string type.

        Args:
            series (pd.Series): The categorical feature series.

        Returns:
            pd.Series: The prepared series with missing values filled and converted to string type.
        """
        series_prepared = series.fillna(self.fill_value)
        series_prepared = series_prepared.astype("str")
        return series_prepared

    def _find_new_values(self, series: pd.Series) -> pd.Series:
        """
        Identifies and handles new categorical values that were not seen during fitting.

        New values are replaced with the fill value if it was seen during fitting;
        otherwise, they are replaced with the first seen category.

        Args:
            series (pd.Series): The categorical feature series.

        Returns:
            pd.Series: The series with new categorical values handled appropriately.
        """
        observed_values = np.unique(series)
        expected_values = self._unique_values[series.name]
        new_values = list(set(observed_values) - set(expected_values))

        if new_values:
            bad_values_mask = series.isin(new_values)
            series[bad_values_mask] = (
                self.fill_value
                if self.fill_value in expected_values
                else expected_values[0]
            )

        return series

    def fit(self, data: pd.DataFrame):
        """
        Fits the transformer by identifying categorical features and fitting encoders for each.

        Args:
            data (pd.DataFrame): The input DataFrame containing the features.

        Returns:
            CategoricalFeaturesTransformer: The fitted transformer instance.
        """
        _data = data.copy()
        _data = self._add_pandas_category_for_fillna(_data, is_fitting=True)

        self.cat_features = find_categorical_features(_data, config=self.config)

        for feature in self.cat_features:
            _data[feature] = self._prepare_data_dtypes(_data[feature])
            self._unique_values[feature] = np.unique(_data[feature]).tolist()

            self.encoders[feature] = DmlLabelEncoder().fit(data=_data, feature=feature)
            if feature == self.target_name:
                _logger.info(
                    f"LabelEncoder applied to target variable '{self.config['target_name']}'."
                )

            # The following code is commented out to prevent increasing the number of features
            # and potential degradation of pipeline performance.
            #
            # elif data[feature].nunique() >= self.max_unique_values:
            #     self.encoders[feature] = DmlOrdinalEncoder().fit(
            #         data=_data, feature=feature
            #     )
            #
            # else:
            #     self.encoders[feature] = DmlOneHotEncoder().fit(
            #         data=_data, feature=feature
            #     )

        self.fitted = True
        return self

    def serialize(self) -> dict:
        """
        Serializes the transformer into a dictionary for storage or transmission.

        Returns:
            dict: The serialized representation of the transformer.
        """
        init_dict = {
            "config": self.config,
            "fill_value": self.fill_value,
            "copy": self.copy,
            "max_unique_values": self.max_unique_values,
        }

        encoders = {key: encoder.serialize() for key, encoder in self.encoders.items()}

        additional_dict = {
            "encoders": encoders,
            "fitted": self.fitted,
            "cat_features": self.cat_features,
        }

        return self._serialize(init_data=init_dict, additional_data=additional_dict)

    @classmethod
    def deserialize(cls, data):
        """
        Deserializes the transformer from a dictionary to restore its state.

        Args:
            data (dict): The serialized representation of the transformer.

        Returns:
            CategoricalFeaturesTransformer: The deserialized transformer instance.
        """
        instance = cls._deserialize(data)

        encoders = data["additional"]["encoders"]

        encoders = {
            key: SerializedObject(encoder).deserialize()
            for key, encoder in encoders.items()
        }

        instance.encoders = encoders
        instance.fitted = data["additional"]["fitted"]
        instance.cat_features = data["additional"]["cat_features"]

        return instance

    def transform(self, data):
        """
        Transforms the input data by encoding categorical features.

        Args:
            data (pd.DataFrame): The input DataFrame to transform.

        Returns:
            pd.DataFrame: The transformed DataFrame with encoded categorical features.

        Raises:
            NotFittedError: If the transformer has not been fitted before transformation.
        """
        self.check_is_fitted
        data = self._add_pandas_category_for_fillna(data)

        x_transformed = self._copy(data)
        encoded_features = list(set(self.cat_features) & set(data.columns))

        for feature in encoded_features:
            x_transformed[feature] = self._prepare_data_dtypes(x_transformed[feature])
            x_transformed[feature] = self._find_new_values(x_transformed[feature])

            encoder = self.encoders[feature]
            x_transformed = encoder.transform(data=x_transformed, feature=feature)

        return x_transformed

    def inverse_transform(self, data: pd.DataFrame):
        """
        Reverts the transformation by decoding the encoded categorical features back to their original form.

        Args:
            data (pd.DataFrame): The DataFrame with encoded categorical features.

        Returns:
            pd.DataFrame: The DataFrame with categorical features reverted to their original categories.

        Raises:
            NotFittedError: If the transformer has not been fitted before inverse transformation.
        """
        self.check_is_fitted
        x_transformed = self._copy(data)

        for feature, encoder in sorted(self.encoders.items(), reverse=True):
            x_transformed = encoder.inverse_transform(x_transformed, feature)
        return x_transformed