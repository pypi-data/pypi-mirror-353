from typing import List, Dict
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
from dreamml.pipeline.fitter import FitterBase
from dreamml.stages.batch_selection.batch_selection_model_stage import (
    get_batch_selection_model_params,
)
from dreamml.stages.stage import BaseStage
from dreamml.utils.confidence_interval import create_bootstrap_scores
from dreamml.utils.confidence_interval import calculate_conf_interval
from dreamml.features.feature_selection.select_subset_features import (
    select_subset_features_reverse,
)
from dreamml.stages.model_based_stage import ModelBasedStage
from dreamml.stages.algo_info import AlgoInfo
from dreamml.utils import ValidationType
from dreamml.features.feature_selection._shap_importance import ShapFeatureSelection

_logger = get_logger(__name__)


class BatchSelectionReverseModelStage(ModelBasedStage):
    """
    Stage for batch TOP@ feature selection and model training in reverse order.
    
    This stage performs feature selection by iteratively removing the least important features 
    based on SHAP values and trains models at each step to identify the optimal feature set.
    """

    name = "batch_r"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: FitterBase,
        vectorization_name: str = None,
        stage_params: str = "step_10",
    ):
        """
        Initializes the BatchSelectionReverseModelStage.

        Args:
            algo_info (AlgoInfo): Information about the algorithm being used.
            config (ConfigStorage): Configuration storage object.
            fitter (FitterBase): Fitter object for training models.
            vectorization_name (str, optional): Name of the vectorization method. Defaults to None.
            stage_params (str, optional): Parameters for the stage. Defaults to "step_10".
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
        Checks if the estimator has been fitted.

        Raises:
            NotFittedError: If the estimator is not fitted.

        Returns:
            bool: True if fitted.
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
        Sets the features to be used for model training.

        If no features are provided, it retrieves them from the evaluation set.

        Args:
            data_storage (DataSet): Data storage object.
            used_features (List, optional): List of features to use. Defaults to None.

        Returns:
            List: List of features to be used after dropping text features.
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
        Calculates the threshold for stopping model training based on specified criteria.

        Args:
            y_pred (pd.Series): Vector of model predictions.
            y_true (pd.Series): Vector of true values.
            criteria (str, optional): Criterion for stopping.
                - 'model_score': Stop if the model score exceeds the base model score.
                - 'model_ci': Stop if the model score falls within the confidence interval of the base model score.
                Defaults to None.

        Returns:
            float: Threshold value for stopping model training.
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
        self, model, data_storage, used_features, features_step: int = 10
    ):
        """
        Performs batch feature selection by iteratively removing features and training models.

        Args:
            model (BoostingBaseModel): Instance of the model to train.
            data_storage (DataSet): Data storage object.
            used_features (List): List of features to use.
            features_step (int, optional): Number of features to remove at each step. Defaults to 10.

        Returns:
            tuple:
                BoostingBaseModel: Recommended final model.
                Dict: Dictionary containing all trained models and their predictions.
        """
        models_dict = {}
        sample_for_validation = (
            self.config_storage.stages.batch_selection.sample_for_validation
        )  # valid, test, oot; valid on cv -> OOF
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
        shap = ShapFeatureSelection(
            model_,
            self.config_storage.pipeline.eval_metric,
            metric_params=self.metric_params,
            task=self.task,
        )

        feature_importance = shap._calculate_feature_importance(
            data_storage.get_train(
                used_features, vectorization_name=self.vectorization_name
            )[0]
        )
        n_features = np.arange(
            feature_importance.shape[0],
            self.stage_params["min_features"],
            -self.stage_params["features_step"],
        )

        # Determine the sample for metric calculation, stopping, and best model selection
        if sample_for_validation == "test":
            y_true = data["test"][1]
        elif sample_for_validation == "oot":
            y_true = data["OOT"][1]
        else:  # "valid"
            y_true = self.fitter.get_validation_target(
                data_storage, vectorization_name=self.vectorization_name
            )

        # Process of building models with TOP@ feature selection
        for _ in tqdm(n_features):
            selected_features = select_subset_features_reverse(
                feature_importance,
                self.remaining_features,
                bot_k=self.stage_params["features_step"],
            )
            if len(selected_features) == 0:
                break
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

            shap = ShapFeatureSelection(
                model_candidate,
                self.config_storage.pipeline.eval_metric,
                metric_params=self.metric_params,
                task=self.task,
            )

            feature_importance = shap._calculate_feature_importance(
                data_storage.get_train(
                    selected_features, vectorization_name=self.vectorization_name
                )[0]
            )
            model_name = f"{model_candidate.model_name}.{len(selected_features)}_reverse.S{features_step}"
            self.add_cv_score(model_name)

            if sample_for_validation == "test":
                pred = model_candidate.transform(data["test"][0])
            if sample_for_validation == "oot":
                pred = model_candidate.transform(data["OOT"][0])

            models_dict[model_name] = {
                "estimator": model_candidate,
                "predictions": pred,
            }

        models_scores = {
            key: self.eval_metric(y_true, models_dict[key]["predictions"])
            for key in models_dict
        }

        if len(models_scores) == 0:
            return model_, models_dict

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
            best_model_ci (tuple): Confidence interval of the best model.
            models_dict (Dict): Dictionary of all models and their details.
            models_scores (Dict): Dictionary of all models and their scores.
            best_model (str): Identifier of the best model.

        Returns:
            str: Identifier of the recommended final model.
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
        Adds the cross-validation score to the CV scores dictionary if Cross-Validation is used.

        Args:
            model_name (str): Name of the model.
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
        Executes the main function to run the batch selection reverse stage.

        Args:
            model (BoostingBaseModel): Instance of the model to train.
            used_features (List[str]): List of features to use.
            data_storage (DataSet): Data storage object.
            models (List[BoostingBaseModel], optional): List of models obtained from CV. Defaults to None.

        Returns:
            BaseStage: The fitted stage instance.
        """
        np.random.seed(self.config_storage.pipeline.reproducibility.random_seed)
        if not used_features:
            used_features = model.used_features
        self.used_features = self._set_used_features(
            data_storage=data_storage, used_features=used_features
        )

        # TODO: Maximizing and minimizing the metric are necessary for permutation importance, not for SHAP
        final_model, models_dict = self._batch_feature_selection(
            model=model,
            data_storage=data_storage,
            used_features=used_features,
            features_step=self.stage_params["features_step"],
        )

        self.final_model = final_model
        self.stage_all_models_dict = models_dict
        self.used_features = final_model.used_features
        self.prediction = self.prediction_out(data_storage)
        self.is_fitted = True

        return self