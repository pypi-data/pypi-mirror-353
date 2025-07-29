def make_weights_for_balanced_classes(labels, num_labels):
    """
    Create a list of weights to balance classes based on their frequency.

    Args:
        labels (list of int): A list of integer labels representing class assignments.
        num_labels (int): The total number of unique classes.

    Returns:
        list of float: A list of weights corresponding to each label, 
                       where each weight is inversely proportional to the class frequency.

    Raises:
        IndexError: If a label in `labels` is not in the range [0, num_labels - 1].
        TypeError: If `labels` is not a list of integers or if `num_labels` is not an integer.
    """
    total_count = len(labels)
    count_per_class = [0] * num_labels
    for label in labels:
        count_per_class[label] += 1
    weight_per_class = [total_count / c if c > 0 else 0 for c in count_per_class]
    weights = [weight_per_class[label] for label in labels]
    return weights