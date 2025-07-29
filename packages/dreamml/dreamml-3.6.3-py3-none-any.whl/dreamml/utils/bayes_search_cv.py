from joblib import Parallel, delayed
from skopt import BayesSearchCV
from sklearn.model_selection._search import BaseSearchCV
from sklearn.model_selection._validation import check_cv, _fit_and_score
from sklearn.base import is_classifier, clone
from sklearn.metrics import check_scoring
from sklearn.utils.validation import indexable
from typing import Sized
import numpy as np
from scipy.stats import rankdata
from collections import defaultdict
from functools import partial


class BayesSearchCVF(BayesSearchCV, BaseSearchCV):
    """
    Bayesian optimization search over hyperparameters.

    This class extends `BayesSearchCV` and `BaseSearchCV` to perform hyperparameter
    optimization using Bayesian methods. It searches over specified parameter spaces
    to find the best combination of hyperparameters based on cross-validated performance.

    Args:
        estimator: The object to use to fit the data. This should implement the
            scikit-learn estimator interface.
        search_spaces: Dictionary with parameters names (`str`) as keys and distributions
            or lists of parameters to try. This can include nested parameter
            spaces for different estimators.
        optimizer_kwargs (dict, optional): Extra arguments to pass to the optimizer.
        n_iter (int, default=50): Number of parameter settings that are sampled.
            Trades off runtime vs quality of the solution.
        scoring (str or callable, optional): A single string or a callable to evaluate
            the predictions on the test set.
        fit_params (dict, optional): Parameters to pass to the fit method of the estimator.
        n_jobs (int, default=1): Number of parallel jobs to run.
        n_points (int, default=1): Number of points to evaluate at each iteration.
        refit (bool, default=True): Refit the best estimator with the entire dataset.
        cv (int, cross-validation generator, or an iterable, optional): Determines the
            cross-validation splitting strategy.
        verbose (int, default=0): Controls the verbosity of the output.
        pre_dispatch (str, int, or None, default="2*n_jobs"): Controls the number of jobs
            that get dispatched during parallel execution.
        random_state (int, RandomState instance or None, default=None): Random state for
            reproducibility.
        error_score (str or numeric, default="raise"): Value to assign to the score if
            an error occurs in estimator fitting. If set to "raise", the error is raised.
        return_train_score (bool, default=False): If `True`, the training score is
            included in the `cv_results_`.

    Raises:
        ValueError: If the `search_spaces` is not valid.
    """

    def __init__(
        self,
        estimator,
        search_spaces,
        optimizer_kwargs=None,
        n_iter=50,
        scoring=None,
        fit_params=None,
        n_jobs=1,
        n_points=1,
        refit=True,
        cv=None,
        verbose=0,
        pre_dispatch="2*n_jobs",
        random_state=None,
        error_score="raise",
        return_train_score=False,
    ):
        """
        Initialize the BayesSearchCVF with the provided parameters.

        Args:
            estimator: The object to use to fit the data.
            search_spaces: Dictionary with parameters names as keys and distributions
                or lists of parameters to try.
            optimizer_kwargs (dict, optional): Extra arguments to pass to the optimizer.
            n_iter (int, default=50): Number of parameter settings that are sampled.
            scoring (str or callable, optional): A single string or a callable to evaluate
                the predictions on the test set.
            fit_params (dict, optional): Parameters to pass to the fit method of the estimator.
            n_jobs (int, default=1): Number of parallel jobs to run.
            n_points (int, default=1): Number of points to evaluate at each iteration.
            refit (bool, default=True): Refit the best estimator with the entire dataset.
            cv (int, cross-validation generator, or an iterable, optional): Determines the
                cross-validation splitting strategy.
            verbose (int, default=0): Controls the verbosity of the output.
            pre_dispatch (str, int, or None, default="2*n_jobs"): Controls the number of jobs
                that get dispatched during parallel execution.
            random_state (int, RandomState instance or None, default=None): Random state for
                reproducibility.
            error_score (str or numeric, default="raise"): Value to assign to the score if
                an error occurs in estimator fitting.
            return_train_score (bool, default=False): If `True`, the training score is
                included in the `cv_results_`.

        Raises:
            ValueError: If the `search_spaces` is not valid.
        """
        self.search_spaces = search_spaces
        self.n_iter = n_iter
        self.n_points = n_points
        self.random_state = random_state
        self.optimizer_kwargs = optimizer_kwargs
        self._check_search_space(self.search_spaces)
        self.fit_params = fit_params

        BaseSearchCV.__init__(
            self,
            estimator=estimator,
            scoring=scoring,
            n_jobs=n_jobs,
            refit=refit,
            cv=cv,
            verbose=verbose,
            pre_dispatch=pre_dispatch,
            error_score=error_score,
            return_train_score=return_train_score,
        )

    def _fit(self, X, y, groups, parameter_iterable):
        """
        Fit the model using Bayesian optimization over the provided parameter space.

        This method performs the search over hyperparameters by fitting the estimator
        on different parameter combinations and evaluating their performance using
        cross-validation.

        Args:
            X: Training data.
            y: Target values.
            groups: Group labels for the samples used while splitting the dataset.
            parameter_iterable: Iterable over parameter settings to try.

        Returns:
            self: Returns the instance itself.

        Raises:
            Exception: If an error occurs during the fitting of the estimator.
        """
        estimator = self.estimator
        cv = check_cv(self.cv, y, classifier=is_classifier(estimator))
        self.scorer_ = check_scoring(self.estimator, scoring=self.scoring)

        X, y, groups = indexable(X, y, groups)
        n_splits = cv.get_n_splits(X, y, groups)
        if self.verbose > 0 and isinstance(parameter_iterable, Sized):
            n_candidates = len(parameter_iterable)
            print(
                "Fitting {0} folds for each of {1} candidates, totalling"
                " {2} fits".format(n_splits, n_candidates, n_candidates * n_splits)
            )

        base_estimator = clone(self.estimator)
        pre_dispatch = self.pre_dispatch

        cv_iter = list(cv.split(X, y, groups))
        out = Parallel(
            n_jobs=self.n_jobs, verbose=self.verbose, pre_dispatch=pre_dispatch
        )(
            delayed(_fit_and_score)(
                clone(base_estimator),
                X,
                y,
                self.scorer_,
                train,
                test,
                self.verbose,
                parameters,
                fit_params=self.fit_params,
                return_train_score=self.return_train_score,
                return_n_test_samples=True,
                return_times=True,
                return_parameters=True,
                error_score=self.error_score,
            )
            for parameters in parameter_iterable
            for train, test in cv_iter
        )

        # if one choose to see train score, "out" will contain train score info
        if self.return_train_score:
            (
                fit_failed,
                test_scores,
                train_scores,
                test_sample_counts,
                fit_time,
                score_time,
                parameters,
            ) = zip(*[d.values() for d in out])
        else:
            (
                fit_failed,
                test_scores,
                test_sample_counts,
                fit_time,
                score_time,
                parameters,
            ) = zip(*[d.values() for d in out])

        candidate_params = parameters[::n_splits]
        n_candidates = len(candidate_params)

        results = dict()

        def _store(key_name, array, weights=None, splits=False, rank=False):
            """
            Store the scores and times in the `cv_results_` dictionary.

            Args:
                key_name (str): The name of the metric (e.g., 'test_score').
                array (list): The list of scores or times to store.
                weights (array-like, optional): Weights for averaging.
                splits (bool, default=False): Whether to store scores for each split.
                rank (bool, default=False): Whether to store the rank of the scores.

            Returns:
                None
            """
            array = np.array(array, dtype=np.float64).reshape(n_candidates, n_splits)
            if splits:
                for split_i in range(n_splits):
                    results["split%d_%s" % (split_i, key_name)] = array[:, split_i]

            array_means = np.average(array, axis=1, weights=weights)
            results["mean_%s" % key_name] = array_means
            # Weighted std is not directly available in numpy
            array_stds = np.sqrt(
                np.average(
                    (array - array_means[:, np.newaxis]) ** 2, axis=1, weights=weights
                )
            )
            results["std_%s" % key_name] = array_stds

            if rank:
                results["rank_%s" % key_name] = np.asarray(
                    rankdata(-array_means, method="min"), dtype=np.int32
                )

        _store("test_score", test_scores, splits=True, rank=True, weights=None)
        if self.return_train_score:
            _store("train_score", train_scores, splits=True)
        _store("fit_time", fit_time)
        _store("score_time", score_time)

        best_index = np.flatnonzero(results["rank_test_score"] == 1)[0]
        best_parameters = candidate_params[best_index]

        # Use one MaskedArray and mask all the places where the param is not
        # applicable for that candidate. Use defaultdict as each candidate may
        # not contain all the params
        param_results = defaultdict(
            partial(
                np.ma.array,
                np.empty(
                    n_candidates,
                ),
                mask=True,
                dtype=object,
            )
        )
        for cand_i, params in enumerate(candidate_params):
            for name, value in params.items():
                # An all masked empty array gets created for the key
                # `"param_%s" % name` at the first occurence of `name`.
                # Setting the value at an index also unmasks that index
                param_results["param_%s" % name][cand_i] = value

        results.update(param_results)

        # Store a list of param dicts at the key 'params'
        results["params"] = candidate_params

        self.cv_results_ = results
        self.best_index_ = best_index
        self.n_splits_ = n_splits

        if self.refit:
            # Fit the best estimator using the entire dataset
            # Clone first to work around broken estimators
            best_estimator = clone(base_estimator).set_params(**best_parameters)
            if y is not None:
                best_estimator.fit(X, y, **self.fit_params)
            else:
                best_estimator.fit(X, **self.fit_params)
            self.best_estimator_ = best_estimator
        return self