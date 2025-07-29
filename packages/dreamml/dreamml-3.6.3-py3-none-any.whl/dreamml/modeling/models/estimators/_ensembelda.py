import logging
from typing import List, Optional
import gensim
from gensim.models import EnsembleLda
import gensim.corpora as corpora
from scipy.sparse import csr_matrix
from typing import Dict, Any

from dreamml.logging import get_logger
from dreamml.modeling.models.estimators import BaseModel
from dreamml.data import TopicModelingData

_logger = get_logger(__name__)


class EnsembeldaModel(BaseModel):
    """EnsembeldaModel with a standardized API for dreamml_base.

    Attributes:
        model_name (str): Name of the algorithm (e.g., 'lda', 'ensembelda', 'bertopic', etc.).
        params (dict): Dictionary containing hyperparameters.
        task (str): Name of the task (e.g., 'topic_modeling').
        used_features (List[str]): List of selected features based on specific metric values.
        estimator (callable): Instance of the trained model.
        categorical_features (List[str]): List of categorical features.
        fitted (bool): Indicates whether the model has been trained (`True`) or not (`False`).
        topic_modeling_data (TopicModelingData): Data specific to topic modeling.
    """

    model_name = "ensembelda"

    def __init__(
        self,
        estimator_params: Dict[str, Any],
        task: str,
        used_features: List[str],
        categorical_features: List[str],
        metric_name: str,
        metric_params: Dict[str, Any],
        parallelism: int = -1,
        train_logger: Optional[logging.Logger] = None,
        **params,
    ):
        """Initializes the EnsembeldaModel.

        Args:
            estimator_params (Dict[str, Any]): Dictionary of hyperparameters.
            task (str): Name of the task (e.g., 'topic_modeling').
            used_features (List[str]): List of selected features based on specific metric values.
            categorical_features (List[str]): List of categorical features.
            metric_name (str): Name of the metric.
            metric_params (Dict[str, Any]): Dictionary of metric parameters.
            parallelism (int, optional): Degree of parallelism. Defaults to -1.
            train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
            **params: Additional parameters.

        Raises:
            KeyError: If the task is not supported by the estimators.
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
        self.topic_modeling_data = TopicModelingData()
        self.topic_modeling_data.model_type = self.model_name

    @property
    def _estimators(self) -> Dict[str, Any]:
        """Returns a dictionary of supported estimators.

        Returns:
            Dict[str, Any]: Dictionary mapping task names to estimator classes.
        """
        estimators = {
            "topic_modeling": EnsembleLda,
        }
        return estimators

    def fit(self, data):
        """Trains the EnsembeldaModel on the provided data.

        Args:
            data: Training data.

        Raises:
            ValueError: If the vectorization name is neither 'bow' nor 'tfidf'.
        """
        if self.vectorization_name == "bow":
            self.topic_modeling_data.dictionary = data[0][self.used_features[0]]["dict"]
            self.topic_modeling_data.corpus = data[0][self.used_features[0]][
                "bow_corpus"
            ]
        elif self.vectorization_name == "tfidf":
            X = data[0][self.used_features]
            sparse_matrix = csr_matrix(X.values)
            self.topic_modeling_data.corpus = gensim.matutils.Sparse2Corpus(
                sparse_matrix, documents_columns=True
            )
            self.topic_modeling_data.dictionary = corpora.Dictionary(
                [X.columns.tolist()]
            )
        else:
            raise ValueError(
                f"Unsupported vectorization name: {self.vectorization_name}"
            )

        self.estimator = self.estimator_class(
            corpus=self.topic_modeling_data.corpus,
            id2word=self.topic_modeling_data.dictionary,
            passes=self.params["passes"],
            num_topics=self.params["num_topics"],
            num_models=self.params["num_models"],
            iterations=self.params["iterations"],
            random_state=self.params["random_state"],
            per_word_topics=True,
        )

        self.estimator.recluster(eps=0.5)
        self.topic_modeling_data.base_model = self.estimator
        self.fitted = True

    def transform(self, data):
        """Transforms the input data into topic distributions.

        Args:
            data: Data to be transformed.

        Returns:
            List: List of topic distributions for each document.

        Raises:
            ValueError: If the vectorization name is neither 'bow' nor 'tfidf'.
        """
        if self.vectorization_name == "bow":
            self.topic_modeling_data.corpus = data[self.used_features[0]]["bow_corpus"]
            pred_topics = []
            for doc in self.topic_modeling_data.corpus:
                topic_dist = self.estimator[doc]
                pred_topics.append(topic_dist)
        elif self.vectorization_name == "tfidf":
            X = data[self.used_features]
            sparse_matrix = csr_matrix(X.values)
            self.topic_modeling_data.corpus = gensim.matutils.Sparse2Corpus(
                sparse_matrix, documents_columns=True
            )
            pred_topics = []
            for doc in self.topic_modeling_data.corpus:
                topic_dist = self.estimator[doc]
                pred_topics.append(topic_dist)
        else:
            raise ValueError(
                f"Unsupported vectorization name: {self.vectorization_name}"
            )

        return pred_topics

    def serialize(self) -> dict:
        """Serializes the model into a dictionary.

        Returns:
            dict: Serialized model data.
        """
        data = super().serialize()

        additional_dict = {
            "topic_modeling_data": self.topic_modeling_data,
        }

        data["additional"].update(additional_dict)

        return data

    @classmethod
    def deserialize(cls, data: dict):
        """Deserializes the model from a dictionary.

        Args:
            data (dict): Serialized model data.

        Returns:
            EnsembeldaModel: An instance of EnsembeldaModel.
        """
        instance = super().deserialize(data)

        instance.topic_modeling_data = data["additional"]["topic_modeling_data"]

        return instance

    def evaluate_and_print(self, **eval_sets):
        """Evaluates the model on provided evaluation sets and prints the results.

        Args:
            **eval_sets: Variable length evaluation datasets.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        # Method implementation goes here
        pass