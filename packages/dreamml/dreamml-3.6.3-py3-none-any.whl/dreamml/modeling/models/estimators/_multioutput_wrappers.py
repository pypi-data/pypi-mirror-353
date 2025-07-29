from collections import defaultdict
from typing import List, Tuple, Dict, Callable, Union

import numpy as np
import pandas as pd
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import LabelBinarizer
from sklearn.utils.fixes import delayed
from sklearn.base import clone
from joblib import Parallel

from dreamml.utils.serialize import Serializable


class OneVsRestClassifierWrapper(OneVsRestClassifier, Serializable):
    """A wrapper for the One-vs-Rest classifier with additional serialization capabilities.

    This class extends sklearn's OneVsRestClassifier by adding serialization methods
    and handling best iterations for each binary classifier.

    Args:
        estimator: The base estimator from which the One-vs-Rest classifiers are built.
        n_jobs (int, optional): The number of jobs to run in parallel. If set to 0, defaults to 1.
        verbose (int, optional): The verbosity level. Defaults to 0.
        get_best_iteration_func (Callable): A function to determine the best iteration for an estimator.
        n_estimators (Union[int, List[int]]): The number of estimators to use. Can be a single integer
            or a list of integers corresponding to each class.

    Attributes:
        verbose (int): The verbosity level.
        _best_iteration_per_binary (List[int]): Best iteration numbers for each binary classifier.
        get_best_iteration_func (Callable): Function to get the best iteration from an estimator.
        n_estimators (Union[int, List[int]]): Number of estimators.
        estimators_ (List): List of fitted binary estimators.
        n_features_in_ (int): Number of features seen during fit.
        feature_names_in_ (List[str]): Names of features seen during fit.
    """

    def __init__(
        self,
        estimator,
        *,
        n_jobs=None,
        verbose=0,
        get_best_iteration_func: Callable,
        n_estimators: Union[int, List[int]]
    ):
        super().__init__(estimator=estimator, n_jobs=1 if n_jobs == 0 else n_jobs)
        self.verbose = verbose
        self._best_iteration_per_binary: List[int] = []
        self.get_best_iteration_func = get_best_iteration_func
        self.n_estimators = n_estimators
        self.estimators_ = None
        self.n_features_in_ = None
        self.feature_names_in_ = None

    def _fit_binary(self, estimator, X, y, class_idx: int, **fit_params):
        """Fit a single binary estimator.

        Args:
            estimator: The estimator to fit.
            X (pd.DataFrame): The feature data.
            y (pd.Series or np.ndarray): The target data for the binary classification.
            class_idx (int): The index of the class being fitted.
            **fit_params: Additional parameters to pass to the estimator's fit method.

        Returns:
            Tuple[estimator, int, int]: A tuple containing the fitted estimator, class index,
                and the best iteration number.

        Raises:
            ValueError: If the target `y` contains only one unique class.
        """
        unique_y = np.unique(y)
        if len(unique_y) == 1:
            raise ValueError("The number of classes must be greater than 1.")
        else:
            estimator = clone(estimator)

            estimator.set_params(n_estimators=self.n_estimators[class_idx])
            estimator.fit(X, y, **fit_params)
            best_iteration = self.get_best_iteration_func(estimator)

        return estimator, class_idx, best_iteration

    def _init_sklearn_label_binarizer(self, y):
        """Initialize the LabelBinarizer for the target variable.

        Args:
            y (pd.DataFrame or np.ndarray): The target data to binarize.
        """
        self.label_binarizer_ = LabelBinarizer(sparse_output=True)
        self.label_binarizer_.fit_transform(y)
        self.classes_ = self.label_binarizer_.classes_

    def _remove_nan_values(
        self,
        eval_set_for_class_idx: List[Tuple[pd.DataFrame, pd.Series]],
        X: pd.DataFrame,
        y_slice_for_class_idx: pd.Series,
    ):
        """Remove rows with NaN values in the target for training and validation sets.

        This method ensures that the One-vs-Rest approach handles cases where the target
        contains NaN values by ignoring such rows during training and validation.

        Args:
            eval_set_for_class_idx (List[Tuple[pd.DataFrame, pd.Series]]): List of evaluation sets
                for the specific class.
            X (pd.DataFrame): The feature data.
            y_slice_for_class_idx (pd.Series): The target data slice for the specific class.

        Returns:
            Tuple[List[Tuple[pd.DataFrame, pd.Series]], pd.DataFrame, pd.Series]:
                A tuple containing the cleaned evaluation sets, feature data without NaNs,
                and target data without NaNs.
        """
        mask_y = y_slice_for_class_idx.isna()
        X = X[~mask_y]
        y_slice_for_class_idx = y_slice_for_class_idx[~mask_y]

        for idx, (X_sample, y_sample) in enumerate(eval_set_for_class_idx):
            mask_y_sample = y_sample.isna()
            X_sample = X_sample[~mask_y_sample]
            y_sample = y_sample[~mask_y_sample]
            eval_set_for_class_idx[idx] = (X_sample, y_sample)

        return eval_set_for_class_idx, X, y_slice_for_class_idx

    def fit(self, X, y, **fit_params):
        """Fit the One-vs-Rest classifier.

        This method fits a binary classifier for each class in a One-vs-Rest fashion,
        handling NaN values in the target and determining the best iteration for each binary classifier.

        Args:
            X (pd.DataFrame or np.ndarray): The feature data.
            y (pd.DataFrame or np.ndarray): The target data.
            **fit_params: Additional parameters to pass to the underlying estimator's fit method.

        Returns:
            self: Returns the instance itself.

        Raises:
            ValueError: If `n_estimators` is neither an integer nor a list of integers corresponding to each class.
        """
        num_classes = y.shape[1]
        self._best_iteration_per_binary = [0 for _ in range(num_classes)]

        if isinstance(self.n_estimators, int):
            self.n_estimators = [self.n_estimators for _ in range(num_classes)]

        eval_set = fit_params.pop("eval_set", [(X, y)])
        eval_set_sliced = get_eval_set_sliced(eval_set, num_classes)

        self._init_sklearn_label_binarizer(y.fillna(value=0))

        delayed_func_kwargs_list = []
        for class_idx in range(num_classes):
            eval_set_for_class_idx = eval_set_sliced[class_idx]
            y_slice_for_class_idx = (
                y.iloc[:, class_idx] if isinstance(y, pd.DataFrame) else y[:, class_idx]
            )

            (
                eval_set_for_class_idx,
                X_without_nan,
                y_slice_for_class_idx,
            ) = self._remove_nan_values(
                eval_set_for_class_idx, X, y_slice_for_class_idx
            )

            fit_params["eval_set"] = eval_set_for_class_idx
            y_slice = y_slice_for_class_idx

            delayed_func_kwargs = dict(
                estimator=self.estimator,
                X=X_without_nan,
                y=y_slice,
                class_idx=class_idx,
                **fit_params
            )
            delayed_func_kwargs_list.append(delayed_func_kwargs)

        parallel = Parallel(n_jobs=self.n_jobs, verbose=self.verbose)

        delayed_func = delayed(self._fit_binary)

        artifacts = parallel(
            delayed_func(**kwargs) for kwargs in delayed_func_kwargs_list
        )

        self.estimators_ = [artifact[0] for artifact in artifacts]
        for estimator, class_idx, best_iteration in artifacts:
            self._best_iteration_per_binary[class_idx] = best_iteration

        if hasattr(self.estimators_[0], "n_features_in_"):
            self.n_features_in_ = self.estimators_[0].n_features_in_
        if hasattr(self.estimators_[0], "feature_names_in_"):
            self.feature_names_in_ = self.estimators_[0].feature_names_in_

        return self

    @property
    def best_iteration(self) -> List[int]:
        """List of best iteration numbers for each binary classifier.

        Returns:
            List[int]: Best iteration numbers.
        """
        return self._best_iteration_per_binary

    def serialize(self) -> dict:
        """Serialize the classifier to a dictionary.

        This method captures both the initialization parameters and the additional
        attributes required to fully reconstruct the classifier.

        Returns:
            dict: A dictionary containing serialized data of the classifier.
        """
        init_dict = {
            "estimator": self.estimator,
            "n_jobs": self.n_jobs,
            "get_best_iteration_func": self.get_best_iteration_func,  # FIXME: serialization
            "n_estimators": self.n_estimators,
        }

        additional_dict = {
            "estimator": self.estimator,
            "label_binarizer_": self.label_binarizer_,
            "classes_": self.classes_,
            "estimators_": self.estimators_,
            "n_features_in_": self.n_features_in_,
            "feature_names_in_": self.feature_names_in_,
            "_best_iteration_per_binary": self._best_iteration_per_binary,
            "n_estimators": self.n_estimators,
        }

        return self._serialize(init_data=init_dict, additional_data=additional_dict)

    @classmethod
    def deserialize(cls, data):
        """Deserialize a dictionary to reconstruct the classifier instance.

        Args:
            data (dict): The serialized data of the classifier.

        Returns:
            OneVsRestClassifierWrapper: The deserialized classifier instance.
        """
        instance = cls._deserialize(data)

        instance.estimator = data["additional"]["estimator"]
        instance.label_binarizer_ = data["additional"]["label_binarizer_"]
        instance.classes_ = data["additional"]["classes_"]
        instance.estimators_ = data["additional"]["estimators_"]
        instance.n_features_in_ = data["additional"]["n_features_in_"]
        instance.feature_names_in_ = data["additional"]["feature_names_in_"]
        instance._best_iteration_per_binary = data["additional"][
            "_best_iteration_per_binary"
        ]
        instance.n_estimators = data["additional"]["n_estimators"]

        return instance


def get_eval_set_sliced(
    eval_sets: List[Tuple[pd.DataFrame, pd.DataFrame]], num_classes: int
) -> Dict[int, List[Tuple[pd.DataFrame, pd.Series]]]:
    """Slice evaluation sets by each class index.

    This function takes a list of evaluation sets and splits the target variable
    for each class, returning a dictionary where each key corresponds to a class index
    and the value is a list of tuples containing the feature data and the sliced target.

    Args:
        eval_sets (List[Tuple[pd.DataFrame, pd.DataFrame]]): A list of tuples where each tuple
            contains feature data and target data.
        num_classes (int): The number of classes to slice the evaluation sets into.

    Returns:
        Dict[int, List[Tuple[pd.DataFrame, pd.Series]]]: A dictionary mapping each class index
            to its corresponding list of evaluation sets with sliced target variables.
    """
    eval_sets_by_class_idx = defaultdict(list)
    for X, y in eval_sets:
        for class_idx in range(num_classes):
            y_slice = (
                y.iloc[:, class_idx] if isinstance(y, pd.DataFrame) else y[:, class_idx]
            )

            eval_sets_by_class_idx[class_idx].append((X, y_slice))

    return eval_sets_by_class_idx