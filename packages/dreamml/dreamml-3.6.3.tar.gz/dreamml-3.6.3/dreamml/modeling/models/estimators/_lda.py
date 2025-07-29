import logging
from typing import List, Optional
import gensim
from gensim.models import LdaModel
import gensim.corpora as corpora
from scipy.sparse import csr_matrix
from typing import Dict, Any

from dreamml.modeling.models.estimators import BaseModel
from dreamml.data import TopicModelingData


class LDAModel(BaseModel):
    """Latent Dirichlet Allocation (LDA) Model for Topic Modeling.

    This class implements the LDA algorithm for topic modeling tasks, 
    extending the BaseModel. It supports both Bag of Words (BoW) and TF-IDF 
    vectorization methods.

    Attributes:
        model_name (str): The name of the model, set to "lda".
        estimator_class (Type): The estimator class used for modeling.
        topic_modeling_data (TopicModelingData): Data structure for topic modeling.
        estimator (LdaModel): The fitted LDA model.
        fitted (bool): Indicates whether the model has been fitted.
    """

    model_name = "lda"

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
        """Initializes the LDAModel with specified parameters.

        Args:
            estimator_params (Dict[str, Any]): Parameters for the estimator.
            task (str): The task type, e.g., "topic_modeling".
            used_features (List[str]): List of feature names to be used.
            categorical_features (List[str]): List of categorical feature names.
            metric_name: The name of the metric to evaluate.
            metric_params: Parameters for the evaluation metric.
            parallelism (int, optional): Degree of parallelism. Defaults to -1.
            train_logger (Optional[logging.Logger], optional): Logger for training. Defaults to None.
            **params: Additional keyword arguments.

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
    def _estimators(self):
        """Dictionary mapping task names to estimator classes.

        Returns:
            Dict[str, Type]: A dictionary with task names as keys and estimator classes as values.
        """
        estimators = {
            "topic_modeling": LdaModel,
        }
        return estimators

    def fit(self, data):
        """Fits the LDA model to the provided data.

        Depending on the vectorization method ('bow' or 'tfidf'), it prepares 
        the corpus and dictionary required for training the LDA model.

        Args:
            data: The input data used for fitting the model.

        Raises:
            ValueError: If the vectorization method is not supported.
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
            raise ValueError(f"Unsupported vectorization method: {self.vectorization_name}")

        self.estimator = self.estimator_class(
            corpus=self.topic_modeling_data.corpus,
            id2word=self.topic_modeling_data.dictionary,
            passes=self.params["passes"],
            num_topics=self.params["num_topics"],
            alpha=self.params["alpha"],
            eta=self.params["eta"],
            random_state=self.params["random_state"],
            per_word_topics=True,
        )

        self.topic_modeling_data.base_model = self.estimator
        self.fitted = True

    def transform(self, data):
        """Transforms the input data into topic distributions using the fitted LDA model.

        Args:
            data: The input data to transform.

        Returns:
            List[List[Tuple[int, float]]]: A list where each element is a list of tuples 
            representing topic probabilities for a document.

        Raises:
            AttributeError: If the model has not been fitted yet.
        """
        if not self.fitted:
            raise AttributeError("The model must be fitted before calling transform.")

        if self.vectorization_name == "bow":
            self.topic_modeling_data.corpus = data[self.used_features[0]]["bow_corpus"]
        elif self.vectorization_name == "tfidf":
            X = data[self.used_features]
            sparse_matrix = csr_matrix(X.values)
            self.topic_modeling_data.corpus = gensim.matutils.Sparse2Corpus(
                sparse_matrix, documents_columns=True
            )
        else:
            raise ValueError(f"Unsupported vectorization method: {self.vectorization_name}")

        pred_topics = self.estimator.get_document_topics(
            self.topic_modeling_data.corpus, minimum_probability=0
        )
        return pred_topics

    def serialize(self) -> dict:
        """Serializes the model into a dictionary format.

        Returns:
            dict: A dictionary containing the serialized model data.
        """
        data = super().serialize()

        additional_dict = {
            "topic_modeling_data": self.topic_modeling_data,
        }

        data["additional"].update(additional_dict)

        return data

    @classmethod
    def deserialize(cls, data):
        """Deserializes the model from a dictionary.

        Args:
            data (dict): The dictionary containing the serialized model data.

        Returns:
            LDAModel: An instance of LDAModel initialized with the provided data.
        """
        instance = super().deserialize(data)

        instance.topic_modeling_data = data["additional"]["topic_modeling_data"]

        return instance

    def evaluate_and_print(self, **eval_sets):
        """Evaluates the model on the provided evaluation sets and prints the results.

        Args:
            **eval_sets: Variable length keyword arguments representing different evaluation datasets.

        Raises:
            NotImplementedError: Indicates that the method is not yet implemented.
        """
        pass