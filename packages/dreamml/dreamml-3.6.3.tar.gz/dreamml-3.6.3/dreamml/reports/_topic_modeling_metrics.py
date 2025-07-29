from typing import Optional, Tuple
import numpy as np
import pandas as pd
import math

from sklearn.metrics import average_precision_score
from scipy import stats

from dreamml.configs.config_storage import ConfigStorage
from dreamml.modeling.metrics.metrics_mapping import metrics_mapping
from dreamml.logging import get_logger
from dreamml.utils.vectorization_eval_set import get_eval_set_with_embeddings

_logger = get_logger(__name__)


class CalculateTopicModelingMetrics:
    """
    A class to calculate various metrics for topic modeling models, including Gini and PR-AUC.
    Supports bootstrapping for confidence interval estimation and selection of best models based on metrics.

    Attributes:
        models (dict): A dictionary of models to evaluate.
        predictions_ (dict): A dictionary to store predictions for each model and evaluation set.
        bootstrap_samples (int): Number of bootstrap samples to use for confidence interval calculations.
        p_value (float): Significance level for confidence intervals.
        metric_name (str): Name of the metric to calculate.
        metric_col_name (str): Column name to use for the metric in dataframes.
        metric_params (dict): Additional parameters for metric calculations.
        task (str): Type of task (e.g., "binary", "multiclass").
        vectorizers (Optional[dict]): A dictionary of vectorizers to apply to the data.
    """

    def __init__(
        self,
        models: dict,
        bootstrap_samples: int = 200,
        p_value: float = 0.05,
        config: ConfigStorage = None,
        metric_name: str = "gini",
        metric_col_name: str = "gini",
        task: str = "binary",
        vectorizers: Optional[dict] = None,
    ) -> None:
        """
        Initializes the CalculateTopicModelingMetrics class with the provided parameters.

        Args:
            models (dict): A dictionary of models to evaluate.
            bootstrap_samples (int, optional): Number of bootstrap samples to use. Defaults to 200.
            p_value (float, optional): Significance level for confidence intervals. Defaults to 0.05.
            config (ConfigStorage, optional): Configuration storage object. Defaults to None.
            metric_name (str, optional): Name of the metric to calculate. Defaults to "gini".
            metric_col_name (str, optional): Column name for the metric in dataframes. Defaults to "gini".
            task (str, optional): Type of task (e.g., "binary", "multiclass"). Defaults to "binary".
            vectorizers (Optional[dict], optional): Dictionary of vectorizers. Defaults to None.

        Raises:
            None
        """
        self.models = models
        self.predictions_ = {}
        self.bootstrap_samples = bootstrap_samples
        self.p_value = p_value
        self.metric_name = metric_name
        self.metric_col_name = metric_col_name
        self.metric_params = config.pipeline.metric_params if config else {}
        self.task = task
        self.vectorizers = vectorizers

    @staticmethod
    def create_prediction(model, data) -> np.array:
        """
        Generates predictions using the provided model and data.

        Tries to transform the data using the model. If a TypeError occurs, returns a zero array.

        Args:
            model: The model to use for making predictions.
            data: The input data for which to generate predictions.

        Returns:
            np.array: The prediction results.
        """
        try:
            pred = model.transform(data)
        except TypeError:
            pred = np.zeros(data.shape[0])

        return pred

    def gini_to_frame(self, scores: dict, **eval_sets) -> pd.DataFrame:
        """
        Converts Gini scores into a pandas DataFrame and calculates metric ratios.

        Args:
            scores (dict): A dictionary of scores with model names as keys.
            **eval_sets: Arbitrary keyword arguments representing evaluation sets.

        Returns:
            pd.DataFrame: A DataFrame containing the Gini scores and metric ratios.
        """
        scores = pd.DataFrame(scores)
        scores = scores.T.reset_index()

        metrics = [self.metric_name]
        scores_name = ["Model Name", "# Features"]
        scores_name += [
            f"{metric} {sample}" for metric in metrics for sample in eval_sets
        ]
        scores.columns = scores_name
        scores = self.calculate_metrics_ratio_gini(
            self.metric_name, self.metric_col_name, scores
        )
        scores["Model Details"] = [
            f"Link to train sheet {model}" for model in scores["Model Name"]
        ]
        return scores

    def pr_auc_to_frame(self, scores: dict, **eval_sets) -> pd.DataFrame:
        """
        Converts PR-AUC scores into a pandas DataFrame and calculates metric ratios.

        Args:
            scores (dict): A dictionary of scores with model names as keys.
            **eval_sets: Arbitrary keyword arguments representing evaluation sets.

        Returns:
            pd.DataFrame: A DataFrame containing the PR-AUC scores and metric ratios.
        """
        scores = pd.DataFrame(scores)
        scores = scores.T.reset_index()

        metrics = ["pr_auc"]
        scores_name = ["Model Name", "# Features"]
        scores_name += [
            f"{metric} {sample}" for metric in metrics for sample in eval_sets
        ]

        scores.columns = scores_name
        scores = self.calculate_metrics_ratio_pr_auc(scores)
        scores["Model Details"] = [
            f"Link to train sheet {model}" for model in scores["Model Name"]
        ]
        return scores

    @staticmethod
    def calculate_metrics_ratio_gini(
        metric_name: str, metric_col_name: str, data: pd.DataFrame
    ):
        """
        Calculates the absolute and relative differences in the Gini metric between training and test/OOT sets.

        Args:
            metric_name (str): The name of the metric.
            metric_col_name (str): The column name of the metric in the DataFrame.
            data (pd.DataFrame): DataFrame containing the metric values for all models and evaluation sets.

        Returns:
            pd.DataFrame: DataFrame with additional columns for absolute and relative metric differences.
        """
        columns = data.columns
        if (
            metric_col_name + " train" in columns
            and metric_col_name + " test" in columns
        ):
            data[metric_col_name + " delta train vs test"] = np.abs(
                data[metric_col_name + " train"] - data[metric_col_name + " test"]
            )
            data[metric_col_name + " delta train vs test, %"] = (
                100
                * data[metric_col_name + " delta train vs test"]
                / data[metric_col_name + " train"]
            )

        if (
            metric_col_name + " train" in columns
            and metric_col_name + " OOT" in columns
        ):
            data[metric_col_name + " delta train vs OOT"] = np.abs(
                data[metric_col_name + " train"] - data[metric_col_name + " OOT"]
            )
            data[metric_col_name + " delta train vs OOT, %"] = (
                100
                * data[metric_col_name + " delta train vs OOT"]
                / data[metric_col_name + " train"]
            )

        data = data.fillna(0)
        data = data.replace(np.nan, 0)
        return data

    @staticmethod
    def calculate_metrics_ratio_pr_auc(data: pd.DataFrame):
        """
        Calculates the absolute and relative differences in the PR-AUC metric between training and test/OOT sets.

        Args:
            data (pd.DataFrame): DataFrame containing the metric values for all models and evaluation sets.

        Returns:
            pd.DataFrame: DataFrame with additional columns for absolute and relative metric differences.
        """
        columns = data.columns
        if "pr_auc train" in columns and "pr_auc test" in columns:
            data["pr_auc delta train vs test"] = np.abs(
                data["pr_auc train"] - data["pr_auc test"]
            )
            data["pr_auc delta train vs test, %"] = (
                100 * data["pr_auc delta train vs test"] / data["pr_auc train"]
            )

        if "pr_auc train" in columns and "pr_auc OOT" in columns:
            data["pr_auc delta train vs OOT"] = np.abs(
                data["pr_auc train"] - data["pr_auc OOT"]
            )
            data["pr_auc delta train vs OOT, %"] = (
                100 * data["pr_auc delta train vs OOT"] / data["pr_auc train"]
            )

        data = data.fillna(0)
        data = data.replace(np.nan, 0)
        return data

    def create_all_predictions(self, **eval_sets):
        """
        Generates predictions for all models across all evaluation sets.

        Applies appropriate vectorizers to the evaluation sets and stores the predictions.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation sets.

        Returns:
            None
        """
        for model_name, model in self.models.items():
            eval_set = eval_sets.copy()

            # FIXME add for bartopic

            if "bertopic" not in model_name:
                if model.vectorization_name == "tfidf":
                    vectorizer_name = (
                        f"vectorization_{model.vectorization_name}_vectorizer"
                    )
                else:
                    vectorizer_name = f"{model.vectorization_name}_vectorizer"
                vectorizer = self.vectorizers[vectorizer_name]
                eval_set = get_eval_set_with_embeddings(vectorizer, eval_set)

            self.predictions_[model_name] = {}
            sample_pred = {}

            for sample_name, (X_sample, _) in eval_set.items():
                pred = self.create_prediction(model, X_sample)
                sample_pred[sample_name] = pred

            self.predictions_[model_name] = sample_pred

    def calculate_gini(self, model_name, **kwargs):
        """
        Calculates the Gini metric for a specified model across all provided evaluation sets.

        Args:
            model_name (str): The name of the model to evaluate.
            **kwargs: Arbitrary keyword arguments representing evaluation sets.

        Returns:
            list: A list containing the number of features and Gini scores for each evaluation set.
        """
        try:
            model = self.models[model_name]
            metrics_score = [len(model.used_features)]
        except TypeError:
            sample_name = next(iter(kwargs))
            metrics_score = [len(kwargs[sample_name][0])]

        for sample in kwargs:
            _, target = kwargs[sample]
            pred = self.predictions_[model_name]
            try:
                metrics_score.append(
                    round(
                        metrics_mapping[self.metric_name](
                            task=self.task, **self.metric_params
                        )(model.topic_modeling_data),
                        4,
                    )
                )
            except ValueError:
                metrics_score.append(0.00001)

        return metrics_score

    def calculate_pr_auc(self, model_name, **kwargs):
        """
        Calculates the PR-AUC metric for a specified model across all provided evaluation sets.

        Args:
            model_name (str): The name of the model to evaluate.
            **kwargs: Arbitrary keyword arguments representing evaluation sets.

        Returns:
            list: A list containing the number of features and PR-AUC scores for each evaluation set.

        Raises:
            ValueError: If there is an issue calculating the average precision score.
        """
        try:
            model = self.models[model_name]
            metrics_score = [len(model.used_features)]
        except TypeError:
            sample_name = next(iter(kwargs))
            metrics_score = [len(kwargs[sample_name][0])]

        for sample in kwargs:
            _, target = kwargs[sample]
            pred = self.predictions_[model_name]
            y_pred = pred[sample]

            try:
                if self.task in ["multilabel", "multiclass"]:
                    zeros_classes = [
                        col for col in target.columns if target[col].sum() == 0
                    ]
                    y_pred = np.delete(
                        pred[sample],
                        [target.columns.get_loc(col) for col in zeros_classes],
                        axis=1,
                    )
                    target = target.drop(columns=zeros_classes)
                metrics_score.append(
                    round(100 * average_precision_score(target, y_pred), 4)
                )
            except ValueError:
                metrics_score.append(0.00001)

        return metrics_score

    def _create_bootstrap_index(self, X: pd.DataFrame) -> np.array:
        """
        Creates a matrix of object indices that are included in each bootstrap sample.

        Args:
            X (pd.DataFrame): Feature matrix to create bootstrap samples from.

        Returns:
            np.array: Array of bootstrap sample indices.
        """
        np.random.seed(27)
        bootstrap_index = np.random.randint(
            0, X.shape[0], size=(self.bootstrap_samples, X.shape[0])
        )
        return bootstrap_index

    def _create_bootstrap_scores(
        self, X: pd.DataFrame, y: pd.Series, y_pred: pd.Series
    ) -> np.array:
        """
        Computes the metric scores for each bootstrap sample.

        Args:
            X (pd.DataFrame): Feature matrix for creating bootstrap samples.
            y (pd.Series): True target values.
            y_pred (pd.Series): Predicted values from the model.

        Returns:
            np.array: Array of bootstrap metric scores.
        """
        counter = 0
        while True:
            try:
                bootstrap_scores = []
                bootstrap_index = self._create_bootstrap_index(X)
                if isinstance(y, pd.Series):
                    y = y.reset_index(drop=True)
                for sample_idx in bootstrap_index:
                    y_true_bootstrap, y_pred_bootstrap = (
                        y.iloc[sample_idx],
                        y_pred[sample_idx],
                    )
                    bootstrap_scores.append(
                        metrics_mapping.get(self.metric_name)(
                            task=self.task, **self.metric_params
                        )(y_true_bootstrap, y_pred_bootstrap)
                        * 100
                    )
            except Exception as e:
                counter += 1
                continue

            finally:
                break

        return np.array(bootstrap_scores)

    @staticmethod
    def _calculate_conf_interval(x: np.array, alpha: float = 0.05):
        """
        Calculates the confidence interval for the mean of a sample.

        Args:
            x (np.array): Sample data.
            alpha (float, optional): Significance level. Defaults to 0.05.

        Returns:
            Tuple[float, float]: Lower and upper bounds of the confidence interval.
        """
        x_mean = np.mean(x)
        q_value = stats.t.ppf(1 - alpha / 2, x.shape[0])

        std_error = q_value * np.sqrt(x_mean) / np.sqrt(x.shape[0])
        return x_mean - std_error, x_mean + std_error

    def get_best_models(self, stats_df: pd.DataFrame, **eval_sets) -> dict:
        """
        Identifies the best models based on the specified metric and confidence intervals.

        Args:
            stats_df (pd.DataFrame): DataFrame containing metric statistics for all models.
            **eval_sets: Arbitrary keyword arguments representing evaluation sets.

        Returns:
            dict: Dictionary containing the best model information for each evaluation set.
        """
        metric_name = self.metric_name
        metric_col_name = self.metric_col_name
        stats_df = stats_df.reset_index(drop=True)
        if metric_name == "logloss":
            best_gini_model_name_test = stats_df[
                stats_df[metric_name + " test"] == stats_df[metric_name + " test"].min()
            ]["Model Name"].to_list()[0]

        else:
            best_gini_model_name_test = stats_df[
                stats_df[metric_name + " test"] == stats_df[metric_name + " test"].max()
            ]["Model Name"].to_list()[0]

        test_scores = self._create_bootstrap_scores(
            X=eval_sets["test"][0],
            y=eval_sets["test"][1],
            y_pred=self.predictions_[best_gini_model_name_test]["test"],
        )
        test_conf_interval = self._calculate_conf_interval(
            test_scores, alpha=self.p_value
        )
        min_num_of_features_test = stats_df[
            (stats_df[metric_name + " test"] >= test_conf_interval[0])
            & (stats_df[metric_name + " test"] <= test_conf_interval[1])
        ]["# Features"].min()
        if not (
            min_num_of_features_test > 0
        ):  # For grouped metrics: select the best model
            min_num_of_features_test = stats_df[
                stats_df["Model Name"] == best_gini_model_name_test
            ]["# Features"].max()
            _logger.info(
                "Best model on test ("
                + metric_name
                + ") selected not based on the confidence interval (see report), but as the model with the best metric on test"
            )

        # In case of a small dataset, the confidence interval may not be well constructed --> reduce p_value to 0.01
        if math.isnan(min_num_of_features_test):
            while self.p_value > 0.01 and math.isnan(min_num_of_features_test):
                self.p_value = np.round(self.p_value / 2, 2)
                test_conf_interval = self._calculate_conf_interval(
                    test_scores, alpha=self.p_value
                )
                min_num_of_features_test = stats_df[
                    (stats_df[metric_name + " test"] >= test_conf_interval[0])
                    & (stats_df[metric_name + " test"] <= test_conf_interval[1])
                ]["# Features"].min()

        min_df_test = stats_df[stats_df["# Features"] == min_num_of_features_test]
        if metric_name == "logloss":
            best_model_name_test = min_df_test[
                min_df_test[metric_name + " test"]
                == min_df_test[metric_name + " test"].min()
            ]["Model Name"].to_list()[0]
        else:
            best_model_name_test = min_df_test[
                min_df_test[metric_name + " test"]
                == min_df_test[metric_name + " test"].max()
            ]["Model Name"].to_list()[0]

        best_idx_test = stats_df[
            stats_df["Model Name"] == best_model_name_test
        ].index[0]

        best_results = {
            "test": {
                "name": best_model_name_test,
                "index": best_idx_test,
                "ci": test_conf_interval,
            }
        }
        if "OOT" in eval_sets.keys():
            if metric_name == "logloss":
                best_gini_model_name_oot = stats_df[
                    stats_df[metric_name + " OOT"]
                    == stats_df[metric_name + " OOT"].min()
                ]["Model Name"].to_list()[0]
            else:
                best_gini_model_name_oot = stats_df[
                    stats_df[metric_name + " OOT"]
                    == stats_df[metric_name + " OOT"].max()
                ]["Model Name"].to_list()[0]

            oot_scores = self._create_bootstrap_scores(
                X=eval_sets["OOT"][0],
                y=eval_sets["OOT"][1],
                y_pred=self.predictions_[best_gini_model_name_oot]["OOT"],
            )

            oot_conf_interval = self._calculate_conf_interval(
                oot_scores, alpha=self.p_value
            )
            min_num_of_features_oot = stats_df[
                (stats_df[metric_name + " OOT"] >= oot_conf_interval[0])
                & (stats_df[metric_name + " OOT"] <= oot_conf_interval[0])
            ]["# Features"].min()
            if not (
                min_num_of_features_oot > 0
            ):  # For grouped metrics: select the best model
                min_num_of_features_oot = stats_df[
                    stats_df["Model Name"] == best_gini_model_name_oot
                ]["# Features"].max()
                _logger.info(
                    "Best model on OOT ("
                    + metric_name
                    + ") selected not based on the confidence interval (see report), but as the model with the best metric on OOT"
                )
            min_df_oot = stats_df[stats_df["# Features"] == min_num_of_features_oot]
            if metric_name == "logloss":
                best_model_name_oot = min_df_oot[
                    min_df_oot[metric_name + " OOT"]
                    == min_df_oot[metric_name + " OOT"].min()
                ]["Model Name"].to_list()[0]
            else:
                best_model_name_oot = min_df_oot[
                    min_df_oot[metric_name + " OOT"]
                    == min_df_oot[metric_name + " OOT"].max()
                ]["Model Name"].to_list()[0]

            best_idx_oot = stats_df[
                stats_df["Model Name"] == best_model_name_oot
            ].index[0]
            best_results["oot"] = {
                "name": best_model_name_oot,
                "index": best_idx_oot,
                "ci": oot_conf_interval,
            }
        return best_results

    def transform(self, **eval_sets):
        """
        Transforms evaluation sets by calculating Gini metrics for all models.

        Generates predictions if not already available and computes Gini scores.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation sets.

        Returns:
            pd.DataFrame: DataFrame containing Gini scores and metric ratios for all models.
        """
        scores = {}
        if not self.predictions_:
            self.create_all_predictions(**eval_sets)
        else:
            _logger.info("Used Pre-calculated predictions")

        for model in self.models:
            scores[model] = self.calculate_gini(model, **eval_sets)

        return self.gini_to_frame(scores, **eval_sets)

    def transform_pr(self, **eval_sets):
        """
        Transforms evaluation sets by calculating PR-AUC metrics for all models.

        Generates predictions if not already available and computes PR-AUC scores.

        Args:
            **eval_sets: Arbitrary keyword arguments representing evaluation sets.

        Returns:
            pd.DataFrame: DataFrame containing PR-AUC scores and metric ratios for all models.
        """
        scores = {}
        if not self.predictions_:
            self.create_all_predictions(**eval_sets)
        else:
            _logger.info("Used Pre-calculated predictions")

        for model in self.models:
            scores[model] = self.calculate_pr_auc(model, **eval_sets)

        return self.pr_auc_to_frame(scores, **eval_sets)