from pathlib import Path
from joblib import parallel_backend
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from dreamml.logging import get_logger
from dreamml.utils.loading_utils import load_yaml
from dreamml.utils.switch_pipeline import SwitchPipeline
from dreamml.utils.bayes_search_cv import BayesSearchCVF
from dreamml.pipeline.fitter import FitterBase
from dreamml.features.text.transformers import (
    Depersonalizer,
    DigitEraser,
    PunctuationEraser,
    WordFilter,
    WordJoiner,
    WordNormalizer,
    WordSplitter,
    WordSynonyms,
    TextCleaner,
)


SYNONYMS_PATH = Path(__file__).parent.parent.parent.parent / "references/synonyms.yaml"
STANDARD_STOPWORDS_PATH = (
    Path(__file__).parent.parent.parent.parent / "references/standard_stopwords.yaml"
)
RUSSIAN_NAMES_SURNAMES_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "references/russian_names_surnames_adj.yaml"
)
_logger = get_logger(__name__)


class NLPModelBayesianOptimizerCV:
    """A class for optimizing NLP models using Bayesian Optimization with Cross-Validation.

    This class prepares a text processing and classification pipeline, defines search spaces
    for hyperparameter optimization, and performs the optimization using Bayesian search.

    Attributes:
        config: Configuration settings for the optimizer.
        fitter (FitterBase): An instance of FitterBase for cross-validation.
        standard_stopwords (set): A set of standard stopwords loaded from a YAML file.
        file_synonyms (dict): A dictionary of synonyms loaded from a YAML file.
        rus_names_dict (dict): A dictionary of Russian names and surnames loaded from a YAML file.
    """

    def __init__(
        self,
        config,
        fitter: FitterBase,
    ):
        """Initializes the NLPModelBayesianOptimizerCV with configuration and fitter.

        Args:
            config: Configuration settings for the optimizer.
            fitter (FitterBase): An instance of FitterBase for cross-validation.

        Raises:
            FileNotFoundError: If any of the YAML configuration files are not found.
            YAMLError: If there is an error parsing the YAML files.
        """
        self.config = config
        self.fitter = fitter
        self.standard_stopwords = load_yaml(STANDARD_STOPWORDS_PATH)
        self.file_synonyms = load_yaml(SYNONYMS_PATH)
        self.rus_names_dict = load_yaml(RUSSIAN_NAMES_SURNames_PATH)

    def prepare_pipeline(self, random_state: int):
        """Prepares the text processing and classification pipeline.

        This method sets up a SwitchPipeline with various text transformers and a classifier.

        Args:
            random_state (int): The random seed for reproducibility.

        Returns:
            SwitchPipeline: The configured machine learning pipeline.

        Raises:
            ValueError: If an invalid random_state is provided.
        """
        return SwitchPipeline(
            [
                (
                    "depersonalizer",
                    Depersonalizer(rus_names_dict=self.rus_names_dict, verbose=False),
                ),
                ("text_cleaner", TextCleaner()),
                ("digit_eraser", DigitEraser()),
                ("punct_eraser", PunctuationEraser()),
                (
                    "word_pipeline",
                    SwitchPipeline(
                        [
                            ("word_splitter", WordSplitter()),
                            ("word_normalizer", WordNormalizer()),
                            (
                                "word_standard_stopwords",
                                WordFilter(stop_words=set(self.standard_stopwords)),
                            ),
                            (
                                "word_additional_stopwords",
                                WordFilter(
                                    stop_words=set(
                                        self.config.data.augmentation.additional_stopwords
                                    )
                                ),
                            ),
                            (
                                "word_synonyms",
                                WordSynonyms(synonyms=self.file_synonyms),
                            ),
                            ("word_joiner", WordJoiner()),
                        ],
                        verbose=False,
                    ),
                ),
                ("vec", TfidfVectorizer(binary=True, min_df=1e-05)),
                (
                    "clf",
                    LogisticRegression(
                        C=10.0,
                        class_weight="balanced",
                        max_iter=2000,
                        n_jobs=1,
                        random_state=random_state,
                        solver="saga",
                    ),
                ),
            ],
            verbose=False,
        )

    def get_search_spaces(self, random_state: int):
        """Defines the hyperparameter search spaces for Bayesian optimization.

        This method sets up different hyperparameter configurations for the pipeline.

        Args:
            random_state (int): The random seed for reproducibility.

        Returns:
            list of dict: A list containing dictionaries of hyperparameter search spaces.

        Raises:
            ValueError: If an invalid random_state is provided.
        """
        common_space = {
            "depersonalizer__enabled": [True, False],
            "text_cleaner__enabled": [True, False],
            "digit_eraser__enabled": [True, False],
            "punct_eraser__enabled": [True, False],
            "word_pipeline__word_normalizer__enabled": [True],
            "word_pipeline__word_standard_stopwords__enabled": [True, False],
            "word_pipeline__word_additional_stopwords__enabled": [True, False],
            "word_pipeline__word_synonyms__enabled": [True, False],
            "vec__min_df": (0.00001, 0.002, "log-uniform"),
            "vec__max_df": (0.3, 1.0, "log-uniform"),
            "vec__analyzer": ["word", "char", "char_wb"],
            "vec__binary": [True, False],
            "vec__norm": ["l1", "l2"],
            # "vec__max_features": [150, 200],  # for fast debug
        }

        logreg_space = {
            **common_space,
            "clf": [
                LogisticRegression(
                    penalty="l1",
                    solver="saga",
                    class_weight="balanced",
                    random_state=random_state,
                    max_iter=2000,
                    n_jobs=1,
                )
            ],
            "clf__C": (0.1, 10.0, "log-uniform"),
            "clf__penalty": ["l1", "l2"],
        }

        return [
            {**logreg_space, "vec": [TfidfVectorizer(ngram_range=(1, 1))]},
            {**logreg_space, "vec": [TfidfVectorizer(ngram_range=(1, 2))]},
        ]

    def optimize(self, X, y):
        """Performs Bayesian hyperparameter optimization on the pipeline.

        This method fits the pipeline to the data using Bayesian search to find the best hyperparameters.

        Args:
            X: Feature matrix.
            y: Target vector.

        Returns:
            BayesSearchCVF: The optimized Bayesian search object.

        Raises:
            ValueError: If the input data X and y have incompatible shapes.
            RuntimeError: If the optimization fails to converge.
        """
        pipeline = self.prepare_pipeline(
            random_state=self.config.pipeline.reproducibility.random_seed
        )
        search_spaces = self.get_search_spaces(
            random_state=self.config.pipeline.reproducibility.random_seed
        )

        opt = BayesSearchCVF(
            pipeline,
            search_spaces=[(space, 30) for space in search_spaces],
            cv=self.fitter.cv.cv,
            n_iter=self.config.stages.optimization.n_iterations,
            random_state=self.config.pipeline.reproducibility.random_seed,
            scoring="neg_log_loss",
            return_train_score=False,
            refit=True,
            error_score=0.0,
            n_jobs=self.config.pipeline.parallelism,
            verbose=self.config.pipeline.verbose,
        )
        with parallel_backend("multiprocessing"):
            opt.fit(X, y)
        return opt

    @staticmethod
    def get_best_hyperparams(opt: BayesSearchCVF):
        """Extracts the best hyperparameters from the optimized Bayesian search.

        This method retrieves the best parameters for the classifier, vectorizer, and text preprocessing steps.

        Args:
            opt (BayesSearchCVF): The optimized Bayesian search object.

        Returns:
            tuple:
                - dict: Best parameters for the classifier excluding 'n_jobs'.
                - dict: Best parameters for the vectorizer.
                - dict: Best parameters for text preprocessing steps.

        Raises:
            AttributeError: If the BayesSearchCVF object does not have the necessary attributes.
        """
        clf_best_params = opt.best_params_["clf"].get_params()
        clf_best_params = {k: v for k, v in clf_best_params.items() if k != "n_jobs"}
        vec_best_params = opt.best_params_["vec"].get_params()
        text_preproc_best_params = {
            "depersonalizer": opt.best_params_["depersonalizer__enabled"],
            "text_cleaner": opt.best_params_["text_cleaner__enabled"],
            "digit_eraser": opt.best_params_["digit_eraser__enabled"],
            "punct_eraser": opt.best_params_["punct_eraser__enabled"],
            "word_pipeline": {
                "word_normalizer": opt.best_params_[
                    "word_pipeline__word_normalizer__enabled"
                ],
                "word_standard_stopwords": opt.best_params_[
                    "word_pipeline__word_standard_stopwords__enabled"
                ],
                "word_additional_stopwords": opt.best_params_[
                    "word_pipeline__word_additional_stopwords__enabled"
                ],
                "word_synonyms": opt.best_params_[
                    "word_pipeline__word_synonyms__enabled"
                ],
            },
        }
        return clf_best_params, vec_best_params, text_preproc_best_params