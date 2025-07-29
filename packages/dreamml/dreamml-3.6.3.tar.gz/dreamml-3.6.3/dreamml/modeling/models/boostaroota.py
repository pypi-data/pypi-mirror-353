import logging
from typing import Optional

import numpy as np
import pandas as pd
import xgboost as xgb
import operator
import warnings
import shap
import lightgbm as lgb
import time

########################################################################################
#
# Main Class and Methods
#
########################################################################################
from dreamml.logging import get_logger

_logger = get_logger(__name__)


class BoostARoota(object):
    """BoostARoota for feature selection using the BoostARoota algorithm.

    This class implements the BoostARoota algorithm for feature selection, which 
    iteratively removes less important features based on feature importance metrics 
    derived from gradient boosting models or user-specified classifiers.

    Attributes:
        metric: The metric to optimize in XGBoost.
        clf: The classifier to use for feature importance if not using the metric.
        cutoff: The cutoff value for feature importance comparison.
        iters: Number of iterations per round.
        max_rounds: Maximum number of rounds to perform.
        delta: Threshold for the stopping criteria.
        silent: If True, suppresses logging output.
        shap_flag: If True, uses SHAP values for feature importance.
        keep_vars_: Variables retained after feature selection.
        _logger: Logger instance for logging.
    """

    def __init__(
        self,
        metric=None,
        clf=None,
        cutoff=4,
        iters=10,
        max_rounds=100,
        delta=0.1,
        silent=False,
        shap_flag=True,
        logger: Optional[logging.Logger] = None,
    ):
        """Initializes the BoostARoota instance with the specified parameters.

        Args:
            metric: The metric to optimize in XGBoost. Defaults to None.
            clf: The classifier to use for feature importance if not using the metric. Defaults to None.
            cutoff: The cutoff value for feature importance comparison. Defaults to 4.
            iters: Number of iterations per round. Defaults to 10.
            max_rounds: Maximum number of rounds to perform. Defaults to 100.
            delta: Threshold for the stopping criteria. Defaults to 0.1.
            silent: If True, suppresses logging output. Defaults to False.
            shap_flag: If True, uses SHAP values for feature importance. Defaults to True.
            logger: Optional logger instance. Defaults to None.

        Raises:
            ValueError: If neither metric nor clf is provided.
            ValueError: If cutoff is less than or equal to 0.
            ValueError: If iters is less than or equal to 0.
            ValueError: If delta is not between 0 and 1.
        """
        self.metric = metric
        self.clf = clf
        self.cutoff = cutoff
        self.iters = iters
        self.max_rounds = max_rounds
        self.delta = delta
        self.silent = silent
        self.shap_flag = shap_flag
        self.keep_vars_ = None
        self._logger = logger

        # Throw errors if the inputted parameters don't meet the necessary criteria
        if (metric is None) and (clf is None):
            raise ValueError("You must provide either 'metric' or 'clf' as arguments.")
        if cutoff <= 0:
            raise ValueError(
                f"cutoff should be greater than 0. You entered {cutoff}."
            )
        if iters <= 0:
            raise ValueError(f"iters should be greater than 0. You entered {iters}.")
        if (delta <= 0) or (delta > 1):
            raise ValueError(f"delta should be between 0 and 1, was {delta}.")

        # Issue warnings for parameters to still let it run
        if (metric is not None) and (clf is not None):
            warnings.warn(
                "Both 'metric' and 'clf' were provided. Defaulting to 'clf' and ignoring 'metric'."
            )
        if delta < 0.02:
            warnings.warn(
                "WARNING: Setting delta below 0.02 may not converge on a solution."
            )
        if max_rounds < 1:
            warnings.warn(
                "WARNING: Setting max_rounds below 1 will automatically set it to 1."
            )

    def fit(self, x, y):
        """Fits the BoostARoota model to the data.

        Args:
            x: The feature dataframe.
            y: The target variable.

        Returns:
            self: Returns the instance itself.

        Raises:
            ValueError: If the input parameters are invalid.
        """
        self.keep_vars_ = _BoostARoota(
            x,
            y,
            metric=self.metric,
            clf=self.clf,
            cutoff=self.cutoff,
            iters=self.iters,
            max_rounds=self.max_rounds,
            delta=self.delta,
            silent=self.silent,
            shap_flag=self.shap_flag,
            logger=self._logger,
        )
        return self

    def transform(self, x):
        """Transforms the data by retaining only the selected features.

        Args:
            x: The feature dataframe to transform.

        Returns:
            pd.DataFrame: The transformed dataframe with selected features.

        Raises:
            ValueError: If the model has not been fitted yet.
        """
        if self.keep_vars_ is None:
            raise ValueError("You need to fit the model first.")
        return x[self.keep_vars_]

    def fit_transform(self, x, y):
        """Fits the model and transforms the data in a single step.

        Args:
            x: The feature dataframe.
            y: The target variable.

        Returns:
            pd.DataFrame: The transformed dataframe with selected features.
        """
        self.fit(x, y)
        return self.transform(x)


########################################################################################
#
# Helper Functions to do the Heavy Lifting
#
########################################################################################


def _create_shadow(x_train):
    """Creates shadow features by shuffling each feature in the dataframe.

    Shadow features are copies of the original features with their values randomly shuffled.
    This helps in determining feature importance by comparing original features with their
    shadow counterparts.

    Args:
        x_train (pd.DataFrame): The original feature dataframe.

    Returns:
        Tuple[pd.DataFrame, List[str]]: 
            - The combined dataframe containing original and shadow features.
            - A list of shadow feature names.
    """
    x_shadow = x_train.copy()
    for c in x_shadow.columns:
        np.random.shuffle(x_shadow[c].values)
    # Rename the shadow features
    shadow_names = ["ShadowVar" + str(i + 1) for i in range(x_train.shape[1])]
    x_shadow.columns = shadow_names
    # Combine original and shadow dataframes
    new_x = pd.concat([x_train, x_shadow], axis=1)
    return new_x, shadow_names


########################################################################################
#
# BoostARoota
#
########################################################################################


def _reduce_vars_xgb(
    x,
    y,
    metric,
    this_round,
    cutoff,
    n_iterations,
    delta,
    silent,
    shap_flag,
    logger=None,
):
    """Reduces variables using XGBoost-based feature importance.

    This function runs multiple iterations of XGBoost training with shadow features
    to determine the importance of original features. It calculates the mean importance
    and retains features that have higher importance than the mean shadow importance.

    Args:
        x (pd.DataFrame): The feature dataframe.
        y (pd.Series or np.ndarray): The target variable.
        metric (str): The metric to optimize in XGBoost.
        this_round (int): The current round number.
        cutoff (int): The cutoff value for feature importance comparison.
        n_iterations (int): Number of iterations to perform.
        delta (float): Threshold for stopping criteria.
        silent (bool): If True, suppresses logging output.
        shap_flag (bool): If True, uses SHAP values for feature importance.
        logger (Optional[logging.Logger]): Logger instance. Defaults to None.

    Returns:
        Tuple[bool, pd.Series]:
            - criteria (bool): Whether the stopping criteria have been met.
            - keep_vars (pd.Series): The names of the variables to retain.
    """
    logger = logger or _logger

    param = {
        "eval_metric": metric,
        "silent": 1,
    }
    for i in range(1, n_iterations + 1):
        seed = 10**5 + 10**3 * this_round + 10 * i
        param["seed"] = seed
        np.random.seed(seed)
        # Create shadow variables and prepare data
        new_x, shadow_names = _create_shadow(x)
        dtrain = xgb.DMatrix(new_x, label=y)
        bst = xgb.train(param, dtrain, verbose_eval=False)
        if i == 1:
            df = pd.DataFrame({"feature": new_x.columns})

        if shap_flag:
            logger.debug("Using BoostARoota with SHAP flag.")
            explainer = shap.TreeExplainer(bst)
            importance_values = explainer.shap_values(new_x)
            columns = list(x.columns) + list(shadow_names)
            importance_values = np.abs(importance_values.mean(axis=0))
            importance = dict(zip(columns, importance_values))
        else:
            logger.debug("Using BoostARoota without SHAP flag.")
            importance = bst.get_fscore()

        importance = sorted(importance.items(), key=operator.itemgetter(1))
        df2 = pd.DataFrame(importance, columns=["feature", f"fscore{i}"])
        df2[f"fscore{i}"] = df2[f"fscore{i}"] / df2[f"fscore{i}"].sum()
        df = pd.merge(df, df2, on="feature", how="outer")
        if not silent:
            logger.info(f"Round: {this_round}, iteration: {i}")

    df["Mean"] = df.mean(axis=1)
    # Separate real and shadow variables
    real_vars = df[~df["feature"].isin(shadow_names)]
    shadow_vars = df[df["feature"].isin(shadow_names)]

    # Calculate mean importance from shadow variables
    mean_shadow = shadow_vars["Mean"].mean() / cutoff
    real_vars = real_vars[real_vars.Mean > mean_shadow]
    # Determine if stopping criteria are met
    if (len(real_vars["feature"]) / len(x.columns)) > (1 - delta):
        criteria = True
    else:
        criteria = False

    return criteria, real_vars["feature"]


def _reduce_vars_sklearn(
    x, y, clf, this_round, cutoff, n_iterations, delta, silent, shap_flag, logger=None
):
    """Reduces variables using a scikit-learn compatible classifier for feature importance.

    This function runs multiple iterations of model training with shadow features using
    the provided classifier to determine feature importance. It calculates the mean importance
    and retains features that have higher importance than the mean shadow importance.

    Args:
        x (pd.DataFrame): The feature dataframe.
        y (pd.Series or np.ndarray): The target variable.
        clf: The classifier to use for feature importance.
        this_round (int): The current round number.
        cutoff (int): The cutoff value for feature importance comparison.
        n_iterations (int): Number of iterations to perform.
        delta (float): Threshold for stopping criteria.
        silent (bool): If True, suppresses logging output.
        shap_flag (bool): If True, uses SHAP values for feature importance.
        logger (Optional[logging.Logger]): Logger instance. Defaults to None.

    Returns:
        Tuple[bool, pd.Series]:
            - criteria (bool): Whether the stopping criteria have been met.
            - keep_vars (pd.Series): The names of the variables to retain.
    """
    logger = logger or _logger

    # Set up parameters for LightGBM
    params = {
        "objective": "binary",
        "boosting_type": "gbdt",
        "learning_rate": 0.05134,
        "num_leaves": 51,
        "max_depth": 3,
        "subsample": 0.7,
        "verbose": -1,
    }
    for i in range(1, n_iterations + 1):
        # Create shadow variables and prepare data
        new_x, shadow_names = _create_shadow(x)
        seed = 10**5 + 10**3 * this_round + 10 * i
        params["seed"] = seed
        dtrain = lgb.Dataset(new_x, label=y)
        bst = lgb.train(params, dtrain, verbose_eval=False)

        if i == 1:
            df = pd.DataFrame({"feature": new_x.columns})
            df2 = df.copy()

        if shap_flag:
            logger.debug("Using LGBM BoostARoota with SHAP flag.")
            explainer = shap.TreeExplainer(bst)
            importance_values = explainer.shap_values(new_x)[0]
            importance = np.abs(importance_values.mean(axis=0))
            df2[f"fscore{i}"] = importance
        else:
            importance = bst.feature_importance()
            df2[f"fscore{i}"] = importance
            logger.debug("Using LGBM BoostARoota without SHAP flag.")

        df2[f"fscore{i}"] = df2[f"fscore{i}"] / df2[f"fscore{i}"].sum()
        df = pd.merge(df, df2, on="feature", how="outer")
        if not silent:
            logger.info(f"Round: {this_round}, iteration: {i}")

    df["Mean"] = df.mean(axis=1)
    # Separate real and shadow variables
    real_vars = df[~df["feature"].isin(shadow_names)]
    shadow_vars = df[df["feature"].isin(shadow_names)]

    # Calculate mean importance from shadow variables
    mean_shadow = shadow_vars["Mean"].mean() / cutoff
    real_vars = real_vars[real_vars.Mean > mean_shadow]

    # Determine if stopping criteria are met
    if (len(real_vars["feature"]) / len(x.columns)) > (1 - delta):
        criteria = True
    else:
        criteria = False

    return criteria, real_vars["feature"]


# Main function exposed to run the algorithm
def _BoostARoota(
    x, y, metric, clf, cutoff, iters, max_rounds, delta, silent, shap_flag, logger=None
):
    """Executes the BoostARoota feature selection algorithm.

    This function iteratively reduces the feature set based on feature importance until
    the stopping criteria are met or the maximum number of rounds is reached.

    Args:
        x (pd.DataFrame): The feature dataframe, one-hot encoded.
        y (pd.Series or np.ndarray): The target variable labels.
        metric (str, optional): The metric to optimize in XGBoost. Defaults to None.
        clf: The classifier to use for feature importance if metric is not provided. Defaults to None.
        cutoff (int): The cutoff value for feature importance comparison.
        iters (int): Number of iterations per round.
        max_rounds (int): Maximum number of rounds to perform.
        delta (float): Threshold for stopping criteria.
        silent (bool): If True, suppresses logging output.
        shap_flag (bool): If True, uses SHAP values for feature importance.
        logger (Optional[logging.Logger]): Logger instance. Defaults to None.

    Returns:
        pd.Series: The names of the variables to retain.
    """
    new_x = x.copy()
    # Run through loop until stopping criteria are met
    i = 0
    while True:
        # Reduce the dataset on each iteration, exiting with keep_vars as final variables
        i += 1
        if clf is None:
            crit, keep_vars = _reduce_vars_xgb(
                new_x,
                y,
                metric=metric,
                this_round=i,
                cutoff=cutoff,
                n_iterations=iters,
                delta=delta,
                silent=silent,
                shap_flag=shap_flag,
                logger=logger,
            )
        else:
            crit, keep_vars = _reduce_vars_sklearn(
                new_x,
                y,
                clf=clf,
                this_round=i,
                cutoff=cutoff,
                n_iterations=iters,
                delta=delta,
                silent=silent,
                shap_flag=shap_flag,
                logger=logger,
            )
        if crit or (i >= max_rounds):
            break  # Exit and use keep_vars as final variables
        else:
            new_x = new_x[keep_vars].copy()
    if not silent:
        logger.info(f"BoostARoota ran successfully! Algorithm completed {i} rounds.")
    return keep_vars
