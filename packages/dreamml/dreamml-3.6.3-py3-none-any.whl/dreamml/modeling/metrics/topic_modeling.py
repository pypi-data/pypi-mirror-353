import numpy as np
from scipy.spatial.distance import cosine
from typing import Optional
from gensim.models import CoherenceModel
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_distances

from dreamml.modeling.metrics._base_metric import BaseMetric, OptimizableMetricMixin


class TopicModelingMetric(BaseMetric):
    """
    Base class for topic modeling metrics.

    Attributes:
        _task_type (str): The type of task, set to "topic_modeling".
    """
    _task_type: str = "topic_modeling"

    def __init__(
        self,
        model_name: Optional[str] = None,
        task: Optional[str] = None,
        **params,
    ):
        """
        Initializes the TopicModelingMetric.

        Args:
            model_name (Optional[str]): The name of the model. Defaults to None.
            task (Optional[str]): The task type. Defaults to None.
            **params: Additional keyword arguments.

        Raises:
            ValueError: If invalid parameters are provided.
        """
        super().__init__(
            model_name=model_name,
            task=task,
            **params,
        )

    def __call__(self, topic_modeling_data):
        """
        Computes the metric score based on the provided topic modeling data.

        Args:
            topic_modeling_data: Data required for computing the metric.

        Returns:
            The score computed by the metric.

        Raises:
            NotImplementedError: If the score function is not implemented.
        """
        return self._score_function(topic_modeling_data)


class LogPerplexity(TopicModelingMetric, OptimizableMetricMixin):
    """
    Metric for calculating the log perplexity of a topic model.

    Attributes:
        name (str): The name of the metric, set to "log_perplexity".
        maximize (bool): Whether to maximize the metric. Set to False.
    """
    name = "log_perplexity"
    maximize = False

    def _score_function(self, topic_modeling_data):
        """
        Calculates the log perplexity of the topic model.

        Args:
            topic_modeling_data: Data required for computing log perplexity, including the base model and corpus.

        Returns:
            float: The log perplexity score.

        Raises:
            AttributeError: If the base model does not have a log_perplexity method.
        """
        perplexity = topic_modeling_data.base_model.log_perplexity(
            topic_modeling_data.corpus
        )
        return perplexity


class Coherence(TopicModelingMetric, OptimizableMetricMixin):
    """
    Metric for calculating the coherence of a topic model.

    Attributes:
        name (str): The name of the metric, set to "coherence".
        maximize (bool): Whether to maximize the metric. Set to True.
    """
    name = "coherence"
    maximize = True

    def _score_function(self, topic_modeling_data):
        """
        Calculates the coherence score of the topic model.

        Args:
            topic_modeling_data: Data required for computing coherence, including model type, base model,
                                 tokenized documents, and dictionary.

        Returns:
            float: The coherence score.

        Raises:
            ValueError: If the model type is unsupported.
            AttributeError: If required attributes are missing from topic_modeling_data.
        """
        if topic_modeling_data.model_type == "bertopic":
            topic_info = topic_modeling_data.base_model.get_topic_info()
            topics = []
            for topic_id in range(len(topic_info)):
                topic = topic_modeling_data.base_model.get_topic(topic_id)
                if topic:
                    topics.append([word for word, _ in topic])

            cm = CoherenceModel(
                topics=topics,
                texts=topic_modeling_data.tokenized_docs,
                dictionary=topic_modeling_data.dictionary,
                coherence="u_mass",
            )

        elif topic_modeling_data.model_type in ("lda", "ensembelda"):
            cm = CoherenceModel(
                model=topic_modeling_data.base_model,
                corpus=topic_modeling_data.corpus,
                coherence="u_mass",
            )
        else:
            raise ValueError(f"Unsupported model type: {topic_modeling_data.model_type}")

        return cm.get_coherence()


class AverageDistance(TopicModelingMetric, OptimizableMetricMixin):
    """
    Metric for calculating the average cosine distance between topic embeddings or vectors.

    Attributes:
        name (str): The name of the metric, set to "average_distance".
        maximize (bool): Whether to maximize the metric. Set to True.
    """
    name = "average_distance"
    maximize = True

    def _score_function(self, topic_modeling_data):
        """
        Calculates the average cosine distance between topics.

        Args:
            topic_modeling_data: Data required for computing average distance, including model type and base model.

        Returns:
            float: The average cosine distance.

        Raises:
            ValueError: If the model type is unsupported.
            AttributeError: If required attributes are missing from topic_modeling_data.
        """
        if topic_modeling_data.model_type == "bertopic":
            topic_embeddings = topic_modeling_data.base_model.topic_embeddings_
            cosine_dist = cosine_distances(topic_embeddings)
            average_distance = np.mean(
                cosine_dist[np.triu_indices_from(cosine_dist, k=1)]
            )

        elif topic_modeling_data.model_type in ("lda", "ensembelda"):
            topic_vectors = topic_modeling_data.base_model.get_topics()
            num_topics = len(topic_vectors)
            distances = []

            for i in range(num_topics):
                for j in range(i + 1, num_topics):
                    dist = cosine(topic_vectors[i], topic_vectors[j])
                    distances.append(dist)
            average_distance = np.mean(distances)
        else:
            raise ValueError(f"Unsupported model type: {topic_modeling_data.model_type}")

        return average_distance


class SilhouetteScore(TopicModelingMetric, OptimizableMetricMixin):
    """
    Metric for calculating the silhouette score of topic clusters.

    Attributes:
        name (str): The name of the metric, set to "silhouette_score".
        maximize (bool): Whether to maximize the metric. Set to True.
    """
    name = "silhouette_score"
    maximize = True

    def _score_function(self, topic_modeling_data):
        """
        Calculates the silhouette score based on the task type.

        Args:
            topic_modeling_data: Data required for computing the silhouette score. For anomaly detection,
                                 it should include 'x' and 'scores'. For other tasks, it should include the base model,
                                 documents, and predicted topics.

        Returns:
            float: The average silhouette score.

        Raises:
            KeyError: If required keys are missing from topic_modeling_data.
            ValueError: If the task type is unsupported or if the silhouette score calculation fails.
        """
        if self._task == "anomaly_detection":
            try:
                x = topic_modeling_data["x"]
                scores = topic_modeling_data["scores"]
            except KeyError as e:
                raise KeyError(f"Missing key in topic_modeling_data: {e}")

            silhouette_avg = silhouette_score(x, scores)
        else:
            try:
                embeddings = (
                    topic_modeling_data.base_model.embedding_model.embedding_model.encode(
                        topic_modeling_data.docs
                    )
                )
                silhouette_avg = silhouette_score(
                    embeddings, topic_modeling_data.pred_topics
                )
            except AttributeError as e:
                raise AttributeError(f"Missing attribute in topic_modeling_data or base_model: {e}")
            except Exception as e:
                raise ValueError(f"Error computing silhouette score: {e}")

        return silhouette_avg