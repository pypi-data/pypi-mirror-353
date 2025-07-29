from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from sklearn.exceptions import NotFittedError
from operator import ge, le

from dreamml.configs.config_storage import ConfigStorage
from dreamml.data._dataset import DataSet
from dreamml.logging.logger import CombinedLogger
from dreamml.logging import get_logger
from dreamml.modeling.models.estimators import BoostingBaseModel
from dreamml.stages.stage import BaseStage
from dreamml.utils.confidence_interval import create_bootstrap_scores
from dreamml.utils.confidence_interval import calculate_conf_interval
from dreamml.features.feature_selection.select_subset_features import (
    select_subset_features,
)
from dreamml.stages.model_based_stage import ModelBasedStage
from dreamml.stages.algo_info import AlgoInfo
from dreamml.pipeline.fitter import FitterBase
from dreamml.utils import ValidationType

_logger = get_logger(__name__)


def get_batch_selection_model_params():
    """
    Retrieves the parameters for batch selection models.

    Returns:
        dict: A dictionary containing configurations for various batch selection steps.
    """
    shap_fraction_sample = 1.0

    params = {
        "step_10": {
            "features_step": 10,
            "min_features": 40,
            "fraction_sample": shap_fraction_sample,
        },
        "step_5": {
            "features_step": 5,
            "min_features": 10,
            "fraction_sample": shap_fraction_sample,
        },
        "step_10_down": {
            "features_step": 10,
            "min_features": 40,
            "fraction_sample": shap_fraction_sample,
        },
        "step_5_down": {
            "features_step": 5,
            "min_features": 20,
            "fraction_sample": shap_fraction_sample,
        },
        "step_1_down": {
            "features_step": 1,
            "min_features": 1,
            "fraction_sample": shap_fraction_sample,
        },
    }

    return params


class BatchSelectionModelStage(ModelBasedStage):
    """
    Stage for batch TOP@ feature selection and model building.
    """

    name = "batch"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: FitterBase,
        vectorization_name: str = None,
        stage_params: str = "step_10",
    ):
        """
        Initializes the BatchSelectionModelStage.

        Args:
            algo_info (AlgoInfo): Information about the algorithm.
            config (ConfigStorage): Configuration storage instance.
            fitter (FitterBase): Fitter instance for training models.
            vectorization_name (Optional[str], optional): Name of the vectorization method. Defaults to None.
            stage_params (str, optional): Stage parameters key. Defaults to "step_10".
        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
        )
        # General params
        self.config_storage = config
        self.predictions = None
        self.stage_all_models_dict = None
        self.stage_params = get_batch_selection_model_params()[stage_params]
        self.all_cv_mean_scores = {}
        self.maximize = self.eval_metric.maximize
        self.metric_comp = ge if self.maximize else le
        self.choose_best_model = max if self.maximize else min
        self.remaining_features = config.data.columns.remaining_features

    @property
    def check_is_fitted(self):
        """
        Checks if the estimator is fitted.

        Raises:
            NotFittedError: If the estimator is not fitted.

        Returns:
            bool: True if the estimator is fitted.
        """
        if not self.is_fitted:
            msg = (
                "This estimator is not fitted yet. Call 'fit' with "
                "appropriate arguments before using this estimator."
            )
            raise NotFittedError(msg)
        return True

    def _set_used_features(self, data_storage: DataSet, used_features: List = None):
        """
        Sets the features to be used for modeling.

        Args:
            data_storage (DataSet): The data storage instance.
            used_features (List, optional): List of features to use. Defaults to None.

        Returns:
            List: List of features after setting and dropping text features.
        """
        if not used_features:
            data = data_storage.get_eval_set(
                used_features, vectorization_name=self.vectorization_name
            )
            used_features = data["train"][0].columns.tolist()

        used_features = self._drop_text_features(data_storage, used_features)
        return used_features

    def _stop_criteria(
        self, y_pred: pd.Series, y_true: pd.Series, criteria: str = None
    ) -> float:
        """
        Calculates the threshold for stopping model building.

        Args:
            y_pred (pd.Series): The predicted values from the model.
            y_true (pd.Series): The true target values.
            criteria (str, optional): The stopping criteria ('model_score' or 'model_ci'). Defaults to None.

        Returns:
            float: The threshold value for stopping model building.
        """
        if criteria == "model_score":
            return self.eval_metric(y_true, y_pred)
        elif criteria == "model_ci":
            bootstrap_samples = (
                self.config_storage.stages.batch_selection.bootstrap_samples
            )
            random_seed = self.config_storage.pipeline.reproducibility.random_seed
            scores = create_bootstrap_scores(
                y_true,
                y_true,
                y_pred,
                self.eval_metric,
                bootstrap_samples,
                random_seed,
                task=self.task,
            )
            ci = calculate_conf_interval(scores)
            return ci[0]
        else:
            return np.inf

    def _batch_feature_selection(
        self,
        model,
        feature_importance,
        data_storage,
        used_features,
        features_step: int = 10,
        min_features: int = 10,
    ):
        """
        Builds and selects the best model based on feature importance.

        Args:
            model (BoostingBaseModel): The model instance to train.
            feature_importance (pd.DataFrame): DataFrame containing feature names and their importance metrics.
            data_storage (DataSet): The data storage instance.
            used_features (List[str]): List of features currently in use.
            features_step (int, optional): Step size for number of features to add. Defaults to 10.
            min_features (int, optional): Minimum number of features to start with. Defaults to 10.

        Returns:
            Tuple[BoostingBaseModel, Dict]: 
                - The recommended final model.
                - A dictionary containing all built models with their estimators and predictions.
        """
        models_dict = {}
        sample_for_validation = (
            self.config_storage.stages.batch_selection.sample_for_validation
        )  # valid, test, oot; valid on cv -> OOF
        n_features = np.arange(min_features, feature_importance.shape[0], features_step)
        data = data_storage.get_eval_set(
            used_features, vectorization_name=self.vectorization_name
        )

        model_ = self._init_model(used_features=used_features, hyperparams=model.params)
        model_, _, y_pred = self.fitter.train(
            estimator=model_,
            data_storage=data_storage,
            metric=self.eval_metric,
            used_features=used_features,
            vectorization_name=self.vectorization_name,
        )
        # Determine the dataset for metric calculation, stopping, and selecting the best model
        if sample_for_validation == "test":
            y_pred = model_.transform(data["test"][0])
            y_true = data["test"][1]
            metric_to_stop = self._stop_criteria(
                y_pred, y_true, self.config_storage.stages.batch_selection.stop_criteria
            )
        elif sample_for_validation == "oot":
            y_pred = model_.transform(data["OOT"][0])
            y_true = data["OOT"][1]
            metric_to_stop = self._stop_criteria(
                y_pred, y_true, self.config_storage.stages.batch_selection.stop_criteria
            )
        else:  # "valid"
            y_true = self.fitter.get_validation_target(
                data_storage, vectorization_name=self.vectorization_name
            )
            metric_to_stop = self._stop_criteria(
                y_pred, y_true, self.config_storage.stages.batch_selection.stop_criteria
            )

        # Process of building models with TOP@ feature selection
        for n in tqdm(n_features):
            selected_features = select_subset_features(
                feature_importance, self.remaining_features, top_k=n
            )
            model_for_step = self._init_model(
                used_features=selected_features, hyperparams=model_.params
            )
            model_candidate, _, pred = self.fitter.train(
                estimator=model_for_step,
                data_storage=data_storage,
                metric=self.eval_metric,
                used_features=selected_features,
                vectorization_name=self.vectorization_name,
            )

            model_name = f"{model_candidate.model_name}.{len(selected_features)}.S{features_step}"
            self.add_cv_score(model_name)

            if sample_for_validation == "test":
                pred = model_candidate.transform(data["test"][0])
            if sample_for_validation == "oot":
                pred = model_candidate.transform(data["OOT"][0])

            models_dict[model_name] = {
                "estimator": model_candidate,
                "predictions": pred,
            }

            metric = self.eval_metric(y_true, pred)

            if self.metric_comp(metric, metric_to_stop):
                break
        else:  # If no stopping condition met, add the base model
            model_name = (
                f"{model_.model_name}.{feature_importance.shape[0]}.S{features_step}"
            )
            self.add_cv_score(model_name)
            models_dict[model_name] = {"estimator": model_, "predictions": y_pred}
            # Select the best model
        if self.task in ["regression", "timeseries"]:
            models_scores = {
                key: self.eval_metric(y_true, models_dict[key]["predictions"])
                for key in models_dict
            }
        else:
            models_scores = {
                key: self.eval_metric(y_true, models_dict[key]["predictions"])
                for key in models_dict
            }

        # Calculate confidence interval for the best model
        best_model = self.choose_best_model(models_scores, key=models_scores.get)
        best_model_pred = models_dict[best_model]["predictions"]
        best_model_scores = create_bootstrap_scores(
            y_true,
            y_true,
            best_model_pred,
            self.eval_metric,
            task=self.task,
        )
        best_model_ci = calculate_conf_interval(best_model_scores)

        recommend_final_model = self.choose_recommend_final_model(
            best_model_ci, models_dict, models_scores, best_model
        )
        logger = CombinedLogger([self._logger or _logger])
        logger.info(
            f"Best model after {self.name}{self.stage_params['features_step']} stage: {best_model}"
        )
        logger.info(
            f"Recommended model after {self.name}{self.stage_params['features_step']} stage: {recommend_final_model}"
        )

        return models_dict[recommend_final_model]["estimator"], models_dict

    @staticmethod
    def choose_recommend_final_model(
        best_model_ci, models_dict, models_scores, best_model
    ):
        """
        Selects all suitable models based on the confidence interval of the best model.

        Args:
            best_model_ci (Tuple[float, float]): Confidence interval of the best model's metric.
            models_dict (Dict): Dictionary of models with their estimators and predictions.
            models_scores (Dict): Dictionary of models and their metric scores.
            best_model (str): The name of the best model.

        Returns:
            str: The name of the recommended final model.
        """
        suitable_models_list = [
            key
            for key in models_scores
            if best_model_ci[0] <= models_scores[key] <= best_model_ci[1]
        ]
        if not suitable_models_list:
            suitable_models_list.append(best_model)
        suitable_models_dict = {
            key: len(models_dict[key]["estimator"].used_features)
            for key in suitable_models_list
        }
        return min(suitable_models_dict, key=suitable_models_dict.get)

    def add_cv_score(self, model_name: str):
        """
        Adds the cross-validation mean score to the score dictionary if Cross-Validation is used.

        Args:
            model_name (str): The name of the model.
        """
        if self.fitter.validation_type == ValidationType.CV:
            self.all_cv_mean_scores[model_name] = self.fitter.cv_mean_score

    def _fit(
        self,
        model: BoostingBaseModel,
        used_features: List[str],
        data_storage: DataSet,
        models: List[BoostingBaseModel] = None,
    ) -> BaseStage:
        """
        Main function to run the batch selection and model building stage.

        Args:
            model (BoostingBaseModel): The model instance to train.
            used_features (List[str]): The list of features to use.
            data_storage (DataSet): The data storage instance.
            models (List[BoostingBaseModel], optional): List of models obtained from cross-validation. Defaults to None.

        Returns:
            BaseStage: The fitted stage instance.

        Raises:
            NotImplementedError: If the method '_set_params' is called.
        """
        np.random.seed(self.config_storage.pipeline.reproducibility.random_seed)
        if not used_features:
            used_features = model.used_features
        self.used_features = self._set_used_features(
            data_storage=data_storage, used_features=used_features
        )

        if self.fitter.validation_type == ValidationType.CV:
            splitter_df = data_storage.get_cv_splitter_df(
                self.fitter.cv.get_required_columns()
            )
        else:
            splitter_df = None

        # TODO: Maximizing and minimizing the metric is needed for permutation importance, not for Shap
        importance_ = self.fitter.calculate_importance(
            estimators=model,
            data_storage=data_storage,
            used_features=used_features,
            splitter_df=splitter_df,
            fraction_sample=self.stage_params["fraction_sample"],
            vectorization_name=self.vectorization_name,
        )

        final_model, models_dict = self._batch_feature_selection(
            model=model,
            feature_importance=importance_,
            data_storage=data_storage,
            used_features=used_features,
            features_step=self.stage_params["features_step"],
            min_features=self.stage_params["min_features"],
        )

        self.final_model = final_model
        self.stage_all_models_dict = models_dict
        self.used_features = final_model.used_features
        self.prediction = self.prediction_out(data_storage)
        self.is_fitted = True

        return self

    def _set_params(self, params: dict):
        """
        Sets the parameters for the stage.

        Args:
            params (dict): A dictionary of parameters.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError