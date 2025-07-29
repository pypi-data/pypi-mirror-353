from pathlib import Path
import logging
from typing import List, Optional
import gensim.corpora as corpora
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from typing import Dict, Any
from hdbscan import HDBSCAN
from umap import UMAP

from dreamml.modeling.models.estimators import BaseModel
from dreamml.data import TopicModelingData


class BERTopicModel(BaseModel):
    """A BERTopic model for topic modeling tasks.

    This class implements the BERTopic algorithm for identifying and modeling topics
    within a corpus of documents. It extends the BaseModel class and integrates
    UMAP for dimensionality reduction and HDBSCAN for clustering.

    Attributes:
        model_name (str): The name of the model, set to "bertopic".
        estimator_class (class): The BERTopic estimator class.
        model_path (str): Path to the sentence transformer embedding model.
        topic_modeling_data (TopicModelingData): Data structure for storing topic modeling data.
        umap_model (UMAP): The UMAP model used for dimensionality reduction.
        hdbscan_model (HDBSCAN): The HDBSCAN model used for clustering.
        umap_params (dict): Parameters for initializing the UMAP model.
        hdbscan_params (dict): Parameters for initializing the HDBSCAN model.
        estimator (BERTopic): The BERTopic estimator instance.
        fitted (bool): Indicates whether the model has been fitted.
    """
    model_name = "bertopic"

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str],
        categorical_features: List[str],
        metric_name,
        metric_params,
        parallelism: int = -1,
        train_logger: Optional[logging.Logger] = None,
        **params,
    ):
        """Initializes the BERTopicModel with the given parameters.

        Args:
            estimator_params (Dict[str, Any]): Parameters for the estimator.
            task (str): The task type for the model.
            used_features (List[str]): List of features to be used.
            categorical_features (List[str]): List of categorical features.
            metric_name: The name of the metric to be used.
            metric_params: Parameters for the metric.
            parallelism (int, optional): Degree of parallelism. Defaults to -1.
            train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
            **params: Additional keyword arguments.
        """
        super().__init__(
            estimator_params,
            task,
            used_features,
            categorical_features,
            metric_name,
            metric_params,
            parallelism=parallelism,
            train_logger=train_logger,
            **params,
        )
        self.estimator_class = self._estimators.get(self.task)
        self.model_path = str(
            Path(__file__).parent.parent.parent.parent / "references/models/e5"
        )
        self.topic_modeling_data = TopicModelingData()
        self.topic_modeling_data.model_type = self.model_name

        self.umap_model = None
        self.hdbscan_model = None

        self.umap_params = self.get_umap_params(estimator_params)
        self.hdbscan_params = self.get_hdbscan_params(estimator_params)

    @property
    def _estimators(self):
        """Returns a dictionary of available estimators.

        Returns:
            dict: A dictionary mapping task names to estimator classes.
        """
        estimators = {
            "topic_modeling": BERTopic,
        }
        return estimators

    def get_umap_params(self, params):
        """Extracts UMAP parameters from the given parameter dictionary.

        Args:
            params (dict): A dictionary containing UMAP parameters.

        Returns:
            dict: A dictionary of UMAP parameters.
        """
        return {
            "n_neighbors": params["n_neighbors"],
            "n_components": params["n_components"],
            "min_dist": params["min_dist"],
            "metric": params["metric_umap"],
            "n_epochs": params["umap_epochs"],
        }

    def get_hdbscan_params(self, params):
        """Extracts HDBSCAN parameters from the given parameter dictionary.

        Args:
            params (dict): A dictionary containing HDBSCAN parameters.

        Returns:
            dict: A dictionary of HDBSCAN parameters.
        """
        return {
            "min_cluster_size": params["min_cluster_size"],
            "max_cluster_size": params["max_cluster_size"],
            "min_samples": params["min_samples"],
            "metric": params["metric_hdbscan"],
            "cluster_selection_method": params["cluster_selection_method"],
            "prediction_data": params["prediction_data"],
        }

    def fit(self, data):
        """Fits the BERTopic model to the provided data.

        Processes the input data, initializes the embedding, UMAP, and HDBSCAN models,
        and fits the BERTopic estimator.

        Args:
            data: The input data to fit the model on.

        Raises:
            KeyError: If required parameters are missing in estimator_params.
        """
        X = data[0][self.used_features[0]].values
        self.topic_modeling_data.docs = X
        self.topic_modeling_data.tokenized_docs = [doc.split() for doc in X]
        self.topic_modeling_data.dictionary = corpora.Dictionary(
            [doc.split() for doc in X]
        )

        embedding_model = SentenceTransformer(self.model_path, similarity_fn_name="dot")

        self.umap_model = UMAP(**self.umap_params)
        self.hdbscan_model = HDBSCAN(**self.hdbscan_params)

        self.estimator = self.estimator_class(
            language="multilingual",
            embedding_model=embedding_model,
            umap_model=self.umap_model,
            hdbscan_model=self.hdbscan_model,
            verbose=True,
        )
        self.estimator.fit(X)

        self.topic_modeling_data.base_model = self.estimator
        self.fitted = True

    def transform(self, data):
        """Transforms the input data using the fitted BERTopic model.

        Processes the input data and predicts topic assignments for each document.

        Args:
            data: The input data to transform.

        Returns:
            List[int]: A list of predicted topic indices for each document.

        Raises:
            AttributeError: If the model has not been fitted yet.
        """
        X = data[self.used_features[0]].values
        self.topic_modeling_data.docs = X
        self.topic_modeling_data.tokenized_docs = [doc.split() for doc in X]
        self.topic_modeling_data.dictionary = corpora.Dictionary(
            [doc.split() for doc in X]
        )

        probs, pred_topics = self.estimator.transform(X)
        return pred_topics

    def serialize(self) -> dict:
        """Serializes the model and its components into a dictionary.

        Aggregates the serialized data from the base class and adds additional
        components specific to the BERTopic model.

        Returns:
            dict: A dictionary containing the serialized model data.
        """
        data = super().serialize()

        additional_dict = {
            "topic_modeling_data": self.topic_modeling_data,
            "umap_model": self.umap_model,
            "hdbscan_model": self.hdbscan_model,
        }

        data["additional"].update(additional_dict)

        return data

    @classmethod
    def deserialize(cls, data):
        """Deserializes the model from the provided data dictionary.

        Reconstructs the BERTopicModel instance from the serialized data.

        Args:
            data (dict): The serialized model data.

        Returns:
            BERTopicModel: The deserialized BERTopicModel instance.
        """
        instance = super().deserialize(data)

        instance.topic_modeling_data = data["additional"]["topic_modeling_data"]
        instance.umap_model = data["additional"]["umap_model"]
        instance.hdbscan_model = data["additional"]["hdbscan_model"]

        return instance

    def evaluate_and_print(self, **eval_sets):
        """Evaluates the model on the provided evaluation sets and prints the results.

        Transforms the documents to obtain topic assignments and stores the predicted topics.

        Args:
            **eval_sets: Arbitrary keyword arguments representing different evaluation sets.

        Raises:
            NotImplementedError: If the method is not fully implemented.
        """
        topics, probs = self.estimator.transform(self.topic_modeling_data.docs)
        self.topic_modeling_data.pred_topics = topics