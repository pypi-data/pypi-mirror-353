import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.tree import DecisionTreeRegressor
from sklearn.exceptions import NotFittedError

from dreamml.utils.errors import MissedColumnError
from dreamml.utils.serialize import Serializable


class LogTargetTransformer(BaseEstimator, TransformerMixin, Serializable):
    """Transforms the target variable to a logarithmic scale.

    This transformer applies a logarithmic transformation to the target variable,
    adjusting for any negative values by shifting with a bias.

    Attributes:
        bias (float): The bias added to the target before applying the logarithm.
        tolerance (float): Small value added to avoid log(0).
        target_min (float): The minimum value of the target variable.
        fitted (bool): Indicates whether the transformer has been fitted.
    """

    def __init__(self, bias: float = 5, tolerance: float = 1e-5):
        """Initializes the LogTargetTransformer.

        Args:
            bias (float, optional): Bias added to the target before logging. Defaults to 5.
            tolerance (float, optional): Value to add to avoid log(0). Defaults to 1e-5.
        """
        self.bias = bias
        self.tolerance = tolerance
        self.target_min = None
        self.fitted = None

    @property
    def check_is_fitted(self):
        """Checks if the transformer has been fitted.

        Raises:
            NotFittedError: If the transformer is not fitted.

        Returns:
            bool: True if fitted.
        """
        if not self.fitted:
            msg = (
                "This estimator is not fitted yet. Call 'fit' with "
                "appropriate arguments before using this estimator."
            )
            raise NotFittedError(msg)
        return True

    def fit(self, target: pd.Series) -> None:
        """Fits the transformer by computing the minimum value of the target.

        Args:
            target (pd.Series): The target variable.

        Returns:
            self: Fitted transformer.
        """
        self.target_min = target.min()
        self.fitted = True
        return self

    def transform(self, target: pd.Series) -> pd.Series:
        """Applies logarithmic transformation to the target variable.

        Args:
            target (pd.Series): The target variable.

        Raises:
            ValueError: If the transformed target contains non-positive values.

        Returns:
            pd.Series: The log-transformed target variable.
        """
        self.check_is_fitted

        modified_target = target - self.target_min + self.bias
        if (modified_target <= 0).sum() > 0:
            raise ValueError(
                "LogTargetTransformer modified target contains values less than zero, please increase `bias` value"
            )

        return np.log(modified_target) + 1

    def inverse_transform(self, target: pd.Series) -> pd.Series:
        """Reverts the logarithmic transformation to retrieve original target values.

        Args:
            target (pd.Series): The log-transformed target variable.

        Returns:
            pd.Series: The original target variable.
        """
        self.check_is_fitted
        return np.exp(target - 1) + self.target_min - self.bias

    def serialize(self) -> dict:
        """Serializes the transformer state.

        Returns:
            dict: A dictionary containing the serialized state.
        """
        init_dict = {
            "bias": self.bias,
            "tolerance": self.tolerance,
        }

        additional_dict = {"target_min": self.target_min, "fitted": self.fitted}

        return self._serialize(init_data=init_dict, additional_data=additional_dict)

    @classmethod
    def deserialize(cls, data):
        """Deserializes the transformer from a dictionary.

        Args:
            data (dict): The serialized transformer state.

        Returns:
            LogTargetTransformer: The deserialized transformer instance.
        """
        instance = cls._deserialize(data)

        instance.target_min = data["additional"]["target_min"]
        instance.fitted = data["additional"]["fitted"]

        return instance


class DecisionTreeFeatureImportance(BaseEstimator, TransformerMixin):
    """Selects features based on decision tree importance.

    This transformer evaluates the importance of each feature by training a
    decision tree and calculating the correlation between the tree's predictions
    and the target variable. Features with correlation above a specified threshold
    are selected.

    Attributes:
        threshold (float): The correlation threshold for feature selection.
        remaining_features (List[str]): Features to always keep.
        cat_features (List[str], optional): List of categorical features to retain.
        scores (Dict[str, float]): Correlation scores for each feature.
    """

    def __init__(self, threshold, remaining_features=[], cat_features=None):
        """Initializes the DecisionTreeFeatureImportance transformer.

        Args:
            threshold (float): Correlation threshold for selecting features.
            remaining_features (List[str], optional): Features to always retain. Defaults to [].
            cat_features (List[str], optional): Categorical features to retain. Defaults to None.
        """
        self.threshold = threshold
        self.remaining_features = remaining_features
        self.cat_features = cat_features
        self.scores = {}

    @property
    def check_is_fitted(self):
        """Checks if the transformer has been fitted.

        Raises:
            NotFittedError: If the transformer is not fitted.

        Returns:
            bool: True if fitted.
        """
        if not self.scores:
            msg = (
                "This estimator is not fitted yet. Call 'fit' with "
                "appropriate arguments before using this estimator."
            )
            raise NotFittedError(msg)
        return True

    @staticmethod
    def calculate_tree(feature: pd.Series, target: pd.Series) -> float:
        """Trains a decision tree and calculates correlation with the target.

        Args:
            feature (pd.Series): The feature column.
            target (pd.Series): The target variable.

        Returns:
            float: The correlation score between the tree's predictions and the target.
        """
        feature = feature.fillna(-9999).values.reshape(-1, 1)
        tree = DecisionTreeRegressor(max_depth=3)
        tree.fit(feature, target)

        prediction = tree.predict(feature)
        score = np.corrcoef(prediction, target)

        return np.round(100 * score[0, 1], 2)

    def fit(self, data, target=None):
        """Fits the transformer by calculating correlation scores for each feature.

        Args:
            data (pd.DataFrame): Feature matrix.
            target (pd.Series): Target variable.

        Raises:
            MissedColumnError: If any categorical features are missing from the data.

        Returns:
            self: Fitted transformer.
        """
        if self.cat_features:
            missed_cols = list(set(self.cat_features) - set(data.columns))
            if missed_cols:
                raise MissedColumnError(f"Missed {list(missed_cols)} columns in data.")

            numeric_features = list(set(data.columns) - set(self.cat_features))
        else:
            numeric_features = data.columns

        for feature in tqdm(numeric_features):
            self.scores[feature] = self.calculate_tree(data[feature], target)

        return self

    def transform(self, data, target=None):
        """Selects features based on the correlation threshold.

        Features with correlation above the threshold or listed in remaining_features
        are marked as selected.

        Args:
            data (pd.DataFrame): Feature matrix.
            target (pd.Series, optional): Target variable. Defaults to None.

        Raises:
            NotFittedError: If the transformer is not fitted.

        Returns:
            pd.DataFrame: DataFrame containing feature names, their correlation scores,
                          and selection flags.
        """
        self.check_is_fitted
        scores = pd.Series(self.scores)
        scores = pd.DataFrame({"Variable": scores.index, "Correlation": scores.values})
        scores["Correlation_abs"] = np.abs(scores["Correlation"])
        scores["Selected"] = scores.apply(
            lambda row: (
                1
                if row["Correlation_abs"] > self.threshold
                or row["Variable"] in self.remaining_features
                else 0
            ),
            axis=1,
        )
        scores = scores.sort_values(by="Correlation_abs", ascending=False)
        scores = scores.drop("Correlation_abs", axis=1)
        scores = scores.fillna(0)

        if self.cat_features:
            cat_features_scores = pd.DataFrame(
                {
                    "Variable": self.cat_features,
                    "Correlation": "categorical feature",
                    "Selected": 1,
                }
            )
            scores = scores.append(cat_features_scores, ignore_index=True)

        mask = scores["Selected"] == 1
        self.used_features = scores.loc[mask, "Variable"].tolist()

        return scores.reset_index(drop=True)