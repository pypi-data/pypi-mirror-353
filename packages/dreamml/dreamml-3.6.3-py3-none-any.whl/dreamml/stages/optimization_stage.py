import logging
from copy import deepcopy
from operator import gt, lt
from typing import Any, Dict

import numpy as np
from typing import List

from dreamml.data._hadoop import create_spark_session, stop_spark_session
import optuna
import pandas as pd
from py4j.protocol import Py4JJavaError
from sklearn.exceptions import NotFittedError
from hyperopt import hp

from dreamml.features.feature_vectorization import TfidfVectorization
from dreamml.features.text import TextFeaturesTransformer
from dreamml.modeling.metrics import metrics_mapping
from dreamml.modeling.models.estimators import BoostingBaseModel, BaseModel
from dreamml.modeling.models.optimizer._bayesian_cv_nlp import (
    NLPModelBayesianOptimizerCV,
)
from dreamml.pipeline.fitter import FitterBase
from dreamml.stages.stage import BaseStage
from dreamml.utils.temporary_directory import TempDirectory

optuna.logging.set_verbosity(optuna.logging.WARNING)

from dreamml.configs.config_storage import ConfigStorage
from dreamml.data._dataset import DataSet
from dreamml.utils import ValidationType
from dreamml.utils.spark_init import init_spark_env
from dreamml.utils.spark_session_configuration import spark_conf
from dreamml.stages.model_based_stage import ModelBasedStage
from dreamml.stages.algo_info import AlgoInfo
from dreamml.utils.get_n_iterartions import get_n_iterations
from dreamml.utils.splitter import concatenate_all_samples

from dreamml.modeling.models.optimizer import (
    BayesianOptimizationModel,
    CVBayesianOptimizationModel,
    OptunaOptimizationModel,
    CVOptunaOptimizationModel,
    DistributedOptimizationModel,
    DistributedOptimizationCVModel,
)
from dreamml.logging import get_logger


_logger = get_logger(__name__)


class OptimizationStage(ModelBasedStage):
    """Stage for searching and optimizing model hyperparameters.

    This stage handles the optimization of hyperparameters for a given model
    using different optimization strategies such as Optuna, Bayesian Optimization,
    and distributed optimization. It supports both cross-validation and holdout
    validation types.

    Attributes:
        name (str): The name of the stage.
        config_storage (ConfigStorage): Configuration storage object.
        predictions (Any): Predictions made by the model.
        tempdir (TempDirectory): Temporary directory for Spark sessions.
        text_transformer (TextFeaturesTransformer): Transformer for text features.
        vectorizer (TfidfVectorization): Vectorizer for text data.
    """

    name = "optimization"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: FitterBase,
        vectorization_name: str = None,
    ):
        """Initializes the OptimizationStage.

        Args:
            algo_info (AlgoInfo): Information about the algorithm.
            config (ConfigStorage): Configuration storage object.
            fitter (FitterBase): Fitter object to train models.
            vectorization_name (str, optional): Name of the vectorization technique. Defaults to None.
        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
        )
        # TODO Лучше не хранить объект конфига в стейдже, а взять все нужные параметры из него
        self.config_storage = config
        self.predictions = None
        self.tempdir = None
        self.text_transformer = None
        self.vectorizer = None

    @property
    def check_is_fitted(self):
        """Checks if the estimator has been fitted.

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
        """Determines and sets the features to be used for the model.

        Args:
            data_storage (DataSet): Data storage instance.
            used_features (List, optional): List of features to use. Defaults to None.

        Returns:
            List: Updated list of used features.
        """
        if not used_features:
            data = data_storage.get_eval_set(
                used_features, vectorization_name=self.vectorization_name
            )
            used_features = data["train"][0].columns.tolist()

        used_features = self._drop_text_features(data_storage, used_features)
        return used_features

    def _get_cv_optimizer(
        self,
        optimizer_type,
        splitter_df,
        model,
        optimization_grid_params,
        distributed_grid_params,
        optimization_iters,
        optimizer_timeout,
        random_seed,
    ):
        """Retrieves the appropriate cross-validation optimizer based on the optimizer type.

        Args:
            optimizer_type (str): Type of optimizer to use.
            splitter_df (pd.DataFrame): DataFrame for splitting data.
            model (BaseModel): Model to optimize.
            optimization_grid_params (dict): Parameters grid for optimization.
            distributed_grid_params (dict): Parameters grid for distributed optimization.
            optimization_iters (int): Number of iterations for optimization.
            optimizer_timeout (int): Timeout for the optimizer.
            random_seed (int): Seed for randomness.

        Raises:
            ValueError: If an invalid optimizer type is provided.

        Returns:
            Union[CVOptunaOptimizationModel, CVBayesianOptimizationModel, DistributedOptimizationCVModel]:
                The appropriate optimizer instance.
        """
        if optimizer_type == "local":
            return CVOptunaOptimizationModel(
                model=model,
                cv=self.fitter.cv,
                metric=self.eval_metric,
                params_bounds=optimization_grid_params,
                n_iter=optimization_iters,
                timeout=optimizer_timeout,
                seed=random_seed,
                splitter_df=splitter_df,
            )
        elif optimizer_type == "optuna":
            return CVOptunaOptimizationModel(
                model=model,
                cv=self.fitter.cv,
                metric=self.eval_metric,
                params_bounds=optimization_grid_params,
                n_iter=optimization_iters,
                timeout=optimizer_timeout,
                seed=random_seed,
                splitter_df=splitter_df,
            )
        elif optimizer_type == "bayesian":
            return CVBayesianOptimizationModel(
                model=model,
                cv=self.fitter.cv,
                metric=self.eval_metric,
                maximize=self.eval_metric.maximize,
                params_bounds=optimization_grid_params,
                n_iter=optimization_iters,
                timeout=optimizer_timeout,
                seed=random_seed,
                splitter_df=splitter_df,
            )
        elif optimizer_type == "distributed":
            return DistributedOptimizationCVModel(
                model=model,
                metric=self.eval_metric,
                cv=self.fitter.cv,
                params_bounds=distributed_grid_params,
                n_iter=optimization_iters,
                timeout=optimizer_timeout,
                seed=random_seed,
                splitter_df=splitter_df,
            )
        else:
            raise ValueError(f"Wrong optimizer type: {optimizer_type}")

    def _get_ho_optimizer(
        self,
        optimizer_type,
        model,
        data,
        optimization_grid_params,
        distributed_grid_params,
        optimization_iters,
        optimizer_timeout,
        random_seed,
    ):
        """Retrieves the appropriate holdout optimizer based on the optimizer type.

        Args:
            optimizer_type (str): Type of optimizer to use.
            model (BaseModel): Model to optimize.
            data (dict): Evaluation data.
            optimization_grid_params (dict): Parameters grid for optimization.
            distributed_grid_params (dict): Parameters grid for distributed optimization.
            optimization_iters (int): Number of iterations for optimization.
            optimizer_timeout (int): Timeout for the optimizer.
            random_seed (int): Seed for randomness.

        Raises:
            ValueError: If an invalid optimizer type is provided.

        Returns:
            Union[OptunaOptimizationModel, BayesianOptimizationModel, DistributedOptimizationModel]:
                The appropriate optimizer instance.
        """
        if optimizer_type == "local":
            return OptunaOptimizationModel(
                model=model,
                metric=self.eval_metric,
                eval_set=data["valid"],
                params_bounds=optimization_grid_params,
                n_iter=optimization_iters,
                timeout=optimizer_timeout,
                seed=random_seed,
            )
        elif optimizer_type == "optuna":
            return OptunaOptimizationModel(
                model=model,
                metric=self.eval_metric,
                eval_set=data["valid"],
                params_bounds=optimization_grid_params,
                n_iter=optimization_iters,
                timeout=optimizer_timeout,
                seed=random_seed,
            )
        elif optimizer_type == "bayesian":
            return BayesianOptimizationModel(
                model=model,
                metric=self.eval_metric,
                maximize=self.eval_metric.maximize,
                eval_set=data["valid"],
                params_bounds=optimization_grid_params,
                n_iter=optimization_iters,
                timeout=optimizer_timeout,
                seed=random_seed,
            )
        elif optimizer_type == "distributed":
            return DistributedOptimizationModel(
                model=model,
                metric=self.eval_metric,
                params_bounds=distributed_grid_params,
                n_iter=optimization_iters,
                timeout=optimizer_timeout,
                seed=random_seed,
            )
        else:
            raise ValueError(f"Wrong optimizer type: {optimizer_type}")

    @staticmethod
    def get_hyperopt_grid(bound_params):
        """Generates a Hyperopt parameter grid based on the bound parameters.

        Args:
            bound_params (dict): Dictionary of parameter bounds.

        Returns:
            dict: Hyperopt parameter grid.
        """
        bound_steps_grid = {  # Hyperparameter tuning steps
            "lr": 0.025,  # "pyboost"
            "learning_rate": 0.025,  # "xgboost"
            "min_child_weight": 10,  # "xgboost"
            "colsample_bytree": 0.05,  # "xgboost"
            "subsample": 0.05,  # "xgboost"
            "reg_lambda": 0.1,  # "xgboost", "lightgbm"
            "reg_alpha": 0.1,  # "xgboost", "lightgbm"
            "gamma": 0.05,  # "xgboost"
            "colsample_bylevel": 0.1,  # "catboost"
            "min_split_gain": 0.05,  # "lightgbm"
        }

        hyperopt_grid = {}
        for x in bound_params:
            if x in ["lr", "learning_rate"]:
                hyperopt_grid[x] = hp.loguniform(
                    x, bound_params[x][0], bound_params[x][1]
                )
            elif isinstance(bound_params[x][0], str):
                hyperopt_grid[x] = hp.choice(x, bound_params[x])
            else:
                hyperopt_grid[x] = hp.quniform(
                    x,
                    bound_params[x][0],
                    bound_params[x][1],
                    bound_steps_grid.get(x, 1.0),
                )

        return hyperopt_grid

    def _set_optimizer(
        self,
        model,
        opt_type,
        data_storage: DataSet,
        used_features: List = None,
        splitter_df: pd.DataFrame = None,
    ):
        """Selects and sets the optimizer based on the optimization type.

        Args:
            model (BaseModel): Model to optimize.
            opt_type (str): Type of optimization ("auto", "local", "optuna", "bayesian", "distributed").
            data_storage (DataSet): Data storage instance.
            used_features (List, optional): List of features to use. Defaults to None.
            splitter_df (pd.DataFrame, optional): Splitter DataFrame for CV. Defaults to None.

        Returns:
            Union[
                OptunaOptimizationModel,
                DistributedOptimizationModel,
                BayesianOptimizationModel,
                CVOptunaOptimizationModel,
                CVBayesianOptimizationModel,
                DistributedOptimizationCVModel
            ]: The selected optimizer instance.
        """
        optimization_iters = self.config_storage.stages.optimization.n_iterations
        optimizer_timeout = self.config_storage.stages.optimization.optimizer_timeout

        if optimizer_timeout == "auto":
            optimization_iters = None

        if optimization_iters == "auto":
            optimization_iters = get_n_iterations(data_storage.get_dev_n_samples())
            self.config_storage.stages.optimization.n_iterations_used = (
                optimization_iters
            )
        model_name = model.model_name  # XGBoost, LightGBM, CatBoost, etc
        optimization_grid_params = self.config_storage.models[
            model_name.lower()
        ].optimization_bounds

        if model_name == "iforest":
            self.eval_metric = metrics_mapping.get("avg_anomaly_score")(task=model.task)

        distributed_grid_params = self.get_hyperopt_grid(optimization_grid_params)

        data = data_storage.get_eval_set(
            used_features, vectorization_name=self.vectorization_name
        )
        random_seed = self.config_storage.pipeline.reproducibility.random_seed
        parallelism = self.config_storage.pipeline.parallelism
        # TODO: в следующих релизах mpack добавть подачу parallelism в гиперопт (сейчас в dreamml.modeling по дефолту 5)

        train_size = data["train"][0].shape[0]
        self._check_optimization_params(optimization_grid_params, train_size)

        validation_type = self.fitter.validation_type
        if validation_type == ValidationType.CV:
            if splitter_df is None:
                raise ValueError(f"splitter_df is required for cross-validation.")

            return self._get_cv_optimizer(
                opt_type,
                splitter_df,
                model,
                optimization_grid_params,
                distributed_grid_params,
                optimization_iters,
                optimizer_timeout,
                random_seed,
            )
        else:
            assert validation_type == ValidationType.HOLDOUT

            return self._get_ho_optimizer(
                opt_type,
                model,
                data,
                optimization_grid_params,
                distributed_grid_params,
                optimization_iters,
                optimizer_timeout,
                random_seed,
            )

    def _check_optimization_params(
        self, optimization_grid_params: dict, train_size: int
    ):
        """Validates and adjusts optimization parameters based on training size.

        Args:
            optimization_grid_params (dict): Parameters grid for optimization.
            train_size (int): Size of the training data.

        Returns:
            dict: Adjusted optimization parameters.
        """
        if (
            "min_child_samples" in optimization_grid_params
        ):  # xgboost, catboost, lightgbm
            return self._calc_dynamic_min_child_samples(
                optimization_grid_params, train_size, "min_child_samples"
            )
        elif "min_data_in_leaf" in optimization_grid_params:  # pyboost
            return self._calc_dynamic_min_child_samples(
                optimization_grid_params, train_size, "min_data_in_leaf"
            )
        return optimization_grid_params

    @staticmethod
    def _calc_dynamic_min_child_samples(
        optimization_grid_params: dict, train_size: int, param_name: str
    ):
        """Calculates dynamic minimum child samples based on training size.

        Args:
            optimization_grid_params (dict): Parameters grid for optimization.
            train_size (int): Size of the training data.
            param_name (str): Name of the parameter to adjust.

        Returns:
            dict: Updated optimization parameters.
        """
        min_child_samples = optimization_grid_params[param_name]
        right_border = max(train_size // 4, 5)
        optimization_grid_params[param_name] = (min_child_samples[0], right_border)
        return optimization_grid_params

    def _get_optimized_model(
        self,
        init_hyperparams: Dict[str, Any],
        data_storage: DataSet,
        used_features: List = None,
    ):
        """Optimizes the model's hyperparameters.

        Args:
            init_hyperparams (Dict[str, Any]): Initial hyperparameters of the model.
            data_storage (DataSet): Data storage instance.
            used_features (List, optional): List of features to use. Defaults to None.

        Returns:
            BaseModel: The optimized model instance.
        """
        if self.config_storage.stages.optimization.n_iterations == 0:
            return self
        opt_model = self._init_model(
            used_features=used_features, hyperparams=init_hyperparams
        )
        opt_model.verbose = 0
        opt_type = self.config_storage.stages.optimization.optimizer
        if opt_type == "auto":
            opt_type = "local"
        data = data_storage.get_eval_set(
            used_features, vectorization_name=self.vectorization_name
        )
        if self.fitter.validation_type == ValidationType.CV:
            x, y = data_storage.get_cv_data_set(
                used_features, vectorization_name=self.vectorization_name
            )
        else:
            if self.task == "anomaly_detection":  # iforest
                x = concatenate_all_samples(data)
                y = None
            else:
                x, y = data["train"]
                if (
                    self.config_storage.data.use_sampling
                    and data_storage.get_dev_n_samples() >= 250000
                ):
                    x, y = data_storage.sample(
                        used_features, vectorization_name=self.vectorization_name
                    )

        random_seed = self.config_storage.pipeline.reproducibility.random_seed
        np.random.seed(random_seed)

        if self.fitter.validation_type == ValidationType.CV:
            splitter_df = data_storage.get_cv_splitter_df(
                self.fitter.cv.get_required_columns()
            )
        else:
            splitter_df = None

        optimizer = self._set_optimizer(
            opt_model, opt_type, data_storage, used_features, splitter_df
        )
        if opt_type == "distributed":
            try:
                init_spark_env(libraries_required=True)

                # Temporary (permanent) config during hyperopt testing
                spark_config = deepcopy(spark_conf)
                spark_config.set("spark.dynamicAllocation.maxExecutors", "5").set(
                    "spark.executor.cores", "1"
                )

                spark = create_spark_session(
                    spark_config=spark_config, temp_dir=self.tempdir
                )
                max_params = optimizer.fit(x, y, data)  # CV - max params, HO - None

                stop_spark_session(spark=spark, temp_dir=self.tempdir)
            except (Py4JJavaError, ImportError) as e:
                logging.exception(
                    f"{'*' * 127}\nBayesianOptimizationModel is used instead DistributedOptimizationModel "
                    f"because: {str(e)}\n{'*' * 127}\n"
                )
                optimizer = self._set_optimizer(
                    opt_model, "optuna", data_storage, used_features, splitter_df
                )
                max_params = optimizer.fit(x, y)
        else:
            max_params = optimizer.fit(x, y)

        if self.fitter.validation_type != ValidationType.CV:
            max_params = optimizer.model.params

        best_params = deepcopy(init_hyperparams)
        best_params.update(max_params)

        msg = f"\ninit_hyperparams: {init_hyperparams}\n\n"
        msg += f"max_params: {max_params}"
        _logger.debug(msg)

        best_estimator = self._init_model(
            used_features=used_features, hyperparams=best_params
        )

        return best_estimator

    def _fit(
        self,
        model: BaseModel,
        used_features: List[str],
        data_storage: DataSet,
        models: List[BoostingBaseModel] = None,
    ) -> BaseStage:
        """Main function to execute the optimization stage.

        Args:
            model (BaseModel): Model instance to train.
            used_features (List[str]): List of features to use.
            data_storage (DataSet): Data storage instance.
            models (List[BoostingBaseModel], optional): List of models obtained from CV. Defaults to None.

        Returns:
            BaseStage: The current stage instance after fitting.
        """
        np.random.seed(self.config_storage.pipeline.reproducibility.random_seed)
        self.tempdir = TempDirectory(path=self.config_storage.data.spark.temp_dir_path)
        self.used_features = used_features
        if not self.used_features:
            self.used_features = model.used_features
        model_ = self._init_model(
            used_features=self.used_features, hyperparams=model.params
        )
        model_.verbose = 0
        model_, models_, self.predictions = self.fitter.train(
            estimator=model_,
            data_storage=data_storage,
            metric=self.eval_metric,
            used_features=self.used_features,
            vectorization_name=self.vectorization_name,
        )

        np.random.seed(self.config_storage.pipeline.reproducibility.random_seed)
        new_data_storage = None
        if self._check_nlp_optimization(model_):
            opt_estimator, new_data_storage = self._get_nlp_optimized_models(
                init_hyperparams=model_.params,
                data_storage=data_storage,
            )
            opt_model, opt_models, opt_predictions = self.fitter.train(
                estimator=opt_estimator,
                data_storage=new_data_storage,
                metric=self.eval_metric,
                used_features=opt_estimator.used_features,
                vectorization_name=self.vectorization_name,
            )
        else:
            opt_estimator = self._get_optimized_model(
                init_hyperparams=model_.params,
                data_storage=data_storage,
                used_features=self.used_features,
            )
            opt_model, opt_models, opt_predictions = self.fitter.train(
                estimator=opt_estimator,
                data_storage=data_storage,
                metric=self.eval_metric,
                used_features=self.used_features,
                vectorization_name=self.vectorization_name,
            )

        if self.task == "topic_modeling":
            current_score = self.eval_metric(model_.topic_modeling_data)
            opt_score = self.eval_metric(opt_model.topic_modeling_data)
        elif self.task == "anomaly_detection":  # iforest
            current_score = self.eval_metric(self.predictions)
            opt_score = self.eval_metric(opt_predictions)
        else:
            y_true = self.fitter.get_validation_target(
                data_storage, vectorization_name=self.vectorization_name
            )
            current_score = self.eval_metric(y_true, self.predictions)
            opt_score = self.eval_metric(y_true, opt_predictions)

        selected_model = self.choose_best_model(
            current_score, model_, models_, opt_model, opt_models, opt_score
        )

        if self._check_nlp_optimization(model_) and selected_model == "Optimized_model":
            self.final_model.used_features = self.vectorizer.used_features
            self.used_features = self.vectorizer.used_features
            new_embeddings = new_data_storage.embeddings[self.vectorization_name]

            for sample_name, embedding_df in new_embeddings.items():
                data_storage.set_embedding_sample(
                    self.vectorization_name, sample_name, embedding_df
                )
            msg = f"Replacing embeddings for {self.vectorization_name}."
            _logger.debug(msg)

        self.prediction = self.prediction_out(data_storage)
        self.is_fitted = True
        return self

    def choose_best_model(
        self, current_score, model_, models_, opt_model, opt_models, opt_score
    ):
        """Selects the best model based on the evaluation metric.

        Args:
            current_score: Score of the current model.
            model_ (BaseModel): Current model instance.
            models_ (List[BoostingBaseModel]): List of models from CV.
            opt_model (BaseModel): Optimized model instance.
            opt_models (List[BoostingBaseModel]): List of optimized models from CV.
            opt_score: Score of the optimized model.

        Returns:
            str: Identifier of the selected model ("Optimized_model" or "Base_model").
        """
        comp = gt if self.eval_metric.maximize else lt
        if comp(opt_score, current_score):
            self.final_model = opt_model
            self.models = opt_models
            selected_model = "Optimized_model"
        else:
            # TODO может быть менять имя стейджа, если возвращается модель с предыдущего стейджа
            self.final_model = model_
            self.models = models_
            selected_model = "Base_model"

        self._logging_info(current_score, opt_score, selected_model)
        return selected_model

    def transform(self):
        """Transforms the stage by returning the final model and related information.

        Raises:
            NotFittedError: If the stage has not been fitted.

        Returns:
            tuple: A tuple containing the final model, used features, feature importance,
                   predictions, and list of models.
        """
        self.check_is_fitted
        # estimator, used_features, feature_importance, predictions, cv_estimators
        return (
            self.final_model,
            self.used_features,
            self.feature_importance,
            self.predictions,
            self.models,
        )

    def _set_params(self, params: dict):
        """Sets the parameters for the stage.

        Args:
            params (dict): Dictionary of parameters.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError

    def _logging_info(self, current_score, opt_score, selected_model):
        """Logs detailed information about the model scores and selected model.

        Args:
            current_score: Score of the current model.
            opt_score: Score of the optimized model.
            selected_model (str): Identifier of the selected model.
        """
        msg = "\n"
        msg += "*" * 30
        msg += f"\nMetric name: {self.eval_metric.name} (Maximize: {self.eval_metric.maximize})"
        msg += f"\nBase model score on Valid sample: {round(current_score, 4)}"
        msg += f"\nOptimized model score Valid sample: {round(opt_score, 4)}"
        msg += f"\nSelected model: {selected_model}\n"
        params = "\n\n"
        for k, v in self.final_model.params.items():
            params += f"  {k}: {v}\n"
        msg += f"\nFinal model hyperparameters: {params}"

        if (
            self.config_storage.pipeline.subtask == "nlp"
            and selected_model == "Optimized_model"
        ):
            if self.text_transformer:
                params = "\n\n"
                for k, v in self.text_transformer.text_preprocessing_params.items():
                    params += f"  {k}: {v}\n"
                msg += f"\nTextFeaturesTransformer parameters: {params}"

            if self.vectorizer:
                params = "\n\n"
                for k, v in self.vectorizer.params.items():
                    params += f"  {k}: {v}\n"
                msg += f"\nVectorizer parameters: {params}"

        msg += "*" * 30

        _logger.debug(msg)

    def _check_nlp_optimization(self, model):
        """Checks if NLP optimization is applicable for the given model.

        Args:
            model (BaseModel): Model instance to check.

        Returns:
            bool: True if NLP optimization is applicable, False otherwise.
        """
        availability = False
        if self.config_storage.pipeline.subtask == "nlp":
            if self.vectorization_name == "tfidf":
                if model.model_name == "log_reg":
                    if self.fitter.validation_type == ValidationType.CV:
                        availability = True
        return availability

    def _get_nlp_optimized_models(self, init_hyperparams, data_storage):
        """Optimizes NLP-specific models including text transformation and vectorization.

        Args:
            init_hyperparams (dict): Initial hyperparameters of the model.
            data_storage (DataSet): Data storage instance.

        Returns:
            tuple: Optimized estimator and the new data storage instance.
        """
        new_data_storage = deepcopy(data_storage)
        eval_set = new_data_storage.get_eval_set()
        df_train = new_data_storage.get_cv_data_set(
            used_features=None,
            vectorization_name=None,
        )
        x = df_train[0][self.config_storage.data.columns.text_features[0]]
        y = df_train[1]

        optimizer = NLPModelBayesianOptimizerCV(
            self.config_storage,
            self.fitter,
        )
        opt_ = optimizer.optimize(x, y)
        (clf_best_params, vec_best_params, text_preproc_best_params) = (
            optimizer.get_best_hyperparams(opt_)
        )

        # TextFeaturesTransformer
        self.text_transformer = TextFeaturesTransformer(
            text_features=self.config_storage.data.columns.text_features,
            text_preprocessing_params=text_preproc_best_params,
            additional_stopwords=self.config_storage.data.augmentation.additional_stopwords,
            verbose=True,
        )
        self.text_transformer.fit(None)
        for sample_name in eval_set:
            eval_set[sample_name] = (
                self.text_transformer.transform(eval_set[sample_name][0]),
                eval_set[sample_name][1],
            )

        # TfidfVectorization
        init_vec_hyper_params = deepcopy(
            self.config_storage.pipeline.vectorization.tfidf.params
        )
        init_vec_hyper_params.update(vec_best_params)
        self.vectorizer = TfidfVectorization(
            self.text_transformer.text_features_preprocessed, **init_vec_hyper_params
        )
        x_train, y_train = eval_set["train"]
        self.vectorizer.fit(x_train, y_train)
        for sample_name, (X_sample, y_sample) in eval_set.items():
            new_embeddings = self.vectorizer.transform(X_sample)
            new_data_storage.set_embedding_sample(
                vectorization_name=self.vectorization_name,
                sample_name=sample_name,
                embeddings_df=new_embeddings,
            )

        # LogRegModel
        init_hyperparams.update(clf_best_params)
        opt_estimator = self._init_model(
            used_features=self.vectorizer.used_features,
            hyperparams=init_hyperparams,
        )
        return opt_estimator, new_data_storage