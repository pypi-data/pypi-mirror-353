import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import umap

from dreamml.logging import get_logger

_logger = get_logger(__name__)


class CalculateDetailedMetricsTopicModeling:
    """Calculates detailed metrics for topic modeling models.

    This class handles the processing of topic modeling models, including 
    generating UMAP visualizations and extracting topic words.

    Attributes:
        models (dict): A dictionary of topic modeling models.
        experiment_path (str): The path where experiment results are stored.
        vectorizers_dict (dict): A dictionary of vectorizers used for text processing.
        text_feature (str): The name of the text feature to be used.
        metric_name (str): The name of the metric to evaluate. Defaults to "gini".
        metric_params (dict): Parameters for the metric evaluation.
        umap_params (dict): Parameters for the UMAP dimensionality reduction.
        model: The currently selected topic modeling model.
        num_topics (int): The number of topics identified by the model.
        topic_words (dict): A dictionary mapping topic names to their associated words.
    """

    def __init__(
        self,
        models,
        experiment_path: str,
        vectorizers_dict: dict,
        text_feature: str,
        metric_name: str = "gini",
        metric_params: dict = None,
        umap_params: dict = None,
    ):
        """Initializes the CalculateDetailedMetricsTopicModeling class.

        Args:
            models (dict): A dictionary of topic modeling models.
            experiment_path (str): The path where experiment results are stored.
            vectorizers_dict (dict): A dictionary of vectorizers used for text processing.
            text_feature (str): The name of the text feature to be used.
            metric_name (str, optional): The name of the metric to evaluate. Defaults to "gini".
            metric_params (dict, optional): Parameters for the metric evaluation. Defaults to None.
            umap_params (dict, optional): Parameters for the UMAP dimensionality reduction. Defaults to None.
        """
        self.models = models
        self.model = None
        self.experiment_path = experiment_path
        self.vectorizers_dict = vectorizers_dict
        self.text_feature = text_feature
        self.metric_name = metric_name
        self.metric_params = metric_params

        self.num_topics = 0
        self.topic_words = dict()
        self.umap_params = umap_params or {}

    def make_umap_plot(self, model_type, model_name):
        """Generates and saves a UMAP plot for the specified topic modeling model.

        Depending on the model type, it either creates a scatter plot for LDA models
        or utilizes the BERTopic visualization for BERTopic models.

        Args:
            model_type (str): The type of the model (e.g., "lda", "bertopic").
            model_name (str): The name identifier of the model.

        Raises:
            ValueError: If an unsupported model type is provided.
        """
        if model_type == "lda":
            topic_distributions = np.array(
                [
                    self.model.estimator.get_document_topics(doc, minimum_probability=0)
                    for doc in self.model.topic_modeling_data.corpus
                ]
            )
            doc_topic_dist = np.array(
                [[topic[1] for topic in doc] for doc in topic_distributions]
            )

            umap_model = umap.UMAP(n_components=2, random_state=27, **self.umap_params)
            umap_values = umap_model.fit_transform(doc_topic_dist)

            plt.figure(figsize=(8, 5))
            plt.scatter(
                umap_values[:, 0],
                umap_values[:, 1],
                c=np.argmax(doc_topic_dist, axis=1),
                cmap="viridis",
                s=50,
            )
            plt.title(f"UMAP visualization of topic distribution {model_name}")
            plt.colorbar(label="Topics")
            plt.grid(True)
            plt.savefig(f"{self.experiment_path}/images/umap_{model_name}.png")
            plt.close()

        elif model_type == "bertopic":
            fig = self.model.estimator.visualize_topics()
            fig.write_image(f"{self.experiment_path}/images/umap_{model_name}.png")
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def transform(self, model_name):
        """Transforms the specified model to extract topic words and generate visualizations.

        This method processes the model based on its type (e.g., BERTopic, LDA),
        generates UMAP plots, and extracts the top words for each topic.

        Args:
            model_name (str): The name identifier of the model to transform.

        Returns:
            pd.DataFrame: A DataFrame containing topics and their associated words.

        Raises:
            KeyError: If the specified model or vectorizer is not found in the dictionaries.
        """
        vectorizer = None
        vocab = None
        self.model = self.models[f"{model_name}"]

        try:
            vectorizer = self.vectorizers_dict["vectorization_tfidf_vectorizer"]
            vocab = vectorizer.vectorizers[self.text_feature].vocabulary_
        except Exception as e:
            pass

        try:
            vectorizer = self.vectorizers_dict["bow_vectorizer"]
        except Exception as e:
            pass

        if self.model.model_name == "bertopic":
            self.make_umap_plot(self.model.model_name, model_name)
            top_n_words = self.model.estimator.get_topics()
            for topic_name, words in top_n_words.items():
                if topic_name != -1:
                    self.topic_words.update(
                        {
                            str(topic_name): [
                                re.sub(r"[^а-яА-Яa-zA-Z]+", "", words[i][0])
                                for i in range(0, 10)
                            ]
                        }
                    )

        if self.model.model_name in ["lda", "ensembelda"]:
            if self.model.model_name == "lda":
                self.make_umap_plot("lda", model_name)
            topics_info = self.model.estimator.print_topics()
            self.num_topics = len(topics_info)
            for topic_name, words in topics_info:
                if vectorizer.name == "bow":
                    self.topic_words.update(
                        {
                            str(topic_name): [
                                re.sub(r"[^а-яА-Яa-zA-Z]+", "", word)
                                for word in words.split("+")
                            ]
                        }
                    )
                else:
                    self.topic_words.update(
                        {
                            str(topic_name): [
                                self.get_value_by_key(
                                    vocab,
                                    int(re.search(r"tfidf_(\d+)", word).group(1)),
                                )
                                for word in words.split("+")
                            ]
                        }
                    )

        return pd.DataFrame(data=self.topic_words)

    @staticmethod
    def get_value_by_key(d, value):
        """Retrieves the key corresponding to a given value in a dictionary.

        This method searches for the first key in the dictionary `d` that maps to the specified `value`.

        Args:
            d (dict): The dictionary to search.
            value: The value to find the corresponding key for.

        Returns:
            The key associated with the given value, or None if the value is not found.
        """
        for k, v in d.items():
            if v == value:
                return k