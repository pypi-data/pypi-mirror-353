from collections import namedtuple

AlgoInfo = namedtuple(
    "AlgoInfo",
    [
        "algo_class",
        "algo_params",
        "cat_features",
        "text_features",
        "augmentation_params",
        "bounds_params",
    ],
)
"""AlgoInfo(namedtuple): Represents the configuration information for an algorithm.

Args:
    algo_class: The class of the algorithm.
    algo_params: Parameters for initializing the algorithm.
    cat_features: The categorical features used by the algorithm.
    text_features: The text features used by the algorithm.
    augmentation_params: Parameters for data augmentation.
    bounds_params: Parameters defining the bounds for the algorithm.

Returns:
    An AlgoInfo object containing all the configuration details.

Raises:
    None
"""