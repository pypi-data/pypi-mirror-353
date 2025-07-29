from typing import List, Optional
import numpy as np

from dreamml.configs.config_storage import ConfigStorage
from dreamml.data._dataset import DataSet
from dreamml.pipeline.fitter import FitterBase
from dreamml.stages.algo_info import AlgoInfo
from dreamml.stages.stage import BaseStage
from dreamml.features.feature_vectorization import (
    BowVectorization,
    FastTextVectorization,
    GloveVectorization,
    TfidfVectorization,
    Word2VecVectorization,
)
from dreamml.logging import get_logger

seed = 27
np.random.seed(seed)
_logger = get_logger(__name__)


VECTORIZATION_REGISTRY = {
    "tfidf": TfidfVectorization,
    "word2vec": Word2VecVectorization,
    "fasttext": FastTextVectorization,
    "glove": GloveVectorization,
    "bert": None,
    "bow": BowVectorization,
}


class VectorizationStage(BaseStage):
    """A stage in the pipeline responsible for vectorizing text data.

    This stage handles the transformation of text features into numerical
    vector representations using various vectorization techniques.
    """

    name = "vectorization"

    def __init__(
        self,
        algo_info: AlgoInfo,
        config: ConfigStorage,
        fitter: Optional[FitterBase] = None,
        vectorization_name: str = None,
    ):
        """Initializes the VectorizationStage.

        Args:
            algo_info (AlgoInfo): Information about the algorithm.
            config (ConfigStorage): Configuration storage containing pipeline settings.
            fitter (Optional[FitterBase], optional): An optional fitter instance. Defaults to None.
            vectorization_name (str, optional): The name of the vectorization method to use. Defaults to None.

        """
        super().__init__(
            algo_info=algo_info,
            config=config,
            fitter=fitter,
            vectorization_name=vectorization_name,
        )
        self.config = config
        if self.vectorization_name == "bert":
            self.vectorizer_params = {}
        else:
            self.vectorizer_params = getattr(
                self.config.pipeline.vectorization, self.vectorization_name
            ).params
        self.vectorizer = VECTORIZATION_REGISTRY[self.vectorization_name]
        self.drop_features = config.data.columns.drop_features
        self.text_augmentations = config.data.augmentation.text_augmentations

    def _set_used_features(self, data_storage: DataSet, used_features: List = None):
        """Determines and sets the features to be used for vectorization.

        If no specific features are provided, it retrieves the default
        feature columns from the training set.

        Args:
            data_storage (DataSet): The dataset storage containing data splits.
            used_features (List, optional): A list of feature names to use. Defaults to None.

        Returns:
            List: A list of feature names to be used.

        """
        if not used_features:
            data = data_storage.get_eval_set(vectorization_name=None)
            used_features = data["train"][0].columns.tolist()
        return used_features

    def _fit(
        self,
        model,
        used_features: List[str],
        data_storage: DataSet,
        models=None,
    ) -> BaseStage:
        """Fits the vectorization model to the training data.

        Depending on the vectorization method, it either fits a combined
        vectorizer and estimator or fits the vectorizer separately and sets embeddings.

        Args:
            model: The model to fit.
            used_features (List[str]): A list of feature names to use.
            data_storage (DataSet): The dataset storage containing data splits.
            models: Additional models, if any. Defaults to None.

        Returns:
            BaseStage: The fitted stage instance.

        Raises:
            AttributeError: If the vectorization name is not recognized.

        """
        info_msg = f"Stage vectorization info: starting fit: {self.vectorization_name}"
        _logger.info(info_msg)

        self.used_features = self._set_used_features(
            data_storage=data_storage,
            used_features=used_features,
        )
        text_features = data_storage.text_features_preprocessed
        self.eval_sets = data_storage.get_eval_set(used_features=text_features)

        if self.vectorization_name == "bert":
            # In this case, model is the vectorizer and estimator
            self.start_model = self._init_model(used_features=self.used_features)
            x_train, y_train = self.eval_sets["train"]
            self.start_model.fit(x_train, y_train, *self.eval_sets["valid"])
            self.start_model.evaluate_and_print(**self.eval_sets)
            self.final_model = self.start_model
            self.final_model.used_features = self.start_model.used_features

        else:
            self.vectorizer = self.vectorizer(text_features, **self.vectorizer_params)
            self.vectorizer.fit(*self.eval_sets["train"])
            self._set_embeddings(data_storage)
        return self

    def _set_embeddings(self, data_storage: DataSet):
        """Transforms the data samples into embeddings and updates the data storage.

        Iterates over each data sample, transforms it using the vectorizer,
        and sets the resulting embeddings in the data storage.

        Args:
            data_storage (DataSet): The dataset storage to update with embeddings.

        """
        info_msg = (
            f"Stage vectorization info: starting transform: {self.vectorization_name}"
        )
        _logger.info(info_msg)
        for sample_name, (X_sample, y_sample) in self.eval_sets.items():
            embeddings_df = self.vectorizer.transform(X_sample)
            data_storage.set_embedding_sample(
                vectorization_name=self.vectorization_name,
                sample_name=sample_name,
                embeddings_df=embeddings_df,
            )