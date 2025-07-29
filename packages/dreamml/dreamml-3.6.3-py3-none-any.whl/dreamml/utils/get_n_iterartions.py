def get_n_iterations(shape: int) -> int:
    """
    Selects the number of optimizer iterations based on the number of observations in the development dataset.

    Args:
        shape (int): The number of observations in the development dataset.

    Returns:
        int: The number of optimizer iterations.
    """
    dict_of_shapes_and_iterations = {
        0: 300,
        10000: 200,
        25000: 150,
        50000: 100,
        75000: 50,
        100000: 20,
        200000: 10,
    }

    iterations = 0

    for key, value in dict_of_shapes_and_iterations.items():
        if shape > key:
            iterations = value

    return iterations