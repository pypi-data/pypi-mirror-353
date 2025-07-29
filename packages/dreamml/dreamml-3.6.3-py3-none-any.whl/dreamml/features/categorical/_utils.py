"""
Module providing functions for handling categorical features.

Available entities:
- find_categorical_features: Function to identify categorical features in a given dataset.
- encode_categorical: Applies CategoricalEncoder to each dataset.

=============================================================================
"""

from .categorical_encoder import CategoricalFeaturesTransformer


def encode_categorical(config, **eval_sets):
    """Apply CategoricalEncoder to each dataset in eval_sets.

    Args:
        config (dict): Configuration settings for the transformer.
        **eval_sets (Dict[str, Tuple[pandas.DataFrame, pandas.Series]]):
            Variable-length keyword arguments representing different datasets.
            Each key is the name of the dataset (e.g., 'train', 'valid'), and
            each value is a tuple containing the features DataFrame and the target Series.

    Returns:
        Tuple[Dict[str, Tuple[pandas.DataFrame, pandas.Series]], CategoricalFeaturesTransformer]:
            A tuple containing:
            - The transformed eval_sets with encoded categorical features.
            - The instance of CategoricalFeaturesTransformer used for the transformation.

    Raises:
        KeyError: If the 'train' dataset is not provided in eval_sets.
    """
    transformer = CategoricalFeaturesTransformer(config)
    train = transformer.fit_transform(eval_sets["train"][0])
    eval_sets["train"] = (train, eval_sets["train"][1])

    transformed_samples = [name for name in eval_sets if name != "train"]
    for sample in transformed_samples:
        df = transformer.transform(eval_sets[sample][0])
        eval_sets[sample] = (df, eval_sets[sample][1])

    return eval_sets, transformer