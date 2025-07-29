from copy import deepcopy
from typing import Dict, Optional, Callable

import numpy as np
import pandas as pd

from dreamml.logging import get_logger
from dreamml.modeling.models.estimators import BaseModel
from dreamml.utils.vectorization_eval_set import get_eval_set_with_embeddings

_logger = get_logger(__name__)


class BaseMetricsCalculator:
    """A base class for calculating metrics for multiple models across various evaluation sets.

    This class handles the computation of specified metrics for each model provided,
    across different evaluation datasets. It supports pre-calculated predictions,
    vectorization of datasets, and the calculation of metric ratios.

    Attributes:
        models (Dict[str, BaseModel]): A dictionary of model names to BaseModel instances.
        predictions_ (Dict): A dictionary to store predictions for each model and dataset.
        vectorizers (Dict): A dictionary of vectorizer names to vectorizer instances.
        metrics (Dict): A dictionary of metric names to metric functions.
        calculate_metrics_ratio (bool): Flag to indicate whether to calculate metric ratios.
        transform_target (Optional[Callable]): A callable to transform target values.
    """

    def __init__(
        self,
        models: Dict[str, BaseModel],
        predictions: Optional[Dict] = None,
        vectorizers: Optional[Dict] = None,
        calculate_metrics_ratio: bool = False,
        transform_target: Optional[Callable] = None,
    ) -> None:
        """Initializes the BaseMetricsCalculator with models, predictions, and other configurations.

        Args:
            models (Dict[str, BaseModel]): A dictionary mapping model names to BaseModel instances.
            predictions (Optional[Dict], optional): Pre-calculated predictions. Defaults to None.
            vectorizers (Optional[Dict], optional): A dictionary of vectorizer instances. Defaults to None.
            calculate_metrics_ratio (bool, optional): Whether to calculate the ratio of metrics. Defaults to False.
            transform_target (Optional[Callable], optional): A function to transform target values. Defaults to None.
        """
        self.models = models
        self.predictions_ = predictions or {}
        self.vectorizers = vectorizers
        self.metrics = self._get_metrics_to_calculate()
        self.calculate_metrics_ratio = calculate_metrics_ratio
        self.transform_target = transform_target

    def transform(self, **eval_sets):
        """Calculates metrics for each model and evaluation set, returning the results as a DataFrame.

        If predictions are not pre-calculated, it generates predictions for all models and evaluation sets.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation sets.
                Each key is the name of the dataset, and the value is a tuple containing
                a pandas DataFrame of features and a pandas Series of true target values.

        Returns:
            pd.DataFrame: A DataFrame containing the computed metric values for each model and dataset.

        Raises:
            ValueError: If there is an issue with the input evaluation sets.
        """
        if not self.predictions_:
            self.create_all_predictions(**eval_sets)
        else:
            _logger.info("Used Pre-calculated predictions")

        scores = {}
        for model in self.models:
            scores[model] = self.calculate_metrics(model, **eval_sets)

        return self._to_frame(scores, **eval_sets)

    def _to_frame(self, scores: dict, **eval_sets) -> pd.DataFrame:
        """Converts the scores dictionary into a pandas DataFrame with appropriately named columns.

        Args:
            scores (dict): A dictionary where each key is a model name and the value is a list of metric scores.
            **eval_sets: Arbitrary keyword arguments representing evaluation sets.

        Returns:
            pd.DataFrame: A DataFrame with metric scores, model names, and additional details.

        Raises:
            KeyError: If expected evaluation sets are missing when calculating metric ratios.
        """
        scores = pd.DataFrame(scores)
        scores = scores.T.reset_index()

        scores_name = ["Model Name", "# Features"]
        for metric in self.metrics:
            for sample in eval_sets:
                scores_name.append(f"{metric} {sample}")

            if self.calculate_metrics_ratio:
                scores_name.append(f"{metric} delta train vs test")
                scores_name.append(f"{metric} delta train vs test, %")

                if "OOT" in eval_sets:
                    scores_name.append(f"{metric} delta train vs OOT")
                    scores_name.append(f"{metric} delta train vs OOT, %")

        scores.columns = scores_name
        scores = scores.fillna(0)

        scores["Model Details"] = [
            f"Link to train sheet {model}" for model in scores["Model Name"]
        ]
        return scores

    @staticmethod
    def create_prediction(model: BaseModel, data: pd.DataFrame) -> np.array:
        """Generates predictions using the specified model on the provided dataset.

        Handles different model types, such as autoencoders, and ensures that
        a prediction array is returned even if the model fails to transform.

        Args:
            model (BaseModel): An instance of a machine learning model.
            data (pd.DataFrame): A DataFrame containing the feature matrix for prediction.

        Returns:
            np.array: An array of predictions generated by the model.

        Raises:
            TypeError: If the model's transform method does not support the provided data.
        """
        try:
            if model.model_name in ["ae", "vae"]:
                pred = model.transform(data, return_output=True)
            else:
                pred = model.transform(data)
        except TypeError:
            pred = np.zeros(data.shape[0])

        return pred

    def calculate_metrics(self, model_name, **eval_sets):
        """Calculates metrics for a specific model across all evaluation sets.

        Args:
            model_name (str): The name of the model for which to calculate metrics.
            **eval_sets: Arbitrary keyword arguments representing evaluation sets.

        Returns:
            list: A list containing the number of features used by the model and the computed metric scores.

        Raises:
            KeyError: If the model_name does not exist in the models dictionary.
            ValueError: If there is an issue computing a metric.
        """
        unsupervised_flag = False

        try:
            model = self.models[model_name]
            metrics_score = [len(model.used_features)]

            if model.model_name in ["ae", "vae"]:
                unsupervised_flag = True

        except TypeError:
            sample_name = next(iter(eval_sets))
            metrics_score = [len(eval_sets[sample_name][0])]

        for metric_name, metric in self.metrics.items():
            eval_sets_score = {}
            for sample in eval_sets:
                if unsupervised_flag:
                    target, _ = eval_sets[sample]
                else:
                    _, target = eval_sets[sample]

                if self.transform_target is not None:
                    target = self.transform_target(target)

                pred = self.predictions_[model_name]
                try:
                    score = metric(target, pred[sample])
                except (ValueError, TypeError, KeyError) as e:
                    _logger.exception(f"{e}")
                    score = np.nan

                eval_sets_score[sample] = score

            for sample, score in eval_sets_score.items():
                metrics_score.append(score)

            if self.calculate_metrics_ratio:
                diff = np.abs(eval_sets_score["train"] - eval_sets_score["test"])
                relative_diff = 100 * diff / eval_sets_score["train"]

                metrics_score += [diff, relative_diff]

                if "OOT" in eval_sets:
                    diff = np.abs(eval_sets_score["train"] - eval_sets_score["OOT"])
                    relative_diff = 100 * diff / eval_sets_score["train"]
                    metrics_score += [diff, relative_diff]

        return metrics_score

    def create_all_predictions(self, **eval_sets):
        """Generates predictions for all models across all provided evaluation sets.

        Applies vectorization if vectorizers are provided and the model requires it.
        Stores the predictions in the `predictions_` attribute.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation sets.

        Raises:
            ValueError: If a required vectorizer is not found in the vectorizers dictionary.
        """
        for model_name, model in self.models.items():
            eval_sets_ = deepcopy(eval_sets)
            self.predictions_[model_name] = {}
            samples_preds = {}

            if self.vectorizers and model.vectorization_name != "bert":
                if hasattr(model, "vectorizer_full_name"):
                    vectorizer_name = model.vectorizer_full_name
                else:
                    vectorizer_name = (
                        f"vectorization_{model.vectorization_name}_vectorizer"
                    )

                if not vectorizer_name or vectorizer_name not in self.vectorizers:
                    raise ValueError(f"{vectorizer_name} not found in vectorizers.")
                vectorizer = self.vectorizers[vectorizer_name]
                eval_sets_ = get_eval_set_with_embeddings(vectorizer, eval_sets_)

            for sample_name, (data, _) in eval_sets_.items():
                pred = self.create_prediction(model, data)

                samples_preds[sample_name] = pred

            self.predictions_[model_name] = samples_preds

    def _get_metrics_to_calculate(self):
        """Retrieves the metrics that need to be calculated.

        This method should be implemented by subclasses to specify which metrics
        are relevant for their particular use case.

        Raises:
            NotImplementedError: If the method is not overridden in a subclass.
        """
        raise NotImplementedError